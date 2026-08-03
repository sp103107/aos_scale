from __future__ import annotations

import statistics
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from .actions import ActionRequest
from .application_controller import ApplicationController
from .device_service import DeviceMode, SimulatedFirmwareTransport
from .models import now_rfc3339
from .platform_paths import AppPaths, default_app_paths


@dataclass(frozen=True)
class ReadingSample:
    weight_g: float
    raw_value: int | None
    ready: bool
    device_ms: int | None
    received_at: str
    truth_class: str


class ReadingBuffer:
    def __init__(self, maxlen: int = 128):
        self._values: deque[ReadingSample] = deque(maxlen=maxlen)
        self._lock = threading.Lock()

    def append(self, sample: ReadingSample) -> None:
        with self._lock:
            self._values.append(sample)

    def latest(self) -> ReadingSample | None:
        with self._lock:
            return self._values[-1] if self._values else None

    def recent(self, count: int = 8) -> list[ReadingSample]:
        with self._lock:
            return list(self._values)[-count:]

    def display_weight_g(self, count: int = 8) -> float:
        """Median of recent samples so uncalibrated raw noise does not thrash the UI."""
        samples = self.recent(count)
        if not samples:
            return 0.0
        return float(statistics.median(sample.weight_g for sample in samples))

    def clear(self) -> None:
        with self._lock:
            self._values.clear()


