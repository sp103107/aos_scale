from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .actions import ActionRequest


@dataclass(frozen=True)
class RemoteTransportConfig:
    transport: str
    enabled: bool = False
    require_authentication: bool = True
    retry_limit: int = 2
    offline_local_weighing: bool = True
    remote_calibration_acceptance: bool = False

    def validate(self) -> None:
        if self.transport not in {"bluetooth", "wifi"}:
            raise ValueError("unsupported remote transport")
        if self.retry_limit < 0 or self.retry_limit > 5:
            raise ValueError("retry limit outside supported bounds")
        if not self.require_authentication:
            raise ValueError("anonymous remote commands are forbidden")
        if not self.offline_local_weighing:
            raise ValueError("local weighing may not depend on network availability")
        if self.remote_calibration_acceptance:
            raise ValueError("remote calibration acceptance is forbidden in v0.1.3")


def normalize_remote_action(envelope: dict[str, Any], config: RemoteTransportConfig) -> ActionRequest:
    config.validate()
    if not config.enabled:
        raise PermissionError(f"{config.transport} adapter is disabled")
    if envelope.get("transport") != config.transport:
        raise ValueError("transport mismatch")
    identity = envelope.get("device_identity")
    authenticated = envelope.get("authenticated") is True
    idempotency = envelope.get("idempotency_key")
    if not identity or not authenticated or not idempotency:
        raise PermissionError("authenticated device identity and idempotency key are required")
    return ActionRequest(
        action_type=str(envelope["action_type"]),
        payload=dict(envelope.get("payload") or {}),
        idempotency_key=str(idempotency),
        source=config.transport,
        device_identity=str(identity),
        authenticated=True,
    )
