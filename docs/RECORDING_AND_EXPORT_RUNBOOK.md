# Recording and export runbook

Operator path after the scale is calibrated and zeroed.

## Record a plant

1. Start or resume a harvest run.
2. Connect the scale (if needed) → empty pan → **ZERO**.
3. Optional: **SET TARE** for a container.
4. Scan or type the plant barcode → Enter (or **Use auto ID** if enabled).
5. Hang / place the plant. Wait for stable weight.
6. **Confirm & Record** (manual mode) or wait for automatic save.
7. Confirm the green “Saved …” line. `records.csv` in the session folder updates on each save.

Authoritative truth: `records.jsonl` + individual JSON files in the session directory.  
CSV / XLSX are derivatives for operators (pending_sync if a spreadsheet write fails).

## Export handoff pack

1. Menu **Run → Export Report…**
2. Choose a folder.
3. Files written:

| File | Purpose |
|------|---------|
| `records.csv` / `records.xlsx` | Live session ledger copies |
| `harvest_run_report.csv` | Cultivar totals |
| `harvest_run_report.xlsx` | Summary + record sheet |
| `harvest_run_report.docx` | Printable Word summary |
| `harvest_run_report.json` | Machine-readable summary |

Exports are **non-authoritative handoff copies**.

## Proof checklist

- [ ] Save at least one plant; open session `records.csv` and see the barcode / net grams.
- [ ] Export; open DOCX and CSV from the destination folder.
- [ ] Confirm totals match the plants you weighed.
