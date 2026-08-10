# BBWS SR7 Artifacts

**series_id:** `BBWS_SR7_windows_installer_bringup`  
**product_version_target:** `2.0.0-rc2`  
**generated:** 2026-08-10T02:11:13Z

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR7_WINDOWS_INSTALLER_BRINGUP_SERIES_MAP.v0.1.0.md` |
| Resume pack | `context/resume_pack/BBWS_SR7_resume.v0.1.0.json` |
| Run UX fixes | `app/best_buds_weight_station/pyside_frontend.py`, `alice/authority.py` |
| Path/device hygiene | `app/best_buds_weight_station/settings.py`, `platform_paths.py` |
| Windows build | `packaging/windows/` |
| Installer | `dist/windows/BestBudsWeightStation-Setup-v2.0.0-rc2.exe` |
| Drift concordance | `scripts/validate_drift_concordance_v200_rc2.py` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- Not production-sealed weighing certification
- JSONL remains authoritative for records
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Installer ships a USB bring-up product; calibration with a verified reference mass is required for accurate grams
- Capture loop unchanged: scan → settle → lock → confirm → reset
