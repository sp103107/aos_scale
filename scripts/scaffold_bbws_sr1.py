"""
Scaffold BBWS_SR1 harvest-operator 100-arc series artifacts (Phase A).

Generates ACTIVE_ARC, series blueprint, series map, S01–S10 superpowers,
resume pack, git_arc pointers, and kickoff prompt. Product feature code
is out of scope for this script.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR1_harvest_operator_loop"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SEASONS = [
    {
        "id": "S01",
        "slug": "recording_polish",
        "title": "Harvest recording polish",
        "milestone": "M01",
        "focus": "Confirm/Cancel pacing, saved copy, duplicate/blocked UX",
        "surfaces": ["pyside_frontend.py", "operator_runtime.py", "state_machine.py"],
        "episodes": [
            ("Intent freeze: recording polish goals", "context"),
            ("Confirm/Cancel pacing audit", "implement"),
            ("Saved-record Alice copy", "implement"),
            ("Duplicate / blocked capture UX", "implement"),
            ("Pending confirmation state clarity", "implement"),
            ("Keyboard/focus after save", "implement"),
            ("Regression: manual capture path", "verify"),
            ("Regression: auto capture path", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "hid_scanner",
        "title": "HID scanner integration",
        "milestone": "M02",
        "focus": "Focus ownership, Test Scanner receipts, require-barcode policy",
        "surfaces": ["pyside_frontend.py", "settings.py"],
        "episodes": [
            ("Intent freeze: HID wedge only", "context"),
            ("Focus ownership for plant ID field", "implement"),
            ("Test Scanner receipt path", "implement"),
            ("barcode_required_for_capture soft policy", "implement"),
            ("Scanner blocked / empty scan UX", "implement"),
            ("Settings surface for barcode policy", "implement"),
            ("HID regression without BLE/SPP", "verify"),
            ("Manual plant ID still allowed when policy off", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "sticky_strain",
        "title": "Sticky strain for scan groups",
        "milestone": "M03",
        "focus": "Active strain UI; mid-run change; CSV cultivar stamps",
        "surfaces": ["pyside_frontend.py", "run_manager.py", "storage.py", "spreadsheet.py"],
        "episodes": [
            ("Intent freeze: sticky until changed", "context"),
            ("Active strain model on run context", "implement"),
            ("Main-surface active strain display", "implement"),
            ("Mid-run change strain control", "implement"),
            ("Stamp cultivar on each capture", "implement"),
            ("CSV cultivar column truth", "implement"),
            ("Strain group continuity verify", "verify"),
            ("Mid-run change splits groups correctly", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "csv_recording_truth",
        "title": "CSV recording truth",
        "milestone": "M04",
        "focus": "Row proof, rebuild-from-JSONL, pending_sync UX",
        "surfaces": ["spreadsheet.py", "storage.py"],
        "episodes": [
            ("Intent freeze: JSONL authoritative", "context"),
            ("CSV row field proof matrix", "implement"),
            ("Rebuild CSV from session JSONL", "implement"),
            ("pending_sync operator UX", "implement"),
            ("Append vs rebuild safety", "implement"),
            ("Cultivar + barcode columns locked", "implement"),
            ("Rebuild smoke on fixture session", "verify"),
            ("Corrupt/missing CSV recovery path", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "export_quality",
        "title": "Export quality",
        "milestone": "M05",
        "focus": "Full-plant CSV handoff, DOCX/XLSX polish, plain filenames",
        "surfaces": ["reports.py", "pyside_frontend.py"],
        "episodes": [
            ("Intent freeze: export handoff quality", "context"),
            ("Plain export filenames", "implement"),
            ("Full-plant CSV export completeness", "implement"),
            ("XLSX polish", "implement"),
            ("DOCX polish", "implement"),
            ("Export UI status copy", "implement"),
            ("Export smoke fixtures", "verify"),
            ("Filename safety on Windows", "verify"),
            ("S05 receipt pack + M05 tag plan", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "export_reconcile_gates",
        "title": "Export ↔ JSONL reconcile gates",
        "milestone": "M06",
        "focus": "Counts, cultivar totals, SHA receipts",
        "surfaces": ["reports.py", "scripts/", "tests/"],
        "episodes": [
            ("Intent freeze: reconcile gates", "context"),
            ("Count gate JSONL vs CSV", "implement"),
            ("Cultivar total gate", "implement"),
            ("SHA receipt for export bundle", "implement"),
            ("CLI/script reconcile entry", "implement"),
            ("UI surface for reconcile fail", "implement"),
            ("Passing fixture gate", "verify"),
            ("Intentional mismatch fail gate", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "field_e2e",
        "title": "Physical field E2E",
        "milestone": "M07",
        "focus": "scan→weigh→record→CSV evidence receipts; metrology non-claim",
        "surfaces": ["docs/", "reports/"],
        "episodes": [
            ("Intent freeze: field E2E runbook", "context"),
            ("Field runbook document", "implement"),
            ("Evidence receipt schema", "implement"),
            ("Simulated field path with simulator", "implement"),
            ("CSV proof after simulated harvest", "implement"),
            ("Non-claims stamp on field receipts", "implement"),
            ("Simulator E2E verify", "verify"),
            ("Operator checklist verify", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "crash_resume",
        "title": "Crash/resume operator polish",
        "milestone": "M08",
        "focus": "Storage recovery UX after interrupt",
        "surfaces": ["storage.py", "pyside_frontend.py", "settings.py"],
        "episodes": [
            ("Intent freeze: crash/resume polish", "context"),
            ("Recent-run resume messaging", "implement"),
            ("Partial JSONL recovery UX", "implement"),
            ("pending_sync after crash", "implement"),
            ("CSV rebuild after resume", "implement"),
            ("Alice guidance on resume", "implement"),
            ("Crash fixture verify", "verify"),
            ("Clean resume verify", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "governance_light",
        "title": "Light governance",
        "milestone": "M09",
        "focus": "Void/note, cal id on record, operator id clarity",
        "surfaces": ["models.py", "storage.py", "pyside_frontend.py"],
        "episodes": [
            ("Intent freeze: light governance", "context"),
            ("Operator id clarity on records", "implement"),
            ("Calibration id stamp on capture", "implement"),
            ("Void/note field support", "implement"),
            ("UI for note/void soft path", "implement"),
            ("CSV columns for governance fields", "implement"),
            ("Governance field verify", "verify"),
            ("Non-claim: not Metrc compliance", "verify"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "package_smoke_closeout",
        "title": "Windows package smoke + series closeout",
        "milestone": "M10",
        "focus": "Packaging smoke + series closeout + GitHub prerelease tag",
        "surfaces": ["packaging/", "docs/", "VERSION"],
        "episodes": [
            ("Intent freeze: package smoke + series end", "context"),
            ("Package entry smoke checklist", "implement"),
            ("VERSION / tag policy lock", "implement"),
            ("Installer smoke notes", "implement"),
            ("Series non-claims final stamp", "implement"),
            ("Resume pack series-complete", "implement"),
            ("Smoke verify (dev entry)", "verify"),
            ("Series map complete stamp", "verify"),
            ("S10 receipt pack", "receipt"),
            ("M10 series closeout + tag plan", "closeout"),
        ],
    },
]

NON_CLAIMS = [
    "Not legal-for-trade / metrology certification",
    "Sticky strain UX ≠ Metrc compliance",
    "HID wedge ≠ BLE/SPP barcode protocol",
    "Season push ≠ release seal / Authenticode",
    "Arc Launcher not claimed as live runtime for Best Buds",
]


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def episode_id(season_id: str, n: int) -> str:
    return f"{season_id}E{n:02d}"


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
                    "BLE/SPP/camera scanner activation",
                    "metrology certification claims",
                    "Arc Launcher M: drive mutation",
                    "auto-push mid-episode",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.{season['slug']}.v1",
        "arc_id": f"{season['id']}_{season['slug']}",
        "series_id": SERIES_ID,
        "title": season["title"],
        "milestone": season["milestone"],
        "focus": season["focus"],
        "runtime_claimed": False,
        "primary_surfaces": season["surfaces"],
        "episodes": episodes,
        "non_claims": NON_CLAIMS,
    }


def main() -> None:
    # ACTIVE_ARC
    write_text(
        ROOT / "ACTIVE_ARC.yaml",
        f"""# BBWS SR1 live pointer — product owns truth (Arc Launcher cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: recording_polish
