# Next lane — recording + CSV/DOCX proof

After calibration UX (BBWS-CALUX S01):

- Session commit already appends `records.csv` / `records.xlsx`.
- `compile_report` now emits JSON + CSV + XLSX + **DOCX**.
- `report.export` copies report artifacts and session CSV/XLSX to the chosen folder.
- PySide save/export dialogs name the files in plain language.

Verification: `tests/test_recording_export_proof.py`.
