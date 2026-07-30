# Calibration Runbook

Maintenance calibration for Best Buds Cultivator Weight Station. Use a verified reference mass, record raw samples, preview the proposed factor, require operator acceptance, and preserve a receipt. Test mode does not overwrite the active factor until Accept. **No legal-for-trade claim.**

## Why calibrate

With factory / firmware factor ≈ `1.0`, the live display is essentially **raw HX711 counts labeled as grams**. That is why empty-pan values can look like hundreds of thousands and noise can look like 30–1000 “grams.” Guided Calibration converts those counts into real grams.

## Before you start

1. Connect the USB scale (Scale Setup → port / 115200 → Connect).
2. Start or resume a harvest run.
3. Empty the pan (no container, no reference mass).
4. Have a **verified reference mass** and enter its true weight in grams in the dialog.
5. Do not scan plant barcodes during the walkthrough.

## Walkthrough steps

1. **Start maintenance calibration** — Opens a calibration session. Stay in this dialog until Accept or Cancel.
2. **Capture zero raw samples** — Pan empty. Wait for live readings, then capture. Uses raw values from the live buffer.
3. **Capture loaded raw samples** — Place the reference mass on the empty pan. Confirm the Reference weight (g) matches the physical mass. Wait for settle, then capture.
4. **Test proposed factor** — Keep or re-place the reference mass. Run test. Review proposed factor and error percent in the output panel.
5. **Accept with second confirmation** — Writes the factor to the device (`SET_CAL`). Live weight should then read near the reference in real grams. A calibration receipt is stored under the session.

## After calibration

1. Empty the pan.
2. Press **ZERO** (zeros the empty pan for operations).
3. Optionally **SET TARE** for a container (NET = GROSS − TARE only; does not replace Zero).
4. Resume normal barcode scanning.

## Notes

- Cancel clears the in-progress session without changing the device factor.
- Physical pass / hanging-load qualification is separate evidence and is not implied by Accept.
- Keep calibration receipts with the run session for audit.
