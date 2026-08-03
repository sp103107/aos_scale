# Field E2E Runbook — BBWS SR1 S07

Scan → weigh → record → CSV proof path for harvest operators.

## Preconditions

- Baseline freeze `v0.1.9-rc2` connect/calibrate soft-path proven
- USB HID keyboard-wedge scanner (optional if barcode policy allows auto ID)
- Physical or simulator scale connected

## Steps

1. Start **New Run** (operator id + initial cultivar).
2. Connect scale → Guided Calibration if uncalibrated → **ZERO**.
3. **Test Scanner** once (HID focus ownership).
4. Set **Active strain** (sticky until changed).
5. Scan plant → wait stable → **Confirm & Record**.
6. Change strain mid-run if the next scan group differs.
7. Confirm `records.csv` grows; pending_sync banner stays clear.
8. **Export Report** → confirm plain `*_plants.csv` + reconcile gate pass.

## Evidence receipt

Write `reports/bbws_s07_field_e2e_receipt.*.json` with:

- session_id, record_count, cultivar_totals
- scanner transport = hid_keyboard_wedge
- metrology non-claim stamped

## Non-claims

- Not legal-for-trade / metrology certification
- Sticky strain UX ≠ Metrc compliance
- HID wedge ≠ BLE/SPP
