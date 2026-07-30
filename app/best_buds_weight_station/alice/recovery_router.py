from __future__ import annotations
from typing import Any

from .response_models import AliceResponse, RequiredAction, Severity, TruthClass


class AliceRecoveryRouter:
    def route(self, condition: dict[str, Any], *, session_id: str | None = None,
              correlation_id: str | None = None) -> AliceResponse:
        if condition.get("serial_disconnected"):
            return AliceResponse(
                state="DISCONNECTED", truth_class=TruthClass.FAIL, severity=Severity.ERROR,
                operator_message="The scale connection was lost before the record was committed. The weight was not saved. Reconnect the device and re-establish a stable reading.",
                required_action=RequiredAction("reconnect_device"),
                allowed_actions=["reconnect_device", "open_diagnostics", "cancel_session"],
                blocked_actions=["success_beep", "advance_to_next_barcode"],
                session_id=session_id, correlation_id=correlation_id,
            )
        if condition.get("ledger_valid") and condition.get("checkpoint_behind"):
            receipt = condition.get("recovery_receipt")
            if receipt and receipt.get("status") == "recovered":
                rebuilt = int(receipt.get("checkpoint_rebuilt_count", 1))
                return AliceResponse(
                    state="SESSION_READY", truth_class=TruthClass.RECEIPT_CONFIRMED, severity=Severity.INFO,
                    operator_message=f"The session was recovered from the authoritative event ledger. {rebuilt} checkpoint was rebuilt. No uncommitted weight was restored.",
                    required_action=RequiredAction("review_run_summary"),
                    allowed_actions=["review_run_summary", "start_capture", "open_recovery_details"],
                    evidence_refs=[{"evidence_type": "recovery_receipt", "reference": receipt.get("receipt_id")}],
                    non_claims=["No in-memory-only or uncommitted weight was restored."],
                    session_id=session_id, correlation_id=correlation_id,
                )
            return AliceResponse(
                state="RECOVERY_REQUIRED", truth_class=TruthClass.BLOCKED, severity=Severity.WARNING,
                operator_message="The event ledger is valid, but the session checkpoint is behind. Rebuild derived state from the ledger before capture resumes.",
                required_action=RequiredAction("recover_from_ledger"),
                allowed_actions=["recover_from_ledger", "open_recovery_details", "cancel_session"],
                blocked_actions=["start_capture"], session_id=session_id, correlation_id=correlation_id,
            )
        return AliceResponse(
            state="ERROR", truth_class=TruthClass.BLOCKED, severity=Severity.ERROR,
            operator_message="Recovery evidence is insufficient. Do not resume capture until an administrator reviews the session ledger and checkpoint.",
            required_action=RequiredAction("open_recovery_details"),
            allowed_actions=["open_recovery_details", "cancel_session"],
            blocked_actions=["start_capture", "success_beep"], session_id=session_id, correlation_id=correlation_id,
        )
