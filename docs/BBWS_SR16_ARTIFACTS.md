# BBWS SR16 Artifacts

**series_id:** `BBWS_SR16_rc10_ship`  
**product_version_target:** `2.0.0-rc10`

| Artifact | Path |
|----------|------|
| pytest rc10 | `tests/test_lock_sensitivity.py`, `tests/test_auto_record_alert.py` |
| Drift concordance | `scripts/validate_drift_concordance_v200_rc10.py` |
| Windows build | `packaging/windows/build_windows.ps1` |
| Setup | `dist/windows/BestBudsWeightStation-Setup-v2.0.0-rc10.exe` |
| Zip | `dist/windows/BestBudsWeightStation-windows-x64-v2.0.0-rc10.zip` |
| Build receipt | `dist/windows/windows_build_receipt.v2.0.0-rc10.json` |
| Debian package | `dist/debian/best-buds-weight-station_2.0.0-rc10_amd64.deb` |
| Series closeout | `reports/sr16_rc10_ship_closeout.json` |
| Drift report | `reports/drift_concordance_report.v2.0.0-rc10.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- JSONL remains authoritative for weight records
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Packaged Setup is not Authenticode-signed
- Physical COM 100 g remains operator follow-up unless a live scale is connected
- Debian package ships Tk fallback; Windows Setup is the primary operator surface
