from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_primary_ui_has_seven_routine_actions_and_advanced_menus():
    text=(ROOT/'app/best_buds_weight_station/pyside_frontend.py').read_text()
    for label in ('START / RESUME','CONNECT SCALE','ZERO','SET TARE','CONFIRM & RECORD','CANCEL','FINISH RUN'):
        assert label in text
    for label in ('Guided Calibration...','Diagnostics','Export Report...','Recover Run'):
        assert label in text
    main=text[text.index('class MainWindow'):]
    assert '("CALIBRATE SCALE"' not in main
    assert 'SIMULATOR MODE - NO PHYSICAL SCALE' in main

def test_design_tokens_and_fallback_are_aligned():
    tokens=json.loads((ROOT/'frontend/design_tokens.v0.1.8.json').read_text())
    assert tokens['layout']['main_action_count']==7
    assert tokens['platform_priority'][0]=='windows_pyside6'
    fallback=(ROOT/'app/best_buds_weight_station/production_ui.py').read_text(encoding='utf-8')
    assert 'SIMULATOR MODE - NO PHYSICAL SCALE' in fallback
    assert 'Alice — next step' in fallback

def test_canonical_serial_path_is_unambiguous():
    readme=(ROOT/'README.md').read_text()
    legacy=(ROOT/'app/best_buds_weight_station/serial_adapter.py').read_text()
    assert 'PySerialTransport -> DeviceService -> ScaleReadingWorker' in readme
    assert 'LEGACY_COMPATIBILITY_ADAPTER = True' in legacy
