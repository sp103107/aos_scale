# BBWS SR15 — rc9 Test Gate + Windows Setup Series Map

**series_id:** `BBWS_SR15_rc9_test_and_windows_package`  
**parent:** `BBWS_SR14_auto_record_after_lock` / `bbws-sr14-complete`  
**baseline:** `bbws-pre-sr15-test-package`  
**product version target:** `2.0.0-rc9`

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + contract freeze | Freeze SR15 contract; baseline tag; Arc artifacts | `sr15_s01_scaffold_and_contract_freeze.v0.1.0.json` |
| **S02** | M02 | pytest SR12–14 + full suite | Fail closed on SR12/SR13/SR14 tests then full pytest | `sr15_s02_pytest_sr12_sr14.v0.1.0.json` |
| **S03** | M03 | Simulator self-test + ui-smoke | --self-test --simulator and --ui-smoke --simulator | `sr15_s03_simulator_self_test_smoke.v0.1.0.json` |
| **S04** | M04 | pytest-qt operator dialogs | Offscreen Qt: duplicate Cancel writes nothing; Station Settings auto-record | `sr15_s04_pytest_qt_operator_dialogs.v0.1.0.json` |
| **S05** | M05 | Bugbot review | Cursor Bugbot on SR12–SR14 branch changes | `sr15_s05_bugbot_review.v0.1.0.json` |
| **S06** | M06 | Defect pass or none | Fix confirmed defects only; operator-code fixes bump rc10 | `sr15_s06_defect_pass_or_none.v0.1.0.json` |
| **S07** | M07 | Docs + rc9 Setup note | WINDOWS_BUILD and RELEASE_CANDIDATE note that rc9 has Setup | `sr15_s07_docs_rc9_setup.v0.1.0.json` |
| **S08** | M08 | Windows Setup + zip | build_windows.ps1; hard fail if ISCC missing | `sr15_s08_windows_setup_build.v0.1.0.json` |
| **S09** | M09 | Packaged upgrade smoke | Silent upgrade to rc9; data marker and self-test | `sr15_s09_upgrade_smoke.v0.1.0.json` |
| **S10** | M10 | SR15 series closeout + tags | series_complete; tag bbws-sr15-complete (keep v2.0.0-rc9 unless S06 forced rc10) | `sr15_s10_release_and_closeout.v0.1.0.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- JSONL remains authoritative for weight records
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not a remote weighing server
- Packaged Setup is not Authenticode-signed
- Physical COM 100 g remains operator follow-up unless a live scale is connected
- pytest-qt is a test extra only — not an operator runtime dependency
