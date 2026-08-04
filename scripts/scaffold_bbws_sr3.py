"""
Scaffold BBWS_SR3 station capture UX 100-arc series (Phase A).

Generates ACTIVE_ARC, blueprint, series map, SR3 superpowers, resume pack,
git_arc pointers, and kickoff. Does not implement product features.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR3_station_capture_ux"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

NON_CLAIMS = [
    "Lock weight is not a legal-for-trade hold decision",
    "Plant log is not a Metrc plant list",
    "Scan button is HID focus only — not BLE/SPP scanner protocol",
    "Arc Launcher is cited doctrine, not mutated as live Best Buds runtime",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "ux_contract_freeze",
        "title": "Scaffold + UX contract freeze",
        "milestone": "M01",
        "focus": "Freeze capture loop contract and non-claims",
        "surfaces": ["ACTIVE_ARC.yaml", "cursor/", "docs/"],
        "episodes": [
            ("Intent freeze: scan lock confirm loop", "context"),
            ("Inventory PySide capture surfaces", "context"),
            ("Inventory Tk capture surfaces", "context"),
            ("Write UX contract receipt", "implement"),
            ("Authorize S02 barcode/scan scope", "implement"),
            ("Authorize S03–S04 lock-weight scope", "implement"),
            ("Authorize S05 plant-log scope", "implement"),
            ("Verify non-claims stamped", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "active_barcode_scan",
        "title": "Active barcode stay + Scan button",
        "milestone": "M02",
        "focus": "Keep scanned tag visible; Scan focuses field",
        "surfaces": ["pyside_frontend.py"],
        "episodes": [
            ("Intent freeze: barcode persistence", "context"),
            ("Keep barcode after accept", "implement"),
            ("Clear barcode on confirm/cancel only", "implement"),
            ("Main-row Scan focuses barcode", "implement"),
            ("Test Scanner menu-only", "implement"),
            ("Active barcode banner copy", "implement"),
            ("Scan focus verify", "verify"),
            ("Clear-on-confirm verify", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "lock_weight_runtime",
        "title": "Lock weight state machine + action",
        "milestone": "M03",
        "focus": "WEIGHT_STABLE until capture.weight.lock",
        "surfaces": ["state_machine.py", "application_controller.py", "actions.py", "operator_runtime.py"],
        "episodes": [
            ("Intent freeze: lock before confirm", "context"),
            ("Manual stable stops at WEIGHT_STABLE", "implement"),
            ("Add capture.weight.lock action", "implement"),
            ("Wire controller + runtime lock", "implement"),
            ("Cancel from WEIGHT_STABLE", "implement"),
            ("Alice authority copy for lock", "implement"),
            ("Lock gate unit verify", "verify"),
            ("Auto mode unchanged verify", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "lock_weight_pyside",
        "title": "Lock weight PySide UI",
        "milestone": "M04",
        "focus": "Lock button + locked readout + Confirm gate",
        "surfaces": ["pyside_frontend.py", "operator_surface.py"],
        "episodes": [
            ("Intent freeze: Lock then Confirm", "context"),
            ("Add Lock weight action button", "implement"),
            ("Enable Lock only in WEIGHT_STABLE", "implement"),
            ("Confirm only in MANUAL_CONFIRM", "implement"),
            ("Show locked weight display unit", "implement"),
            ("Clear lock UI after confirm", "implement"),
            ("Button enable matrix verify", "verify"),
            ("Cancel clears lock UI verify", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "plant_run_log",
        "title": "Run plant log PySide",
        "milestone": "M05",
        "focus": "Last 50 commits read-only list",
        "surfaces": ["pyside_frontend.py", "operator_runtime.py"],
        "episodes": [
            ("Intent freeze: log is not Metrc", "context"),
            ("Snapshot recent_plants helper", "implement"),
            ("PySide plant log widget", "implement"),
            ("Refresh log on timer", "implement"),
            ("Show barcode time net strain flags", "implement"),
            ("Empty-run log copy", "implement"),
            ("Log refresh verify", "verify"),
            ("Cap 50 verify", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "tk_capture_parity",
        "title": "Tk parity for capture UX loop",
        "milestone": "M06",
        "focus": "Barcode stay, Scan, Lock, short log in Tk",
        "surfaces": ["production_ui.py"],
        "episodes": [
            ("Intent freeze: Tk shared runtime", "context"),
            ("Tk barcode persistence", "implement"),
            ("Tk Scan focus button", "implement"),
            ("Tk Lock weight button", "implement"),
            ("Tk recent plants list", "implement"),
            ("Tk confirm/cancel clear", "implement"),
            ("Tk loop verify", "verify"),
            ("Non-claim stamp", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "snapshot_fields",
        "title": "Snapshot fields for capture UX",
        "milestone": "M07",
        "focus": "active_barcode, locked_weight_g, recent_plants",
        "surfaces": ["operator_runtime.py", "application_controller.py"],
        "episodes": [
            ("Intent freeze: snapshot contract", "context"),
            ("Expose active_barcode", "implement"),
            ("Expose locked_weight_g", "implement"),
            ("Expose recent_plants", "implement"),
            ("Bind PySide refresh", "implement"),
            ("Bind Tk refresh", "implement"),
            ("Snapshot keys verify", "verify"),
            ("No-run empty defaults verify", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "capture_ux_tests",
        "title": "Tests for lock gate and plant log",
        "milestone": "M08",
        "focus": "State lock, barcode persistence, recent list",
        "surfaces": ["tests/"],
        "episodes": [
            ("Intent freeze: test matrix", "context"),
            ("Lock before confirm test", "implement"),
            ("Auto mode still auto-records", "implement"),
            ("Recent plants snapshot test", "implement"),
            ("Cancel from WEIGHT_STABLE test", "implement"),
            ("Light UI contract notes", "implement"),
            ("Pytest green verify", "verify"),
            ("Regression smoke verify", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "docs_nonclaims",
        "title": "Runbook + dual-UI note + non-claims",
        "milestone": "M09",
        "focus": "Operator docs for new loop",
        "surfaces": ["docs/"],
        "episodes": [
            ("Intent freeze: docs only", "context"),
            ("OPERATOR_RUNBOOK lock loop", "implement"),
            ("BBWS_SR3_ARTIFACTS index", "implement"),
            ("Dual-UI note update", "implement"),
            ("Non-claims page stamp", "implement"),
            ("Calibration unrelated note", "implement"),
            ("Docs consistency verify", "verify"),
            ("No Metrc claim verify", "verify"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "series_closeout",
        "title": "Series closeout + bbws-sr3-complete",
        "milestone": "M10",
        "focus": "ACTIVE_ARC series_complete + tag + push",
        "surfaces": ["ACTIVE_ARC.yaml", "reports/", "git_arc/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Season ledger complete", "implement"),
            ("Closeout report", "implement"),
            ("ACTIVE_ARC series_complete", "implement"),
            ("Tag bbws-sr3-complete", "implement"),
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
    return f"sr3_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "run artifact polish SR4",
                    "firmware SET_UNIT kg/lb",
                    "BLE/SPP scanner",
                    "Metrc sync",
                    "Arc Launcher / M: mutation",
                    "auto-push mid-episode",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr3.{season['slug']}.v1",
        "arc_id": f"SR3_{season['id']}_{season['slug']}",
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
    write_text(
        ROOT / "ACTIVE_ARC.yaml",
        f"""# BBWS SR3 live pointer — product owns truth (Arc Launcher cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: ux_contract_freeze
