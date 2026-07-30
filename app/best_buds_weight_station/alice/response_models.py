from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
import uuid

from ..models import now_rfc3339


class TruthClass(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"
    UNIT_TEST_PASS = "UNIT_TEST_PASS"
    SIMULATOR_PASS = "SIMULATOR_PASS"
    UI_SMOKE_PASS = "UI_SMOKE_PASS"
    NATIVE_PLATFORM_PASS = "NATIVE_PLATFORM_PASS"
    PHYSICAL_DEVICE_PASS = "PHYSICAL_DEVICE_PASS"
    SOURCE_PRESENT = "SOURCE_PRESENT"
    RECEIPT_CONFIRMED = "RECEIPT_CONFIRMED"
    PENDING = "PENDING"
    NON_CLAIM = "NON_CLAIM"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RequiredAction:
    action_type: str
    required: bool = True
    label: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandProposal:
    command_type: str
    envelope: dict[str, Any]
    requires_operator_confirmation: bool = False
    retry_policy: str = "never_automatic_after_ambiguous_failure"


@dataclass
class AliceResponse:
    state: str
    truth_class: TruthClass
    severity: Severity
    operator_message: str
    required_action: RequiredAction | None = None
    allowed_actions: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    command_proposal: CommandProposal | None = None
    evidence_refs: list[dict[str, Any] | str] = field(default_factory=list)
    non_claims: list[str] = field(default_factory=list)
    correlation_id: str | None = None
    session_id: str | None = None
    response_id: str = field(default_factory=lambda: f"alice-response-{uuid.uuid4()}")
    response_version: str = "1.0.0"
    timestamp: str = field(default_factory=now_rfc3339)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["truth_class"] = self.truth_class.value
        data["severity"] = self.severity.value
        return data
