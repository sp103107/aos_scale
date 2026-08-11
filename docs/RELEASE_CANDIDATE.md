# Release candidate notes — v2.0.0-rc3

**Tag intent:** **Scale Face harvest-mode RC** — PySide Scale Face UI mode on top of
the 2.0.0-rc2 Windows installer RC.  
**Not** a production seal or legal-for-trade release.

## New in rc3 (SR8)

- **Scale Face (Harvest)** mode: View → Scale Face (Harvest) or Ctrl+Shift+F
- Harvest / SETUP segment toggle on one face (not a separate process)
- Hero weight uses `frozen_display_weight` while locked; status pill + Alice one-liner
- Barcode field + SCAN; last 1–3 saved records strip
- HARVEST strip: ZERO · SET TARE · LOCK WEIGHT · CONFIRM & RECORD · CANCEL · compact START/RESUME
- SETUP strip: CONNECT · ZERO · SET TARE · CALIBRATE (existing guided dialog) · TEST SCANNER
- Esc / Exit Scale Face returns to the full desktop MainWindow
- Full UI `ROUTINE_ACTION_LAYOUT` remains exactly eight actions

## Carried from rc2

- Finish Run closeout + locked-weight display freeze + Resume Run picker
- Install hygiene (LOCALAPPDATA data root) and Windows Setup.exe packaging
- Capture loop: Scan → settle → Lock → Confirm → reset
- Operator onboarding doors and JSONL authority

## What this RC does **not** claim

- No production-ready weighing seal
- No legal-for-trade / NTEP / Weights & Measures certification
- No Metrc sync or compliance
- No remote/LAN weighing server
- No guarantee that displayed grams are accurate until Guided Calibration with a verified reference mass

## Operator bring-up checklist

1. Open [START_HERE.md](../START_HERE.md) or [OPERATOR_ONBOARDING.md](OPERATOR_ONBOARDING.md).
2. Launch `launch_best_buds.bat`.
3. New Run → Connect Scale → Guided Calibration → ZERO.
4. Optional: View → Scale Face (Harvest) for hang-side Lock/Confirm pacing.
5. Capture plants; Export / Reconcile when done; Finish Run.

## Related

- [BBWS_SR8_ARTIFACTS.md](BBWS_SR8_ARTIFACTS.md)
- [WINDOWS_DEVICE_BRINGUP.md](WINDOWS_DEVICE_BRINGUP.md)
- Drift gate: `scripts/validate_drift_concordance_v200_rc3.py`
