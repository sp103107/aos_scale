"""
Scaffold BBWS_SR5 run artifact polish 100-arc series (Phase A / S01).

Generates ACTIVE_ARC, blueprint, series map, SR5 superpowers, resume pack,
git_arc pointers, and kickoff. Does not implement product features.

Doctrine cite only (do not mutate salvage / Arc Launcher):
- M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_book_spine_capsule_template_v0_1_10
- M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_output_response_meta_pack_v1_5_0
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR5_run_artifact_polish"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

NON_CLAIMS = [
    "Handoff artifacts are non-authoritative; JSONL remains truth",
    "Not legal-for-trade or Metrc compliance",
    "Book Spine / Output Response / Arc Launcher are cite-only",
    "Salvage is not imported as a spreadsheet runtime",
    "Capture loop unchanged: scan → settle → lock → confirm → reset",
    "Do not drop cultivator/strain CSV columns",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "artifact_contract_freeze",
        "title": "Scaffold + artifact polish contract freeze",
        "milestone": "M01",
        "focus": "Freeze artifact-vs-JSONL contract, non-claims, series map",
        "surfaces": ["ACTIVE_ARC.yaml", "cursor/", "docs/", "scripts/scaffold_bbws_sr5.py"],
        "episodes": [
            ("Intent freeze: polish vs authority", "context"),
            ("Inventory current CSV/XLSX/DOCX surfaces", "context"),
            ("Inventory Book Spine export cites", "context"),
            ("Write contract freeze receipt", "implement"),
            ("Authorize S02 selection map scope", "implement"),
            ("Authorize S03–S05 format polish scope", "implement"),
            ("Authorize S06–S07 bundle/reconcile scope", "implement"),
            ("Verify JSONL authority rule", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "salvage_selection_map",
        "title": "Salvage selection map Book Spine + Output Response",
        "milestone": "M02",
        "focus": "Map salvage export patterns to BBWS report targets",
        "surfaces": ["docs/BBWS_SR5_SELECTION_MAP.md"],
        "episodes": [
            ("Intent freeze: cite-only mapping", "context"),
            ("Map Book Spine csv/xlsx exports", "implement"),
            ("Map Output Response bundle manifests", "implement"),
            ("Draft BBWS target table", "implement"),
            ("Reject salvage spreadsheet runtime import", "implement"),
            ("Stamp non-claims on selection map", "implement"),
            ("Verify selection coverage", "verify"),
            ("Verify no Metrc claim", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "csv_handoff_polish",
        "title": "CSV plants + summary handoff polish",
        "milestone": "M03",
        "focus": "UTF-8 plants CSV + clearer strain summary CSV",
        "surfaces": ["app/best_buds_weight_station/reports.py", "app/best_buds_weight_station/spreadsheet.py"],
        "episodes": [
            ("Intent freeze: keep HEADERS", "context"),
            ("Keep cultivator and strain columns", "implement"),
            ("Polish summary CSV headers/context", "implement"),
            ("UTF-8 plants CSV write", "implement"),
            ("Stable plain_export_stem filenames", "implement"),
            ("Reject dropping JSONL fields", "implement"),
            ("Verify HEADERS contract", "verify"),
            ("Verify summary totals", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "xlsx_handoff_polish",
        "title": "XLSX Summary/Records/NonClaims polish",
        "milestone": "M04",
        "focus": "Header style, freeze panes, widths, NonClaims sheet",
        "surfaces": ["app/best_buds_weight_station/reports.py"],
        "episodes": [
            ("Intent freeze: sheet layout only", "context"),
            ("Style header rows", "implement"),
            ("Freeze top row + column widths", "implement"),
            ("Keep Summary and Records sheets", "implement"),
            ("Add NonClaims sheet", "implement"),
            ("Legacy alias xlsx unchanged path", "implement"),
            ("Verify HEADERS on Records", "verify"),
            ("Verify NonClaims text labels", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "docx_handoff_polish",
        "title": "DOCX cover + tables + footer polish",
        "milestone": "M05",
        "focus": "Cover block, cultivator/strain tables, non-claim footer",
        "surfaces": ["app/best_buds_weight_station/reports.py"],
        "episodes": [
            ("Intent freeze: DOCX presentation", "context"),
            ("Cover run/session/totals block", "implement"),
            ("Cultivator/strain column labels", "implement"),
            ("Strain totals table polish", "implement"),
            ("Plant records table polish", "implement"),
            ("Non-claim footer", "implement"),
            ("Verify python-docx optional path", "verify"),
            ("Verify non-claim paragraph", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "handoff_bundle_manifest",
        "title": "Handoff bundle manifest JSON",
        "milestone": "M06",
        "focus": "reports/handoff_bundle_manifest.json listing artifacts",
        "surfaces": ["app/best_buds_weight_station/reports.py"],
        "episodes": [
            ("Intent freeze: BBWS-owned schema", "context"),
            ("List artifact paths in manifest", "implement"),
            ("Include records_sha256", "implement"),
            ("Stamp authoritative false", "implement"),
            ("Stamp non_claims array", "implement"),
            ("Wire into compile_report artifacts", "implement"),
            ("Verify manifest written", "verify"),
            ("Verify cite-only Output Response", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "reconcile_receipt_polish",
        "title": "Reconcile receipt polish",
        "milestone": "M07",
        "focus": "Keep JSONL gate; extend receipt with bundle path",
        "surfaces": ["app/best_buds_weight_station/reports.py"],
        "episodes": [
            ("Intent freeze: gate unchanged", "context"),
            ("Keep count/cultivar/SHA checks", "implement"),
            ("Add bundle path to receipt", "implement"),
            ("Stamp non_claims on receipt", "implement"),
            ("Ensure polished files still pass", "implement"),
            ("Receipt path stable", "implement"),
            ("Verify pass on matching export", "verify"),
            ("Verify fail on count mismatch path", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "artifact_docs",
        "title": "Operator runbook + export smoke notes",
        "milestone": "M08",
        "focus": "Docs for polished handoff artifacts",
        "surfaces": ["docs/"],
        "episodes": [
            ("Intent freeze: docs only", "context"),
            ("BBWS_SR5_ARTIFACTS index", "implement"),
            ("Operator artifact polish runbook", "implement"),
            ("Export smoke checklist", "implement"),
            ("Non-claims page stamp", "implement"),
            ("Link selection map", "implement"),
            ("Docs consistency verify", "verify"),
            ("No Metrc claim verify", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "artifact_verify",
        "title": "Tests for CSV/XLSX/DOCX/manifest contracts",
        "milestone": "M09",
        "focus": "Automated polish contract tests",
        "surfaces": ["tests/"],
        "episodes": [
            ("Intent freeze: test matrix", "context"),
            ("CSV HEADERS + cultivator/strain test", "implement"),
            ("XLSX NonClaims sheet test", "implement"),
            ("DOCX non-claim text test", "implement"),
            ("Bundle manifest test", "implement"),
            ("Reconcile still passes test", "implement"),
            ("Pytest green verify", "verify"),
            ("Reproducible compile verify", "verify"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "series_closeout",
        "title": "Series closeout + bbws-sr5-complete",
        "milestone": "M10",
        "focus": "ACTIVE_ARC series_complete + tag + push",
        "surfaces": ["ACTIVE_ARC.yaml", "reports/", "git_arc/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Season ledger complete", "implement"),
            ("Closeout report", "implement"),
            ("ACTIVE_ARC series_complete", "implement"),
            ("Tag bbws-sr5-complete", "implement"),
            ("Push origin HEAD + tags", "implement"),
            ("Remote tag verify", "verify"),
            ("Pointer verify", "verify"),
            ("S10 receipt pack", "receipt"),
            ("M10 series closeout", "closeout"),
        ],
    },
]


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def episode_id(season_id: str, n: int) -> str:
    return f"{season_id}E{n:02d}"


def sp_name(season: dict) -> str:
    return f"sr5_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


def build_superpower(season: dict) -> dict:
    episodes = []
    for i, (title, kind) in enumerate(season["episodes"], start=1):
        eid = episode_id(season["id"], i)
        episodes.append(
            {
                "id": eid,
                "title": title,
                "kind": kind,
                "status": "planned",
                "objective": title,
                "authorized_scope": season["surfaces"],
                "forbidden_scope": [
                    "capture workflow / state machine mutation",
                    "JSONL authority changes",
                    "drop cultivator/strain CSV columns",
                    "Metrc sync",
                    "import salvage spreadsheet runtime",
                    "Arc Launcher / M: mutation",
                    "auto-push mid-episode",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr5.{season['slug']}.v1",
        "arc_id": f"SR5_{season['id']}_{season['slug']}",
        "series_id": SERIES_ID,
        "title": season["title"],
        "milestone": season["milestone"],
        "focus": season["focus"],
        "runtime_claimed": False,
        "primary_surfaces": season["surfaces"],
        "episodes": episodes,
        "non_claims": NON_CLAIMS,
        "doctrine_cite": [
            "M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_book_spine_capsule_template_v0_1_10",
            "M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_output_response_meta_pack_v1_5_0",
        ],
    }


def main() -> None:
    write_text(
        ROOT / "ACTIVE_ARC.yaml",
        f"""# BBWS SR5 live pointer — product owns truth (salvage / Arc Launcher cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: artifact_contract_freeze
