from __future__ import annotations

from dataclasses import dataclass


def frozen_display_weight(weight_g: float, locked_weight_g: float | None) -> float:
    """Weight for the main operator display.

    While a capture is locked (MANUAL_CONFIRM), the big number must freeze at
    the locked value until Confirm & Record or Cancel releases it; otherwise
    the live reading shows. Display-only — capture law is unchanged.
    """
    if locked_weight_g is not None:
        return float(locked_weight_g)
    return float(weight_g)


@dataclass(frozen=True)
class RoutineActionSpec:
    action_id: str
    label: str
    row: int
    column: int
    columnspan: int = 1
    emphasis: str = "default"


ROUTINE_ACTION_LAYOUT: tuple[RoutineActionSpec, ...] = (
    RoutineActionSpec("start_resume", "START / RESUME", 0, 0),
    RoutineActionSpec("connect_scale", "CONNECT SCALE", 0, 1),
    RoutineActionSpec("zero_scale", "ZERO", 0, 2),
    RoutineActionSpec("set_tare", "SET TARE", 0, 3),
    RoutineActionSpec("lock_weight", "LOCK WEIGHT", 1, 0),
    RoutineActionSpec("confirm_record", "CONFIRM & RECORD", 1, 1, 2, "primary"),
    RoutineActionSpec("cancel_item", "CANCEL", 1, 3, 1, "danger"),
    RoutineActionSpec("finish_run", "FINISH RUN", 2, 0, 2),
)


# Scale Face harvest strip — separate from the full-UI 8-action grid so that
# ROUTINE_ACTION_LAYOUT contract stays intact (BBWS SR8).
SCALE_FACE_HARVEST_ACTIONS: tuple[RoutineActionSpec, ...] = (
    RoutineActionSpec("zero_scale", "ZERO", 0, 0),
    RoutineActionSpec("set_tare", "SET TARE", 0, 1),
    RoutineActionSpec("lock_weight", "LOCK WEIGHT", 0, 2, emphasis="primary"),
    RoutineActionSpec("confirm_record", "CONFIRM & RECORD", 0, 3, emphasis="primary"),
    RoutineActionSpec("cancel_item", "CANCEL", 1, 0, emphasis="danger"),
    RoutineActionSpec("start_resume", "START / RESUME", 1, 1, emphasis="default"),
)


# Scale Face SETUP strip — opens existing dialogs; does not reimplement calibration.
SCALE_FACE_SETUP_ACTIONS: tuple[RoutineActionSpec, ...] = (
    RoutineActionSpec("connect_scale", "CONNECT", 0, 0),
    RoutineActionSpec("zero_scale", "ZERO", 0, 1),
    RoutineActionSpec("set_tare", "SET TARE", 0, 2),
    RoutineActionSpec("calibrate", "CALIBRATE", 0, 3),
    RoutineActionSpec("test_scanner", "TEST SCANNER", 1, 0, 2),
)


def scale_face_harvest_action_ids() -> tuple[str, ...]:
    """Stable harvest-mode action ids for Scale Face (presentation contract)."""
    return tuple(spec.action_id for spec in SCALE_FACE_HARVEST_ACTIONS)


def scale_face_setup_action_ids() -> tuple[str, ...]:
    """Stable SETUP-mode action ids for Scale Face (presentation contract)."""
    return tuple(spec.action_id for spec in SCALE_FACE_SETUP_ACTIONS)


def validate_routine_action_layout() -> None:
    """Fail if two routine controls occupy the same grid cell."""

    if len(ROUTINE_ACTION_LAYOUT) != 8:
        raise ValueError("The routine operator surface must expose exactly eight actions.")
    occupied: dict[tuple[int, int], str] = {}
    for action in ROUTINE_ACTION_LAYOUT:
        if action.columnspan < 1:
            raise ValueError(f"Invalid column span for {action.action_id}")
        for column in range(action.column, action.column + action.columnspan):
            cell = (action.row, column)
            previous = occupied.get(cell)
            if previous:
                raise ValueError(f"Routine action overlap: {previous} and {action.action_id} at {cell}")
            occupied[cell] = action.action_id


validate_routine_action_layout()
