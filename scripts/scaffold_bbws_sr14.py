"""
Scaffold BBWS_SR14 Auto-Record After Lock series.

Focus: setting that records when Lock hits (Confirm skipped), then an audible
beep on successful save. Existing automatic (stable→commit) stays unchanged.

Doctrine cite only: C:/aos_arc_launcher_v0_4_21
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR14_auto_record_after_lock"
PARENT_SERIES = "BBWS_SR13_duplicate_barcode_pre_gate"
PARENT_TAG = "bbws-sr13-complete"
BASELINE_TAG = "bbws-pre-sr14-auto-lock"
PRODUCT_VERSION = "2.0.0-rc9"
PRODUCT_DURING = "2.0.0-rc8"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
SLUG = "auto_record_after_lock"
SR = "sr14"
SRU = "SR14"
MAP_TITLE = "Auto-Record After Lock"
SERIES_GOAL = "Add auto_record_after_lock (default off) so Lock records immediately, plus an operator beep on save."
KICKOFF_LINE = "Continue series toward auto-record after Lock + beep. Duplicate pre-gate already shipped."
CONTRACT = {"auto_record_after_lock": True, "beep_on_save": True, "automatic_mode_unchanged": True}

NON_CLAIMS = [
    "Not legal-for-trade / Metrc compliance",
    "JSONL remains authoritative for weight records",
    "Capture loop remains scan → settle → lock → confirm → reset; Confirm is automatic when the setting is on",
    "Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only",
    "Not a remote weighing server",
    "Audible beep is an operator cue, not certification",
    "Existing automatic mode (record on stable) is unchanged",
    "Duplicate pre-gate from SR13 still warns before any auto-record",
]

SEASONS = [
    ("S01", "scaffold_and_contract_freeze", "Scaffold + contract freeze", "M01",
     "Freeze SR14 contract; baseline tag; Arc artifacts",
     ["ACTIVE_ARC.yaml", "cursor/", "scripts/scaffold_bbws_sr14.py", "reports/"]),
    ("S02", "settings_auto_record_after_lock", "Settings bool", "M02",
     "AppSettings.auto_record_after_lock default false + persist",
     ["app/best_buds_weight_station/settings.py", "app/best_buds_weight_station/actions.py"]),
    ("S03", "lock_commits_when_enabled", "Lock commits when enabled", "M03",
     "capture.weight.lock calls confirm when the setting is on",
     ["app/best_buds_weight_station/application_controller.py"]),
    ("S04", "station_settings_toggle", "Station Settings toggle", "M04",
     "Station Settings + lock UI handles saved record",
     ["app/best_buds_weight_station/pyside_frontend.py", "app/best_buds_weight_station/production_ui.py"]),
    ("S05", "operator_beep", "Operator beep", "M05",
     "Windows MessageBeep on terminal success/warning/error; silent in pytest",
     ["app/best_buds_weight_station/operator_beep.py", "app/best_buds_weight_station/application_controller.py"]),
    ("S06", "scripted_auto_lock_tests", "Scripted auto-lock tests", "M06",
     "Lock commits when on; Confirm still required when off; dup gate holds",
     ["tests/", "reports/"]),
    ("S07", "docs_auto_lock", "Docs + auto-lock", "M07",
     "Operator docs: Station Settings auto-record after Lock",
     ["docs/", "docs/OPERATOR_ONBOARDING.md", "docs/BBWS_SR14_ARTIFACTS.md"]),
    ("S08", "no_unrelated_churn", "No unrelated churn", "M08",
     "This bump is auto-record + beep only",
     ["reports/"]),
    ("S09", "rc9_windows_packaging", "Bump to 2.0.0-rc9 + Windows packaging", "M09",
     "Version/drift/manifest — SR14 only",
     ["VERSION", "pyproject.toml", "packaging/windows/", "scripts/", "manifests/"]),
    ("S10", "release_and_closeout", "SR14 series closeout + tags", "M10",
     "Docs/release, tag v2.0.0-rc9 + bbws-sr14-complete",
     ["ACTIVE_ARC.yaml", "context/", "git_arc/", "reports/"]),
]



def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sp_name(season_id: str, slug: str) -> str:
    return f"{SR}_{season_id.lower()}_{slug}.v{VERSION}.json"


def main() -> None:
    seasons = [
        {
            "id": sid, "slug": slug, "title": title, "milestone": mile,
            "focus": focus, "surfaces": surfaces,
        }
        for sid, slug, title, mile, focus, surfaces in SEASONS
    ]
    write_text(
        ROOT / "ACTIVE_ARC.yaml",
        f"""# BBWS {SRU} live pointer — product owns truth (salvage cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: scaffold_and_contract_freeze
