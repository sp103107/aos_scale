from __future__ import annotations

import json
import math
import re
import uuid
from pathlib import Path
from typing import Any, Callable

from .actions import ActionRequest, ActionResult, ActionType
from .alice import AliceResponseAgent, TruthClass
from .device_service import DeviceMode, DeviceService, SimulatedFirmwareTransport
from .models import StabilityProfile, now_rfc3339
from .run_manager import LoadedRun, RunDefinition, RunManager
from .scale_control import ScaleControlService
from .scale_profiles import (
    ScaleProfile,
    ScaleProfileStore,
    ScaleStabilityParams,
    validate_device_id,
)
from .operator_beep import play_operator_beep
from .operator_voice import speak_operator_cue
from .settings import AppSettings, SettingsStore
from .stability_sensitivity import apply_lock_sensitivity
from .state_machine import CaptureMachine, State
from .storage import atomic_json, parse_jsonl


class InvalidActionState(RuntimeError):
    pass


_ACTIVE_CAPTURE_STATES = {
    State.BARCODE_CAPTURED,
    State.WAITING_FOR_LOAD,
    State.WEIGHING,
    State.WAITING_FOR_STABLE_WEIGHT,
    State.WEIGHT_STABLE,
    State.AUTO_RECORD,
    State.MANUAL_CONFIRM,
    State.LOCAL_COMMIT_PENDING,
    State.RECORD_SAVED,
}


