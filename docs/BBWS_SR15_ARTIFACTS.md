# BBWS SR15 Artifacts

**series_id:** `BBWS_SR15_rc9_test_and_windows_package`  
**product_version_target:** `2.0.0-rc9`

| Artifact | Path |
|----------|------|
| pytest SR12–14 | `tests/test_sr12_characterize_stream.py` |
| pytest-qt | `tests/test_sr15_qt_operator_dialogs.py` |
| Windows build | `packaging/windows/build_windows.ps1` |
| Setup | `dist/windows/BestBudsWeightStation-Setup-v2.0.0-rc9.exe` |
| Zip | `dist/windows/BestBudsWeightStation-windows-x64-v2.0.0-rc9.zip` |
| Build receipt | `dist/windows/windows_build_receipt.v2.0.0-rc9.json` |
| Upgrade smoke | `packaging/windows/windows_upgrade_smoke_receipt.v2.0.0-rc9.json` |
| Series closeout | `reports/sr15_s10_series_closeout.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- JSONL remains authoritative for weight records
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not a remote weighing server
- Packaged Setup is not Authenticode-signed
- Physical COM 100 g remains operator follow-up unless a live scale is connected
- pytest-qt is a test extra only — not an operator runtime dependency
