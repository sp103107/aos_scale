from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from ..actions import ActionRequest
from ..application_controller import ApplicationController
from ..hardware_buttons import ButtonEvent, LocalHardwareButtonAdapter
from ..remote_boundaries import RemoteTransportConfig
from ..simulator import stable_sequence
from ..version import __version__


def _definition(mode: str, session_id: str, run_id: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "operator_id": "OP-DRYRUN",
        "facility_id": "BEST-BUDS",
        "station_id": "WS-DRYRUN-01",
        "cultivars": [{"cultivar_id": "CV-DRYRUN", "name": "Dry Run Cultivar"}],
        "capture_mode": mode,
        "unit": "g",
        "container_id": "BIN-DRYRUN",
        "tare_g": 50.0,
        "maximum_capacity_g": 10000.0,
        "session_id": session_id,
    }


def _run_capture(root: Path, mode: str, barcode: str) -> dict[str, Any]:
    controller = ApplicationController(root / "config")
    data_root = root / "data"
    controller.settings_store.update(data_root=str(data_root), capture_mode=mode)

    created = controller.dispatch(
        ActionRequest(
            "run.new",
            {
                "definition": _definition(mode, f"SESSION-{mode.upper()}", f"DRYRUN-{mode.upper()}"),
                "data_root": str(data_root),
                "simulator": True,
            },
        )
    )
    if created.status != "completed":
        raise RuntimeError(f"run.new failed: {created.to_dict()}")

    connected = controller.dispatch(ActionRequest("device.connect", {"simulator": True}))
    if connected.truth_class != "SIMULATOR_PASS":
        raise RuntimeError(f"device.connect failed: {connected.to_dict()}")

    zero = controller.dispatch(ActionRequest("scale.zero", {"readings_g": [0.0, 0.1, -0.1, 0.0, 0.0]}))
    if zero.status != "completed":
        raise RuntimeError(f"scale.zero failed: {zero.to_dict()}")

    tare = controller.dispatch(
        ActionRequest("scale.container_tare.set", {"container_id": "BIN-DRYRUN", "tare_g": 50.0})
    )
    if tare.status != "completed":
        raise RuntimeError(f"scale.container_tare.set failed: {tare.to_dict()}")

    submitted = controller.dispatch(ActionRequest("barcode.submit", {"barcode": barcode}))
    if submitted.status not in {"accepted", "completed"}:
        raise RuntimeError(f"barcode.submit failed: {submitted.to_dict()}")

    terminal = None
    for reading in stable_sequence(1250.0):
        terminal = controller.dispatch(
            ActionRequest("reading.ingest", {"weight_g": reading.weight_g, "raw_value": reading.raw_value})
        )

    if mode == "manual":
        if controller.state != "MANUAL_CONFIRM":
            raise RuntimeError(f"manual mode did not reach MANUAL_CONFIRM: {controller.state}")
        terminal = controller.dispatch(ActionRequest("capture.confirm"))

    if terminal is None or terminal.truth_class != "RECEIPT_CONFIRMED":
        raise RuntimeError(f"terminal receipt not confirmed: {terminal.to_dict() if terminal else None}")
    if controller.loaded_run is None or controller.loaded_run.store.sequence != 1:
        raise RuntimeError("authoritative store sequence did not advance")

    pointer = controller.settings_store.read_recent_run()
    if pointer is None or pointer.get("last_sequence") != 1:
        raise RuntimeError(f"durable recent-run pointer mismatch: {pointer}")

    session_manifest = controller.loaded_run.manifest_path
    controller2 = ApplicationController(root / "config")
    loaded = controller2.dispatch(ActionRequest("run.load", {"selection": str(session_manifest)}))
    if loaded.status != "completed":
        raise RuntimeError(f"run.load failed: {loaded.to_dict()}")
    if controller2.loaded_run is None or controller2.loaded_run.store.sequence != 1:
        raise RuntimeError("loaded run sequence mismatch")

    controller3 = ApplicationController(root / "config")
    resumed = controller3.dispatch(ActionRequest("run.resume"))
    if resumed.status != "completed":
        raise RuntimeError(f"run.resume failed: {resumed.to_dict()}")
    if controller3.loaded_run is None or controller3.loaded_run.store.sequence != 1:
        raise RuntimeError("resumed run sequence mismatch")

    return {
        "mode": mode,
        "record_id": controller.last_record["record_id"],
        "gross_g": controller.last_record["gross_g"],
        "tare_g": controller.last_record["tare_g"],
        "net_g": controller.last_record["net_g"],
        "truth_class": terminal.truth_class,
        "state": controller.state,
        "sequence": controller.loaded_run.store.sequence,
        "recent_pointer_sequence": pointer["last_sequence"],
        "load_resume_verified": True,
        "session_manifest": str(session_manifest),
    }