episode_id: S01E01
milestone: M01
status: active
parent_series_id: {PARENT_SERIES}
parent_tag: {PARENT_TAG}
baseline_tag: {BASELINE_TAG}
product_version_target: {PRODUCT_VERSION}
product_version_during_impl: {PRODUCT_DURING}
doctrine_source: C:/aos_arc_launcher_v0_4_21
updated_at: {NOW}
runtime_claimed: false
capture_law: scan_settle_lock_confirm_reset
next_action: Execute S01 scaffold + auto-record after lock contract freeze
""",
    )
    write_json(
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_{SR}_{SLUG}.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": PARENT_SERIES,
            "parent_tag": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "series_goal": SERIES_GOAL,
            "runtime_claimed": False,
            "version": VERSION,
            "shape": "10 seasons × 10 episodes = 100",
            "seasons": [
                {"season_id": f"{s['id']}_{s['slug']}", "title": s["title"], "milestone": s["milestone"],
                 "episode_count": 10, "focus": s["focus"], "superpower_ref": f"superpowers/{sp_name(s['id'], s['slug'])}"}
                for s in seasons
            ],
            "total_episodes": 100,
            "non_claims": NON_CLAIMS,
        },
    )
    write_json(
        ROOT / "manifests" / f"bbws_{SR}_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "seasons": [
                {"season_id": s["id"], "slug": s["slug"], "milestone": s["milestone"], "title": s["title"]}
                for s in seasons
            ],
            "non_claims": NON_CLAIMS,
        },
    )
    rows = "\n".join(
        f"| **{s['id']}** | {s['milestone']} | {s['title']} | {s['focus']} | `{sp_name(s['id'], s['slug'])}` |"
        for s in seasons
    )
    write_text(
        ROOT / "cursor" / f"BBWS_{SRU}_AUTO_RECORD_AFTER_LOCK_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS {SRU} — {MAP_TITLE} Series Map

**series_id:** `{SERIES_ID}`  
**parent:** `{PARENT_SERIES}` / `{PARENT_TAG}`  
**baseline:** `{BASELINE_TAG}`  
**product version target:** `{PRODUCT_VERSION}`

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
{rows}

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )
    forbidden = [
        "JSONL authority changes",
        "claim legal-for-trade or Metrc",
        "mutate salvage or Arc Launcher",
        "firmware bump",
    ]
    for s in seasons:
        episodes = [
            {
                "id": f"{s['id']}E{i:02d}",
                "title": f"{s['title']} episode {i:02d}",
                "kind": "implement" if i < 8 else "closeout",
                "status": "planned",
                "objective": s["focus"],
                "authorized_scope": s["surfaces"],
                "forbidden_scope": forbidden,
                "runtime_claimed": False,
            }
            for i in range(1, 11)
        ]
        write_json(
            ROOT / "superpowers" / sp_name(s["id"], s["slug"]),
            {
                "version": VERSION,
                "schema_version": f"bbws.{SR}.{s['slug']}.v1",
                "arc_id": f"{SRU}_{s['id']}_{s['slug']}",
                "series_id": SERIES_ID,
                "title": s["title"],
                "milestone": s["milestone"],
                "focus": s["focus"],
                "runtime_claimed": False,
                "product_version_target": PRODUCT_VERSION,
                "primary_surfaces": s["surfaces"],
                "episodes": episodes,
                "non_claims": NON_CLAIMS,
            },
        )
    write_json(
        ROOT / "context" / "resume_pack" / f"BBWS_{SRU}_resume.v{VERSION}.json",
        {
            "pack_id": f"BBWS_{SRU}_resume",
            "version": VERSION,
            "series_id": SERIES_ID,
            "updated_at": NOW,
            "active": {"season_id": "S01", "episode_id": "S01E01", "status": "ready_to_execute"},
            "parent_tag": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "decision_locks": {
                "capture_loop": "scan_settle_lock_confirm_reset",
                "duplicate_pre_gate": True,
                "auto_record_after_lock": True,
            },
            "non_claims": NON_CLAIMS,
        },
    )
    write_text(
        ROOT / "kickoff_prompts" / f"BBWS_{SRU}_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS {SRU} — Human Chat Kickoff

Continue series `{SERIES_ID}` toward `{PRODUCT_VERSION}`. {KICKOFF_LINE}
""",
    )
    write_text(
        ROOT / "docs" / f"BBWS_{SRU}_ARTIFACTS.md",
        f"""# BBWS {SRU} Artifacts

**series_id:** `{SERIES_ID}`  
**product_version_target:** `{PRODUCT_VERSION}`

| Artifact | Path |
|----------|------|
| Setting | `app/best_buds_weight_station/settings.py` |
| Lock→commit | `app/best_buds_weight_station/application_controller.py` |
| Beep | `app/best_buds_weight_station/operator_beep.py` |
| Station Settings | `app/best_buds_weight_station/pyside_frontend.py` |
| Tests | `tests/test_sr14_auto_record_after_lock.py` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )
    write_text(
        ROOT / "context" / "ledger" / f"bbws_{SR}_ledger.md",
        f"""# BBWS {SRU} Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | Phase0/S01 | Scaffold ACTIVE_ARC, blueprint, maps, {SRU} superpowers |
""",
    )
    write_json(
        ROOT / "reports" / f"{SR}_s01_contract_freeze.v{VERSION}.json",
        {
            "receipt_id": f"{SR}_s01_contract_freeze",
            "series_id": SERIES_ID,
            "status": "accepted",
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "acceptance": CONTRACT,
            "non_claims": NON_CLAIMS,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "series_pointer.v0.1.0.json",
        {
            "series_id": SERIES_ID,
            "parent_tag": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "planned_tags": ["v2.0.0-rc9", "bbws-sr14-complete"],
            "updated_at": NOW,
        },
    )
    print(f"BBWS_{SRU} scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
