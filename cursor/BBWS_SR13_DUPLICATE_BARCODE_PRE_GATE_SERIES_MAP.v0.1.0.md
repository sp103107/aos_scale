# BBWS SR13 — Duplicate Barcode Pre-Gate Series Map

**series_id:** `BBWS_SR13_duplicate_barcode_pre_gate`  
**parent:** `BBWS_SR12_post_cal_characterize_stream` / `bbws-sr12-complete`  
**baseline:** `bbws-pre-sr13-dup-gate`  
**product version target:** `2.0.0-rc8`

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + contract freeze | Freeze SR13 contract; baseline tag; Arc artifacts | `sr13_s01_scaffold_and_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Backend duplicate lookup | barcode.submit blocks when barcode is already in the session store | `sr13_s02_backend_duplicate_lookup.v0.1.0.json` |
| **S03** | M03 | Acknowledge continue path | acknowledge_duplicate continues scan and tags duplicate_status accepted | `sr13_s03_acknowledge_continue.v0.1.0.json` |
| **S04** | M04 | Continue/Cancel UI | PySide and Tk warn before weigh; Cancel writes nothing | `sr13_s04_operator_continue_cancel_ui.v0.1.0.json` |
| **S05** | M05 | Scripted duplicate tests | Block, continue+accepted, automatic cannot silent-commit | `sr13_s05_scripted_duplicate_tests.v0.1.0.json` |
| **S06** | M06 | Automatic path gate | Gate also blocks future auto-commit (SR14) by sitting on scan | `sr13_s06_automatic_path_gate.v0.1.0.json` |
| **S07** | M07 | Docs + duplicate warn | Operator docs: duplicate warning before record | `sr13_s07_docs_duplicate_warn.v0.1.0.json` |
| **S08** | M08 | No unrelated churn | This bump is duplicate-gate only; auto-record stays SR14 | `sr13_s08_no_unrelated_churn.v0.1.0.json` |
| **S09** | M09 | Bump to 2.0.0-rc8 + Windows packaging | Version/drift/manifest — SR13 only | `sr13_s09_rc8_windows_packaging.v0.1.0.json` |
| **S10** | M10 | SR13 series closeout + tags | Docs/release, tag v2.0.0-rc8 + bbws-sr13-complete | `sr13_s10_release_and_closeout.v0.1.0.json` |

## Non-claims

- Not legal-for-trade / Metrc compliance
- Duplicate warning is session-local (this run's JSONL), not a Metrc plant list
- JSONL remains authoritative for weight records
- Capture loop unchanged: scan → settle → lock → confirm → reset (gate sits on scan)
- Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only
- Not a remote weighing server
- Continue still records a second weight for the same barcode when the operator accepts
- Auto-record-after-lock remains deferred to SR14
