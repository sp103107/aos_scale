# BBWS SR13 Artifacts

**series_id:** `BBWS_SR13_duplicate_barcode_pre_gate`  
**product_version_target:** `2.0.0-rc8`

| Artifact | Path |
|----------|------|
| Duplicate gate | `app/best_buds_weight_station/application_controller.py` |
| Scan flag | `app/best_buds_weight_station/state_machine.py` |
| Continue/Cancel UI | `app/best_buds_weight_station/pyside_frontend.py` |
| Tests | `tests/test_sr13_duplicate_pre_gate.py` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- Duplicate warning is session-local (this run's JSONL), not a Metrc plant list
- JSONL remains authoritative for weight records
- Capture loop unchanged: scan → settle → lock → confirm → reset (gate sits on scan)
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not a remote weighing server
- Continue still records a second weight for the same barcode when the operator accepts
- Auto-record-after-lock remains deferred to SR14
