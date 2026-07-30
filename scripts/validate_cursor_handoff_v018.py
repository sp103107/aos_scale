#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'cursor/CURSOR_UNO_R3_PHYSICAL_INTEGRATION_HANDOFF_V0_1_8.md'
text=path.read_text() if path.exists() else ''
markers=['v0.1.9','cursor-ready','PySerialTransport -> DeviceService -> ScaleReadingWorker','Do not create a hardware-only mini-pack','PHYSICAL_HARDWARE_NOT_RUN','UNO R3','HX711']
missing=[m for m in markers if m not in text]
report={'version':'0.1.9','status':'PASS' if not missing else 'FAIL','handoff':path.relative_to(ROOT).as_posix(),'missing_markers':missing}
print(json.dumps(report,indent=2,sort_keys=True)); raise SystemExit(1 if missing else 0)
