from __future__ import annotations
from collections.abc import Mapping
from typing import Any

from .errors import AuthorityViolation
from .response_models import TruthClass

TRUTH_CLASSES = {item.value for item in TruthClass}

ALLOWED_ACTIONS: dict[str, tuple[str, ...]] = {
    "NO_RUN": (
        "run.new",
        "run.load",
        "run.resume",
        "settings.data_location.set",
        "device.discover",
        "device.connect",
        "device.disconnect",
        "device.ping",
        "device.status",
        "ui.open_scale_setup",
    ),    "RUN_SETUP": ("run.new", "settings.data_location.set", "cancel_session"),
    "RUN_READY": ("device.discover", "device.connect", "run.finish", "settings.capture_mode.set"),
    "DEVICE_CONNECTING": ("device.disconnect", "open_diagnostics"),
    "DISCONNECTED": ("reconnect_device", "open_diagnostics", "cancel_session"),
    "DEVICE_READY": ("begin_session_setup", "tare", "open_diagnostics"),
    "SESSION_SETUP": ("register_cultivar", "review_run_manifest", "cancel_session"),
    "SESSION_READY": ("start_capture", "review_run_summary", "cancel_session"),
    "WAITING_FOR_BARCODE": ("scan_barcode", "barcode.submit", "scale.zero", "scale.container_tare.set", "scale.container_tare.capture", "scale.calibration.start", "run.finish", "open_run_summary"),
    "BARCODE_CAPTURED": ("review_barcode", "cancel_capture"),
    "WAITING_FOR_STABLE_WEIGHT": ("keep_load_still", "cancel_capture", "reconnect_device"),
    "WEIGHT_STABLE": ("record_automatic", "review_capture", "cancel_capture"),
    "AUTO_RECORD": ("wait_for_commit_receipt", "cancel_if_supported"),
    "MANUAL_CONFIRM": ("confirm_and_continue", "capture.confirm", "capture.cancel", "review_capture"),
    "LOCAL_COMMIT_PENDING": ("wait_for_commit_receipt", "open_storage_status"),
    "RECORD_SAVED": ("scan_barcode", "open_record", "open_run_summary"),
    "RECOVERY_REQUIRED": ("recover_from_ledger", "open_recovery_details", "cancel_session"),
    "BLOCKED": ("resolve_blocking_condition", "open_diagnostics", "cancel_session"),
    "ERROR": ("follow_recovery_instruction", "open_diagnostics", "cancel_session"),
    "RUN_FINISHED": ("run.new", "run.load", "report.export", "open_run_summary"),
}

PROHIBITED_DIRECT_ACTIONS = {
    "append_weight_record_directly",
    "overwrite_immutable_event",
    "claim_compliance",
    "claim_certification",
    "claim_production_ready",
    "retry_non_idempotent_automatically",
}

SENSITIVE_KEYS = {
    "password", "secret", "token", "access_token", "refresh_token", "api_key",
    "private_key", "authorization", "cookie", "filesystem_path", "stack_trace",
}


def allowed_actions_for(state: str) -> list[str]:
    return list(ALLOWED_ACTIONS.get(state, ALLOWED_ACTIONS["ERROR"]))


def require_allowed(state: str, action: str) -> None:
    if action in PROHIBITED_DIRECT_ACTIONS or action not in allowed_actions_for(state):
        raise AuthorityViolation(f"Action {action!r} is not allowed in state {state!r}.")


def validate_truth_class(value: str) -> str:
    if value not in TRUTH_CLASSES:
        raise ValueError(f"Unsupported truth class: {value}")
    return value


def operator_safe_error(error: Any) -> str:
    text = str(error).strip().lower()
    if "malformed serial" in text or "raw:" in text or "hx711 test" in text:
        return (
            "The scale replied, but it is not running the weight-station firmware. "
            "In Arduino IDE, upload firmware/elegoo_uno_r3_hx711/best_buds_scale_firmware.ino, "
            "close Serial Monitor, then reconnect at 115200."
        )
    if "serial" in text or "disconnect" in text or "permission" in text or "access is denied" in text:
        return "The scale connection is unavailable. Close Serial Monitor, reconnect the USB cable, and try again."
    if "jsonl" in text or "append" in text or "storage" in text:
        return "Authoritative local storage failed. The weight was not acknowledged as saved."
    if "checkpoint" in text:
        return "The session checkpoint could not be completed. Keep the item in place and start recovery review."
    if "individual" in text and "json" in text:
        return "The individual record file could not be completed. Keep the item in place and start recovery review."
    if "duplicate idempotency" in text:
        return "This command was already processed. Review the original receipt before taking another action."
    return "The requested operation could not be completed. Review station status or contact an administrator."


def redact_operator_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(k): ("[REDACTED]" if str(k).lower() in SENSITIVE_KEYS else redact_operator_payload(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact_operator_payload(v) for v in value]
    if isinstance(value, str) and len(value) > 500:
        return value[:497] + "..."
    return value
