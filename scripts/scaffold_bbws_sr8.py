"""
Scaffold BBWS_SR8 Scale Face harvest mode series.

Focus: PySide Scale Face UI mode (Harvest/SETUP toggle) on the same
OperatorRuntime/capture law, operator docs/tests, then 2.0.0-rc3 closeout.

Doctrine cite only (do not mutate M: salvage or Arc Launcher):
- Arc Launcher canonical naming / blueprint factory / git mutation boundary
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR8_scale_face_harvest_mode"
PARENT_SERIES = "BBWS_SR7_windows_installer_bringup"
PARENT_TAG = "bbws-sr7-complete"
BASELINE_TAG = "bbws-pre-sr8-scale-face"
PRODUCT_VERSION = "2.0.0-rc3"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

NON_CLAIMS = [
    "Not legal-for-trade / Metrc compliance",
    "Not a remote weighing server or separate Scale Face process",
    "Not collapsing Lock+Confirm in manual mode",
    "JSONL remains authoritative for records",
    "Capture loop unchanged: scan → settle → lock → confirm → reset",
    "Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only",
    "Not claiming small 2–5″ hardware support without a later series",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "scale_face_contract_freeze",
        "title": "Scaffold + Scale Face contract freeze",
        "milestone": "M01",
        "focus": "Freeze: mode not app; Harvest/SETUP toggle; PySide-first; capture law locks",
        "surfaces": ["ACTIVE_ARC.yaml", "cursor/", "scripts/scaffold_bbws_sr8.py", "arc_lifecycle/blueprints/", "reports/"],
        "episodes": [
            ("Intent freeze: Scale Face is a UI mode", "context"),
            ("Inventory Harvest vs SETUP action map", "context"),
            ("Inventory PySide MainWindow refresh/gating", "context"),
            ("Write contract freeze receipt", "implement"),
            ("Authorize S02 mode shell entry", "implement"),
            ("Authorize S03–S06 face surfaces", "implement"),
            ("Authorize S07–S10 verify/docs/rc3", "implement"),
            ("Verify non-claims stamped", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "mode_shell_entry",
        "title": "Scale Face mode shell entry/exit",
        "milestone": "M02",
        "focus": "View → Scale Face (Harvest), shortcut, enter/exit shell; no capture changes",
        "surfaces": [
            "app/best_buds_weight_station/scale_face.py",
            "app/best_buds_weight_station/pyside_frontend.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: shell only", "context"),
            ("Add ScaleFaceWindow shell", "implement"),
            ("Wire View menu + Ctrl+Shift+F", "implement"),
            ("Share OperatorRuntime with MainWindow", "implement"),
            ("Esc / Exit returns to MainWindow", "implement"),
            ("Fullscreen-friendly show path", "implement"),
            ("Keep Tk full UI only (no Scale Face)", "implement"),
            ("Verify entry/exit without capture mutation", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "weight_status_surface",
        "title": "Hero weight + status surface",
        "milestone": "M03",
        "focus": "Hero weight, unit, status pill, locked freeze, Alice one-liner",
        "surfaces": [
            "app/best_buds_weight_station/scale_face.py",
            "app/best_buds_weight_station/operator_surface.py",
            "app/best_buds_weight_station/ui_tokens.py",
        ],
        "episodes": [
            ("Intent freeze: display-only freeze", "context"),
            ("Hero weight via frozen_display_weight", "implement"),
            ("Status pill from capture state", "implement"),
            ("Alice one-liner muted truth class", "implement"),
            ("Run/strain muted header", "implement"),
            ("Reuse ui_tokens colors/pills", "implement"),
            ("Verify lock freezes display", "verify"),
            ("Verify unlock restores live weight", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "harvest_action_bar",
        "title": "HARVEST action bar",
        "milestone": "M04",
        "focus": "ZERO/TARE/LOCK/CONFIRM/CANCEL + compact START/RESUME; existing gating",
        "surfaces": [
            "app/best_buds_weight_station/scale_face.py",
            "app/best_buds_weight_station/operator_surface.py",
            "app/best_buds_weight_station/pyside_frontend.py",
        ],
        "episodes": [
            ("Intent freeze: harvest strip only", "context"),
            ("Add SCALE_FACE_HARVEST_ACTIONS helper", "implement"),
            ("Wire ZERO SET TARE LOCK CONFIRM CANCEL", "implement"),
            ("Compact START/RESUME when needed", "implement"),
            ("Mirror MainWindow button enable rules", "implement"),
            ("Call existing MainWindow methods", "implement"),
            ("Keep ROUTINE_ACTION_LAYOUT at 8", "verify"),
            ("Verify gating matches WEIGHT_STABLE/MANUAL_CONFIRM", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "barcode_recent_strip",
        "title": "Barcode field + recent records strip",
        "milestone": "M05",
        "focus": "Barcode field, SCAN, last 1–3 saved lines",
        "surfaces": [
            "app/best_buds_weight_station/scale_face.py",
            "app/best_buds_weight_station/pyside_frontend.py",
        ],
        "episodes": [
            ("Intent freeze: scan before weigh", "context"),
            ("Barcode field + Enter submit", "implement"),
            ("SCAN opens existing scan dialog", "implement"),
            ("Last 1–3 records strip", "implement"),
            ("Enable barcode only when Ready", "implement"),
            ("Keep plant-log table off the face", "implement"),
            ("Verify SCAN/submit path", "verify"),
            ("Verify recent strip updates after confirm", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "setup_toggle_panel",
        "title": "SETUP toggle panel",
        "milestone": "M06",
        "focus": "SETUP strip: Connect / Zero / Tare / Guided Calibration / Test Scanner",
        "surfaces": [
            "app/best_buds_weight_station/scale_face.py",
            "app/best_buds_weight_station/operator_surface.py",
        ],
        "episodes": [
            ("Intent freeze: toggle swaps bottom row", "context"),
            ("Add SCALE_FACE_SETUP_ACTIONS helper", "implement"),
            ("Harvest/SETUP segment toggle", "implement"),
            ("CONNECT → scale setup", "implement"),
            ("CALIBRATE opens existing guided cal dialog", "implement"),
            ("TEST SCANNER opens existing dialog", "implement"),
            ("Verify no second window for SETUP strip", "verify"),
            ("Verify cal still uses CalibrationDialog", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "authority_contract_tests",
        "title": "Scale Face authority contract tests",
        "milestone": "M07",
        "focus": "Helpers, harvest/setup ids, freeze, routine layout still 8, menu wiring",
        "surfaces": ["tests/test_sr8_scale_face.py", "app/best_buds_weight_station/"],
        "episodes": [
            ("Intent freeze: contract tests only", "context"),
            ("Test harvest/setup action helpers", "implement"),
            ("Test frozen_display_weight still authoritative", "implement"),
            ("Test ROUTINE_ACTION_LAYOUT length 8", "implement"),
            ("Test pyside menu wiring string presence", "implement"),
            ("Avoid GUI smoke flakiness", "implement"),
            ("Verify pytest green for SR8", "verify"),
            ("Verify no capture-law test regressions", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "operator_smoke_docs",
        "title": "Operator smoke docs for Scale Face",
        "milestone": "M08",
        "focus": "Operator onboarding Scale Face section + START_HERE note",
        "surfaces": [
            "docs/OPERATOR_ONBOARDING.md",
            "START_HERE.md",
            "docs/BBWS_SR8_ARTIFACTS.md",
        ],
        "episodes": [
            ("Intent freeze: docs only", "context"),
            ("Add Scale Face section to OPERATOR_ONBOARDING", "implement"),
            ("Brief note in START_HERE", "implement"),
            ("Update BBWS_SR8_ARTIFACTS if needed", "implement"),
            ("Document Harvest/SETUP toggle", "implement"),
            ("Document Esc exit", "implement"),
            ("Verify docs mention Scale Face", "verify"),
            ("Verify non-claims preserved", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "rc3_drift_receipts",
        "title": "Bump to 2.0.0-rc3 + drift receipts",
        "milestone": "M09",
        "focus": "Version surfaces, drift concordance rc3, manifest, pytest",
        "surfaces": [
            "VERSION",
            "app/best_buds_weight_station/version.py",
            "pyproject.toml",
            "packaging/windows/BestBudsWeightStation.iss",
            "scripts/validate_drift_concordance_v200_rc3.py",
            "reports/",
            "manifests/",
        ],
        "episodes": [
            ("Intent freeze: 2.0.0-rc3", "context"),
            ("Bump version surfaces", "implement"),
            ("Add v200_rc3 drift script from rc2", "implement"),
            ("Update CHANGELOG and RC docs", "implement"),
            ("Regenerate file manifest", "implement"),
            ("Run drift concordance", "verify"),
            ("Run pytest", "verify"),
            ("Leave archival rc2 receipts untouched", "implement"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "series_closeout",
        "title": "SR8 series closeout + tags",
        "milestone": "M10",
        "focus": "ACTIVE_ARC series_complete, resume/ledger, tag v2.0.0-rc3 + bbws-sr8-complete, push",
        "surfaces": ["ACTIVE_ARC.yaml", "context/", "git_arc/", "reports/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Mark ACTIVE_ARC series_complete", "implement"),
            ("Update resume pack + ledger", "implement"),
            ("Tag v2.0.0-rc3", "implement"),
            ("Tag bbws-sr8-complete", "implement"),
            ("Commit closeout artifacts", "implement"),
            ("Push origin main --tags", "implement"),
            ("Verify remote tags", "verify"),
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
    return f"sr8_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "capture workflow / state machine law mutation",
                    "JSONL authority changes",
                    "claim legal-for-trade or Metrc",
                    "mutate M: salvage or Arc Launcher",
                    "auto-push mid-episode",
                    "remote/LAN weighing server",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr8.{season['slug']}.v1",
        "arc_id": f"SR8_{season['id']}_{season['slug']}",
        "series_id": SERIES_ID,
        "title": season["title"],
        "milestone": season["milestone"],
        "focus": season["focus"],
        "runtime_claimed": False,
        "product_version_target": PRODUCT_VERSION,
        "primary_surfaces": season["surfaces"],
        "episodes": episodes,
        "non_claims": NON_CLAIMS,
        "doctrine_cite": [
            "C:/aos_arc_launcher_v0_4_21/docs/CANONICAL_ARC_NAMING_MODEL.md",
            "C:/aos_arc_launcher_v0_4_21/docs/GIT_MUTATION_BOUNDARY.md",
        ],
    }


def main() -> None:
    write_text(
        ROOT / "ACTIVE_ARC.yaml",
        f"""# BBWS SR8 live pointer — product owns truth (salvage cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: scale_face_contract_freeze
