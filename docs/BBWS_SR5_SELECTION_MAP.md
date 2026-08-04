# BBWS SR5 — Salvage → BBWS Selection Map

**series_id:** `BBWS_SR5_run_artifact_polish`  
**generated:** 2026-08-04T21:53:56Z

Cite-only. Do not import salvage spreadsheet runtimes into Best Buds.

| Pattern | Salvage cue | BBWS surface |
|---------|-------------|--------------|
| CSV export blocks | Book Spine `exports/csv` | `*_plants.csv` + summary CSV via `compile_report` |
| XLSX workbench | Book Spine `exports/xlsx` + excel workbench triplets | Summary / Records / NonClaims sheets |
| Handoff packaging | Book Spine `repo_handoff/` | plain stems, non-claim stamps |
| Bundle / mount manifest | Output Response Meta export manifests | `reports/handoff_bundle_manifest.json` |

**Must not change:** JSONL authority; capture loop; cultivator/strain CSV columns.
