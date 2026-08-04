"""BBWS SR4 polish contract tests — styles/tokens only; capture loop unchanged."""
from pathlib import Path

from best_buds_weight_station.ui_tokens import (
    CAPTURE_PILL_BY_STATE,
    COLOR_PRIMARY,
    build_pyside_stylesheet,
    capture_pill_label,
)


ROOT = Path(__file__).parents[1]
APP = ROOT / "app" / "best_buds_weight_station"


def test_capture_pill_labels_are_text_not_empty():
    for state, label in CAPTURE_PILL_BY_STATE.items():
        assert label and label == capture_pill_label(state)
        assert label[0].isupper() or label.isupper()


def test_stylesheet_keeps_green_confirm_and_eyebrow():
    qss = build_pyside_stylesheet()
    assert "primaryAction" in qss
    assert COLOR_PRIMARY in qss
    assert "QLabel#eyebrow" in qss
    assert "QLabel#statusPill" in qss
    assert "QLabel#lockedMetric" in qss


def test_pyside_uses_token_module_and_eyebrows():
    text = (APP / "pyside_frontend.py").read_text(encoding="utf-8")
    assert "build_pyside_stylesheet" in text
    assert "_eyebrow(" in text
    assert "capture_pill" in text
    assert 'setObjectName("lockedMetric")' in text
    assert "Scan capture" in text or "SCAN CAPTURE" in text or '_eyebrow("Scan capture"' in text


def test_tk_imports_tokens_and_status_pill():
    text = (APP / "production_ui.py").read_text(encoding="utf-8")
    assert "from .ui_tokens import" in text
    assert "capture_pill" in text
    assert "SCAN CAPTURE" in text
    assert "CULTIVATOR" in text and "STRAIN" in text


def test_no_react_import_from_salvage():
    for name in ("pyside_frontend.py", "production_ui.py", "ui_tokens.py"):
        text = (APP / name).read_text(encoding="utf-8").lower()
        assert "from react" not in text
        assert "import react" not in text
        assert "jsx" not in text


def test_capture_action_wiring_unchanged():
    """Polish must not rename lock/confirm action ids in surface layout."""
    from best_buds_weight_station.operator_surface import ROUTINE_ACTION_LAYOUT

    ids = {spec.action_id for spec in ROUTINE_ACTION_LAYOUT}
    assert "lock_weight" in ids and "confirm_record" in ids


def test_design_token_docs_exist():
    assert (ROOT / "docs" / "BBWS_SR4_DESIGN_TOKENS.md").exists()
    assert (ROOT / "docs" / "BBWS_SR4_SELECTION_MAP.md").exists()
