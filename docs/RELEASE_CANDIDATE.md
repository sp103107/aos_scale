# Release candidate notes — v2.0.0-rc6

**Tag intent:** **Scale profile + stability governance RC** — device identity, scale profiles,
post-cal characterization, and capture stability gates on top of the 2.0.0-rc3 Scale Face RC.  
**Not** a production seal or legal-for-trade release.

## New in rc4 (SR9)

- Firmware/host **device identity** persistence (unique board id; collision needs operator action)
- Typed atomic **scale profile** store under config (CRUD / archive; active-per-device)
- **Calibration binding** to the active device profile; reconnect apply + verify
- Post-cal **100 g characterization** (bounded recommend; operator confirm)
- Capture **stability runtime** gates (spread/stddev/trend/hold; recoverable timeout)
- Scale Setup UI for identity, profiles, characterization, and diagnostics

## Carried from rc3

- Scale Face (Harvest) mode with Harvest/SETUP toggle
- Finish Run closeout + locked-weight display freeze + Resume Run picker
- Install hygiene (LOCALAPPDATA data root) and Windows Setup.exe packaging
- Capture loop: Scan → settle → Lock → Confirm → reset
- Operator onboarding doors and JSONL authority

## What this RC does **not** claim

- No production-ready weighing seal
- No legal-for-trade / NTEP / Weights & Measures certification
- No Metrc sync or compliance
- No remote/LAN weighing server
- 100 g characterization is **repeatability evidence**, not certification
- No guarantee that displayed grams are accurate until Guided Calibration with a verified reference mass

## Operator bring-up checklist

1. Open [START_HERE.md](../START_HERE.md) or [OPERATOR_ONBOARDING.md](OPERATOR_ONBOARDING.md).
2. Launch `launch_best_buds.bat`.
3. New Run → Connect Scale → Guided Calibration → ZERO.
4. Optional: run post-cal characterization and confirm recommended stability settings.
5. Capture plants; Export / Reconcile when done; Finish Run.

## Related

- [BBWS_SR9_ARTIFACTS.md](BBWS_SR9_ARTIFACTS.md)
- [WINDOWS_DEVICE_BRINGUP.md](WINDOWS_DEVICE_BRINGUP.md)
- Drift gate: `scripts/validate_drift_concordance_v200_rc4.py`
