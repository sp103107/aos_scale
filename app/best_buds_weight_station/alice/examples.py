from __future__ import annotations
from typing import Any

from .response_agent import AliceResponseAgent
from .response_models import TruthClass


def robust_examples() -> dict[str, dict[str, Any]]:
    agent = AliceResponseAgent()
    commit = {
        "status": "committed", "local_commit": True, "receipt_id": "commit-000042",
        "record_id": "BB-HR-2026-0719-A-000042", "jsonl_event_id": "event-000042",
        "individual_record_path": "records/000042.json", "checkpoint_version": 42,
        "record_hash": "a" * 64, "net_g": 1200.0, "derivative_status": {"xlsx": "updated"},
    }
    return {
        "missing_cultivar": agent.respond("SESSION_SETUP", context={"cultivar_roster": []}).to_dict(),
        "automatic_commit": agent.respond("LOCAL_COMMIT_PENDING", backend_result=commit).to_dict(),
        "manual_confirm": agent.respond("MANUAL_CONFIRM", context={"net_g": 1200.0}).to_dict(),
        "jsonl_failure": agent.respond("LOCAL_COMMIT_PENDING", backend_result={"status": "failure", "failure_code": "AUTHORITATIVE_APPEND_FAILED", "local_commit": False}).to_dict(),
        "xlsx_pending": agent.respond("LOCAL_COMMIT_PENDING", backend_result={**commit, "derivative_status": {"xlsx": "pending_sync"}}).to_dict(),
        "duplicate": agent.respond("LOCAL_COMMIT_PENDING", backend_result={"status": "duplicate", "original_receipt_id": "commit-000042", "record_id": "BB-HR-2026-0719-A-000042"}).to_dict(),
        "serial_disconnect": agent.respond("ERROR", recovery_condition={"serial_disconnected": True}).to_dict(),
        "restart_recovery": agent.respond("RECOVERY_REQUIRED", recovery_condition={"ledger_valid": True, "checkpoint_behind": True, "recovery_receipt": {"status": "recovered", "receipt_id": "recovery-1", "checkpoint_rebuilt_count": 1}}).to_dict(),
        "firmware_blocked": {
            "statement_id": "alice-evidence-firmware-compile-v0.1.2",
            "subject": "Arduino UNO R3 firmware evidence boundary",
            "truth_class": TruthClass.BLOCKED.value,
            "statement": "Firmware source is present, but compilation is blocked because the Arduino AVR toolchain is unavailable in this environment.",
            "evidence_refs": [
                {"evidence_type": "firmware_source", "truth_class": TruthClass.SOURCE_PRESENT.value, "reference": "firmware/elegoo_uno_r3_hx711/best_buds_scale_firmware.ino"},
                {"evidence_type": "firmware_compile", "truth_class": TruthClass.BLOCKED.value, "reference": "reports/firmware_compile_receipt.v0.1.2.json"},
                {"evidence_type": "physical_hardware", "truth_class": TruthClass.NOT_RUN.value, "reference": "repo_release_state.json"},
            ],
            "non_claims": [
                "No firmware compile or upload pass.",
                "No physical UNO R3, HX711, load-cell, calibration, or hanging-load pass.",
            ],
        },
        "simulator_vs_physical": {
            "statement_id": "alice-evidence-simulator-boundary-v0.1.2",
            "subject": "Serial simulator versus physical weighing hardware",
            "truth_class": TruthClass.SIMULATOR_PASS.value,
            "statement": "Automatic and manual capture passed with the serial simulator. No physical UNO R3, HX711, load cell, calibration, or hanging-load test was performed.",
            "evidence_refs": [
                {"evidence_type": "simulator_self_test", "reference": "validation/simulator_self_test.v0.1.2.json"}
            ],
            "non_claims": [
                "Simulator evidence does not prove physical hardware operation or calibration."
            ],
        },
    }
