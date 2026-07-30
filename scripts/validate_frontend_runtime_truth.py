from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    production = (ROOT / "app/best_buds_weight_station/production_ui.py").read_text(encoding="utf-8")
    pyside = (ROOT / "app/best_buds_weight_station/pyside_frontend.py").read_text(encoding="utf-8")
    runtime = (ROOT / "app/best_buds_weight_station/operator_runtime.py").read_text(encoding="utf-8")
    controller = (ROOT / "app/best_buds_weight_station/application_controller.py").read_text(encoding="utf-8")
    checks = {
        "pyside_primary": "launch_pyside" in production and "class MainWindow" in pyside,
        "scale_setup_dialog": "class ScaleSetupDialog" in pyside,
        "tare_dialog": "class TareDialog" in pyside and "capture_container_tare" in pyside,
        "calibration_dialog": "class CalibrationDialog" in pyside and "accept_calibration" in pyside,
        "background_worker": "class ScaleReadingWorker" in runtime and "reading.ingest" in runtime,
        "worker_shutdown": "self.runtime.close()" in pyside and "worker.stop" in runtime,
        "no_synthetic_physical_zero": '"readings_g": [0.0' not in production and '"readings_g": [0.0' not in pyside,
        "scale_setup_not_placeholder": "Scale Setup may be opened locally" not in controller,
        "alice_state_refresh": "_refresh_alice_for_state" in controller,
        "barcode_keyboard_path": "returnPressed.connect(self.submit_barcode)" in pyside,
        "barcode_labeled": "PLANT OR CONTAINER BARCODE" in pyside and "PLANT OR CONTAINER BARCODE" in production,
        "shared_action_layout": "ROUTINE_ACTION_LAYOUT" in pyside and "ROUTINE_ACTION_LAYOUT" in production,
        "physical_warning_not_success": "PHYSICAL SERIAL - TESTING REQUIRED" in pyside and "PHYSICAL SERIAL - TESTING REQUIRED" in production,
        "dead_contract_stubs_removed": "_LegacyCallbackNamesForContract" not in production,
        "windows_first_paths": "LOCALAPPDATA" in (ROOT / "app/best_buds_weight_station/platform_paths.py").read_text(encoding="utf-8"),
    }
    failures = [name for name, passed in checks.items() if not passed]
    result = {"status": "FAIL" if failures else "PASS", "checks": checks, "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
