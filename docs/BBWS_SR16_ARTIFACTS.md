# BBWS SR16 Artifacts

**series_id:** `BBWS_SR16_rc10_ship`  
**product_version_target:** `2.0.0-rc10.1`

| Artifact | Path |
|----------|------|
| Zero hotfix | `app/best_buds_weight_station/pyside_frontend.py`, `operator_runtime.py`, `ui_action_runner.py` |
| Drift concordance | `scripts/validate_drift_concordance_v200_rc10_1.py` |
| Windows build | `packaging/windows/build_windows.ps1` |
| Setup | `dist/windows/BestBudsWeightStation-Setup-v2.0.0-rc10.1.exe` |
| Zip | `dist/windows/BestBudsWeightStation-windows-x64-v2.0.0-rc10.1.zip` |
| Build receipt | `dist/windows/windows_build_receipt.v2.0.0-rc10.1.json` |
| Debian package | `dist/debian/best-buds-weight-station_2.0.0-rc10.1_amd64.deb` |
| Series closeout | `reports/sr16_rc10_1_ship_closeout.json` |
| Drift report | `reports/drift_concordance_report.v2.0.0-rc10.1.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- JSONL remains authoritative for weight records
- Packaged Setup is not Authenticode-signed
- Physical COM validation remains operator follow-up
- Debian package ships Tk fallback; Windows Setup is the primary operator surface
