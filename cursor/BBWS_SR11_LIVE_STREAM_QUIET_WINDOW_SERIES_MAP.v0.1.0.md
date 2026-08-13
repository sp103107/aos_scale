# BBWS SR11 — Live Stream Quiet Window Series Map

**series_id:** `BBWS_SR11_live_stream_quiet_window`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR10_calibration_handshake_integrity` / `bbws-sr10-complete`  
**baseline:** `bbws-pre-sr11-stream-quiet`  
**product version target:** `2.0.0-rc6`  
**product version during impl:** `2.0.0-rc5` (bump in S09 only after S07 physical pass)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR11_resume*.json
→ cursor/BBWS_SR11_*_SERIES_MAP*.md
→ superpowers/sr11_sNN_*.json
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + contract freeze | Freeze SR11 contract; baseline tag; Arc artifacts | `sr11_s01_scaffold_and_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Quiet window around resume/load | Stop worker before profile apply on run.resume / run.load / new-run-when-connected | `sr11_s02_quiet_resume_load.v0.1.0.json` |
| **S03** | M03 | Skip redundant SET_CAL | If STATUS factor matches active profile, install stability only | `sr11_s03_skip_redundant_set_cal.v0.1.0.json` |
| **S04** | M04 | Ensure worker before Guided Cal samples | ensure_reading_worker before collect_raw_samples / start_calibration | `sr11_s04_ensure_worker_for_cal.v0.1.0.json` |
| **S05** | M05 | Restart worker + clear error | After quiet apply, restart worker and clear last_worker_error on success | `sr11_s05_restart_clear_error.v0.1.0.json` |
| **S06** | M06 | Scripted quiet-window tests | Resume under stream leaves worker running; skip SET_CAL when matched | `sr11_s06_scripted_quiet_tests.v0.1.0.json` |
| **S07** | M07 | Physical resume + Guided Cal gate | Connect → Resume → live grams → Guided Cal empty samples | `sr11_s07_physical_resume_cal_gate.v0.1.0.json` |
| **S08** | M08 | Docs + resume recovery | Bring-up resume recovery; do not reopen stream under SET_CAL | `sr11_s08_docs_resume_recovery.v0.1.0.json` |
| **S09** | M09 | Bump to 2.0.0-rc6 + Windows packaging | Version/drift/manifest; Setup/zip; rc5→rc6 upgrade smoke — only after S07 pass | `sr11_s09_rc6_windows_packaging.v0.1.0.json` |
| **S10** | M10 | SR11 series closeout + tags | Docs/release, tag v2.0.0-rc6 + bbws-sr11-complete, push | `sr11_s10_release_and_closeout.v0.1.0.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- 100 g characterization is repeatability evidence, not certification
- Scale profiles/receipts are local operational evidence only
- JSONL remains authoritative for weight records
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Firmware device identity must be unique; collision requires operator intervention
- Archived profiles never erase historical calibration or weight evidence
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not a remote weighing server
- Quiet-window resume is operational integrity only — not certification
