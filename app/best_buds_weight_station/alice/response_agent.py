from __future__ import annotations
from typing import Any

from .authority import operator_safe_error
from .command_builder import AliceCommandBuilder
from .receipt_interpreter import AliceReceiptInterpreter
from .recovery_router import AliceRecoveryRouter
from .response_models import AliceResponse, RequiredAction, Severity, TruthClass
from .state_interpreter import AliceStateInterpreter

REQUIRED_START_FIELDS = (
    "operator_id", "facility_id", "station_id", "run_id", "measurement_stage",
    "weight_purpose", "capture_mode", "stability_profile_id", "maximum_capacity_g", "cultivars",
)


def validate_start_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in REQUIRED_START_FIELDS if not manifest.get(key)]
    if missing:
        return {
            "accepted": False,
            "missing": missing,
            "alice_message": "Run setup is blocked until required fields are complete.",
            "truth_class": TruthClass.BLOCKED.value,
        }
    if not manifest.get("data_root_writable"):
        return {
            "accepted": False,
            "missing": ["data_root_writable"],
            "alice_message": "Local authoritative storage preflight failed.",
            "truth_class": TruthClass.BLOCKED.value,
        }
    return {
        "accepted": True,
        "missing": [],
        "alice_message": "Run manifest accepted. Review before capture.",
        "truth_class": TruthClass.PASS.value,
    }


class AliceResponseAgent:
    def __init__(self) -> None:
        self.states = AliceStateInterpreter()
        self.commands = AliceCommandBuilder()
        self.receipts = AliceReceiptInterpreter()
        self.recovery = AliceRecoveryRouter()

    def respond(self, state: str, *, context: dict[str, Any] | None = None,
                backend_result: dict[str, Any] | None = None,
                recovery_condition: dict[str, Any] | None = None,
                session_id: str | None = None, correlation_id: str | None = None) -> AliceResponse:
        if backend_result is not None:
            return self.receipts.interpret(backend_result, state=state, session_id=session_id, correlation_id=correlation_id)
        if recovery_condition is not None:
            return self.recovery.route(recovery_condition, session_id=session_id, correlation_id=correlation_id)
        return self.states.interpret(state, context, session_id=session_id, correlation_id=correlation_id)

    def blocked_from_exception(self, state: str, error: Exception, *, session_id: str | None = None) -> AliceResponse:
        return AliceResponse(
            state="ERROR", truth_class=TruthClass.FAIL, severity=Severity.ERROR,
            operator_message=operator_safe_error(error),
            required_action=RequiredAction("follow_recovery_instruction"),
            allowed_actions=["follow_recovery_instruction", "open_diagnostics", "cancel_session"],
            blocked_actions=["success_beep", "advance_to_next_barcode"], session_id=session_id,
        )
