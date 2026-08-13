# BBWS SR9 — Scale Profile and Stability Governance Series Map

**series_id:** `BBWS_SR9_scale_profile_stability_governance`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR8_scale_face_harvest_mode` / `bbws-sr8-complete`  
**baseline:** `bbws-pre-sr9-scale-profile`  
**product version target:** `2.0.0-rc4`  
**product version during impl:** `2.0.0-rc3` (bump in S09)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR9_resume*.json
→ cursor/BBWS_SR9_*_SERIES_MAP*.md
→ superpowers/sr9_sNN_*.json
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + identity/profile/stability contract freeze | Freeze: rc3 baseline, SR9 laws, identity/profile/stability non-claims | `sr9_s01_contract_and_baseline_freeze.v0.1.0.json` |
| **S02** | M02 | Firmware EEPROM device identity | SET_DEVICE_ID EEPROM persist, protocol docs, host validation | `sr9_s02_device_identity_persistence.v0.1.0.json` |
| **S03** | M03 | Typed atomic scale profile store | CRUD/archive, hash, active-per-device semantics | `sr9_s03_scale_profile_store.v0.1.0.json` |
| **S04** | M04 | Calibration binds to device profile | Accept cal creates/updates profile; reconnect apply+verify SET_CAL | `sr9_s04_calibration_profile_binding.v0.1.0.json` |
| **S05** | M05 | 100 g post-cal stability characterization | 120-sample characterization, bounded recommend, operator confirm | `sr9_s05_post_cal_stability_characterization.v0.1.0.json` |
| **S06** | M06 | Capture stability runtime gates | Trend gate, recoverable timeout, snapshot diagnostics | `sr9_s06_capture_stability_runtime.v0.1.0.json` |
| **S07** | M07 | Scale Setup profile management UI | Identity, profile CRUD/archive, characterization, diagnostics | `sr9_s07_profile_management_ui.v0.1.0.json` |
| **S08** | M08 | Physical + regression validation | Unit/integration/simulator tests + COM physical checklist | `sr9_s08_physical_and_regression_validation.v0.1.0.json` |
| **S09** | M09 | Bump to 2.0.0-rc4 + Windows packaging | Version/drift/manifest; Setup/zip; rc3→rc4 upgrade smoke | `sr9_s09_rc4_windows_packaging.v0.1.0.json` |
| **S10** | M10 | SR9 series closeout + tags | Docs/release, tag v2.0.0-rc4 + bbws-sr9-complete, push | `sr9_s10_release_and_closeout.v0.1.0.json` |

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
