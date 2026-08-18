# Intended User — Best Buds Weight Station

**runtime_claimed:** false  
**product_version:** `2.0.0-rc9`

## Who this product is for

Primary user: a **cultivator harvest-station operator** (or floor supervisor) who:

- Starts and finishes harvest weighing runs
- Scans plant or container barcodes (USB HID keyboard-wedge)
- Locks a stable weight, then confirms the plant into the local run ledger
- Needs clear Cultivator (company/grower) vs Strain labels
- Exports CSV / XLSX / DOCX handoffs for office or partner use

## Who this product is not for

| Role | Why not |
|------|---------|
| Metrc compliance clerk | This app does not sync Metrc or claim regulatory plant lists |
| Legal-for-trade / NTEP inspector | Grams are bring-up / operational; not Weights & Measures certified |
| Cloud SaaS admin | Local-first; no required cloud account |
| Firmware-only engineer | Use Arduino/firmware docs; this is the PC operator surface |

## Success for the intended user

1. Launch the app and connect a scale (or simulator).
2. Complete Guided Calibration with a verified mass.
3. Scan → lock → confirm plants without losing the barcode until confirm.
4. Trust that **JSONL** holds the authoritative record; exports are handoffs.

## Non-claims

- Not Metrc compliance
- Not legal-for-trade
- Plant log is a run convenience list, not a regulatory plant inventory
