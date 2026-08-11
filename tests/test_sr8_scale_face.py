"""BBWS SR8 Scale Face contract tests — helpers, freeze, layout, menu wiring."""
from __future__ import annotations

from pathlib import Path

from best_buds_weight_station.operator_surface import (
    ROUTINE_ACTION_LAYOUT,
    SCALE_FACE_HARVEST_ACTIONS,
    SCALE_FACE_SETUP_ACTIONS,
    frozen_display_weight,
    scale_face_harvest_action_ids,
    scale_face_setup_action_ids,
    validate_routine_action_layout,
)

ROOT = Path(__file__).resolve().parents[1]


def test_scale_face_harvest_action_ids():
    assert scale_face_harvest_action_ids() == (
        "zero_scale",
        "set_tare",
        "lock_weight",
        "confirm_record",
        "cancel_item",
        "start_resume",
    )
    assert len(SCALE_FACE_HARVEST_ACTIONS) == 6


def test_scale_face_setup_action_ids():
    assert scale_face_setup_action_ids() == (
        "connect_scale",
        "zero_scale",
        "set_tare",
        "calibrate",
        "test_scanner",
    )
    assert len(SCALE_FACE_SETUP_ACTIONS) == 5


def test_routine_action_layout_still_eight():
    validate_routine_action_layout()
    assert len(ROUTINE_ACTION_LAYOUT) == 8


def test_frozen_display_weight_for_scale_face():
    assert frozen_display_weight(1234.5, 1000.0) == 1000.0
    assert frozen_display_weight(999.9, None) == 999.9


def test_scale_face_module_documented():
    text = (ROOT / "app" / "best_buds_weight_station" / "scale_face.py").read_text(encoding="utf-8")
    assert "ScaleFaceWindow" in text
    assert '"""' in text
    assert "frozen_display_weight" in text
    assert "HARVEST" in text
    assert "SETUP" in text


def test_pyside_menu_wiring_scale_face():
    text = (ROOT / "app" / "best_buds_weight_station" / "pyside_frontend.py").read_text(encoding="utf-8")
    assert 'Scale Face (Harvest)' in text
    assert "Ctrl+Shift+F" in text
    assert "open_scale_face" in text
    assert "from .scale_face import ScaleFaceWindow" in text
