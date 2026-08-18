# BBWS SR14 Artifacts

**series_id:** `BBWS_SR14_auto_record_after_lock`  
**product_version_target:** `2.0.0-rc9`

| Artifact | Path |
|----------|------|
| Setting | `app/best_buds_weight_station/settings.py` |
| Lock→commit | `app/best_buds_weight_station/application_controller.py` |
| Beep | `app/best_buds_weight_station/operator_beep.py` |
| Station Settings | `app/best_buds_weight_station/pyside_frontend.py` |
| Tests | `tests/test_sr14_auto_record_after_lock.py` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- JSONL remains authoritative for weight records
- Capture loop remains scan → settle → lock → confirm → reset; Confirm is automatic when the setting is on
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not a remote weighing server
- Audible beep is an operator cue, not certification
- Existing automatic mode (record on stable) is unchanged
- Duplicate pre-gate from SR13 still warns before any auto-record