episode_id: S01E01
milestone: M01
status: active
parent_series_id: BBWS_SR2_tk_linux_display_units
parent_tag: bbws-sr2-complete
baseline_freeze: v0.1.9-rc2
doctrine_source: C:/aos_arc_launcher_v0_4_21
updated_at: {NOW}
runtime_claimed: false
capture_law: scan_settle_lock_confirm_reset
next_action: Execute S01E01 UX contract freeze
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
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr3_station_capture_ux.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": "BBWS_SR2_tk_linux_display_units",
            "parent_arc_id": "bbws-sr2-complete",
            "series_goal": (
                "Harvest station capture UX: keep scanned barcode visible, Scan focus, "
                "Lock weight then Confirm, run plant log; Tk parity; grams still authoritative."
            ),
            "runtime_claimed": False,
            "version": VERSION,
            "shape": "10 seasons × 10 episodes = 100",
            "capture_law": "scan_settle_lock_confirm_reset",
            "github_push_cadence": "after_series_closeout",
            "seasons": seasons_bp,
            "total_episodes": 100,
            "non_claims": NON_CLAIMS,
        },
    )

    write_json(
        ROOT / "manifests" / f"bbws_sr3_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr3_station_capture_ux.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR3_STATION_CAPTURE_UX_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR3_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR3_STATION_CAPTURE_UX_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR3 — Station Capture UX Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR2_tk_linux_display_units` / `bbws-sr2-complete`  
**capture law:** scan → settle → lock → confirm → reset

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR3_resume*.json
→ cursor/BBWS_SR3_*_SERIES_MAP*.md
→ superpowers/sr3_sNN_*.json (current season)
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
{rows}

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )

    for s in SEASONS:
        write_json(ROOT / "superpowers" / sp_name(s), build_superpower(s))

    write_json(
        ROOT / "context" / "resume_pack" / f"BBWS_SR3_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR3_resume",
            "version": VERSION,
            "series_id": SERIES_ID,
            "updated_at": NOW,
            "active": {
                "season_id": "S01",
                "episode_id": "S01E01",
                "milestone": "M01",
                "status": "ready_to_execute",
            },
            "parent_series": "BBWS_SR2_tk_linux_display_units",
            "completed_seasons": [],
            "decision_locks": {
                "capture_loop": "scan_settle_lock_confirm_reset",
                "plant_log": "read_only_last_50_from_jsonl",
                "scan_button": "focus_barcode_hid_wedge",
                "push_cadence": "series_closeout",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR3_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR3_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR3 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR3_resume.v{VERSION}.json`
3. `cursor/BBWS_SR3_STATION_CAPTURE_UX_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr3_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: scan→settle→lock→confirm→reset; plant log read-only; HID Scan focus only; no SR4 artifact polish in this series.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR3 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}

Load `ACTIVE_ARC.yaml` and `BBWS_SR3_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "parent_tag": "bbws-sr2-complete",
            "planned_tags": ["bbws-sr3-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "ux_contract_freeze",
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
        ROOT / "context" / "ledger" / "bbws_sr3_ledger.md",
        f"""# BBWS SR3 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | PhaseA | Scaffold ACTIVE_ARC, blueprint, maps, SR3 superpowers, resume pack, git_arc |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR3_ARTIFACTS.md",
        f"""# BBWS SR3 Artifacts

**series_id:** `{SERIES_ID}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR3_STATION_CAPTURE_UX_SERIES_MAP.v{VERSION}.md` |
| Blueprint | `arc_lifecycle/blueprints/series_bbws_sr3_station_capture_ux.v{VERSION}.json` |
| Resume pack | `context/resume_pack/BBWS_SR3_resume.v{VERSION}.json` |
| Ledger | `context/ledger/bbws_sr3_ledger.md` |

Follow-on (not this series): BBWS SR4 run artifact polish.
""",
    )
    print(f"BBWS_SR3 Phase A scaffold complete series={SERIES_ID}")


if __name__ == "__main__":
    main()
