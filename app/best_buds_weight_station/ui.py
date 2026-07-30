from __future__ import annotations

from typing import Any

from .alice import AliceResponseAgent, TruthClass


def alice_panel_snapshot(response: dict[str, Any]) -> dict[str, str]:
    required = response.get("required_action") or {}
    evidence = response.get("evidence_refs") or []
    blocked = response.get("blocked_actions") or []
    return {
        "message": str(response.get("operator_message", "")),
        "truth_class": str(response.get("truth_class", "PENDING")),
        "required_action": str(required.get("action_type", response.get("required_operator_action", "none"))),
        "blocking_reason": ", ".join(blocked) if blocked else "none",
        "evidence_summary": "\n".join(str(item) for item in evidence) if evidence else "No evidence references for this instruction.",
    }


def process_terminal_result(machine, agent: AliceResponseAgent, result: Any, *, session_id: str | None = None):
    record = None
    feedback_kind = "success"
    if isinstance(result, dict):
        backend_result = result
        feedback_kind = "warning" if result.get("status") == "duplicate" else "success"
    else:
        record, receipt = result
        backend_result = receipt.to_dict()
    response = agent.respond("LOCAL_COMMIT_PENDING", backend_result=backend_result, session_id=session_id)
    advanced = response.truth_class == TruthClass.RECEIPT_CONFIRMED
    if advanced:
        machine.complete_terminal_result(feedback_kind)
    return response, record, advanced


def launch(data_root: str | None = None, simulator: bool = False, smoke: bool = False, capture_mode: str = "manual") -> int:
    from .production_ui import launch as production_launch
    return production_launch(data_root, simulator, smoke, capture_mode)
