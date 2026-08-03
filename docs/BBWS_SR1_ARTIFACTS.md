# BBWS SR1 Artifacts

Harvest-operator 100-arc series (`BBWS_SR1_harvest_operator_loop`) owned in this repo.

## Arc scaffolding

| Path | Purpose |
|------|---------|
| `ACTIVE_ARC.yaml` | Live season/episode pointer |
| `arc_lifecycle/blueprints/series_bbws_sr1_harvest_operator_loop.v0.1.0.json` | Series blueprint |
| `cursor/BBWS_SR1_HARVEST_OPERATOR_LOOP_SERIES_MAP.v0.1.0.md` | Human series map |
| `manifests/bbws_sr1_series_map.v0.1.0.json` | Machine series map |
| `superpowers/s01_*.json` … `s10_*.json` | Season episode packs |
| `context/resume_pack/BBWS_SR1_resume.v0.1.0.json` | Resume pack |
| `git_arc/active/*` | Commit/push plans only (no auto-push) |
| `kickoff_prompts/BBWS_SR1_HUMAN_CHAT_KICKOFF.md` | New-chat kickoff |

## Scripts

| Path | Purpose |
|------|---------|
| `scripts/scaffold_bbws_sr1.py` | Phase A scaffold generator |
| `scripts/bbws_sr1_season_closeout.py` | Season E10 closeout + pointer advance |
| `scripts/bbws_sr1_smoke_verify.py` | Simulator product smoke |
| `scripts/reconcile_export_jsonl.py` | Export↔JSONL reconcile CLI |

## Product surfaces touched

- Sticky active strain (`run.set_active_cultivar`)
- HID Test Scanner receipts + barcode policy settings
- Recording polish (soft confirm pacing, duplicate warning, cancel focus)
- CSV rebuild from JSONL + pending_sync UX
- Plain plant CSV export + reconcile gates
- Light governance note/void fields on confirm
