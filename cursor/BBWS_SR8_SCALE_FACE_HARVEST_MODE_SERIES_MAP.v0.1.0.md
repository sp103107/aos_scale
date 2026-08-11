# BBWS SR8 — Scale Face Harvest Mode Series Map

**series_id:** `BBWS_SR8_scale_face_harvest_mode`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR7_windows_installer_bringup` / `bbws-sr7-complete`  
**baseline:** `bbws-pre-sr8-scale-face`  
**product version target:** `2.0.0-rc3`

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR8_resume*.json
→ cursor/BBWS_SR8_*_SERIES_MAP*.md
→ superpowers/sr8_sNN_*.json
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + Scale Face contract freeze | Freeze: mode not app; Harvest/SETUP toggle; PySide-first; capture law locks | `sr8_s01_scale_face_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Scale Face mode shell entry/exit | View → Scale Face (Harvest), shortcut, enter/exit shell; no capture changes | `sr8_s02_mode_shell_entry.v0.1.0.json` |
| **S03** | M03 | Hero weight + status surface | Hero weight, unit, status pill, locked freeze, Alice one-liner | `sr8_s03_weight_status_surface.v0.1.0.json` |
| **S04** | M04 | HARVEST action bar | ZERO/TARE/LOCK/CONFIRM/CANCEL + compact START/RESUME; existing gating | `sr8_s04_harvest_action_bar.v0.1.0.json` |
| **S05** | M05 | Barcode field + recent records strip | Barcode field, SCAN, last 1–3 saved lines | `sr8_s05_barcode_recent_strip.v0.1.0.json` |
| **S06** | M06 | SETUP toggle panel | SETUP strip: Connect / Zero / Tare / Guided Calibration / Test Scanner | `sr8_s06_setup_toggle_panel.v0.1.0.json` |
| **S07** | M07 | Scale Face authority contract tests | Helpers, harvest/setup ids, freeze, routine layout still 8, menu wiring | `sr8_s07_authority_contract_tests.v0.1.0.json` |
| **S08** | M08 | Operator smoke docs for Scale Face | Operator onboarding Scale Face section + START_HERE note | `sr8_s08_operator_smoke_docs.v0.1.0.json` |
| **S09** | M09 | Bump to 2.0.0-rc3 + drift receipts | Version surfaces, drift concordance rc3, manifest, pytest | `sr8_s09_rc3_drift_receipts.v0.1.0.json` |
| **S10** | M10 | SR8 series closeout + tags | ACTIVE_ARC series_complete, resume/ledger, tag v2.0.0-rc3 + bbws-sr8-complete, push | `sr8_s10_series_closeout.v0.1.0.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- Not a remote weighing server or separate Scale Face process
- Not collapsing Lock+Confirm in manual mode
- JSONL remains authoritative for records
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not claiming small 2–5″ hardware support without a later series
