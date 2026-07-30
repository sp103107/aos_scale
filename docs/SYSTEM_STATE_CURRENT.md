# System State Current - v0.1.9

## Current truth

- Full repository version: `0.1.9`
- Current phase: `rc3c12_final_polish_and_drift_review`
- Execution posture: `real_execution_allowed` for safe local software lanes with evidence capture
- Primary target: Windows 10/11 + PySide6
- Secondary target: Linux + PySide6; Tk fallback
- Canonical serial path: `PySerialTransport -> DeviceService -> ScaleReadingWorker`
- Routine actions: seven, using one shared non-overlapping layout contract
- Barcode capture: labeled, keyboard/scanner focused, Enter-submitted
- Physical serial presentation: amber `TESTING REQUIRED` until physical evidence passes
- JSON stage catalog and resumable Python stage runner: implemented
- Current/historical/compatibility drift taxonomy: enforced
- Generated package metadata: excluded from repository release shape
- Physical UNO R3, HX711, load cell, calibration, and plant loop: not run
- Native Windows executable and PySide6 runtime: not run on this host
- Production-grade and release-seal gates: not passed

## Next action

Run `python -m best_buds_weight_station.bootstrap --profile cursor-ready`. After it returns the evidence-gated Cursor-ready verdict, hand the full repository to Cursor for UNO R3/HX711 physical integration. Do not reinterpret source presence, simulator evidence, or scripted serial evidence as physical proof.