class ApplicationController:
    """Transport-neutral application controller.

    The controller routes canonical actions into the existing CaptureMachine,
    SessionStore, device service, and Alice. It does not implement a second
    persistence authority or a competing capture state machine.
    """

    def __init__(self, config_dir: str | Path, *, beep: Callable[[str], None] | None = None):
        self.settings_store = SettingsStore(config_dir)
        self.run_manager = RunManager(self.settings_store)
        self.agent = AliceResponseAgent()
        self.loaded_run: LoadedRun | None = None
        self.machine: CaptureMachine | None = None
        self.device: DeviceService | None = None
        self.scale: ScaleControlService | None = None
        self.feedback_events: list[str] = []
        audio = beep

        def _beep(kind: str) -> None:
            self.feedback_events.append(kind)
            if audio is not None:
                audio(kind)
            else:
                play_operator_beep(kind)

        self.beep = _beep
        self.last_alice_response: dict[str, Any] | None = None
        self.last_record: dict[str, Any] | None = None
        self._action_cache: dict[str, ActionResult] = {}
        self.active_scale_profile: ScaleProfile | None = None
        self._scale_profile_store = ScaleProfileStore(self.settings_store.config_dir)

    @property
    def scale_profiles(self) -> ScaleProfileStore:
        return self._scale_profile_store

    def _default_stability_profile(self) -> StabilityProfile:
        """Hanging settle on physical; settle_ms=0 for simulator / software dry-runs.

        Characterized scale profiles still install their own settle_ms (typically 1200).
        Pre-characterization physical default matches the hanging model hold.
        """
        settle_ms = 0
        if self.device is not None and self.device.mode != DeviceMode.SERIAL_SIMULATOR:
            settle_ms = 1200
        return StabilityProfile(settle_ms=settle_ms)

    def _resolve_stability_profile(self, device_id: str | None = None) -> StabilityProfile:
        device_id = device_id or (self.device.status.device_id if self.device else None)
        if not device_id:
            return self._default_stability_profile()
        try:
            active = self._scale_profile_store.get_active_for_device(str(device_id))
        except ValueError:
            return self._default_stability_profile()
        if active is None:
            return self._default_stability_profile()
        self.active_scale_profile = active
        return active.to_stability_profile()

    def _effective_stability_profile(self, device_id: str | None = None) -> StabilityProfile:
        base = self._resolve_stability_profile(device_id)
        return apply_lock_sensitivity(base, self.settings.lock_sensitivity)

    def _install_effective_profile(self, device_id: str | None = None) -> None:
        if self.machine is not None:
            self.machine.set_profile(self._effective_stability_profile(device_id))

    def _is_auto_record_path(self, request: ActionRequest) -> bool:
        if not self.loaded_run:
            return False
        mode = self.loaded_run.definition.capture_mode
        if request.action_type == ActionType.READING_INGEST.value:
            return mode == "automatic"
        if request.action_type == ActionType.CAPTURE_CONFIRM.value:
            if mode == "automatic":
                return True
            return bool(self.settings.auto_record_after_lock)
        return False

    def _play_record_alert(self, feedback_kind: str) -> None:
        mode = self.settings.auto_record_alert
        if mode == "off":
            return
        if feedback_kind == "warning":
            if mode in {"beep", "both"}:
                self.feedback_events.append("warning")
                play_operator_beep("warning")
            if mode in {"voice", "both"}:
                speak_operator_cue("Saved with warning")
            return
        if mode in {"beep", "both"}:
            self.feedback_events.append("success")
            play_operator_beep("success")
        if mode in {"voice", "both"}:
            speak_operator_cue(self.settings.auto_record_alert_phrase)

    def _apply_active_scale_profile(self) -> dict[str, Any] | None:
        """After STATUS: load active profile by device_id, apply SET_CAL if needed, install stability.

        When STATUS already reports a factor matching the active profile, skip SET_CAL
        (SR11) and only install stability gates — avoids stream interleaving on Resume.
        """
        if not self.device or not self.device.status.connected:
            return None
        device_id = self.device.status.device_id
        if not device_id:
            return None
        try:
            active = self._scale_profile_store.get_active_for_device(str(device_id))
        except ValueError:
            # Non-BBWS simulator IDs are valid on the wire but not profile-bound yet.
            return None
        if active is None:
            self.active_scale_profile = None
            return None
        status = self.device.read_status()
        reported = float(status["calibration_factor"])
        target = float(active.calibration_factor)
        if math.isclose(reported, target, rel_tol=1e-5, abs_tol=1e-5):
            stability = self._effective_stability_profile(str(device_id))
            if self.machine is not None:
                self.machine.set_profile(stability)
            self.active_scale_profile = active
            return {
                "profile_id": active.profile_id,
                "device_id": active.device_id,
                "calibration_factor": reported,
                "stability_profile_id": stability.profile_id,
                "set_cal_applied": False,
            }
        applied = self.device.apply_calibration_factor(target)
        stability = self._effective_stability_profile(str(device_id))
        if self.machine is not None:
            self.machine.set_profile(stability)
        self.active_scale_profile = active
        return {
            "profile_id": active.profile_id,
            "device_id": active.device_id,
            "calibration_factor": applied["calibration_factor"],
            "stability_profile_id": stability.profile_id,
            "set_cal_applied": True,
        }

    def list_scale_profiles(self, *, include_archived: bool = False) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self._scale_profile_store.list_profiles(include_archived=include_archived)]

    def archive_scale_profile(self, profile_id: str) -> dict[str, Any]:
        return self._scale_profile_store.archive(profile_id).to_dict()

    def set_connected_device_id(self, device_id: str) -> dict[str, Any]:
        if not self.device or not self.device.status.connected:
            raise InvalidActionState("connect a scale before setting device id")
        device_id = validate_device_id(device_id)
        return self.device.set_device_id(device_id)

    def _upsert_calibration_profile(
        self,
        *,
        device_id: str,
        calibration_factor: float,
        calibration_receipt_id: str | None,
        firmware_version: str | None = None,
    ) -> ScaleProfile:
        """Create or update the active profile after a successful calibration accept."""
        device_id = validate_device_id(device_id)
        active = self._scale_profile_store.get_active_for_device(device_id)
        if active is not None:
            return self._scale_profile_store.update(
                active.profile_id,
                calibration_factor=float(calibration_factor),
                calibration_receipt_id=calibration_receipt_id,
                firmware_version=firmware_version or active.firmware_version,
                status="active",
            )
        return self._scale_profile_store.create(
            name=f"{device_id} profile",
            device_id=device_id,
            calibration_factor=float(calibration_factor),
            calibration_receipt_id=calibration_receipt_id,
            firmware_version=firmware_version,
            activate=True,
        )

    @property
    def state(self) -> str:
        if self.loaded_run is None:
            return State.NO_RUN.value
        if self.machine is None:
            return State.RUN_READY.value
        return self.machine.state.value

    @property
    def settings(self) -> AppSettings:
        return self.settings_store.load()

    def operator_state_label(self) -> str:
        labels = {
            "NO_RUN": "NO RUN",
            "RUN_READY": "RUN READY",
            "DISCONNECTED": "DEVICE DISCONNECTED",
            "DEVICE_CONNECTING": "CONNECTING SCALE",
            "DEVICE_READY": "SCALE READY",
            "WAITING_FOR_BARCODE": "READY TO SCAN",
            "BARCODE_CAPTURED": "BARCODE SCANNED",
            "WAITING_FOR_LOAD": "WAITING FOR PLANT",
            "WEIGHING": "WEIGHING",
            "WAITING_FOR_STABLE_WEIGHT": "WEIGHING — WAITING FOR STABILITY",
            "WEIGHT_STABLE": "STABLE — LOCK WEIGHT",
            "MANUAL_CONFIRM": "LOCKED — CONFIRM & RECORD",
            "LOCAL_COMMIT_PENDING": "RECORDING",
            "RECORD_SAVED": "SAVED",
            "RECOVERY_REQUIRED": "RECOVERY REQUIRED",
            "BLOCKED": "BLOCKED",
            "ERROR": "NOT SAVED",
            "RUN_FINISHED": "RUN FINISHED",
        }
        return labels.get(self.state, self.state.replace("_", " "))

    def _refresh_alice_for_state(self, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
        session = self.loaded_run.store.context.session_id if self.loaded_run else None
        response = self.agent.respond(self.state, context=context or {}, session_id=session).to_dict()
        self.last_alice_response = response
        return response

    def _result(self, request: ActionRequest, status: str, truth: str, message: str,
                data: dict[str, Any] | None = None, *, terminal: bool = True) -> ActionResult:
        result = ActionResult(
            action_id=request.action_id,
            action_type=request.action_type,
            status=status,
            truth_class=truth,
            state=self.state,
            message=message,
            data=data or {},
            terminal=terminal,
        )
        if request.idempotency_key:
            self._action_cache[request.idempotency_key] = result
        return result

    def dispatch(self, request: ActionRequest) -> ActionResult:
        request.validate()
        if request.idempotency_key and request.idempotency_key in self._action_cache:
            return self._action_cache[request.idempotency_key]
        if request.source in {"bluetooth", "wifi"}:
            setting = self.settings
            enabled = setting.bluetooth_enabled if request.source == "bluetooth" else setting.wifi_enabled
            if not enabled:
                return self._result(request, "blocked", "BLOCKED", f"{request.source} transport is disabled by default")
        handlers = {
            ActionType.RUN_NEW.value: self._run_new,
            ActionType.RUN_LOAD.value: self._run_load,
            ActionType.RUN_RESUME.value: self._run_resume,
            ActionType.RUN_FINISH.value: self._run_finish,
            ActionType.SETTINGS_DATA_LOCATION_SET.value: self._set_data_location,
            ActionType.SETTINGS_CAPTURE_MODE_SET.value: self._set_capture_mode,
            ActionType.SETTINGS_DISPLAY_UNIT_SET.value: self._set_display_unit,
            ActionType.DEVICE_DISCOVER.value: self._device_discover,
            ActionType.DEVICE_CONNECT.value: self._device_connect,
            ActionType.DEVICE_DISCONNECT.value: self._device_disconnect,
            ActionType.DEVICE_STATUS.value: self._device_status,
            ActionType.DEVICE_PING.value: self._device_ping,
            ActionType.DEVICE_RECONNECT.value: self._device_reconnect,
            ActionType.DEVICE_STREAM_START.value: self._device_stream_start,
            ActionType.DEVICE_STREAM_STOP.value: self._device_stream_stop,
            ActionType.SCALE_ZERO.value: self._scale_zero,
            ActionType.SCALE_CONTAINER_TARE_CAPTURE.value: self._tare_capture,
            ActionType.SCALE_CONTAINER_TARE_SET.value: self._tare_set,
            ActionType.SCALE_CALIBRATION_START.value: self._calibration_start,
            ActionType.SCALE_CALIBRATION_SAMPLE.value: self._calibration_sample,
            ActionType.SCALE_CALIBRATION_TEST.value: self._calibration_test,
            ActionType.SCALE_CALIBRATION_ACCEPT.value: self._calibration_accept,
            ActionType.SCALE_CALIBRATION_CANCEL.value: self._calibration_cancel,
            ActionType.SCALE_DEVICE_ID_SET.value: self._scale_device_id_set,
            ActionType.SCALE_PROFILE_LIST.value: self._scale_profile_list,
            ActionType.SCALE_PROFILE_ACTIVATE.value: self._scale_profile_activate,
            ActionType.SCALE_PROFILE_ARCHIVE.value: self._scale_profile_archive,
            ActionType.SCALE_PROFILE_RENAME.value: self._scale_profile_rename,
            ActionType.SCALE_CALIBRATION_CHARACTERIZE.value: self._calibration_characterize,
            ActionType.SCALE_PROFILE_CONFIRM_STABILITY.value: self._scale_profile_confirm_stability,
            ActionType.BARCODE_SUBMIT.value: self._barcode_submit,
            ActionType.READING_INGEST.value: self._reading_ingest,
            ActionType.CAPTURE_WEIGHT_LOCK.value: self._capture_weight_lock,
            ActionType.CAPTURE_CONFIRM.value: self._capture_confirm,
            ActionType.CAPTURE_CANCEL.value: self._capture_cancel,
            ActionType.RUN_SET_ACTIVE_CULTIVAR.value: self._set_active_cultivar,
            ActionType.SETTINGS_BARCODE_POLICY_SET.value: self._set_barcode_policy,
            ActionType.SETTINGS_AUTO_RECORD_AFTER_LOCK_SET.value: self._set_auto_record_after_lock,
            ActionType.SETTINGS_LOCK_SENSITIVITY_SET.value: self._set_lock_sensitivity,
            ActionType.SETTINGS_AUTO_RECORD_ALERT_SET.value: self._set_auto_record_alert,
            ActionType.SPREADSHEET_REBUILD.value: self._rebuild_spreadsheet,
            ActionType.STATE_RECOVER.value: self._recover,
            ActionType.STATE_FLUSH.value: self._flush,
            ActionType.REPORT_EXPORT.value: self._export,
            ActionType.REPORT_RECONCILE.value: self._reconcile,
            ActionType.UI_OPEN_SCALE_SETUP.value: self._open_scale_setup,
        }
        try:
            return handlers[request.action_type](request)
        except Exception as exc:
            session = self.loaded_run.store.context.session_id if self.loaded_run else None
            response = self.agent.blocked_from_exception(self.state, exc, session_id=session)
            self.last_alice_response = response.to_dict()
            detail = f"{type(exc).__name__}: {exc}"
            message = response.operator_message or detail
            # Keep casual operator text clean; stash tech detail in data only.
            generic = "the requested operation could not be completed"
            if detail not in message and message.strip().lower().startswith(generic):
                message = f"{message} ({detail})"
            return self._result(
                request,
                "failed",
                response.truth_class.value,
                message,
                {
                    "error_class": type(exc).__name__,
                    "error_detail": detail,
                    "alice_response": self.last_alice_response,
                },
            )

    def _scale_session_dir(self) -> Path:
        if self.loaded_run is not None:
            return self.loaded_run.store.session_dir
        path = self.settings_store.config_dir / "maintenance_scale"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _bind_scale_service(self) -> None:
        """Attach ScaleControlService whenever a validated device is connected."""
        if not self.device or not self.device.status.connected:
            self.scale = None
            return
        self.scale = ScaleControlService(self.device, self._scale_session_dir())

    def _require_scale(self) -> ScaleControlService:
        if not self.device or not self.device.status.connected or not self.scale:
            raise InvalidActionState(
                "Connect the scale first (Scale → Scale Setup → Connect), wait for live readings, then try again."
            )
        return self.scale

    def _install_loaded_run(self, loaded: LoadedRun) -> None:
        self.loaded_run = loaded
        profile = self._effective_stability_profile()
        self.machine = CaptureMachine(loaded.store, profile, beep=self.beep)
        self.scale = None
        # Keep an already-connected USB/simulator scale bound without forcing reconnect.
        if self.device and self.device.status.connected:
            self._bind_scale_service()
            applied = self._apply_active_scale_profile()
            if applied is None and self.machine is not None:
                self._install_effective_profile()
            self.machine.connect()
            if self.machine.state != State.RECOVERY_REQUIRED:
                self.machine.start_session(loaded.definition.capture_mode)
            self.loaded_run.store.context.device_id = self.device.status.device_id or self.device.status.port
            self.loaded_run.store.context.firmware_version = self.device.status.firmware_version or "unknown"
        rows = [row for row in parse_jsonl(loaded.store.records_path) if row.get("event_type") == "weight_record"]
        self.last_record = rows[-1] if rows else None
        context = {"cultivar_roster": loaded.definition.cultivars}
        start_state = State.WAITING_FOR_BARCODE.value if self.scale else State.DISCONNECTED.value
        self.last_alice_response = self.agent.respond(start_state, context=context, session_id=loaded.store.context.session_id).to_dict()

    def _run_new(self, request: ActionRequest) -> ActionResult:
        if self.loaded_run and self.loaded_run.store.sequence > 0:
            finished = self.machine is not None and self.machine.state == State.RUN_FINISHED
            if not finished:
                raise InvalidActionState("finish or close the current run before creating another")
        definition = RunDefinition(**request.payload["definition"])
        simulator = bool(request.payload.get("simulator", False))
        loaded = self.run_manager.create(
            definition,
            data_root=request.payload.get("data_root"),
            evidence_truth_class="simulator" if simulator else "NOT_RUN",
        )
        self._install_loaded_run(loaded)
        return self._result(request, "completed", "UNIT_TEST_PASS", "New run created on local storage", {
            "session_manifest": str(loaded.manifest_path),
            "session_id": loaded.store.context.session_id,
            "run_id": loaded.store.context.run_id,
        })

    def _run_load(self, request: ActionRequest) -> ActionResult:
        loaded = self.run_manager.load(request.payload["selection"])
        self._install_loaded_run(loaded)
        truth = "UNIT_TEST_PASS"
        return self._result(request, "completed", truth, "Run loaded and authoritative ledger validated", {
            "session_id": loaded.store.context.session_id,
            "record_count": loaded.store.sequence,
            "recovery_required": loaded.store.recovery_required,
        })

    def _run_resume(self, request: ActionRequest) -> ActionResult:
        loaded = self.run_manager.resume_latest()
        self._install_loaded_run(loaded)
        return self._result(request, "completed", "UNIT_TEST_PASS", "Latest run loaded from the durable recent-run pointer", {
            "session_id": loaded.store.context.session_id,
            "record_count": loaded.store.sequence,
            "recovery_required": loaded.store.recovery_required,
        })

    def _run_finish(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.loaded_run and self.machine
        # RECORD_SAVED is a committed terminal state — finishing right after the
        # last saved plant is the normal operator flow, so it must not block.
        blocked_states = _ACTIVE_CAPTURE_STATES - {State.RECORD_SAVED}
        if self.machine.state in blocked_states:
            raise InvalidActionState("cancel or complete the current item before finishing the run")
        manifest = self.run_manager.finish(self.loaded_run)
        self.machine.state = State.RUN_FINISHED
        self._refresh_alice_for_state()
        return self._result(request, "completed", "RECEIPT_CONFIRMED", "Run finished; prior records remain immutable", {"manifest": manifest})

    def _set_data_location(self, request: ActionRequest) -> ActionResult:
        if self.loaded_run and self.loaded_run.store.sequence > 0:
            raise InvalidActionState("data location cannot change during an active committed run")
        settings = self.settings_store.update(data_root=str(request.payload["path"]))
        return self._result(request, "completed", "UNIT_TEST_PASS", "Data location validated and saved", {"data_root": settings.data_root})

    def _set_capture_mode(self, request: ActionRequest) -> ActionResult:
        mode = str(request.payload["capture_mode"])
        settings = self.settings_store.update(capture_mode=mode)
        if self.loaded_run:
            self.loaded_run.definition.capture_mode = mode
        if self.machine:
            self.machine.mode = mode
        return self._result(request, "completed", "UNIT_TEST_PASS", "Capture mode updated", {"capture_mode": settings.capture_mode})

    def _set_barcode_policy(self, request: ActionRequest) -> ActionResult:
        required = bool(request.payload.get("barcode_required_for_capture", True))
        settings = self.settings_store.update(barcode_required_for_capture=required)
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            "Barcode policy updated (HID keyboard-wedge scanners only this series).",
            {"barcode_required_for_capture": settings.barcode_required_for_capture},
        )

    def _set_auto_record_after_lock(self, request: ActionRequest) -> ActionResult:
        enabled = bool(request.payload.get("auto_record_after_lock", False))
        settings = self.settings_store.update(auto_record_after_lock=enabled)
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            "Auto-record after Lock updated. Confirm is skipped when this is on.",
            {"auto_record_after_lock": settings.auto_record_after_lock},
        )

    def _set_lock_sensitivity(self, request: ActionRequest) -> ActionResult:
        value = int(request.payload.get("lock_sensitivity", 50))
        if not 0 <= value <= 100:
            raise ValueError("lock_sensitivity must be between 0 and 100")
        settings = self.settings_store.update(lock_sensitivity=value)
        self._install_effective_profile()
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Lock sensitivity set to {settings.lock_sensitivity}.",
            {"lock_sensitivity": settings.lock_sensitivity},
        )

    def _set_auto_record_alert(self, request: ActionRequest) -> ActionResult:
        mode = str(request.payload.get("auto_record_alert", "beep"))
        phrase = request.payload.get("auto_record_alert_phrase")
        changes: dict[str, Any] = {"auto_record_alert": mode}
        if phrase is not None:
            changes["auto_record_alert_phrase"] = str(phrase).strip()
        settings = self.settings_store.update(**changes)
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Auto-record alert set to {settings.auto_record_alert}.",
            {
                "auto_record_alert": settings.auto_record_alert,
                "auto_record_alert_phrase": settings.auto_record_alert_phrase,
            },
        )

    def _set_display_unit(self, request: ActionRequest) -> ActionResult:
        from .units import normalize_display_unit

        display_unit = normalize_display_unit(str(request.payload.get("display_unit", "g")))
        settings = self.settings_store.update(display_unit=display_unit)
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Display unit set to {display_unit}. Records remain in grams (not legal-for-trade).",
            {"display_unit": settings.display_unit, "storage_unit": settings.unit},
        )

    def _set_active_cultivar(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.loaded_run and self.machine
        if self.machine.state in _ACTIVE_CAPTURE_STATES and self.machine.state != State.WAITING_FOR_BARCODE:
            raise InvalidActionState("finish or cancel the current plant before changing strain")
        name = str(request.payload.get("name") or "").strip()
        cultivar_id = str(request.payload.get("cultivar_id") or "").strip()
        if not name:
            raise ValueError("cultivar name is required")
        if not cultivar_id:
            slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()[:24] or "CV"
            cultivar_id = f"CV-{slug}"
        result = self.loaded_run.store.set_active_cultivar(cultivar_id=cultivar_id, name=name)
        # Keep LoadedRun.definition roster aligned with sticky active strain.
        self.loaded_run.definition.cultivars = [
            {"cultivar_id": cultivar_id, "name": name},
            *[
                item
                for item in self.loaded_run.definition.cultivars
                if str(item.get("cultivar_id")) != cultivar_id
            ],
        ]
        response = self._refresh_alice_for_state(context={"active_cultivar": name})
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Active strain set to {name}. Scans use this strain until you change it.",
            {"active_cultivar": result, "alice_response": response},
        )

    def _rebuild_spreadsheet(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.loaded_run
        rebuilt = self.loaded_run.store.rebuild_spreadsheets()
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"CSV/XLSX rebuilt from JSONL ({rebuilt.get('rebuilt_rows', 0)} rows).",
            {"rebuild": rebuilt},
        )

    def _reconcile(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.loaded_run
        from .reports import reconcile_export_to_jsonl

        receipt = reconcile_export_to_jsonl(self.loaded_run.store.session_dir)
        status = "completed" if receipt.get("status") == "pass" else "failed"
        return self._result(
            request,
            status,
            "UNIT_TEST_PASS" if status == "completed" else "BLOCKED",
            f"Export↔JSONL reconcile {receipt.get('status')}.",
            {"reconcile": receipt},
        )

    def _device_discover(self, request: ActionRequest) -> ActionResult:
        ports = [item.__dict__ for item in DeviceService.discover_ports()]
        return self._result(request, "completed", "SOURCE_PRESENT", "Serial-port discovery completed", {"ports": ports, "physical_device_pass": False})

    def _device_connect(self, request: ActionRequest) -> ActionResult:
        # Scale Setup may validate USB/serial before a harvest run exists.
        setup_only = self.loaded_run is None or self.machine is None
        simulator = bool(request.payload.get("simulator", False))
        mode = DeviceMode.SERIAL_SIMULATOR if simulator else DeviceMode.PHYSICAL_SERIAL
        factory = (lambda port, baud, timeout: SimulatedFirmwareTransport(port, baud, timeout)) if simulator else None
        # Physical USB boards commonly reset on open; allow a bounded settle window.
        settle_s = 0.0 if simulator else float(request.payload.get("settle_s", 2.0))
        self.device = DeviceService(mode=mode, transport_factory=factory, settle_s=settle_s)
        port = "SIMULATOR" if simulator else str(request.payload["port"])
        baud = int(request.payload.get("baud", self.settings.baud_rate or 115200))
        if self.machine is not None:
            self.machine.state = State.DEVICE_CONNECTING
        try:
            status = self.device.connect(port, baud=baud)
        except Exception:
            # Restore a safe disconnected state so a failed attempt is not left half-connected.
            if self.device:
                self.device.disconnect(silent=True, reason="connect_failed")
            self.device = None
            self.scale = None
            if self.machine is not None:
                self.machine.disconnect()
            raise
        if not simulator:
            self.settings_store.update(serial_port=port, baud_rate=baud)
        self._bind_scale_service()
        profile_apply = self._apply_active_scale_profile()
        if setup_only:
            response = self._refresh_alice_for_state(context={"device_status": status.to_dict()})
            truth = "SIMULATOR_PASS" if simulator else "SOURCE_PRESENT"
            return self._result(
                request,
                "completed",
                truth,
                "Scale connected. You can calibrate now, or start a harvest run when ready to record plants.",
                {
                    "device_status": status.to_dict(),
                    "baud_rate": baud,
                    "setup_only": True,
                    "physical_device_pass": False,
                    "active_scale_profile": profile_apply,
                    "alice_response": response,
                },
            )
        assert self.loaded_run and self.machine
        self.loaded_run.store.context.device_id = status.device_id or port
        self.loaded_run.store.context.firmware_version = status.firmware_version or "unknown"
        self.loaded_run.store.context.evidence_truth_class = "simulator" if simulator else "SOURCE_PRESENT"
        if profile_apply is None:
            self._install_effective_profile(status.device_id)
        self.machine.connect()
        if self.machine.state != State.RECOVERY_REQUIRED:
            self.machine.start_session(self.loaded_run.definition.capture_mode)
        response = self._refresh_alice_for_state(context={"device_status": status.to_dict()})
        truth = "SIMULATOR_PASS" if simulator else "SOURCE_PRESENT"
        return self._result(request, "completed", truth, "Scale connection and protocol validation completed", {
            "device_status": status.to_dict(),
            "baud_rate": baud,
            "setup_only": False,
            "physical_device_pass": False,
            "active_scale_profile": profile_apply,
            "alice_response": response,
        })

    def _device_disconnect(self, request: ActionRequest) -> ActionResult:
        if self.device:
            self.device.disconnect(reason="operator_request")
        self.device = None
        self.scale = None
        if self.machine:
            self.machine.disconnect()
        response = self._refresh_alice_for_state() if self.loaded_run else None
        return self._result(request, "completed", "UNIT_TEST_PASS", "Scale disconnected", {"alice_response": response})

    def _device_status(self, request: ActionRequest) -> ActionResult:
        if not self.device:
            return self._result(request, "completed", "NOT_RUN", "No scale connection has been established", {"connected": False})
        stale = self.device.is_stale()
        return self._result(request, "completed", self.device.status.truth_class, "Scale status read", {
            "device_status": self.device.status.to_dict(),
            "stale": stale,
            "physical_device_pass": False,
        })

    def _device_ping(self, request: ActionRequest) -> ActionResult:
        if not self.device or not self.device.status.connected:
            raise InvalidActionState("connect a scale before sending PING")
        response = self.device.ping()
        return self._result(request, "completed", self.device.status.truth_class, "Scale PING acknowledged", {"protocol_response": response})

    def _device_reconnect(self, request: ActionRequest) -> ActionResult:
        if not self.device:
            raise InvalidActionState("no prior scale connection is available")
        status = self.device.reconnect(max_attempts=int(request.payload.get("max_attempts", 2)))
        self._bind_scale_service()
        profile_apply = self._apply_active_scale_profile()
        if self.machine and self.loaded_run:
            if profile_apply is None:
                self._install_effective_profile(status.device_id)
            self.machine.connect()
            if self.machine.state != State.RECOVERY_REQUIRED:
                self.machine.start_session(self.loaded_run.definition.capture_mode)
        response = self._refresh_alice_for_state(context={"device_status": status.to_dict()})
        return self._result(
            request,
            "completed",
            status.truth_class,
            "Scale reconnected and protocol validated",
            {
                "device_status": status.to_dict(),
                "active_scale_profile": profile_apply,
                "alice_response": response,
            },
        )

    def _device_stream_start(self, request: ActionRequest) -> ActionResult:
        if not self.device or not self.device.status.connected:
            raise InvalidActionState("connect a scale before starting the stream")
        response = self.device.start_stream()
        return self._result(request, "completed", self.device.status.truth_class, "Scale stream started", {"protocol_response": response})

    def _device_stream_stop(self, request: ActionRequest) -> ActionResult:
        if not self.device or not self.device.status.connected:
            raise InvalidActionState("connect a scale before stopping the stream")
        response = self.device.stop_stream() if self.device.status.streaming else {"kind": "A", "fields": ["ALREADY_STOPPED"]}
        return self._result(request, "completed", self.device.status.truth_class, "Scale stream stopped", {"protocol_response": response})

    def _barcode_submit(self, request: ActionRequest) -> ActionResult:
        self._require_capture_ready()
        assert self.machine and self.loaded_run
        barcode = str(request.payload["barcode"])
        acknowledge = bool(request.payload.get("acknowledge_duplicate"))
        normalized = barcode.strip().upper()
        already = normalized in self.loaded_run.store.barcodes
        if already and not acknowledge:
            response = self.agent.respond(
                self.machine.state.value,
                session_id=self.loaded_run.store.context.session_id,
            ).to_dict()
            self.last_alice_response = response
            return self._result(
                request,
                "blocked",
                "PENDING",
                "This barcode was already recorded in this run. Continue to weigh it again, or cancel the scan.",
                {
                    "duplicate_barcode": True,
                    "barcode": barcode.strip(),
                    "requires_operator_choice": True,
                    "alice_response": response,
                },
                terminal=False,
            )
        self.machine.scan(
            barcode,
            duplicate_status="accepted" if already and acknowledge else "none",
        )
        response = self.agent.respond(self.machine.state.value, session_id=self.loaded_run.store.context.session_id).to_dict()  # type: ignore[union-attr]
        self.last_alice_response = response
        return self._result(request, "accepted", "PENDING", "Barcode accepted; waiting for a stable load", {"alice_response": response, "duplicate_acknowledged": bool(already and acknowledge)}, terminal=False)

    def _reading_ingest(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.machine and self.loaded_run
        if self.machine.state != State.WAITING_FOR_STABLE_WEIGHT:
            raise InvalidActionState("the application is not waiting for a weight reading")
        weight = float(request.payload["weight_g"])
        raw = request.payload.get("raw_value")
        terminal = self.machine.reading(weight, raw=raw, ready=bool(request.payload.get("ready", True)))
        if terminal is None or not isinstance(terminal, (tuple, dict)):
            state = self.machine.state.value
            context = {"net_g": weight - self.loaded_run.store.context.tare_g}
            response = self.agent.respond(state, context=context, session_id=self.loaded_run.store.context.session_id).to_dict()
            self.last_alice_response = response
            return self._result(request, "accepted", "PENDING", "Weight sample processed", {"stable": bool(getattr(terminal, "stable", False)), "alice_response": response}, terminal=False)
        return self._process_terminal(request, terminal)

    def _capture_weight_lock(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.machine
        try:
            locked = self.machine.lock_weight()
        except RuntimeError as exc:
            return self._result(request, "failed", "UNIT_TEST_PASS", str(exc), {})
        if bool(self.settings.auto_record_after_lock):
            return self._capture_confirm(request)
        response = self._refresh_alice_for_state(
            context={
                "weight_locked": True,
                "locked_weight_g": getattr(locked, "weight_g", None),
            }
        )
        weight_g = float(getattr(locked, "weight_g", 0.0) or 0.0)
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Weight locked at {weight_g:.3f} g — press Confirm & Record when ready.",
            {
                "locked_weight_g": weight_g,
                "alice_response": response,
            },
        )

    def _capture_confirm(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.machine
        note = request.payload.get("operator_note")
        void_status = str(request.payload.get("void_status") or "none")
        terminal = self.machine.confirm(
            raw=request.payload.get("raw_value"),
            operator_note=str(note).strip() if note else None,
            void_status=void_status,
        )
        return self._process_terminal(request, terminal)

    def _process_terminal(self, request: ActionRequest, terminal: Any) -> ActionResult:
        assert self.machine and self.loaded_run
        record = None
        feedback = "success"
        if isinstance(terminal, dict):
            backend_result = terminal
            feedback = "warning" if terminal.get("status") == "duplicate" else "success"
        else:
            record, receipt = terminal
            backend_result = receipt.to_dict()
            if record and str(record.get("duplicate_status")) not in {"", "none", "None"}:
                feedback = "warning"
        response = self.agent.respond(
            State.LOCAL_COMMIT_PENDING.value,
            backend_result=backend_result,
            session_id=self.loaded_run.store.context.session_id,
            correlation_id=request.action_id,
        )
        self.last_alice_response = response.to_dict()
        confirmed = response.truth_class == TruthClass.RECEIPT_CONFIRMED
        if not confirmed:
            return self._result(request, "failed", response.truth_class.value, response.operator_message, {"alice_response": self.last_alice_response})
        auto_path = self._is_auto_record_path(request)
        alert_mode = self.settings.auto_record_alert
        if auto_path and alert_mode != "off":
            noop = lambda _kind: None
            saved_beep = self.machine.beep
            self.machine.beep = noop
            try:
                self.machine.complete_terminal_result(feedback)
            finally:
                self.machine.beep = saved_beep
            self._play_record_alert(feedback)
        else:
            self.machine.complete_terminal_result(feedback)
        if record is not None:
            self.last_record = record
        message = response.operator_message
        if record is not None:
            barcode = record.get("barcode_raw") or record.get("record_id")
            net = record.get("net_g")
            cultivar = record.get("cultivar_normalized_name") or ""
            message = f"Saved {barcode}: {float(net):.3f} g net ({cultivar}). Scan the next plant."
            if feedback == "warning":
                message = f"Saved with duplicate barcode warning — {message}"
            pending = self.loaded_run.store.pending_sync_count()
            if pending:
                message += f" CSV sync pending ({pending}). Use Recover/Rebuild CSV if needed."
        return self._result(request, "completed", response.truth_class.value, message, {
            "record": record,
            "backend_result": backend_result,
            "alice_response": self.last_alice_response,
            "feedback": feedback,
        })

    def _capture_cancel(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.machine
        self.machine.cancel_capture()
        response = self._refresh_alice_for_state(context={"capture_cancelled": True})
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            "Current plant cancelled — not saved. Scan again when ready.",
            {"committed_records_unchanged": True, "alice_response": response},
            terminal=True,
        )

    def _scale_zero(self, request: ActionRequest) -> ActionResult:
        self._require_scale_maintenance(allow_without_run=True)
        scale = self._require_scale()
        provided = request.payload.get("readings_g")
        values = [float(value) for value in provided] if provided is not None else None
        receipt = scale.zero_scale(values)
        response = self._refresh_alice_for_state(context={"maintenance_result": "zeroed"})
        return self._result(
            request,
            "completed",
            receipt.truth_class,
            "Scale zeroed. Keep the pan empty — live weight should read near 0 g.",
            {"zero_receipt": receipt.__dict__, "physical_device_pass": False, "alice_response": response},
        )

    def _tare_set(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        scale = self._require_scale()
        assert self.loaded_run
        record = scale.set_known_tare(str(request.payload["container_id"]), float(request.payload["tare_g"]), self.loaded_run.definition.operator_id)
        self.loaded_run.store.context.container_id = record.container_id
        self.loaded_run.store.context.tare_g = record.tare_g
        response = self._refresh_alice_for_state(context={"tare_g": record.tare_g})
        return self._result(request, "completed", record.truth_class, "Known container tare saved", {"tare_record": record.__dict__, "alice_response": response})

    def _tare_capture(self, request: ActionRequest) -> ActionResult:
        self._require_scale_maintenance(allow_without_run=False)
        scale = self._require_scale()
        assert self.loaded_run
        record = scale.capture_tare(str(request.payload["container_id"]), request.payload["readings_g"], self.loaded_run.definition.operator_id)
        self.loaded_run.store.context.container_id = record.container_id
        self.loaded_run.store.context.tare_g = record.tare_g
        response = self._refresh_alice_for_state(context={"tare_g": record.tare_g})
        return self._result(request, "completed", record.truth_class, "Stable container tare captured and saved", {"tare_record": record.__dict__, "physical_device_pass": False, "alice_response": response})

    def _calibration_start(self, request: ActionRequest) -> ActionResult:
        self._require_scale_maintenance(allow_without_run=True)
        scale = self._require_scale()
        active_capture = bool(
            self.machine
            and self.machine.state in _ACTIVE_CAPTURE_STATES
            and self.machine.state != State.WAITING_FOR_BARCODE
        )
        operator_id = (
            self.loaded_run.definition.operator_id
            if self.loaded_run
            else str(request.payload.get("operator_id") or "maintenance")
        )
        session_id = scale.start_calibration(
            active_capture=active_capture,
            operator_id=operator_id,
            maintenance_authorized=bool(request.payload.get("maintenance_authorized")),
        )
        return self._result(request, "completed", "UNIT_TEST_PASS", "Calibration workflow started", {"calibration_session_id": session_id, "physical_device_pass": False})

    def _calibration_sample(self, request: ActionRequest) -> ActionResult:
        scale = self._require_scale()
        scale.add_calibration_samples(
            str(request.payload["kind"]),
            request.payload["samples"],
            reference_weight_g=request.payload.get("reference_weight_g"),
        )
        if request.payload["kind"] == "loaded":
            proposal = scale.calculate_calibration()
            return self._result(request, "completed", "UNIT_TEST_PASS", "Calibration factor proposal calculated", {"proposal": proposal.__dict__, "physical_device_pass": False})
        return self._result(request, "completed", "UNIT_TEST_PASS", "Zero-load calibration samples accepted", {})

    def _calibration_test(self, request: ActionRequest) -> ActionResult:
        scale = self._require_scale()
        result = scale.test_calibration(request.payload["samples"])
        message = result.get("operator_summary") or "Proposed calibration factor tested"
        return self._result(request, "completed", result["truth_class"], message, {"calibration_test": result, "physical_device_pass": False})

    def _calibration_accept(self, request: ActionRequest) -> ActionResult:
        scale = self._require_scale()
        receipt = scale.accept_calibration(
            maintenance_authorized=bool(request.payload.get("maintenance_authorized")),
            second_confirmation=bool(request.payload.get("second_confirmation")),
        )
        if self.loaded_run:
            self.loaded_run.store.context.calibration_id = receipt["receipt_id"]
        profile_binding: dict[str, Any] | None = None
        device_id = receipt.get("device_id") or (self.device.status.device_id if self.device else None)
        try:
            if device_id:
                profile = self._upsert_calibration_profile(
                    device_id=str(device_id),
                    calibration_factor=float(receipt["accepted_factor"]),
                    calibration_receipt_id=str(receipt["receipt_id"]),
                    firmware_version=(
                        self.device.status.firmware_version if self.device else None
                    ),
                )
                self.active_scale_profile = profile
                if self.machine is not None:
                    self._install_effective_profile(str(device_id))
                profile_binding = profile.to_dict()
        except ValueError:
            # Non-BBWS device ids remain calibratable but are not profile-bound yet.
            profile_binding = None
        prompt_assign = False
        if profile_binding is None and device_id:
            try:
                validate_device_id(str(device_id))
            except ValueError:
                prompt_assign = True
        return self._result(
            request,
            "completed",
            receipt["truth_class"],
            "Calibration factor accepted by the connected test device",
            {
                "calibration_receipt": receipt,
                "scale_profile": profile_binding,
                "prompt_characterize": True,
                "characterize_recommended": True,
                "prompt_assign_device_id": prompt_assign,
                "physical_device_pass": False,
            },
        )

    def _calibration_cancel(self, request: ActionRequest) -> ActionResult:
        scale = self._require_scale()
        return self._result(request, "completed", "UNIT_TEST_PASS", "Calibration workflow cancelled", scale.cancel_calibration())

    def _scale_device_id_set(self, request: ActionRequest) -> ActionResult:
        device_id = validate_device_id(str(request.payload.get("device_id") or ""))
        assigned = self.set_connected_device_id(device_id)
        profile_apply = self._apply_active_scale_profile()
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Device id set to {device_id}",
            {
                "device_id": assigned.get("device_id"),
                "device_status": assigned.get("status"),
                "active_scale_profile": profile_apply,
                "physical_device_pass": False,
            },
        )

    def _scale_profile_list(self, request: ActionRequest) -> ActionResult:
        include_archived = bool(request.payload.get("include_archived", False))
        profiles = self.list_scale_profiles(include_archived=include_archived)
        return self._result(
            request,
            "completed",
            "SOURCE_PRESENT",
            f"{len(profiles)} scale profile(s)",
            {"profiles": profiles, "include_archived": include_archived},
        )

    def _scale_profile_activate(self, request: ActionRequest) -> ActionResult:
        profile_id = str(request.payload.get("profile_id") or "")
        if not profile_id:
            raise ValueError("profile_id is required")
        profile = self._scale_profile_store.activate(profile_id)
        applied = None
        if self.device and self.device.status.connected and self.device.status.device_id == profile.device_id:
            applied = self._apply_active_scale_profile()
        else:
            self.active_scale_profile = profile
            if self.machine is not None:
                self._install_effective_profile(profile.device_id)
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Activated profile {profile.name}",
            {"profile": profile.to_dict(), "active_scale_profile": applied},
        )

    def _scale_profile_archive(self, request: ActionRequest) -> ActionResult:
        profile_id = str(request.payload.get("profile_id") or "")
        if not profile_id:
            raise ValueError("profile_id is required")
        profile = self._scale_profile_store.archive(profile_id)
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Archived profile {profile.name}",
            {"profile": profile.to_dict()},
        )

    def _scale_profile_rename(self, request: ActionRequest) -> ActionResult:
        profile_id = str(request.payload.get("profile_id") or "")
        name = str(request.payload.get("name") or "")
        if not profile_id:
            raise ValueError("profile_id is required")
        profile = self._scale_profile_store.rename(profile_id, name)
        if self.active_scale_profile and self.active_scale_profile.profile_id == profile.profile_id:
            self.active_scale_profile = profile
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Renamed profile to {profile.name}",
            {"profile": profile.to_dict()},
        )

    def _calibration_characterize(self, request: ActionRequest) -> ActionResult:
        """100 g hanging-load characterization → recommendation only (no auto-activate)."""
        self._require_scale_maintenance(allow_without_run=True)
        scale = self._require_scale()
        samples = request.payload.get("samples")
        if samples is None:
            raise ValueError("characterization samples are required (buffer or payload)")
        reference = float(request.payload.get("reference_weight_g") or 100.0)
        characterization = scale.characterize_stability(
            list(samples),
            reference_weight_g=reference,
        )
        receipt_id = f"characterization-{uuid.uuid4()}"
        receipt = {
            "receipt_id": receipt_id,
            "kind": "stability_characterization",
            "created_at": now_rfc3339(),
            "device_id": self.device.status.device_id if self.device else None,
            "characterization": characterization,
            "non_claim": characterization.get("non_claim"),
            "truth_class": characterization.get("truth_class"),
            "physical_device_pass": False,
        }
        atomic_json(self._scale_session_dir() / "maintenance_receipts" / f"{receipt_id}.json", receipt)
        characterization = dict(characterization)
        characterization["characterization_receipt_id"] = receipt_id
        return self._result(
            request,
            "completed",
            characterization.get("truth_class") or "UNIT_TEST_PASS",
            "Stability characterization complete — confirm before activating a profile",
            {
                "characterization": characterization,
                "characterization_receipt": receipt,
                "recommended_stability": characterization.get("recommended_stability"),
                "auto_activated": False,
                "prompt_confirm_stability": True,
                "physical_device_pass": False,
            },
        )

    def _scale_profile_confirm_stability(self, request: ActionRequest) -> ActionResult:
        """Operator-confirmed stability params → create/update active profile + install."""
        device_id = validate_device_id(str(request.payload.get("device_id") or ""))
        if not self.device or not self.device.status.connected:
            raise InvalidActionState("connect a scale before confirming a stability profile")
        status = self.device.read_status()
        calibration_factor = float(status["calibration_factor"])
        raw_stability = (
            request.payload.get("stability")
            or request.payload.get("recommended_stability")
            or {}
        )
        if not isinstance(raw_stability, dict) or not raw_stability:
            raise ValueError("recommended stability params are required")
        stability = ScaleStabilityParams.from_dict(raw_stability)
        name = str(request.payload.get("name") or "").strip() or f"{device_id} hanging"
        characterization_receipt_id = request.payload.get("characterization_receipt_id")
        active = self._scale_profile_store.get_active_for_device(device_id)
        if active is not None:
            profile = self._scale_profile_store.update(
                active.profile_id,
                name=name,
                calibration_factor=calibration_factor,
                stability=stability,
                characterization_receipt_id=characterization_receipt_id
                or active.characterization_receipt_id,
                firmware_version=status.get("firmware_version") or active.firmware_version,
                status="active",
            )
        else:
            profile = self._scale_profile_store.create(
                name=name,
                device_id=device_id,
                calibration_factor=calibration_factor,
                stability=stability,
                characterization_receipt_id=characterization_receipt_id,
                firmware_version=status.get("firmware_version"),
                activate=True,
            )
        self.active_scale_profile = profile
        if self.machine is not None:
            self._install_effective_profile(device_id)
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Stability profile confirmed for {device_id}",
            {
                "profile": profile.to_dict(),
                "calibration_factor": calibration_factor,
                "physical_device_pass": False,
                "non_claim": "Characterization is repeatability evidence, not legal-for-trade certification.",
            },
        )

    def _recover(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.machine and self.loaded_run
        if self.machine.state != State.RECOVERY_REQUIRED:
            raise InvalidActionState("recovery is not required")
        receipt = self.machine.recover()
        self.machine.state = State.DEVICE_READY
        self.machine.start_session(self.loaded_run.definition.capture_mode)
        response = self.agent.respond(
            State.RECOVERY_REQUIRED.value,
            recovery_condition=receipt,
            session_id=self.loaded_run.store.context.session_id,
        )
        self.last_alice_response = response.to_dict()
        return self._result(request, "completed", "RECEIPT_CONFIRMED", response.operator_message, {"recovery_receipt": receipt, "alice_response": self.last_alice_response})

    def _flush(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.loaded_run
        if self.loaded_run.store.snapshot_path.exists():
            snapshot = json.load(self.loaded_run.store.snapshot_path.open(encoding="utf-8"))
            snapshot["maintenance_flush_at"] = now_rfc3339()
            atomic_json(self.loaded_run.store.snapshot_path, snapshot)
        receipt = {"receipt_id": f"flush-{request.action_id}", "status": "flushed", "sequence": self.loaded_run.store.sequence, "created_at": now_rfc3339()}
        atomic_json(self.loaded_run.store.session_dir / "maintenance_receipts" / f"{receipt['receipt_id']}.json", receipt)
        return self._result(request, "completed", "RECEIPT_CONFIRMED", "Current committed state was flushed; this did not create a plant record", {"flush_receipt": receipt})

    def _export(self, request: ActionRequest) -> ActionResult:
        self._require_run()
        assert self.loaded_run
        result = self.run_manager.export(self.loaded_run, request.payload["destination"])
        paths = result.get("paths") or []
        summary = ", ".join(Path(path).name for path in paths) if paths else "no files"
        return self._result(
            request,
            "completed",
            "UNIT_TEST_PASS",
            f"Export completed ({summary}). Reports are handoff copies — session JSONL remains authoritative.",
            result,
        )

    def _open_scale_setup(self, request: ActionRequest) -> ActionResult:
        ports = [item.__dict__ for item in DeviceService.discover_ports()]
        return self._result(request, "completed", "SOURCE_PRESENT", "Scale Setup route resolved with current device state", {
            "ui_route": "scale_setup",
            "ports": ports,
            "settings": {"serial_port": self.settings.serial_port, "baud_rate": self.settings.baud_rate, "simulator_enabled": self.settings.simulator_enabled},
            "device_status": self.device.status.to_dict() if self.device else {"connected": False},
        })

    def _require_run(self) -> None:
        if not self.loaded_run or not self.machine:
            raise InvalidActionState("no run is loaded")

    def _require_capture_ready(self) -> None:
        self._require_run()
        assert self.machine
        if self.machine.state != State.WAITING_FOR_BARCODE:
            raise InvalidActionState("the station is not ready for a barcode")

    def _require_maintenance_ready(self) -> None:
        self._require_scale_maintenance(allow_without_run=False)

    def _require_scale_maintenance(self, *, allow_without_run: bool) -> None:
        if not allow_without_run:
            self._require_run()
        self._require_scale()
        if self.machine and self.machine.state in _ACTIVE_CAPTURE_STATES and self.machine.state != State.WAITING_FOR_BARCODE:
            raise InvalidActionState("Finish or cancel the current plant first, then try again.")
