# Release candidate notes — v2.0.0-rc7

**Tag intent:** **Post-cal 100 g Stability Test stream fix** — after Guided Cal Accept, characterize
restarts the live reader so the stability test does not starve.  
**Not** a production seal or legal-for-trade release.

## New in rc7 (SR12)

- `collect_weight_samples` calls `ensure_reading_worker` (same contract as Guided Cal raw collect)
- Starve errors include the last scale-worker note
- Alice copy for “not enough live weight samples” tells the operator to wait for live grams or Disconnect → Connect
- Capture law unchanged: Scan → settle → Lock → Confirm → reset

## Carried from rc6 (SR11)

- Quiet window around Resume/Load so SET_CAL is not issued under a live reader
- Skip redundant SET_CAL when STATUS factor already matches the active profile

## New in rc6 (SR11) / rc5 (SR10) / rc4 (SR9)

See the rc6 notes below for handshake, quiet Accept, device identity, and characterization.

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
4. After Accept, run 100 g Stability Test with a verified mass; Confirm to activate the profile.
5. Capture plants; Export / Reconcile when done; Finish Run.

## Related

- [BBWS_SR12_ARTIFACTS.md](BBWS_SR12_ARTIFACTS.md)
- [WINDOWS_DEVICE_BRINGUP.md](WINDOWS_DEVICE_BRINGUP.md)
- Drift gate: `scripts/validate_drift_concordance_v200_rc7.py`

---

# Prior — v2.0.0-rc6

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
