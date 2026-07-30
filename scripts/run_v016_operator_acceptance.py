from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from best_buds_weight_station.version import __version__
from best_buds_weight_station.operator_runtime import OperatorRuntime


def wait_for_samples(runtime: OperatorRuntime, count: int = 8, timeout: float = 3.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if len(runtime.buffer.recent(count)) >= count:
            return
        time.sleep(0.05)
    raise TimeoutError(f"expected {count} live samples")


def wait_for_state(runtime: OperatorRuntime, state: str, timeout: float = 3.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if runtime.controller.state == state:
            return
        time.sleep(0.05)
    raise TimeoutError(f"expected state {state}; got {runtime.controller.state}")


def definition(run_id: str, mode: str) -> dict:
    return {
        "run_id": run_id,
        "operator_id": "OPERATOR-ACCEPTANCE",
        "facility_id": "BEST-BUDS",
        "station_id": "WEIGHT-STATION-01",
        "cultivars": [{"cultivar_id": "CV-001", "name": "Acceptance Cultivar"}],
        "capture_mode": mode,
        "unit": "g",
        "container_id": "DEFAULT",
        "tare_g": 0.0,
        "maximum_capacity_g": 10000.0,
    }


def automatic_flow(root: Path) -> dict:
    runtime = OperatorRuntime(root / "automatic", capture_mode="automatic")
    try:
        runtime.dispatch("run.new", {"definition": definition("V016-AUTO", "automatic"), "data_root": str(root / "automatic"), "simulator": True})
        runtime.connect_simulator()
        runtime.zero_scale()
        runtime.simulator_set_weight(100.0)
        runtime.buffer.clear(); wait_for_samples(runtime)
        tare = runtime.capture_container_tare("HOOK-SLING")
        runtime.simulator_set_weight(1350.0)
        runtime.buffer.clear(); wait_for_samples(runtime)
        submitted = runtime.submit_barcode("AUTO-PLANT-001")
        wait_for_state(runtime, "WAITING_FOR_BARCODE")
        snap = runtime.snapshot()
        return {"submitted": submitted, "tare": tare, "snapshot": snap, "pass": bool(snap["last_saved"] and snap["last_saved"]["net_g"] == 1250.0)}
    finally:
        runtime.close()


def manual_and_calibration_flow(root: Path) -> dict:
    runtime = OperatorRuntime(root / "manual", capture_mode="manual")
    try:
        runtime.dispatch("run.new", {"definition": definition("V016-MANUAL", "manual"), "data_root": str(root / "manual"), "simulator": True})
        runtime.connect_simulator()
        runtime.zero_scale()
        runtime.simulator_set_weight(1500.0)
        runtime.buffer.clear(); wait_for_samples(runtime)
        runtime.submit_barcode("MANUAL-PLANT-001")
        wait_for_state(runtime, "MANUAL_CONFIRM")
        confirmed = runtime.dispatch("capture.confirm")
        wait_for_state(runtime, "WAITING_FOR_BARCODE")

        runtime.start_calibration()
        runtime.simulator_set_weight(0.0); runtime.buffer.clear(); wait_for_samples(runtime)
        zero = runtime.add_calibration_zero_samples()
        runtime.simulator_set_weight(2000.0); runtime.buffer.clear(); wait_for_samples(runtime)
        proposal = runtime.add_calibration_loaded_samples(2000.0)
        runtime.buffer.clear(); wait_for_samples(runtime)
        tested = runtime.test_calibration()
        accepted = runtime.accept_calibration()
        snap = runtime.snapshot()
        return {
            "confirmed": confirmed,
            "zero_samples": zero,
            "proposal": proposal,
            "tested": tested,
            "accepted": accepted,
            "snapshot": snap,
            "pass": bool(snap["last_saved"] and accepted["status"] == "completed"),
        }
    finally:
        runtime.close()


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="bbws-v016-operator-") as td:
        root = Path(td)
        automatic = automatic_flow(root)
        manual = manual_and_calibration_flow(root)
        passed = automatic["pass"] and manual["pass"]
        result = {
            "version": __version__,
            "status": "PASS" if passed else "FAIL",
            "automatic_frontend_runtime": automatic,
            "manual_and_calibration_runtime": manual,
            "physical_device": "NOT_RUN",
            "windows_native_runtime": "NOT_RUN",
        }
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
