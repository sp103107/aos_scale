from __future__ import annotations

from dataclasses import dataclass


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
