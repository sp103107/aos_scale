# BBWS SR14 — Auto-Record After Lock Series Map

**series_id:** `BBWS_SR14_auto_record_after_lock`  
**parent:** `BBWS_SR13_duplicate_barcode_pre_gate` / `bbws-sr13-complete`  
**baseline:** `bbws-pre-sr14-auto-lock`  
**product version target:** `2.0.0-rc9`

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + contract freeze | Freeze SR14 contract; baseline tag; Arc artifacts | `sr14_s01_scaffold_and_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Settings bool | AppSettings.auto_record_after_lock default false + persist | `sr14_s02_settings_auto_record_after_lock.v0.1.0.json` |
| **S03** | M03 | Lock commits when enabled | capture.weight.lock calls confirm when the setting is on | `sr14_s03_lock_commits_when_enabled.v0.1.0.json` |
| **S04** | M04 | Station Settings toggle | Station Settings + lock UI handles saved record | `sr14_s04_station_settings_toggle.v0.1.0.json` |
| **S05** | M05 | Operator beep | Windows MessageBeep on terminal success/warning/error; silent in pytest | `sr14_s05_operator_beep.v0.1.0.json` |
| **S06** | M06 | Scripted auto-lock tests | Lock commits when on; Confirm still required when off; dup gate holds | `sr14_s06_scripted_auto_lock_tests.v0.1.0.json` |
| **S07** | M07 | Docs + auto-lock | Operator docs: Station Settings auto-record after Lock | `sr14_s07_docs_auto_lock.v0.1.0.json` |
| **S08** | M08 | No unrelated churn | This bump is auto-record + beep only | `sr14_s08_no_unrelated_churn.v0.1.0.json` |
| **S09** | M09 | Bump to 2.0.0-rc9 + Windows packaging | Version/drift/manifest — SR14 only | `sr14_s09_rc9_windows_packaging.v0.1.0.json` |
| **S10** | M10 | SR14 series closeout + tags | Docs/release, tag v2.0.0-rc9 + bbws-sr14-complete | `sr14_s10_release_and_closeout.v0.1.0.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- JSONL remains authoritative for weight records
- Capture loop remains scan → settle → lock → confirm → reset; Confirm is automatic when the setting is on
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not a remote weighing server
- Audible beep is an operator cue, not certification
- Existing automatic mode (record on stable) is unchanged
- Duplicate pre-gate from SR13 still warns before any auto-record
