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
    "WEIGHT_STABLE": ("lock_weight", "capture.weight.lock", "review_capture", "cancel_capture", "capture.cancel"),
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
    raw = str(error).strip()
    text = raw.lower()
    # Pass through already operator-facing controller/scale messages.
    if raw and (
        type(error).__name__ == "InvalidActionState"
        or "measured" in text
        or "calibration was not saved" in text
        or "connect the scale first" in text
        or "keep the same" in text
        or "wait until" in text
    ):
        return raw
    if "local tolerance" in text or "calibration test did not pass" in text:
        return (
            "Calibration test did not match the reference mass closely enough. "
            "Keep the same verified mass on the pan, wait for it to settle, then run Test again. "
            "Calibration was not saved."
        )
    if "connect a validated scale" in text or "connect a scale before" in text:
        return "Connect the scale first (Scale → Scale Setup → Connect), wait for live readings, then try again."
    if "no run is loaded" in text:
        return "Start or resume a harvest run first when recording plants. Maintenance calibration can run after the scale is connected."
    if "at least three live" in text:
        return "Wait until the live weight is updating, then capture samples again."
    if "steadier pan" in text or "do not match the loaded pan" in text:
        return raw
    if "zero stability" in text:
        # Prefer the detailed scale_control message when it already explains spread vs limit.
        if "swung" in text and "limit" in text:
            return raw
        return (
            "Zero needs a steady empty pan. The main live number is averaged, so it can look calm "
            "while ZERO still sees device noise. Leave the pan empty, wait 2 seconds, press ZERO again."
        )
    # True wrong-firmware sketches (raw HX711 dumpers) — not stream/command interleave.
    if "hx711 test" in text or "raw hx711 test sketch" in text or (
        "malformed serial" in text and text.strip().startswith("malformed serial line from raw")
    ):
        return (
            "The scale replied, but it is not running the weight-station firmware. "
            "In Arduino IDE, upload firmware/elegoo_uno_r3_hx711/best_buds_scale_firmware.ino, "
            "close Serial Monitor, then reconnect at 115200."
        )
    if "malformed serial" in text or "set_cal" in text or "calibration factor was not acknowledged" in text:
        return (
            "The scale was still streaming while saving calibration, so the reply got mixed up. "
            "Try Accept again (the app now pauses live readings first). "
            "If it keeps failing, Disconnect → Connect, re-run Test, then Accept."
        )
    if "calibration rejected" in text:
        return "The scale rejected the calibration factor. Re-run Guided Calibration from Start, then Accept again."
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
    if type(error).__name__ == "AssertionError":
        return "Connect the scale first (Scale → Scale Setup → Connect), then try again."
    return "The requested operation could not be completed. Check the on-screen next step and try again."


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