episode_id: S01E01
milestone: M01
status: active
parent_series_id: BBWS_SR4_operator_surface_polish
parent_tag: bbws-sr4-complete
baseline_tag: bbws-pre-sr5-artifact-polish
baseline_freeze: v0.1.9-rc2
doctrine_source: C:/aos_arc_launcher_v0_4_21
book_spine_ref: M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_book_spine_capsule_template_v0_1_10
output_response_ref: M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_output_response_meta_pack_v1_5_0
updated_at: {NOW}
runtime_claimed: false
capture_law: scan_settle_lock_confirm_reset
artifact_law: handoff_polish_jsonl_authoritative
next_action: Execute S01E01 artifact polish contract freeze
""",
    )

    seasons_bp = [
        {
            "season_id": f"{s['id']}_{s['slug']}",
            "title": s["title"],
            "milestone": s["milestone"],
            "episode_count": 10,
            "focus": s["focus"],
            "superpower_ref": f"superpowers/{sp_name(s)}",
        }
        for s in SEASONS
    ]
    write_json(
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr5_run_artifact_polish.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": "BBWS_SR4_operator_surface_polish",
            "parent_arc_id": "bbws-sr4-complete",
            "baseline_tag": "bbws-pre-sr5-artifact-polish",
            "series_goal": (
                "Polish Best Buds run handoff artifacts (CSV/XLSX/DOCX) and write a "
                "handoff bundle manifest without changing JSONL authority or capture loop."
            ),
            "runtime_claimed": False,
            "version": VERSION,
            "shape": "10 seasons × 10 episodes = 100",
            "capture_law": "scan_settle_lock_confirm_reset",
            "artifact_law": "handoff_polish_jsonl_authoritative",
            "github_push_cadence": "after_series_closeout",
            "seasons": seasons_bp,
            "total_episodes": 100,
            "non_claims": NON_CLAIMS,
            "doctrine_cite": [
                "M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_book_spine_capsule_template_v0_1_10",
                "M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_output_response_meta_pack_v1_5_0",
            ],
        },
    )

    write_json(
        ROOT / "manifests" / f"bbws_sr5_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr5_run_artifact_polish.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR5_RUN_ARTIFACT_POLISH_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR5_resume.v{VERSION}.json",
            "seasons": [
                {
                    "season_id": s["id"],
                    "slug": s["slug"],
                    "milestone": s["milestone"],
                    "title": s["title"],
                    "superpower": f"superpowers/{sp_name(s)}",
                    "episodes": [episode_id(s["id"], i) for i in range(1, 11)],
                }
                for s in SEASONS
            ],
            "non_claims": NON_CLAIMS,
        },
    )

    rows = "\n".join(
        f"| **{s['id']}** | {s['milestone']} | {s['title']} | {s['focus']} | `{sp_name(s)}` |"
        for s in SEASONS
    )
    write_text(
        ROOT / "cursor" / f"BBWS_SR5_RUN_ARTIFACT_POLISH_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR5 — Run Artifact Polish Series Map

**series_id:** `{SERIES_ID}`  
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
{rows}

## Salvage selection map (cite-only)

| Pattern | Salvage source | BBWS target |
|---------|----------------|-------------|
| CSV export blocks | Book Spine `exports/csv` | plants + summary CSV |
| XLSX workbench | Book Spine `exports/xlsx` | Summary/Records/NonClaims sheets |
| Handoff packaging | Book Spine `repo_handoff/` | export naming + non-claims |
| Bundle manifest | Output Response Meta export manifests | `handoff_bundle_manifest.json` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )

    for s in SEASONS:
        write_json(ROOT / "superpowers" / sp_name(s), build_superpower(s))

    write_json(
        ROOT / "context" / "resume_pack" / f"BBWS_SR5_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR5_resume",
            "version": VERSION,
            "series_id": SERIES_ID,
            "updated_at": NOW,
            "active": {
                "season_id": "S01",
                "episode_id": "S01E01",
                "milestone": "M01",
                "status": "ready_to_execute",
            },
            "parent_series": "BBWS_SR4_operator_surface_polish",
            "parent_tag": "bbws-sr4-complete",
            "baseline_tag": "bbws-pre-sr5-artifact-polish",
            "completed_seasons": [],
            "decision_locks": {
                "capture_loop": "scan_settle_lock_confirm_reset",
                "artifact_scope": "handoff_polish_jsonl_authoritative",
                "salvage": "book_spine_output_response_cite_only",
                "push_cadence": "series_closeout",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR5_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR5_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR5 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR5_resume.v{VERSION}.json`
3. `cursor/BBWS_SR5_RUN_ARTIFACT_POLISH_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr5_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: polish CSV/XLSX/DOCX + handoff manifest only; JSONL authoritative; capture loop unchanged; salvage cite-only.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR5 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}

Load `ACTIVE_ARC.yaml` and `BBWS_SR5_resume.v{VERSION}.json`, then execute the pointed episode.
""",
    )

    write_json(
        ROOT / "git_arc" / "active" / "series_pointer.v0.1.0.json",
        {
            "series_id": SERIES_ID,
            "branch_plan": "main",
            "remote_plan": "origin",
            "push_policy": "after_series_closeout",
            "auto_push": False,
            "parent_tag": "bbws-sr4-complete",
            "baseline_tag": "bbws-pre-sr5-artifact-polish",
            "planned_tags": ["bbws-sr5-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "artifact_contract_freeze",
            "milestone": "M01",
            "commit_plan": "Commit S01 scaffold/contract after E10 closeout",
            "push_plan": "git push origin HEAD after series closeout",
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "episode_pointer.v0.1.0.json",
        {
            "episode_id": "S01E01",
            "status": "next",
            "commit_plan": "no mid-episode push",
            "updated_at": NOW,
        },
    )

    write_text(
        ROOT / "context" / "ledger" / "bbws_sr5_ledger.md",
        f"""# BBWS SR5 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | PhaseA/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR5 superpowers, resume pack, git_arc |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR5_ARTIFACTS.md",
        f"""# BBWS SR5 Artifacts

**series_id:** `{SERIES_ID}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR5_RUN_ARTIFACT_POLISH_SERIES_MAP.v{VERSION}.md` |
| Blueprint | `arc_lifecycle/blueprints/series_bbws_sr5_run_artifact_polish.v{VERSION}.json` |
| Resume pack | `context/resume_pack/BBWS_SR5_resume.v{VERSION}.json` |
| Ledger | `context/ledger/bbws_sr5_ledger.md` |
| Selection map | `docs/BBWS_SR5_SELECTION_MAP.md` |
| Operator runbook | `docs/BBWS_SR5_ARTIFACT_POLISH_RUNBOOK.md` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )

    write_text(
        ROOT / "docs" / "BBWS_SR5_SELECTION_MAP.md",
        f"""# BBWS SR5 — Salvage → BBWS Selection Map

**series_id:** `{SERIES_ID}`  
**generated:** {NOW}

Cite-only. Do not import salvage spreadsheet runtimes into Best Buds.

| Pattern | Salvage cue | BBWS surface |
|---------|-------------|--------------|
| CSV export blocks | Book Spine `exports/csv` | `*_plants.csv` + summary CSV via `compile_report` |
| XLSX workbench | Book Spine `exports/xlsx` + excel workbench triplets | Summary / Records / NonClaims sheets |
| Handoff packaging | Book Spine `repo_handoff/` | plain stems, non-claim stamps |
| Bundle / mount manifest | Output Response Meta export manifests | `reports/handoff_bundle_manifest.json` |

**Must not change:** JSONL authority; capture loop; cultivator/strain CSV columns.
""",
    )
    print(f"BBWS_SR5 Phase A scaffold complete series={SERIES_ID}")


if __name__ == "__main__":
    main()