class ScaleReadingWorker:
    """Background device reader.

    The worker only acquires and normalizes readings. It never writes records.
    When the controller is waiting for a stable weight, samples are routed through
    the canonical ``reading.ingest`` action so the existing state machine remains
    authoritative.
    """

    def __init__(
        self,
        controller: ApplicationController,
        buffer: ReadingBuffer,
        *,
        poll_interval_s: float = 0.05,
        on_sample: Callable[[ReadingSample], None] | None = None,
        on_result: Callable[[dict[str, Any]], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ):
        self.controller = controller
        self.buffer = buffer
        self.poll_interval_s = poll_interval_s
        self.on_sample = on_sample or (lambda sample: None)
        self.on_result = on_result or (lambda result: None)
        self.on_error = on_error or (lambda error: None)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._started_stream = False

    @property
    def running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> None:
        if self.running:
            return
        if not self.controller.device or not self.controller.device.status.connected:
            raise RuntimeError("connect a validated scale before starting the reading worker")
        self._stop.clear()
        if not self.controller.device.status.streaming:
            self.controller.device.start_stream()
            self._started_stream = True
        self._thread = threading.Thread(target=self._run, name="bbws-scale-reader", daemon=True)
        self._thread.start()

    def stop(self, *, stop_stream: bool = True, timeout: float = 2.0) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        if stop_stream and self.controller.device and self.controller.device.status.connected and self.controller.device.status.streaming:
            try:
                self.controller.device.stop_stream()
            except Exception:
                # Intentional stop: do not surface stream-off races as a fatal scale error.
                try:
                    self.controller.device.status.streaming = False
                except Exception:
                    pass
        self._thread = None
        self._started_stream = False

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                device = self.controller.device
                if not device or not device.status.connected:
                    raise ConnectionError("scale disconnected while reading")
                message = device.read_stream_message()
                if message.get("kind") != "W":
                    continue
                sample = ReadingSample(
                    weight_g=float(message["weight_g"]),
                    raw_value=int(message["raw_value"]) if message.get("raw_value") is not None else None,
                    ready=bool(message.get("ready", True)),
                    device_ms=int(message["device_ms"]) if message.get("device_ms") is not None else None,
                    received_at=now_rfc3339(),
                    truth_class=device.status.truth_class,
                )
                self.buffer.append(sample)
                self.on_sample(sample)
                if self.controller.state == "WAITING_FOR_STABLE_WEIGHT":
                    result = self.controller.dispatch(ActionRequest(
                        "reading.ingest",
                        {"weight_g": sample.weight_g, "raw_value": sample.raw_value, "ready": sample.ready},
                        source="scale_worker",
                    )).to_dict()
                    self.on_result(result)
                time.sleep(self.poll_interval_s)
            except TimeoutError:
                time.sleep(self.poll_interval_s)
            except Exception as exc:
                self.on_error(exc)
                break


class OperatorRuntime:
    """UI-neutral operator application facade used by PySide6, Tk, and tests."""

    def __init__(self, data_root: str | Path | None = None, *, capture_mode: str = "manual"):
        self.paths: AppPaths = default_app_paths()
        selected_root = Path(data_root).expanduser().resolve() if data_root else self.paths.runs
        selected_root.mkdir(parents=True, exist_ok=True)
        self.controller = ApplicationController(self.paths.config)
        self.controller.settings_store.update(data_root=str(selected_root), capture_mode=capture_mode)
        self.buffer = ReadingBuffer()
        self.last_worker_error: str | None = None
        self.last_action_result: dict[str, Any] | None = None
        self.worker = ScaleReadingWorker(
            self.controller,
            self.buffer,
            on_result=self._capture_result,
            on_error=self._capture_error,
        )

    def _capture_result(self, result: dict[str, Any]) -> None:
        self.last_action_result = result

    def _capture_error(self, error: Exception) -> None:
        self.last_worker_error = f"{type(error).__name__}: {error}"

    def dispatch(self, action: str, payload: dict[str, Any] | None = None, *, source: str = "local_ui") -> dict[str, Any]:
        result = self.controller.dispatch(ActionRequest(action, payload or {}, source=source)).to_dict()
        self.last_action_result = result
        return result

    def connect_simulator(self) -> dict[str, Any]:
        result = self.dispatch("device.connect", {"simulator": True})
        if result.get("status") == "completed" and self.controller.device and self.controller.device.status.protocol_validated:
            self.start_reading_worker()
        return result

    def connect_serial(self, port: str, baud: int = 115200) -> dict[str, Any]:
        result = self.dispatch("device.connect", {"port": port, "baud": baud})
        # Never start the worker on a failed connect; preserve the original error for the UI.
        if result.get("status") == "completed" and self.controller.device and self.controller.device.status.protocol_validated:
            self.start_reading_worker()
        return result

    def disconnect(self) -> dict[str, Any]:
        self.worker.stop(stop_stream=True)
        return self.dispatch("device.disconnect")

    def start_reading_worker(self) -> None:
        self.worker.start()

    def stop_reading_worker(self) -> None:
        self.worker.stop(stop_stream=True)

    def submit_barcode(self, barcode: str) -> dict[str, Any]:
        return self.dispatch("barcode.submit", {"barcode": barcode.strip()})

    def next_auto_plant_id(self) -> str:
        """Generate a local plant id when barcode hardware is optional/off."""
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        self._auto_plant_seq = getattr(self, "_auto_plant_seq", 0) + 1
        return f"AUTO-{stamp}-{self._auto_plant_seq:03d}"

    def zero_scale(self) -> dict[str, Any]:
        # Deliberately omit readings. The controller must acquire them from the
        # connected device after issuing TARE. Simulator evidence remains explicit.
        was_running = self.worker.running
        if was_running:
            self.worker.stop(stop_stream=True)
            # Let the HX711 finish the last conversion window before TARE.
            time.sleep(0.2)
        result: dict[str, Any] = {"status": "failed", "message": "scale.zero did not run"}
        try:
            result = self.dispatch("scale.zero", {})
            if result.get("status") == "completed":
                # Drop pre-zero samples so the UI does not keep showing -380000.
                self.buffer.clear()
                self.last_worker_error = None
        finally:
            if self.controller.device and self.controller.device.status.connected:
                try:
                    self.worker.start()
                    if result.get("status") == "completed":
                        self.last_worker_error = None
                except Exception as exc:
                    # Zero already applied; stream restart must not look like Zero failed.
                    self.last_worker_error = f"{type(exc).__name__}: {exc}"
        return result

    def set_known_tare(self, container_id: str, tare_g: float) -> dict[str, Any]:
        return self.dispatch("scale.container_tare.set", {"container_id": container_id, "tare_g": tare_g})

    def capture_container_tare(self, container_id: str, sample_count: int = 8) -> dict[str, Any]:
        samples = [item.weight_g for item in self.buffer.recent(sample_count)]
        if len(samples) < 3:
            raise RuntimeError("at least three live scale readings are required to capture tare")
        return self.dispatch("scale.container_tare.capture", {"container_id": container_id, "readings_g": samples})

    def start_calibration(self) -> dict[str, Any]:
        return self.dispatch("scale.calibration.start", {"maintenance_authorized": True})

    def add_calibration_zero_samples(self, sample_count: int = 8) -> dict[str, Any]:
        raw = [float(item.raw_value) for item in self.buffer.recent(sample_count) if item.raw_value is not None]
        if len(raw) < 3:
            raise RuntimeError("at least three live raw readings are required")
        return self.dispatch("scale.calibration.sample", {"kind": "zero", "samples": raw})

    def add_calibration_loaded_samples(self, reference_weight_g: float, sample_count: int = 8) -> dict[str, Any]:
        raw = [float(item.raw_value) for item in self.buffer.recent(sample_count) if item.raw_value is not None]
        if len(raw) < 3:
            raise RuntimeError("at least three live raw readings are required")
        return self.dispatch("scale.calibration.sample", {
            "kind": "loaded",
            "samples": raw,
            "reference_weight_g": float(reference_weight_g),
        })

    def test_calibration(self, sample_count: int = 8) -> dict[str, Any]:
        raw = [float(item.raw_value) for item in self.buffer.recent(sample_count) if item.raw_value is not None]
        if len(raw) < 3:
            raise RuntimeError("at least three live raw readings are required")
        return self.dispatch("scale.calibration.test", {"samples": raw})

    def accept_calibration(self) -> dict[str, Any]:
        # Pause the live reader so SET_CAL/STATUS are not mixed with stream weight lines.
        was_running = self.worker.running
        if was_running:
            self.worker.stop(stop_stream=True)
            time.sleep(0.2)
        result: dict[str, Any] = {"status": "failed", "message": "scale.calibration.accept did not run"}
        try:
            result = self.dispatch("scale.calibration.accept", {
                "maintenance_authorized": True,
                "second_confirmation": True,
            })
            if result.get("status") == "completed":
                self.buffer.clear()
                self.last_worker_error = None
        finally:
            if self.controller.device and self.controller.device.status.connected:
                try:
                    self.worker.start()
                except Exception as exc:
                    self.last_worker_error = f"{type(exc).__name__}: {exc}"
        return result

    def cancel_calibration(self) -> dict[str, Any]:
        return self.dispatch("scale.calibration.cancel")

    def simulator_set_weight(self, weight_g: float) -> None:
        if not self.controller.device or self.controller.device.mode != DeviceMode.SERIAL_SIMULATOR:
            raise RuntimeError("simulator is not connected")
        transport = self.controller.device.transport
        if not isinstance(transport, SimulatedFirmwareTransport):
            raise RuntimeError("unexpected simulator transport")
        transport.set_weight(weight_g)

    def snapshot(self) -> dict[str, Any]:
        controller = self.controller
        latest = self.buffer.latest()
        display_weight = self.buffer.display_weight_g()
        run = controller.loaded_run
        context = run.store.context if run else None
        definition = run.definition if run else None
        response = controller.last_alice_response or {}
        required_action = response.get("required_action") or {}
        tare_g = context.tare_g if context else 0.0
        cal = controller.device.status.calibration_factor if controller.device else None
        settings = controller.settings
        weight_uncalibrated = bool(cal is not None and abs(float(cal) - 1.0) < 1e-6)
        return {
            "version": __import__("best_buds_weight_station.version", fromlist=["__version__"]).__version__,
            "state": controller.state,
            "operator_state": controller.operator_state_label(),
            "alice_message": response.get("operator_message", "Start or resume a run."),
            "alice_truth_class": response.get("truth_class", "NOT_RUN"),
            "alice_required_action": required_action.get("action_type", response.get("required_operator_action", "start or resume a run")),
            "run_id": context.run_id if context else None,
            "operator_id": context.operator_id if context else None,
            "cultivar": (context.cultivar_raw_name if context else None)
            or (definition.cultivars[0]["name"] if definition and definition.cultivars else None),
            "cultivar_id": context.cultivar_id if context else None,
            "calibration_id": context.calibration_id if context else None,
            "container_id": context.container_id if context else None,
            "tare_g": tare_g,
            "weight_g": display_weight,
            "raw_value": latest.raw_value if latest else None,
            "net_g": display_weight - tare_g,
            "weight_uncalibrated": weight_uncalibrated,
            "suggest_calibration_on_new_run": bool(settings.suggest_calibration_on_new_run),
            "warn_on_uncalibrated_weight": bool(settings.warn_on_uncalibrated_weight),
            "barcode_required_for_capture": bool(settings.barcode_required_for_capture),
            "default_reference_weight_g": float(settings.default_reference_weight_g),
            "pending_sync_count": run.store.pending_sync_count() if run else 0,
            "last_saved": controller.last_record,
            "device": controller.device.status.to_dict() if controller.device else {"connected": False, "mode": None},
            "worker_running": self.worker.running,
            "worker_error": self.last_worker_error,
            "capture_mode": definition.capture_mode if definition else controller.settings.capture_mode,
            "scale_service_bound": controller.scale is not None,
        }

    def close(self) -> None:
        try:
            if self.worker.running:
                self.worker.stop(stop_stream=True)
        finally:
            if self.controller.device and self.controller.device.status.connected:
                self.controller.dispatch(ActionRequest("device.disconnect", source="shutdown"))


def scripted_operator_flow(runtime: OperatorRuntime, *, barcode: str = "SCRIPTED-001", weight_g: float = 1250.0) -> dict[str, Any]:
    """Execute the real frontend-facing runtime path using the firmware simulator."""
    definition = {
        "run_id": "OPERATOR-SCRIPTED-RUN",
        "operator_id": "OPERATOR-SCRIPTED",
        "facility_id": "BEST-BUDS",
        "station_id": "WEIGHT-STATION-01",
        "cultivars": [{"cultivar_id": "CV-001", "name": "Scripted Cultivar"}],
        "capture_mode": "automatic",
        "unit": "g",
        "container_id": "DEFAULT",
        "tare_g": 0.0,
        "maximum_capacity_g": 10000.0,
    }
    created = runtime.dispatch("run.new", {"definition": definition, "data_root": runtime.controller.settings.data_root, "simulator": True})
    connected = runtime.connect_simulator()
    runtime.zero_scale()
    runtime.simulator_set_weight(weight_g)
    submitted = runtime.submit_barcode(barcode)
    deadline = time.time() + 3.0
    while time.time() < deadline and runtime.controller.state != "WAITING_FOR_BARCODE":
        time.sleep(0.05)
    snapshot = runtime.snapshot()
    runtime.close()
    return {
        "created": created,
        "connected": connected,
        "submitted": submitted,
        "snapshot": snapshot,
        "status": "PASS" if snapshot["last_saved"] and snapshot["state"] == "WAITING_FOR_BARCODE" else "FAIL",
    }
