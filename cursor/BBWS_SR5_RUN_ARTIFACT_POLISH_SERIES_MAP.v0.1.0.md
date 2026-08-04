# BBWS SR5 — Run Artifact Polish Series Map

**series_id:** `BBWS_SR5_run_artifact_polish`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR4_operator_surface_polish` / `bbws-sr4-complete`  
**baseline:** `bbws-pre-sr5-artifact-polish`  
**artifact law:** handoff polish only; JSONL authoritative  
**capture law (unchanged):** scan → settle → lock → confirm → reset

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR5_resume*.json
→ cursor/BBWS_SR5_*_SERIES_MAP*.md
→ superpowers/sr5_sNN_*.json (current season)
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + artifact polish contract freeze | Freeze artifact-vs-JSONL contract, non-claims, series map | `sr5_s01_artifact_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Salvage selection map Book Spine + Output Response | Map salvage export patterns to BBWS report targets | `sr5_s02_salvage_selection_map.v0.1.0.json` |
| **S03** | M03 | CSV plants + summary handoff polish | UTF-8 plants CSV + clearer strain summary CSV | `sr5_s03_csv_handoff_polish.v0.1.0.json` |
| **S04** | M04 | XLSX Summary/Records/NonClaims polish | Header style, freeze panes, widths, NonClaims sheet | `sr5_s04_xlsx_handoff_polish.v0.1.0.json` |
| **S05** | M05 | DOCX cover + tables + footer polish | Cover block, cultivator/strain tables, non-claim footer | `sr5_s05_docx_handoff_polish.v0.1.0.json` |
| **S06** | M06 | Handoff bundle manifest JSON | reports/handoff_bundle_manifest.json listing artifacts | `sr5_s06_handoff_bundle_manifest.v0.1.0.json` |
| **S07** | M07 | Reconcile receipt polish | Keep JSONL gate; extend receipt with bundle path | `sr5_s07_reconcile_receipt_polish.v0.1.0.json` |
| **S08** | M08 | Operator runbook + export smoke notes | Docs for polished handoff artifacts | `sr5_s08_artifact_docs.v0.1.0.json` |
| **S09** | M09 | Tests for CSV/XLSX/DOCX/manifest contracts | Automated polish contract tests | `sr5_s09_artifact_verify.v0.1.0.json` |
| **S10** | M10 | Series closeout + bbws-sr5-complete | ACTIVE_ARC series_complete + tag + push | `sr5_s10_series_closeout.v0.1.0.json` |

## Salvage selection map (cite-only)

| Pattern | Salvage source | BBWS target |
|---------|----------------|-------------|
| CSV export blocks | Book Spine `exports/csv` | plants + summary CSV |
| XLSX workbench | Book Spine `exports/xlsx` | Summary/Records/NonClaims sheets |
| Handoff packaging | Book Spine `repo_handoff/` | export naming + non-claims |
| Bundle manifest | Output Response Meta export manifests | `handoff_bundle_manifest.json` |

## Non-claims

- Handoff artifacts are non-authoritative; JSONL remains truth
- Not legal-for-trade or Metrc compliance
- Book Spine / Output Response / Arc Launcher are cite-only
- Salvage is not imported as a spreadsheet runtime
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Do not drop cultivator/strain CSV columns
