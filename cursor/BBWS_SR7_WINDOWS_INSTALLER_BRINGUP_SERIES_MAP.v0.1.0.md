# BBWS SR7 — Windows Installer Bring-up Series Map

**series_id:** `BBWS_SR7_windows_installer_bringup`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR6_product_onboarding_release` / `bbws-sr6-complete`  
**baseline:** `bbws-pre-sr7-windows-installer`  
**product version target:** `2.0.0-rc2`

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR7_resume*.json
→ cursor/BBWS_SR7_*_SERIES_MAP*.md
→ superpowers/sr7_sNN_*.json
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + installer/release contract freeze | Freeze SR7 scope: UX fixes, hygiene, installer, rc2 release | `sr7_s01_installer_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Run lifecycle + capture display UX fixes | Finish Run closeout, locked-weight display freeze, resume-run picker | `sr7_s02_run_lifecycle_ux_fixes.v0.1.0.json` |
| **S03** | M03 | Path + device install hygiene | Frozen-exe path truth and runtime COM enumeration only | `sr7_s03_path_device_hygiene.v0.1.0.json` |
| **S04** | M04 | Build host prep (Inno Setup 6 + env) | Install/verify Inno Setup 6 and PyInstaller build env | `sr7_s04_build_host_prep.v0.1.0.json` |
| **S05** | M05 | PyInstaller exe + zip build green | build_windows.ps1 through exe, verify, zip | `sr7_s05_pyinstaller_build_green.v0.1.0.json` |
| **S06** | M06 | Setup.exe build + install/uninstall smoke | Inno installer, per-user install, launch, uninstall preserves runs | `sr7_s06_installer_smoke.v0.1.0.json` |
| **S07** | M07 | Bump product version to 2.0.0-rc2 | version.py, VERSION, pyproject, iss, README, RC docs | `sr7_s07_version_bump_rc2.v0.1.0.json` |
| **S08** | M08 | Drift concordance for 2.0.0-rc2 | rc2 concordance validator, report, version-pinned tests | `sr7_s08_drift_concordance_rc2.v0.1.0.json` |
| **S09** | M09 | Release artifacts: source zip + windows zip + Setup.exe | make_release_bundle source zip, staged Windows artifacts, SHA256 receipts | `sr7_s09_release_artifacts.v0.1.0.json` |
| **S10** | M10 | GitHub Release + bbws-sr7-complete | gh release v2.0.0-rc2, tags, ACTIVE_ARC series_complete | `sr7_s10_series_closeout.v0.1.0.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- Not production-sealed weighing certification
- JSONL remains authoritative for records
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Installer ships a USB bring-up product; calibration with a verified reference mass is required for accurate grams
- Capture loop unchanged: scan → settle → lock → confirm → reset
