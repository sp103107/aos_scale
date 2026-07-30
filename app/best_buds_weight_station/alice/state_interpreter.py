from __future__ import annotations
from typing import Any

from .authority import allowed_actions_for
from .response_models import AliceResponse, RequiredAction, Severity, TruthClass


STATE_INSTRUCTIONS: dict[str, tuple[str, TruthClass, Severity, str | None]] = {
    "NO_RUN": ("Create a new run, load an existing run, or resume the most recent run.", TruthClass.NOT_RUN, Severity.INFO, "run.resume"),
    "RUN_SETUP": ("Complete the run fields and select a writable data location.", TruthClass.PENDING, Severity.INFO, "run.new"),
    "RUN_READY": ("The run is loaded. Connect the scale before scanning a barcode.", TruthClass.PENDING, Severity.INFO, "device.connect"),
    "DEVICE_CONNECTING": ("The scale connection is being validated. Wait for PING and STATUS results.", TruthClass.PENDING, Severity.INFO, "wait_for_device_status"),
    "DISCONNECTED": ("Connect the scale device before continuing.", TruthClass.BLOCKED, Severity.WARNING, "reconnect_device"),
    "DEVICE_READY": ("The device is ready. Complete harvest-run setup before capture.", TruthClass.PASS, Severity.INFO, "begin_session_setup"),
    "SESSION_SETUP": ("Complete the required harvest-run fields and cultivar roster.", TruthClass.PENDING, Severity.INFO, "review_run_manifest"),
    "SESSION_READY": ("The harvest run is ready. Start capture when the scale is clear and stable.", TruthClass.PASS, Severity.INFO, "start_capture"),
    "WAITING_FOR_BARCODE": ("Scan the next plant or container barcode.", TruthClass.PASS, Severity.INFO, "scan_barcode"),
    "BARCODE_CAPTURED": ("Barcode captured. Place the container on the scale and keep it still.", TruthClass.PENDING, Severity.INFO, "keep_load_still"),
    "WAITING_FOR_STABLE_WEIGHT": ("Keep the load centered and still while the weight stabilizes.", TruthClass.PENDING, Severity.INFO, "keep_load_still"),
    "WEIGHT_STABLE": ("Weight is stable. Review the capture before the record command is issued.", TruthClass.PENDING, Severity.INFO, "review_capture"),
    "AUTO_RECORD": ("The automatic record command is pending. Wait for the local commit receipt.", TruthClass.PENDING, Severity.INFO, "wait_for_commit_receipt"),
    "MANUAL_CONFIRM": ("Review the barcode, cultivar, tare, container, and stable weight, then select Confirm & Continue.", TruthClass.PENDING, Severity.INFO, "confirm_and_continue"),
    "LOCAL_COMMIT_PENDING": ("Local commit is pending. Do not remove the container until a terminal receipt is returned.", TruthClass.PENDING, Severity.WARNING, "wait_for_commit_receipt"),
    "RECORD_SAVED": ("The local commit receipt is confirmed. Scan the next container.", TruthClass.RECEIPT_CONFIRMED, Severity.INFO, "scan_barcode"),
    "RECOVERY_REQUIRED": ("Session recovery is required before capture can continue.", TruthClass.BLOCKED, Severity.WARNING, "recover_from_ledger"),
    "BLOCKED": ("A required application gate is blocked. Resolve the stated condition before continuing.", TruthClass.BLOCKED, Severity.WARNING, "resolve_blocking_condition"),
    "ERROR": ("The operation failed. Follow the recovery instruction before continuing.", TruthClass.FAIL, Severity.ERROR, "follow_recovery_instruction"),
    "RUN_FINISHED": ("The run is finished. Records remain immutable; export or start another run.", TruthClass.RECEIPT_CONFIRMED, Severity.INFO, "open_run_summary"),
}


class AliceStateInterpreter:
    def interpret(self, state: str, context: dict[str, Any] | None = None, *,
                  session_id: str | None = None, correlation_id: str | None = None) -> AliceResponse:
        context = context or {}
        if state == "SESSION_SETUP" and not context.get("cultivar_roster"):
            return AliceResponse(
                state=state, truth_class=TruthClass.BLOCKED, severity=Severity.WARNING,
                operator_message="The harvest run cannot begin until at least one cultivar is registered.",
                required_action=RequiredAction("register_cultivar"),
                allowed_actions=["register_cultivar", "review_run_manifest", "cancel_session"],
                blocked_actions=["start_capture"], session_id=session_id, correlation_id=correlation_id,
            )
        message, truth, severity, action = STATE_INSTRUCTIONS.get(state, STATE_INSTRUCTIONS["ERROR"])
        if state == "MANUAL_CONFIRM" and context.get("net_g") is not None:
            message = f"Weight is stable at {float(context['net_g']):.1f} g net. Review the barcode, cultivar, tare, and container, then select Confirm & Continue."
        return AliceResponse(
            state=state, truth_class=truth, severity=severity, operator_message=message,
            required_action=RequiredAction(action) if action else None,
            allowed_actions=allowed_actions_for(state),
            blocked_actions=[], session_id=session_id, correlation_id=correlation_id,
        )
