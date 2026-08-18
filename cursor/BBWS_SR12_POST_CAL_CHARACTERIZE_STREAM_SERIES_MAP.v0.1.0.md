# BBWS SR12 — Post-Cal Characterize Stream Series Map

**series_id:** `BBWS_SR12_post_cal_characterize_stream`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR11_live_stream_quiet_window` / `bbws-sr11-complete`  
**baseline:** `bbws-pre-sr12-characterize`  
**product version target:** `2.0.0-rc7`  
**product version during impl:** `2.0.0-rc6` (bump in S09 only after S06 characterize gate)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR12_resume*.json
→ cursor/BBWS_SR12_*_SERIES_MAP*.md
→ superpowers/sr12_sNN_*.json
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + contract freeze | Freeze SR12 contract; baseline tag; Arc artifacts | `sr12_s01_scaffold_and_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Ensure worker before characterize samples | Call ensure_reading_worker at start of collect_weight_samples | `sr12_s02_ensure_worker_for_characterize.v0.1.0.json` |
| **S03** | M03 | Surface worker error on collect fail | Include last_worker_error when characterization samples starve | `sr12_s03_surface_worker_error_on_collect.v0.1.0.json` |
| **S04** | M04 | Alice characterize copy | Operator-safe message for not enough live weight samples | `sr12_s04_alice_characterize_copy.v0.1.0.json` |
| **S05** | M05 | Scripted characterize tests | Stopped worker recovers; characterize collect does not starve | `sr12_s05_scripted_characterize_tests.v0.1.0.json` |
| **S06** | M06 | Physical post-cal characterize gate | Accept → 100 g Stability Test with mass on pan | `sr12_s06_physical_characterize_gate.v0.1.0.json` |
| **S07** | M07 | Docs + characterize recovery | Bring-up note: 100 g test needs live stream after Accept | `sr12_s07_docs_characterize_recovery.v0.1.0.json` |
| **S08** | M08 | No unrelated churn | This bump is characterize-only; SR13/SR14 stay later series | `sr12_s08_no_unrelated_churn.v0.1.0.json` |
| **S09** | M09 | Bump to 2.0.0-rc7 + Windows packaging | Version/drift/manifest; Setup/zip — only after S06 gate | `sr12_s09_rc7_windows_packaging.v0.1.0.json` |
| **S10** | M10 | SR12 series closeout + tags | Docs/release, tag v2.0.0-rc7 + bbws-sr12-complete | `sr12_s10_release_and_closeout.v0.1.0.json` |

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
- Ensure-worker-before-characterize is operational integrity only — not certification
