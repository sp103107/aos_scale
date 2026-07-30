from __future__ import annotations
from typing import Any
import uuid

from ..envelope import make_envelope
from .errors import IncompleteContext
from .response_models import CommandProposal


class AliceCommandBuilder:
    """Builds typed proposals; it never executes or persists commands."""

    def build(self, command_type: str, payload: dict[str, Any], *, correlation_id: str | None = None,
              idempotency_key: str | None = None, require_confirmation: bool = False) -> CommandProposal:
        clean_type = command_type.strip()
        if not clean_type:
            raise IncompleteContext("command_type is required")
        if not isinstance(payload, dict):
            raise IncompleteContext("command payload must be an object")
        key = idempotency_key or f"alice-{uuid.uuid4()}"
        envelope = make_envelope(
            clean_type,
            payload,
            source="best_buds_weight_station.alice",
            correlation_id=correlation_id,
            idempotency_key=key,
        )
        return CommandProposal(
            command_type=clean_type,
            envelope=envelope,
            requires_operator_confirmation=require_confirmation,
        )

    def weight_record(self, context: dict[str, Any], *, correlation_id: str | None = None,
                      idempotency_key: str | None = None, manual: bool = False) -> CommandProposal:
        required = ("session_id", "run_id", "barcode_raw", "cultivar_id", "container_id", "tare_g", "gross_g", "net_g")
        missing = [name for name in required if context.get(name) is None or context.get(name) == ""]
        if missing:
            raise IncompleteContext("missing weight command fields: " + ", ".join(missing))
        return self.build(
            "weight.record.request",
            {name: context[name] for name in context},
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            require_confirmation=manual,
        )
