# BBWS SR1 — Harvest Operator Loop Series Map

**series_id:** `BBWS_SR1_harvest_operator_loop`  
**shape:** 10 seasons × 10 episodes = 100  
**baseline:** GitHub `aos_scale` `v0.1.9-rc2` + `context/operator_ux_arc` (BBWS-CALUX prequel)  
**doctrine:** Arc Launcher at `C:\aos_arc_launcher_v0_4_21` (read-only cite)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR1_resume*.json
→ cursor/BBWS_SR1_*_SERIES_MAP*.md
→ superpowers/sNN_*.json (current season)
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Harvest recording polish | Confirm/Cancel pacing, saved copy, duplicate/blocked UX | `s01_recording_polish.v0.1.0.json` |
| **S02** | M02 | HID scanner integration | Focus ownership, Test Scanner receipts, require-barcode policy | `s02_hid_scanner.v0.1.0.json` |
| **S03** | M03 | Sticky strain for scan groups | Active strain UI; mid-run change; CSV cultivar stamps | `s03_sticky_strain.v0.1.0.json` |
| **S04** | M04 | CSV recording truth | Row proof, rebuild-from-JSONL, pending_sync UX | `s04_csv_recording_truth.v0.1.0.json` |
| **S05** | M05 | Export quality | Full-plant CSV handoff, DOCX/XLSX polish, plain filenames | `s05_export_quality.v0.1.0.json` |
| **S06** | M06 | Export ↔ JSONL reconcile gates | Counts, cultivar totals, SHA receipts | `s06_export_reconcile_gates.v0.1.0.json` |
| **S07** | M07 | Physical field E2E | scan→weigh→record→CSV evidence receipts; metrology non-claim | `s07_field_e2e.v0.1.0.json` |
| **S08** | M08 | Crash/resume operator polish | Storage recovery UX after interrupt | `s08_crash_resume.v0.1.0.json` |
| **S09** | M09 | Light governance | Void/note, cal id on record, operator id clarity | `s09_governance_light.v0.1.0.json` |
| **S10** | M10 | Windows package smoke + series closeout | Packaging smoke + series closeout + GitHub prerelease tag | `s10_package_smoke_closeout.v0.1.0.json` |

## Decision locks

- Sticky strain until changed (per-scan override is later)
- HID keyboard-wedge only (no BLE/SPP/camera)
- Session JSONL authoritative; CSV/XLSX/DOCX are derivatives
- Push after each season closeout (E10); no auto-push mid-episode
- Tag prereleases at M05 and series end at minimum

## Non-claims

- Not legal-for-trade / metrology certification
- Sticky strain UX ≠ Metrc compliance
- HID wedge ≠ BLE/SPP barcode protocol
- Season push ≠ release seal / Authenticode
- Arc Launcher not claimed as live runtime for Best Buds

## Episode rhythm (every season)

E01 intent/context → E02–E08 implement/verify → E09 receipt → **E10 closeout + save/push plan**
