"""
BBWS SR1 product smoke: simulator capture, sticky strain, rebuild CSV, reconcile.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from best_buds_weight_station.operator_runtime import OperatorRuntime  # noqa: E402
from best_buds_weight_station.reports import reconcile_export_to_jsonl  # noqa: E402


def wait_state(runtime: OperatorRuntime, wanted: str, timeout: float = 5.0) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        state = runtime.controller.state
        if state == wanted:
            return state
        time.sleep(0.05)
    return runtime.controller.state


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="bbws_sr1_smoke_") as tmp:
        runtime = OperatorRuntime(data_root=tmp, capture_mode="manual")
        created = runtime.dispatch(
            "run.new",
            {
                "definition": {
                    "run_id": "BBWS-SR1-SMOKE",
                    "operator_id": "SR1-OPERATOR",
                    "facility_id": "BEST-BUDS",
                    "station_id": "WEIGHT-STATION-01",
                    "cultivars": [{"cultivar_id": "CV-001", "name": "Smoke Cultivar"}],
                    "capture_mode": "manual",
                    "unit": "g",
                    "container_id": "DEFAULT",
                    "tare_g": 0.0,
                    "maximum_capacity_g": 10000.0,
                },
                "data_root": tmp,
                "simulator": True,
            },
        )
        assert created["status"] == "completed", created
        connected = runtime.connect_simulator()
        assert connected["status"] == "completed", connected
        runtime.zero_scale()
        runtime.simulator_set_weight(1250.0)
        submitted = runtime.submit_barcode("SR1-PLANT-001")
        assert submitted["status"] in {"accepted", "completed"}, submitted
        assert wait_state(runtime, "MANUAL_CONFIRM") == "MANUAL_CONFIRM"
        confirmed = runtime.dispatch("capture.confirm", {"operator_note": "first", "void_status": "none"})
        assert confirmed["status"] == "completed", confirmed
        assert wait_state(runtime, "WAITING_FOR_BARCODE") == "WAITING_FOR_BARCODE"

        changed = runtime.dispatch("run.set_active_cultivar", {"name": "Blue Dream"})
        assert changed["status"] == "completed", changed
        runtime.simulator_set_weight(980.0)
        submitted2 = runtime.submit_barcode("SR1-PLANT-002")
        assert submitted2["status"] in {"accepted", "completed"}, submitted2
        assert wait_state(runtime, "MANUAL_CONFIRM") == "MANUAL_CONFIRM"
        confirmed2 = runtime.dispatch(
            "capture.confirm",
            {"operator_note": "sr1 smoke", "void_status": "none"},
        )
        assert confirmed2["status"] == "completed", confirmed2
        record = (confirmed2.get("data") or {}).get("record") or {}
        assert record.get("cultivar_normalized_name") == "Blue Dream", record

        rebuilt = runtime.dispatch("spreadsheet.rebuild")
        assert rebuilt["status"] == "completed", rebuilt
        session_dir = runtime.controller.loaded_run.store.session_dir
        receipt = reconcile_export_to_jsonl(session_dir)
        assert receipt["status"] == "pass", receipt

        # Duplicate warning path
        runtime.simulator_set_weight(900.0)
        runtime.submit_barcode("SR1-PLANT-001")
        assert wait_state(runtime, "MANUAL_CONFIRM") == "MANUAL_CONFIRM"
        dup = runtime.dispatch("capture.confirm", {})
        assert dup["status"] == "completed", dup
        assert (dup.get("data") or {}).get("feedback") == "warning", dup

        out = {
            "status": "PASS",
            "session_dir": str(session_dir),
            "reconcile": receipt,
            "active_cultivar": runtime.snapshot().get("cultivar"),
            "records": 3,
        }
        # Persist field-style receipt for S07
        reports = ROOT / "reports"
        reports.mkdir(exist_ok=True)
        (reports / "bbws_s07_field_e2e_receipt.v0.1.0.json").write_text(
            json.dumps(
                {
                    "receipt_type": "field_e2e_simulator",
                    "status": "pass",
                    "session_dir": str(session_dir),
                    "record_count": 3,
                    "scanner_transport": "hid_keyboard_wedge",
                    "path": "scan→weigh→record→csv→reconcile",
                    "non_claims": [
                        "Not legal-for-trade / metrology certification",
                        "Simulator evidence is not physical metrology proof",
                    ],
                    "reconcile": receipt,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        runtime.close()
        print(json.dumps(out, indent=2, default=str))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
