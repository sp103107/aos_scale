from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .models import now_rfc3339


class ActionType(str, Enum):
    RUN_NEW = "run.new"
    RUN_LOAD = "run.load"
    RUN_RESUME = "run.resume"
    RUN_FINISH = "run.finish"
    SETTINGS_DATA_LOCATION_SET = "settings.data_location.set"
    SETTINGS_CAPTURE_MODE_SET = "settings.capture_mode.set"
    SETTINGS_DISPLAY_UNIT_SET = "settings.display_unit.set"
    DEVICE_DISCOVER = "device.discover"
    DEVICE_CONNECT = "device.connect"
    DEVICE_DISCONNECT = "device.disconnect"
    DEVICE_STATUS = "device.status"
    DEVICE_PING = "device.ping"
    DEVICE_RECONNECT = "device.reconnect"
    DEVICE_STREAM_START = "device.stream.start"
    DEVICE_STREAM_STOP = "device.stream.stop"
    SCALE_ZERO = "scale.zero"
    SCALE_CONTAINER_TARE_CAPTURE = "scale.container_tare.capture"
    SCALE_CONTAINER_TARE_SET = "scale.container_tare.set"
    SCALE_CALIBRATION_START = "scale.calibration.start"
    SCALE_CALIBRATION_SAMPLE = "scale.calibration.sample"
    SCALE_CALIBRATION_TEST = "scale.calibration.test"
    SCALE_CALIBRATION_ACCEPT = "scale.calibration.accept"
    SCALE_CALIBRATION_CANCEL = "scale.calibration.cancel"
    BARCODE_SUBMIT = "barcode.submit"
    READING_INGEST = "reading.ingest"
    CAPTURE_CONFIRM = "capture.confirm"
    CAPTURE_CANCEL = "capture.cancel"
    RUN_SET_ACTIVE_CULTIVAR = "run.set_active_cultivar"
    SETTINGS_BARCODE_POLICY_SET = "settings.barcode_policy.set"
    SPREADSHEET_REBUILD = "spreadsheet.rebuild"
    STATE_RECOVER = "state.recover"
    STATE_FLUSH = "state.flush"
    REPORT_EXPORT = "report.export"
    REPORT_RECONCILE = "report.reconcile"
    UI_OPEN_SCALE_SETUP = "ui.open_scale_setup"


@dataclass(frozen=True)
class ActionRequest:
    action_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    idempotency_key: str | None = None
    source: str = "local_ui"
    device_identity: str | None = None
    authenticated: bool = True
    created_at: str = field(default_factory=now_rfc3339)

    def validate(self) -> None:
        try:
            ActionType(self.action_type)
        except ValueError as exc:
            raise ValueError("unsupported canonical action") from exc
        if self.source in {"bluetooth", "wifi"}:
            if not self.authenticated or not self.device_identity:
                raise PermissionError("remote action requires authenticated device identity")
            if not self.idempotency_key:
                raise ValueError("remote action requires an idempotency key")
        if not isinstance(self.payload, dict):
            raise ValueError("action payload must be an object")


@dataclass
class ActionResult:
    action_id: str
    action_type: str
    status: str
    truth_class: str
    state: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    terminal: bool = True
    created_at: str = field(default_factory=now_rfc3339)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