episode_id: S01E01
milestone: M01
status: active
parent_series_id: {PARENT_SERIES}
parent_tag: {PARENT_TAG}
baseline_tag: {BASELINE_TAG}
product_version_target: {PRODUCT_VERSION}
doctrine_source: C:/aos_arc_launcher_v0_4_21
updated_at: {NOW}
runtime_claimed: false
capture_law: scan_settle_lock_confirm_reset
next_action: Execute S01E01 Scale Face contract freeze
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
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr8_scale_face_harvest_mode.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": PARENT_SERIES,
            "parent_arc_id": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "series_goal": (
                "Add a PySide Scale Face harvest mode (Harvest/SETUP toggle) sharing "
                "OperatorRuntime and capture law, with contract tests, operator docs, "
                f"and product version {PRODUCT_VERSION} closeout."
            ),
            "runtime_claimed": False,
            "version": VERSION,
            "shape": "10 seasons × 10 episodes = 100",
            "github_push_cadence": "after_series_closeout",
            "seasons": seasons_bp,
            "total_episodes": 100,
            "non_claims": NON_CLAIMS,
        },
    )

    write_json(
        ROOT / "manifests" / f"bbws_sr8_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr8_scale_face_harvest_mode.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR8_SCALE_FACE_HARVEST_MODE_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR8_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR8_SCALE_FACE_HARVEST_MODE_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR8 — Scale Face Harvest Mode Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `{PARENT_SERIES}` / `{PARENT_TAG}`  
**baseline:** `{BASELINE_TAG}`  
**product version target:** `{PRODUCT_VERSION}`

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR8_resume*.json
→ cursor/BBWS_SR8_*_SERIES_MAP*.md
→ superpowers/sr8_sNN_*.json
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
        ROOT / "context" / "resume_pack" / f"BBWS_SR8_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR8_resume",
            "version": VERSION,
            "series_id": SERIES_ID,
            "updated_at": NOW,
            "active": {
                "season_id": "S01",
                "episode_id": "S01E01",
                "milestone": "M01",
                "status": "ready_to_execute",
            },
            "parent_series": PARENT_SERIES,
            "parent_tag": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "completed_seasons": [],
            "decision_locks": {
                "capture_loop": "scan_settle_lock_confirm_reset",
                "product_version": PRODUCT_VERSION,
                "scale_face": "pyside_mode_harvest_setup_toggle",
                "routine_layout": "full_ui_eight_actions_unchanged",
                "push_cadence": "series_closeout",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR8_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR8_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR8 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}` toward `{PRODUCT_VERSION}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR8_resume.v{VERSION}.json`
3. `cursor/BBWS_SR8_SCALE_FACE_HARVEST_MODE_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr8_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: Scale Face UI mode only; capture law/JSONL/Alice unchanged; ROUTINE_ACTION_LAYOUT stays 8; salvage cite-only.
Stay on `2.0.0-rc2` until S09 bumps to `{PRODUCT_VERSION}`.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR8 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}  
**Product target:** {PRODUCT_VERSION}

