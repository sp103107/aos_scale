# BBWS SR3 — Station Capture UX Series Map

**series_id:** `BBWS_SR3_station_capture_ux`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR2_tk_linux_display_units` / `bbws-sr2-complete`  
**capture law:** scan → settle → lock → confirm → reset

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR3_resume*.json
→ cursor/BBWS_SR3_*_SERIES_MAP*.md
→ superpowers/sr3_sNN_*.json (current season)
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + UX contract freeze | Freeze capture loop contract and non-claims | `sr3_s01_ux_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Active barcode stay + Scan button | Keep scanned tag visible; Scan focuses field | `sr3_s02_active_barcode_scan.v0.1.0.json` |
| **S03** | M03 | Lock weight state machine + action | WEIGHT_STABLE until capture.weight.lock | `sr3_s03_lock_weight_runtime.v0.1.0.json` |
| **S04** | M04 | Lock weight PySide UI | Lock button + locked readout + Confirm gate | `sr3_s04_lock_weight_pyside.v0.1.0.json` |
| **S05** | M05 | Run plant log PySide | Last 50 commits read-only list | `sr3_s05_plant_run_log.v0.1.0.json` |
| **S06** | M06 | Tk parity for capture UX loop | Barcode stay, Scan, Lock, short log in Tk | `sr3_s06_tk_capture_parity.v0.1.0.json` |
| **S07** | M07 | Snapshot fields for capture UX | active_barcode, locked_weight_g, recent_plants | `sr3_s07_snapshot_fields.v0.1.0.json` |
| **S08** | M08 | Tests for lock gate and plant log | State lock, barcode persistence, recent list | `sr3_s08_capture_ux_tests.v0.1.0.json` |
| **S09** | M09 | Runbook + dual-UI note + non-claims | Operator docs for new loop | `sr3_s09_docs_nonclaims.v0.1.0.json` |
| **S10** | M10 | Series closeout + bbws-sr3-complete | ACTIVE_ARC series_complete + tag + push | `sr3_s10_series_closeout.v0.1.0.json` |

## Non-claims

- Lock weight is not a legal-for-trade hold decision
- Plant log is not a Metrc plant list
- Scan button is HID focus only — not BLE/SPP scanner protocol
- Arc Launcher is cited doctrine, not mutated as live Best Buds runtime
