# BBWS SR8 Artifacts

**series_id:** `BBWS_SR8_scale_face_harvest_mode`  
**product_version_target:** `2.0.0-rc3`  
**generated:** 2026-08-11T03:39:48Z

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR8_SCALE_FACE_HARVEST_MODE_SERIES_MAP.v0.1.0.md` |
| Resume pack | `context/resume_pack/BBWS_SR8_resume.v0.1.0.json` |
| Scale Face UI | `app/best_buds_weight_station/scale_face.py` |
| Action helpers | `app/best_buds_weight_station/operator_surface.py` (`SCALE_FACE_*_ACTIONS`) |
| Menu wiring | `app/best_buds_weight_station/pyside_frontend.py` |
| Contract tests | `tests/test_sr8_scale_face.py` |
| Drift concordance | `scripts/validate_drift_concordance_v200_rc3.py` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- Not a remote weighing server or separate Scale Face process
- Not collapsing Lock+Confirm in manual mode
- JSONL remains authoritative for records
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not claiming small 2–5″ hardware support without a later series
