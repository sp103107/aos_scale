# Operator Onboarding — Best Buds Weight Station

**runtime_claimed:** false  
**audience:** harvest-station operator  
**product_version:** `2.0.0-rc10`  
**template cite:** KS structured onboarding (salvage cite-only)

## Flow map

```text
Launch
→ New Run (Cultivator + Strain)
→ Connect Scale
→ Guided Calibration (verified mass)
→ ZERO → optional SET TARE
→ [Scan → settle → Lock → Confirm] × plants
→ Export Report / Reconcile
→ Finish Run
```

## If you feel lost

> **Ask:** Do I have a run started? Is the scale connected? Am I calibrated?  
> **Next action:** Read the Alice “next step” card on the main screen — it names the current action.

---

## Mission

Weigh plants into a local harvest run with barcodes, keep an honest locked weight before confirm, and export handoff files without claiming Metrc or legal-for-trade status.

---

## 1. Launch

> **Next action:** Double-click `launch_best_buds.bat` (or PowerShell `launch_best_buds.ps1`).

Simulator without hardware: `launch_simulator.bat`.

---

## 2. New run — Cultivator vs Strain

| Field | Meaning |
|-------|---------|
| **Cultivator** | Company / grower (maps to facility id) |
| **Strain** | Sticky plant strain for scans until you Change Strain |

> **Common confusion:** Cultivator is not the plant strain. Strain is sticky per run until changed.

> **Next action:** Run → New Run → fill Harvest-run ID, Operator, Cultivator, Strain → save.

---

## 3. Connect scale and calibrate

> **Next action:** Scale → Scale Setup → pick COM port @ 115200 → Connect.

> **Next action:** In Scale Setup, **Assign Device ID…** (example `BBWS-SCALE-001`). Unique IDs keep calibration + stability profiles bound to the right board.

> **Next action:** Scale → Guided Calibration with a **verified** reference mass. Then empty pan → **ZERO**.

> **Next action (SR9):** After Accept, when prompted (or via Scale Setup → **Run 100 g Stability Test**), hang/place a verified **100 g** mass, review the recommendation, then **Confirm** to activate the hanging-load profile. Reconnect later loads that active profile automatically (`SET_CAL` + stability gates).

> **Accept recovery (SR10):** If Accept reports a leftover reply / handshake timeout, Disconnect → Connect, re-run Test, then Accept. Firmware should be **0.1.5** (Scale Setup STATUS). Close Serial Monitor before retrying.

> **Resume recovery (SR11):** If live grams freeze after **Resume** (or Load Run) while the scale stays connected, Disconnect → Connect to restart the stream. SR11 opens a quiet window around resume/load so profile apply should not leave the reader stuck — use Disconnect→Connect only if it still happens.

> **Stability test recovery (SR12):** If the 100 g Stability Test after Accept reports not enough live samples, wait until live grams move and retry. The station now restarts the live reader before collecting those samples. If grams stay frozen, Disconnect → Connect, then retry.

> **Common confusion:** Large wild numbers before calibration are normal. Do not treat them as trade weight.

> **Non-claim:** 100 g characterization is repeatability evidence only — not legal-for-trade certification. Profiles are local operational evidence; JSONL remains authoritative for plant weights.

---

## 4. Capture loop

### Automatic (recommended for harvest floor)

Set **Capture mode: automatic** when you **Run → New Run**. No Lock or Confirm clicks.

```text
Scan (or type barcode + Enter)
→ Place / hang plant → wait until Stable
→ Record saves automatically (beep) → Ready for next scan
```

> **Next action:** Press **Scan** when Ready; Enter submits the tag.

> **Duplicate barcode (SR13):** If that tag was already recorded in this run, a warning appears **before** weighing. **Cancel** leaves you Ready with no new record. **Continue** lets you weigh it again (tagged as a duplicate).

### Manual (Lock + Confirm every plant)

Choose **Capture mode: manual** on New Run when you want an explicit Lock step before every record.

```text
Scan → Stable → Lock weight → Confirm & Record → Ready for next scan
```

> **Common confusion:** Confirm stays disabled until the weight is **Locked**. That is intentional for manual runs.

> **Auto-record after Lock (SR14, manual only):** Station Settings → **Auto-record after Lock** skips **Confirm** after you press Lock. It does **not** skip Lock. For scan-and-go without any Lock click, use **automatic** capture mode instead.

### Started a run in the wrong mode?

Capture mode is fixed when the run is created. You **cannot** switch manual ↔ automatic mid-run.

**Fix:** **Run → Finish Run** (or leave that session) → **Run → New Run** → pick **automatic** or **manual** as needed.

Barcode stays visible until Confirm in manual mode. Cancel clears the in-progress plant.

---

## 5. Plant log and last saved

The run plant log shows recent confirmed plants (read-only). Last-saved receipt confirms the prior plant.

> **Common confusion:** The plant log is **not** a Metrc plant list.

---

## 5b. Scale Face (Harvest mode)

On Windows PySide, use **View → Scale Face (Harvest)** (or **Ctrl+Shift+F**) for a bench-scale panel: large weight, status pill, barcode + SCAN, and a compact action strip.

| Toggle | What you get |
|--------|----------------|
| **HARVEST** | ZERO · SET TARE · LOCK WEIGHT · CONFIRM & RECORD · CANCEL · compact START/RESUME when needed |
| **SETUP** | CONNECT · ZERO · SET TARE · CALIBRATE (opens Guided Calibration) · TEST SCANNER |

Same capture law as the full UI: Scan → settle → record. In **automatic** runs, Lock/Confirm are not required on stable. In **manual** runs, Lock then Confirm (or auto-record after Lock if that setting is on). Esc or **Exit Scale Face** returns to the full desktop window. New Run details, Export, and plant-log tables stay on the full UI.

> **Next action:** After a run is ready and the scale is connected, open Scale Face for hang-side pacing. Prefer **automatic** capture mode on New Run for scan-and-go harvest.

---

## 6. Export and reconcile

> **Next action:** Run → Export Report… → choose a folder.

Handoffs include CSV, XLSX, DOCX, JSON, and `handoff_bundle_manifest.json`.

> **Next action:** Run → Reconcile Export ↔ JSONL — expect **pass**.

**Authoritative truth:** session `records.jsonl`. Exports are non-authoritative.

---

## 7. Finish

> **Next action:** Finish Run when the session is complete. Committed records remain immutable.

---

## 8. rc10 station tuning (Settings → Station Settings)

- **Lock sensitivity** (0–100): Low = tighter stability / slower to lock; high = wider tolerance / faster lock. Tunes spread and settle on top of the active scale profile — not legal-for-trade.
- **Auto-record alert**: When **automatic capture** saves a plant without Confirm, choose **off**, **beep**, **voice**, or **both** (default beep). Phrase defaults to *Weight recorded*.
- **Finish Run → New Run**: After finishing a run, **Run → New Run** works without restarting the app.

---

## Non-claims

- Not legal-for-trade / Metrc compliance
- Not production-sealed weighing certification
- JSONL remains authoritative; handoffs are derivatives
- HID Scan is keyboard-wedge focus — not BLE/SPP scanner protocol

## Related

- [START_HERE.md](../START_HERE.md)
- [INTENDED_USER.md](INTENDED_USER.md)
- [BBWS_SR5_ARTIFACT_POLISH_RUNBOOK.md](BBWS_SR5_ARTIFACT_POLISH_RUNBOOK.md)
- [RECORDING_AND_EXPORT_RUNBOOK.md](RECORDING_AND_EXPORT_RUNBOOK.md)
