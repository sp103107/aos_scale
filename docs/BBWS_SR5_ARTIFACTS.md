# BBWS SR5 Artifacts

**series_id:** `BBWS_SR5_run_artifact_polish`  
**generated:** 2026-08-04T21:53:56Z

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR5_RUN_ARTIFACT_POLISH_SERIES_MAP.v0.1.0.md` |
| Blueprint | `arc_lifecycle/blueprints/series_bbws_sr5_run_artifact_polish.v0.1.0.json` |
| Resume pack | `context/resume_pack/BBWS_SR5_resume.v0.1.0.json` |
| Ledger | `context/ledger/bbws_sr5_ledger.md` |
| Selection map | `docs/BBWS_SR5_SELECTION_MAP.md` |
| Operator runbook | `docs/BBWS_SR5_ARTIFACT_POLISH_RUNBOOK.md` |
| Closeout report | `reports/bbws_sr5_series_closeout.md` |
| Polish tests | `tests/test_sr5_artifact_polish.py` |
| Report compiler | `app/best_buds_weight_station/reports.py` |

## Non-claims

- Handoff artifacts are non-authoritative; JSONL remains truth
- Not legal-for-trade or Metrc compliance
- Book Spine / Output Response / Arc Launcher are cite-only
- Salvage is not imported as a spreadsheet runtime
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Do not drop cultivator/strain CSV columns