Load `ACTIVE_ARC.yaml` and `BBWS_SR8_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "parent_tag": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "planned_tags": ["v2.0.0-rc3", "bbws-sr8-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "scale_face_contract_freeze",
            "milestone": "M01",
            "commit_plan": "Commit S01 scaffold after E10 closeout",
            "push_plan": "git push origin HEAD --tags after series closeout",
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
        ROOT / "context" / "ledger" / "bbws_sr8_ledger.md",
        f"""# BBWS SR8 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | Phase0/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR8 superpowers, resume pack |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR8_ARTIFACTS.md",
        f"""# BBWS SR8 Artifacts

**series_id:** `{SERIES_ID}`  
**product_version_target:** `{PRODUCT_VERSION}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR8_SCALE_FACE_HARVEST_MODE_SERIES_MAP.v{VERSION}.md` |
| Resume pack | `context/resume_pack/BBWS_SR8_resume.v{VERSION}.json` |
| Scale Face UI | `app/best_buds_weight_station/scale_face.py` |
| Action helpers | `app/best_buds_weight_station/operator_surface.py` (`SCALE_FACE_*_ACTIONS`) |
| Menu wiring | `app/best_buds_weight_station/pyside_frontend.py` |
| Contract tests | `tests/test_sr8_scale_face.py` |
| Drift concordance | `scripts/validate_drift_concordance_v200_rc3.py` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )
    print(f"BBWS_SR8 scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
