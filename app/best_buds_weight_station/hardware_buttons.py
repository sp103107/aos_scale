from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .actions import ActionRequest


DEFAULT_BUTTON_MAP = {
    "green": "capture.confirm",
    "yellow": "scale.zero",
    "red": "capture.cancel",
    "blue": "ui.open_scale_setup",
}


@dataclass(frozen=True)
class ButtonEvent:
    button: str
    event_type: str = "press"
    duration_ms: int = 0


class LocalHardwareButtonAdapter:
    """Local test adapter. It emits canonical actions and never writes storage."""

    def __init__(self, mapping: dict[str, str] | None = None):
        self.mapping = dict(mapping or DEFAULT_BUTTON_MAP)

    def translate(self, event: ButtonEvent, *, payload: dict[str, Any] | None = None) -> ActionRequest:
        key = event.button.lower().strip()
        if key not in self.mapping:
            raise ValueError("unmapped hardware button")
        action = self.mapping[key]
        value = dict(payload or {})
        value["button_event"] = {"button": key, "event_type": event.event_type, "duration_ms": event.duration_ms}
        if action == "scale.calibration.accept" and event.duration_ms < 1500:
            raise PermissionError("calibration acceptance requires protected long-press confirmation")
        return ActionRequest(action_type=action, payload=value, source="local_hardware_button")
