from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any
from ..models import now_rfc3339

STATUSES={"PASS","PASS_WITH_WARNINGS","BLOCKED","NOT_RUN","FAIL","WAITING_FOR_EXTERNAL_ACTION"}

@dataclass
class LaneResult:
    lane: str
    status: str
    reason_code: str
    profile: str
    commands_executed: list[dict[str, Any]] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    blocking_gates: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_action: str | None = None
    required_action: dict[str, Any] | None = None
    created_at: str = field(default_factory=now_rfc3339)
    data: dict[str, Any] = field(default_factory=dict)
    def validate(self):
        if self.status not in STATUSES: raise ValueError(f"unsupported status: {self.status}")
        if not self.lane or not self.reason_code or not self.profile: raise ValueError("lane, reason_code, and profile are required")
    def to_dict(self): self.validate(); return asdict(self)

@dataclass
class HarnessReport:
    profile: str
    status: str
    version: str
    lanes: list[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)
    repairs: list[dict[str, Any]] = field(default_factory=list)
    generated_at: str = field(default_factory=now_rfc3339)
    def to_dict(self): return asdict(self)
