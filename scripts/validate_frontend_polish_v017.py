#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
pyside=(ROOT/'app/best_buds_weight_station/pyside_frontend.py').read_text()
tk=(ROOT/'app/best_buds_weight_station/production_ui.py').read_text()
tokens=json.loads((ROOT/'frontend/design_tokens.v0.1.7.json').read_text())
checks={
 'design_tokens':tokens.get('version')=='0.1.7' and tokens.get('layout',{}).get('main_action_count')==7,
 'pyside_main_actions':all(x in pyside for x in ['START / RESUME','CONNECT SCALE','ZERO','SET TARE','CONFIRM & RECORD','CANCEL','FINISH RUN']),
 'advanced_menus':all(x in pyside for x in ['Guided Calibration...','Diagnostics','Export Report...','Recover Run']),
 'simulator_badge': 'SIMULATOR MODE - NO PHYSICAL SCALE' in pyside and 'SIMULATOR MODE - NO PHYSICAL SCALE' in tk,
 'operator_language': 'Alice - next step' in pyside and 'Truth class:' not in pyside[pyside.index('class MainWindow'):],
 'primary_weight_hierarchy': 'QLabel#weightDisplay' in pyside and 'font-size: 72px' in pyside,
 'barcode_focus': 'self.barcode.setFocus()' in pyside and 'barcode.focus_set()' in tk,
 'status_consistency': 'self.alice_message.setText(str(s["alice_message"]))' in pyside,
 'advanced_not_main_grid': '("CALIBRATE SCALE"' not in pyside[pyside.index('class MainWindow'):],
 'tk_fallback_polished': 'Segoe UI' in tk and 'main_action_count' not in tk,
}
failures=[k for k,v in checks.items() if not v]
report={'version':'0.1.7','status':'FAIL' if failures else 'PASS','checks':checks,'failures':failures,'pyside_runtime':'NOT_RUN','tk_runtime':'SEPARATE_SMOKE_REQUIRED'}
(ROOT/'reports/frontend_polish_validation.v0.1.7.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2,sort_keys=True)); raise SystemExit(1 if failures else 0)
