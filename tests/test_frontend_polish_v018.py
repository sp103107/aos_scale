from __future__ import annotations

import json
from pathlib import Path

from best_buds_weight_station.operator_surface import ROUTINE_ACTION_LAYOUT

ROOT = Path(__file__).resolve().parents[1]


def test_final_polish_removes_generated_and_dead_contract_artifacts():
    # egg-info may exist on disk after editable installs; it must never be
    # git-tracked (source zips come from git archive, so ignored files stay out).
    import subprocess
    tracked = subprocess.run(
        ["git", "ls-files", "app/*.egg-info*"],
        cwd=ROOT, text=True, capture_output=True,
    ).stdout.strip()
    assert not tracked
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "egg-info" in gitignore
    source = (ROOT / "app/best_buds_weight_station/production_ui.py").read_text()
    assert "_LegacyCallbackNamesForContract" not in source


def test_barcode_surface_is_labeled_in_both_frontends():
    tk_source = (ROOT / "app/best_buds_weight_station/production_ui.py").read_text(encoding="utf-8")
    pyside_source = (ROOT / "app/best_buds_weight_station/pyside_frontend.py").read_text(encoding="utf-8")
    assert "PLANT OR CONTAINER BARCODE" in tk_source
    # PySide eyebrow labels are uppercased visually via QSS text-transform (SR4 tokens).
    assert "plant or container barcode" in pyside_source.lower()
    assert 'text="Scan"' in tk_source
    assert 'QPushButton("Scan")' in pyside_source
    assert "Active plant" in tk_source and "Active plant" in pyside_source


def test_physical_serial_pending_state_is_not_success_colored():
    tk_source = (ROOT / "app/best_buds_weight_station/production_ui.py").read_text(encoding="utf-8")
    pyside_source = (ROOT / "app/best_buds_weight_station/pyside_frontend.py").read_text(encoding="utf-8")
    tokens_source = (ROOT / "app/best_buds_weight_station/ui_tokens.py").read_text(encoding="utf-8")
    assert "PHYSICAL SERIAL - TESTING REQUIRED" in tk_source
    assert "PHYSICAL SERIAL - TESTING REQUIRED" in pyside_source
    assert 'bg="#FFF1D6"' in tk_source
    # PySide uses the shared amber warn token (SR4 design tokens) for pending physical serial.
    assert 'COLOR_WARN_BG = "#FFF1D6"' in tokens_source
    assert "background:{COLOR_WARN_BG}" in pyside_source


def test_shared_routine_layout_is_complete_and_non_overlapping():
    assert [item.action_id for item in ROUTINE_ACTION_LAYOUT] == [
        "start_resume", "connect_scale", "zero_scale", "set_tare",
        "lock_weight", "confirm_record", "cancel_item", "finish_run",
    ]
    occupied = set()
    for item in ROUTINE_ACTION_LAYOUT:
        for column in range(item.column, item.column + item.columnspan):
            cell = (item.row, column)
            assert cell not in occupied
            occupied.add(cell)


def test_current_frontend_manifest_reports_executed_tk_truth():
    manifest = json.loads((ROOT / "frontend/frontend_manifest.v0.1.8.json").read_text())
    assert manifest["tk_runtime"] == "PASS"
    assert manifest["pyside_native_runtime"] == "NOT_RUN"
    assert manifest["routine_action_count"] == 7
    assert manifest["barcode_surface"]["label"] == "PLANT OR CONTAINER BARCODE"
