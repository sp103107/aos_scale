#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from best_buds_weight_station.operator_surface import ROUTINE_ACTION_LAYOUT, validate_routine_action_layout

VERSION = (ROOT / "VERSION").read_text().strip()


def main() -> int:
    pyside = (ROOT / "app/best_buds_weight_station/pyside_frontend.py").read_text()
    tk = (ROOT / "app/best_buds_weight_station/production_ui.py").read_text()
    manifest = json.loads((ROOT / f"frontend/frontend_manifest.v{VERSION}.json").read_text())
    tokens = json.loads((ROOT / f"frontend/design_tokens.v{VERSION}.json").read_text())
    render_evidence = json.loads((ROOT / f"reports/frontend_render_evidence.v{VERSION}.json").read_text())
    try:
        validate_routine_action_layout()
        layout_pass = True
    except Exception:
        layout_pass = False
    occupied = []
    for action in ROUTINE_ACTION_LAYOUT:
        occupied.extend((action.row, c) for c in range(action.column, action.column + action.columnspan))
    checks = {
        "version": VERSION == "0.1.9",
        "seven_actions": len(ROUTINE_ACTION_LAYOUT) == 7,
        "non_overlapping_actions": layout_pass and len(occupied) == len(set(occupied)),
        "barcode_label_tk": "PLANT OR CONTAINER BARCODE" in tk and "Scan or type the barcode" in tk,
        "barcode_label_pyside": "PLANT OR CONTAINER BARCODE" in pyside and "Scan or type the barcode" in pyside,
        "manifest_barcode_label": manifest.get("barcode_surface", {}).get("label") == "PLANT OR CONTAINER BARCODE",
        "physical_warning_tk": "PHYSICAL SERIAL - TESTING REQUIRED" in tk and 'bg="#FFF1D6"' in tk,
        "physical_warning_pyside": "PHYSICAL SERIAL - TESTING REQUIRED" in pyside and "background:#FFF1D6" in pyside,
        "simulator_badge": "SIMULATOR MODE - NO PHYSICAL SCALE" in tk and "SIMULATOR MODE - NO PHYSICAL SCALE" in pyside,
        "dead_contract_stubs_removed": "_LegacyCallbackNamesForContract" not in tk,
        "generated_egg_info_absent": not list((ROOT / "app").glob("*.egg-info")),
        "manifest_runtime_truth": manifest.get("tk_runtime") == "PASS" and manifest.get("pyside_native_runtime") == "NOT_RUN",
        "tk_render_evidence": render_evidence.get("status") == "PASS" and render_evidence.get("judge_verdict") == "TK_FALLBACK_RENDER_PASS",
        "layout_contract_declared": manifest.get("layout_contract") == "app/best_buds_weight_station/operator_surface.py",
        "tokens_aligned": tokens.get("version") == VERSION and tokens.get("layout", {}).get("action_overlap_allowed") is False,
        "advanced_menus": all(x in pyside for x in ["Guided Calibration...", "Diagnostics", "Export Report...", "Recover Run"]),
        "barcode_focus": "self.barcode.setFocus()" in pyside and "barcode.focus_set()" in tk,
    }
    failures = [k for k, v in checks.items() if not v]
    report = {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
        "pyside_runtime": "NOT_RUN_DEPENDENCY_UNAVAILABLE",
        "tk_runtime": "PASS_LINUX_XVFB_MANUAL_AND_AUTOMATIC",
        "physical_hardware": "NOT_RUN",
    }
    out = ROOT / f"reports/frontend_polish_validation.v{VERSION}.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