episode_id: S01E01
milestone: M01
status: active
baseline_freeze: v0.1.9-rc2
prequel_arc: context/operator_ux_arc  # BBWS-CALUX — not renumbered into SR1
doctrine_source: C:/aos_arc_launcher_v0_4_21  # read-only
updated_at: {NOW}
runtime_claimed: false
next_action: Execute S01E01 recording-polish context freeze
""",
    )

    # Series blueprint
    seasons_bp = []
    for s in SEASONS:
        seasons_bp.append(
            {
                "season_id": f"{s['id']}_{s['slug']}",
                "title": s["title"],
                "milestone": s["milestone"],
                "episode_count": 10,
                "focus": s["focus"],
                "superpower_ref": f"superpowers/{s['id'].lower()}_{s['slug']}.v{VERSION}.json",
            }
        )
    write_json(
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr1_harvest_operator_loop.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": "BBWS_CALUX_operator_ux",
            "parent_arc_id": "context/operator_ux_arc",
            "series_goal": (
                "Harvest-operator loop after v0.1.9-rc2 freeze: recording polish → HID scanner → "
                "sticky strain → CSV/export truth → field/governance/package closeout."
            ),
            "runtime_claimed": False,
            "version": VERSION,
            "shape": "10 seasons × 10 episodes = 100",
            "baseline_freeze": "v0.1.9-rc2",
            "strain_default": "sticky_until_changed",
            "scanner_policy": "hid_keyboard_wedge_only",
            "csv_law": "session_jsonl_authoritative",
            "github_push_cadence": "after_each_season_closeout",
            "seasons": seasons_bp,
            "total_episodes": 100,
            "non_claims": NON_CLAIMS,
        },
    )

    # Manifest series map
    write_json(
        ROOT / "manifests" / f"bbws_sr1_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr1_harvest_operator_loop.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR1_HARVEST_OPERATOR_LOOP_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR1_resume.v{VERSION}.json",
            "seasons": [
                {
                    "season_id": s["id"],
                    "slug": s["slug"],
                    "milestone": s["milestone"],
                    "title": s["title"],
                    "superpower": f"superpowers/{s['id'].lower()}_{s['slug']}.v{VERSION}.json",
                    "episodes": [episode_id(s["id"], i) for i in range(1, 11)],
                }
                for s in SEASONS
            ],
            "non_claims": NON_CLAIMS,
        },
    )

    # Cursor series map markdown
    rows = "\n".join(
        f"| **{s['id']}** | {s['milestone']} | {s['title']} | {s['focus']} | `{s['id'].lower()}_{s['slug']}.v{VERSION}.json` |"
        for s in SEASONS
    )
    write_text(
        ROOT / "cursor" / f"BBWS_SR1_HARVEST_OPERATOR_LOOP_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR1 — Harvest Operator Loop Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 seasons × 10 episodes = 100  
**baseline:** GitHub `aos_scale` `v0.1.9-rc2` + `context/operator_ux_arc` (BBWS-CALUX prequel)  
**doctrine:** Arc Launcher at `C:\\aos_arc_launcher_v0_4_21` (read-only cite)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR1_resume*.json
→ cursor/BBWS_SR1_*_SERIES_MAP*.md
→ superpowers/sNN_*.json (current season)
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
{rows}

## Decision locks

- Sticky strain until changed (per-scan override is later)
- HID keyboard-wedge only (no BLE/SPP/camera)
- Session JSONL authoritative; CSV/XLSX/DOCX are derivatives
- Push after each season closeout (E10); no auto-push mid-episode
- Tag prereleases at M05 and series end at minimum

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}

## Episode rhythm (every season)

E01 intent/context → E02–E08 implement/verify → E09 receipt → **E10 closeout + save/push plan**
""",
    )

    # Superpowers
    for s in SEASONS:
        write_json(
            ROOT / "superpowers" / f"{s['id'].lower()}_{s['slug']}.v{VERSION}.json",
            build_superpower(s),
        )

    # Resume pack
    write_json(
        ROOT / "context" / "resume_pack" / f"BBWS_SR1_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR1_resume",
            "version": VERSION,
            "series_id": SERIES_ID,
            "updated_at": NOW,
            "active": {
                "season_id": "S01",
                "episode_id": "S01E01",
                "milestone": "M01",
                "status": "ready_to_execute",
            },
            "baseline_freeze": "v0.1.9-rc2",
            "prequel": "context/operator_ux_arc",
            "load_order": [
                "ACTIVE_ARC.yaml",
                f"context/resume_pack/BBWS_SR1_resume.v{VERSION}.json",
                f"cursor/BBWS_SR1_HARVEST_OPERATOR_LOOP_SERIES_MAP.v{VERSION}.md",
                f"superpowers/s01_recording_polish.v{VERSION}.json",
                "next episode S01E01",
            ],
            "completed_seasons": [],
            "decision_locks": {
                "strain_default": "sticky_until_changed",
                "scanner": "hid_keyboard_wedge_only",
                "csv_law": "session_jsonl_authoritative",
                "push_cadence": "season_closeout_only",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR1_HUMAN_CHAT_KICKOFF.md",
        },
    )

    # Kickoff
    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR1_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR1 — Human Chat Kickoff

