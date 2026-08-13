# BBWS SR11 Artifacts

**series_id:** `BBWS_SR11_live_stream_quiet_window`  
**product_version_target:** `2.0.0-rc6`  
**product_version_during_impl:** `2.0.0-rc5`  
**generated:** 2026-08-13T16:08:12Z

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR11_LIVE_STREAM_QUIET_WINDOW_SERIES_MAP.v0.1.0.md` |
| Resume pack | `context/resume_pack/BBWS_SR11_resume.v0.1.0.json` |
| Operator quiet window | `app/best_buds_weight_station/operator_runtime.py` |
| Profile apply skip SET_CAL | `app/best_buds_weight_station/application_controller.py` |
| Contract freeze | `reports/sr11_s01_contract_freeze.v0.1.0.json` |
| Quiet tests | `tests/test_sr11_stream_quiet.py` |

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
