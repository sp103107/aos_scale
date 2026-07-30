from __future__ import annotations
from typing import Any

from .response_models import AliceResponse, RequiredAction, Severity, TruthClass

REQUIRED_COMMIT_FIELDS = (
    "receipt_id", "record_id", "status", "local_commit", "jsonl_event_id",
    "individual_record_path", "checkpoint_version", "record_hash",
)


def valid_commit_receipt(receipt: dict[str, Any] | None) -> bool:
    if not isinstance(receipt, dict):
        return False
    if receipt.get("status") != "committed" or receipt.get("local_commit") is not True:
        return False
    return all(receipt.get(field) not in (None, "") for field in REQUIRED_COMMIT_FIELDS)


def commit_evidence_refs(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"evidence_type": "jsonl_event", "reference": receipt["jsonl_event_id"]},
        {"evidence_type": "individual_record", "reference": receipt["individual_record_path"]},
        {"evidence_type": "checkpoint", "reference": str(receipt["checkpoint_version"])},
        {"evidence_type": "hash_chain", "reference": receipt["record_hash"]},
        {"evidence_type": "commit_receipt", "reference": receipt["receipt_id"]},
    ]


class AliceReceiptInterpreter:
    def interpret(self, result: dict[str, Any], *, state: str = "LOCAL_COMMIT_PENDING",
                  session_id: str | None = None, correlation_id: str | None = None) -> AliceResponse:
        status = result.get("status")
        if status == "duplicate":
            record_id = result.get("record_id")
            receipt_id = result.get("original_receipt_id")
            if not record_id or not receipt_id:
                return AliceResponse(
                    state="BLOCKED", truth_class=TruthClass.BLOCKED,
                    severity=Severity.ERROR,
                    operator_message=(
                        "A duplicate command was reported, but the original commit receipt could not be resolved. "
                        "Do not resubmit automatically. Open diagnostics and verify the authoritative ledger."
                    ),
                    required_action=RequiredAction("open_diagnostics"),
                    allowed_actions=["open_diagnostics", "cancel_session"],
                    blocked_actions=["scan_barcode", "success_beep", "advance_to_next_barcode", "repeat_non_idempotent_command"],
                    correlation_id=correlation_id, session_id=session_id,
                )
            refs = [{"evidence_type": "original_commit_receipt", "reference": receipt_id}]
            return AliceResponse(
                state="RECORD_SAVED", truth_class=TruthClass.RECEIPT_CONFIRMED,
                severity=Severity.INFO,
                operator_message=f"This command was already committed as record {record_id}. No second record was created.",
                required_action=RequiredAction("scan_barcode"),
                allowed_actions=["scan_barcode", "open_record", "open_run_summary"],
                blocked_actions=["repeat_non_idempotent_command"], evidence_refs=refs,
                correlation_id=correlation_id, session_id=session_id,
            )

        receipt = result.get("receipt") if isinstance(result.get("receipt"), dict) else result
        if valid_commit_receipt(receipt):
            record_id = receipt["record_id"]
            net_g = receipt.get("net_g")
            if net_g is None:
                msg = f"Record {record_id} saved locally. Scan the next container."
            else:
                msg = f"Record {record_id} saved locally. Net weight: {float(net_g):.1f} g. Scan the next container."
            non_claims: list[str] = []
            derivative = receipt.get("derivative_status", {})
            if derivative.get("xlsx") == "pending_sync" or result.get("spreadsheet_update") is False:
                msg = "The authoritative local record was saved. The spreadsheet update is pending and will be retried. Scan the next container."
                non_claims.append("Spreadsheet continuation is not authoritative.")
            return AliceResponse(
                state="RECORD_SAVED", truth_class=TruthClass.RECEIPT_CONFIRMED,
                severity=Severity.INFO, operator_message=msg,
                required_action=RequiredAction("scan_barcode"),
                allowed_actions=["scan_barcode", "open_record", "open_run_summary"],
                blocked_actions=[], evidence_refs=commit_evidence_refs(receipt),
                non_claims=non_claims, correlation_id=correlation_id, session_id=session_id,
            )

        failure_code = result.get("failure_code") or receipt.get("failure_code") if isinstance(receipt, dict) else None
        if failure_code == "AUTHORITATIVE_APPEND_FAILED":
            message = "The weight was not saved. Authoritative local storage failed. Keep the container on the scale and contact the station administrator."
        elif failure_code == "INDIVIDUAL_RECORD_WRITE_FAILED":
            message = "The weight was not acknowledged as saved because the individual record file failed. Keep the container on the scale and start recovery review."
        elif failure_code == "CHECKPOINT_WRITE_FAILED":
            message = "The weight was not acknowledged as saved because the session checkpoint failed. Keep the container on the scale and start recovery review."
        elif failure_code == "SERIAL_DISCONNECTED":
            message = "The scale connection was lost before the record was committed. The weight was not saved. Reconnect the device and re-establish a stable reading."
        else:
            message = "The weight was not acknowledged as saved because no valid local commit receipt was returned. Review storage status before continuing."
        return AliceResponse(
            state="ERROR", truth_class=TruthClass.FAIL, severity=Severity.CRITICAL,
            operator_message=message,
            required_action=RequiredAction("follow_recovery_instruction"),
            allowed_actions=["follow_recovery_instruction", "open_diagnostics", "cancel_session"],
            blocked_actions=["success_beep", "advance_to_next_barcode", "repeat_capture_without_review"],
            correlation_id=correlation_id, session_id=session_id,
        )