You are continuing **Best Buds Weight Station** series `{SERIES_ID}`.

## Load first

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR1_resume.v{VERSION}.json`
3. `cursor/BBWS_SR1_HARVEST_OPERATOR_LOOP_SERIES_MAP.v{VERSION}.md`
4. Current season `superpowers/sNN_*.json`
5. Execute the next `SnnEkk` only

## Locks

- Baseline freeze: `v0.1.9-rc2` — do not re-litigate connect/calibrate soft-path
- Sticky strain until changed
- HID scanner only
- JSONL authoritative
- Product owns truth in this repo; Arc Launcher is cite-only
- Push after season E10 closeout only

## Start

Read `ACTIVE_ARC.yaml`. If episode is `S01E01`, freeze recording-polish intent, then implement outward through S01E10.
""",
    )

    # git_arc pointers (plans only — no auto-push)
    write_json(
        ROOT / "git_arc" / "active" / "series_pointer.v0.1.0.json",
        {
            "series_id": SERIES_ID,
            "branch_plan": "main",
            "remote_plan": "origin",
            "push_policy": "after_season_closeout_only",
            "auto_push": False,
            "baseline_tag": "v0.1.9-rc2",
            "planned_tags": [
                "v0.1.9-bbws-s05",
                "v0.1.9-bbws-s07",
                "bbws-sr1-complete",
            ],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "recording_polish",
            "milestone": "M01",
            "commit_plan": "Commit S01 recording polish slice after E10 closeout",
            "push_plan": "git push origin HEAD after season closeout receipt",
            "tag_plan": None,
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "episode_pointer.v0.1.0.json",
        {
            "episode_id": "S01E01",
            "status": "next",
            "commit_plan": "episode checkpoints are local context only; no mid-episode push",
            "updated_at": NOW,
        },
    )

    # Continuation handoff stub
    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR1 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}

Load `ACTIVE_ARC.yaml` and `BBWS_SR1_resume.v{VERSION}.json`, then execute the pointed episode.
Do not mutate Arc Launcher. Do not auto-push mid-episode.
""",
    )

    # Ledger line
    ledger = ROOT / "context" / "ledger" / "bbws_sr1_ledger.md"
    write_text(
        ledger,
        f"""# BBWS SR1 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | PhaseA | Scaffold ACTIVE_ARC, blueprint, maps, S01–S10 superpowers, resume pack, git_arc |
""",
    )

    print("BBWS_SR1 Phase A scaffold complete")
    print(f"  series={SERIES_ID}")
    print(f"  seasons={len(SEASONS)} episodes={sum(10 for _ in SEASONS)}")


if __name__ == "__main__":
    main()
