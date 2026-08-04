# BBWS SR5 — Artifact Polish Runbook

**series_id:** `BBWS_SR5_run_artifact_polish`  
**parent:** `bbws-sr4-complete` / baseline `bbws-pre-sr5-artifact-polish`

## What changed

Handoff packaging for accepted harvest records:

- Summary CSV includes `cultivator,strain,net_g`
- Plants CSV keeps full `HEADERS` (including cultivator + strain), UTF-8
- XLSX: styled headers, freeze panes, Summary / Records / NonClaims sheets
- DOCX: cover block, cultivator/strain tables, non-claim footer
- `reports/handoff_bundle_manifest.json` lists artifacts + SHA + non-claims
- Reconcile receipt checks headers + bundle presence

## What did not change

- Session **JSONL** remains authoritative
- Capture loop: Scan → settle → Lock → Confirm → reset
- Metrc / legal-for-trade non-claims

## Operator smoke

1. Finish or export a run: **Run → Export Report…**
2. Open `*_plants.csv` — confirm cultivator + strain columns
3. Open `*_harvest.xlsx` — Summary, Records, NonClaims sheets
4. Open `*_harvest.docx` — cover + non-claim text
5. Confirm `handoff_bundle_manifest.json` lists the same files
6. **Run → Reconcile Export ↔ JSONL** — expect pass

## Salvage cites (not imported)

- Book Spine: `M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_book_spine_capsule_template_v0_1_10`
- Output Response Meta: `M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_output_response_meta_pack_v1_5_0`

See also: `docs/BBWS_SR5_SELECTION_MAP.md`