def _run_calibration(root: Path) -> dict[str, Any]:
    controller = ApplicationController(root / "config")
    data_root = root / "data"
    controller.settings_store.update(data_root=str(data_root), capture_mode="manual")
    controller.dispatch(
        ActionRequest(
            "run.new",
            {
                "definition": _definition("manual", "SESSION-CAL", "DRYRUN-CAL"),
                "data_root": str(data_root),
                "simulator": True,
            },
        )
    )
    controller.dispatch(ActionRequest("device.connect", {"simulator": True}))
    results = [
        controller.dispatch(ActionRequest("scale.calibration.start", {"maintenance_authorized": True})),
        controller.dispatch(
            ActionRequest("scale.calibration.sample", {"kind": "zero", "samples": [1000, 1001, 999, 1000]})
        ),
        controller.dispatch(
            ActionRequest(
                "scale.calibration.sample",
                {
                    "kind": "loaded",
                    "samples": [101000, 101001, 100999, 101000],
                    "reference_weight_g": 1000.0,
                },
            )
        ),
        controller.dispatch(
            ActionRequest("scale.calibration.test", {"samples": [101000, 101001, 100999, 101000]})
        ),
        controller.dispatch(
            ActionRequest(
                "scale.calibration.accept",
                {"maintenance_authorized": True, "second_confirmation": True},
            )
        ),
    ]
    if any(result.status != "completed" for result in results):
        raise RuntimeError(f"calibration dry run failed: {[r.to_dict() for r in results]}")
    receipt = results[-1].data["calibration_receipt"]
    return {
        "truth_class": results[-1].truth_class,
        "receipt_id": receipt["receipt_id"],
        "reference_weight_g": receipt["proposal"]["reference_weight_g"],
        "physical_device_pass": False,
        "certification_claimed": False,
    }


def run_software_dry_run(work_root: Path | None = None) -> dict[str, Any]:
    """Execute the real software-only operator loop in a disposable workspace.

    This function never claims physical hardware success. It exercises the same
    application controller, store, Alice receipt gate, run manager, calibration
    service, and canonical adapters used by the application.
    """
    if work_root is None:
        with tempfile.TemporaryDirectory(prefix="bbws-software-dry-run-") as td:
            return run_software_dry_run(Path(td))

    work_root = work_root.resolve()
    work_root.mkdir(parents=True, exist_ok=True)
    automatic = _run_capture(work_root / "automatic", "automatic", "AUTO-DRYRUN-001")
    manual = _run_capture(work_root / "manual", "manual", "MANUAL-DRYRUN-001")
    calibration = _run_calibration(work_root / "calibration")

    buttons = LocalHardwareButtonAdapter()
    mapping = {
        name: buttons.translate(ButtonEvent(name)).action_type
        for name in ("green", "yellow", "red", "blue")
    }
    bluetooth = RemoteTransportConfig("bluetooth")
    wifi = RemoteTransportConfig("wifi")
    bluetooth.validate()
    wifi.validate()

    return {
        "status": "PASS",
        "version": __version__,
        "evidence_class": "SIMULATOR_PASS",
        "automatic_loop": automatic,
        "manual_loop": manual,
        "calibration": calibration,
        "canonical_button_mapping": mapping,
        "bluetooth_boundary": "VALIDATED_DISABLED_NOT_RUN",
        "wifi_boundary": "VALIDATED_DISABLED_NOT_RUN",
        "physical_device": "NOT_RUN",
        "firmware_upload": "NOT_RUN",
        "uno_q": "NOT_RUN",
        "non_claims": [
            "No physical UNO, HX711, or load-cell pass.",
            "No physical calibration or hanging-load pass.",
            "No Bluetooth or Wi-Fi runtime activation.",
            "No legal-for-trade certification.",
        ],
    }


def main() -> int:
    print(json.dumps(run_software_dry_run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
