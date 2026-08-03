# BBWS SR2 — Tk/Linux + Display Units Series Map

**series_id:** `BBWS_SR2_tk_linux_display_units`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR1_harvest_operator_loop` / `bbws-sr1-complete`  
**units law:** display-only g/kg/lb; JSONL stays grams

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR2_resume*.json
→ cursor/BBWS_SR2_*_SERIES_MAP*.md
→ superpowers/sr2_sNN_*.json (current season)
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Tk/Linux gap audit vs PySide SR1 | Freeze parity matrix; no feature inventing | `sr2_s01_tk_gap_audit.v0.1.0.json` |
| **S02** | M02 | Tk recording polish parity | Confirm pacing, duplicate warning, cancel→focus | `sr2_s02_tk_recording_polish.v0.1.0.json` |
| **S03** | M03 | Tk HID scanner + barcode policy | Test Scanner receipts; barcode policy settings | `sr2_s03_tk_hid_scanner.v0.1.0.json` |
| **S04** | M04 | Tk sticky strain parity | Change Strain + active banner | `sr2_s04_tk_sticky_strain.v0.1.0.json` |
| **S05** | M05 | Tk CSV rebuild / pending_sync / recover | Rebuild and soft recover paths in Tk | `sr2_s05_tk_csv_recover.v0.1.0.json` |
| **S06** | M06 | Tk export + reconcile | Export handoff + reconcile gate messaging | `sr2_s06_tk_export_reconcile.v0.1.0.json` |
| **S07** | M07 | Display-unit core | g/kg/lb display setting; grams stored | `sr2_s07_display_unit_core.v0.1.0.json` |
| **S08** | M08 | Display unit in PySide + Tk | Weight/tare/net/cal entry use display unit | `sr2_s08_display_unit_uis.v0.1.0.json` |
| **S09** | M09 | Linux launchers + Xvfb Tk smoke | Source launch docs + smoke script/receipt | `sr2_s09_linux_smoke.v0.1.0.json` |
| **S10** | M10 | Dual-UI regression + series closeout | Parity matrix complete + bbws-sr2-complete tag | `sr2_s10_dual_ui_closeout.v0.1.0.json` |

## Non-claims

- Display lb/kg ≠ legal-for-trade / NTEP
- Tk parity ≠ Windows packaging seal
- Linux smoke ≠ Debian production guarantee
- Display unit ≠ changing authoritative ledger units
- Arc Launcher not claimed as live runtime for Best Buds
