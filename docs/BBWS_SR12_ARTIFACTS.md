# BBWS SR12 Artifacts

**series_id:** `BBWS_SR12_post_cal_characterize_stream`  
**product_version_target:** `2.0.0-rc7`  
**product_version_during_impl:** `2.0.0-rc6`  
**generated:** 2026-08-18T22:12:48Z

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR12_POST_CAL_CHARACTERIZE_STREAM_SERIES_MAP.v0.1.0.md` |
| Resume pack | `context/resume_pack/BBWS_SR12_resume.v0.1.0.json` |
| Characterize collect | `app/best_buds_weight_station/operator_runtime.py` |
| Alice starve copy | `app/best_buds_weight_station/alice/authority.py` |
| Contract freeze | `reports/sr12_s01_contract_freeze.v0.1.0.json` |
| Characterize tests | `tests/test_sr12_characterize_stream.py` |

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
