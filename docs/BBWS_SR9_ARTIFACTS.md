# BBWS SR9 Artifacts

**series_id:** `BBWS_SR9_scale_profile_stability_governance`  
**product_version_target:** `2.0.0-rc4`  
**product_version_during_impl:** `2.0.0-rc3`  
**generated:** 2026-08-13T01:54:38Z

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR9_SCALE_PROFILE_STABILITY_GOVERNANCE_SERIES_MAP.v0.1.0.md` |
| Resume pack | `context/resume_pack/BBWS_SR9_resume.v0.1.0.json` |
| Scale profiles | `app/best_buds_weight_station/scale_profiles.py` |
| Stability detector | `app/best_buds_weight_station/stability.py` |
| Firmware identity | `firmware/elegoo_uno_r3_hx711/best_buds_scale_firmware.ino` |
| Contract freeze | `reports/sr9_s01_contract_freeze.v0.1.0.json` |
| Profile tests | `tests/test_sr9_scale_profiles.py` |
| Stability regression | `tests/test_sr9_stability_regression.py` |

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
