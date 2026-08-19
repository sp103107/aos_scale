"""
Scaffold BBWS_SR15 rc9 test gate + Windows Setup series.

Focus: pytest / simulator / pytest-qt / Bugbot, then rebuild Setup.exe for
2.0.0-rc9. Product version stays rc9 unless a blocking operator defect forces rc10.

Doctrine cite only: C:/aos_arc_launcher_v0_4_21
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR15_rc9_test_and_windows_package"
PARENT_SERIES = "BBWS_SR14_auto_record_after_lock"
PARENT_TAG = "bbws-sr14-complete"
BASELINE_TAG = "bbws-pre-sr15-test-package"
PRODUCT_VERSION = "2.0.0-rc9"
PRODUCT_DURING = "2.0.0-rc9"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
SLUG = "rc9_test_and_windows_package"
SR = "sr15"
SRU = "SR15"
MAP_TITLE = "rc9 Test Gate + Windows Setup"
SERIES_GOAL = "Test and debug the 2.0.0-rc9 operator surface, then rebuild Windows Setup.exe."
KICKOFF_LINE = "Stay on 2.0.0-rc9. Fail closed on pytest. Rebuild Setup after the test gate."
CONTRACT = {
    "product_stays_rc9": True,
    "pytest_fail_closed": True,
    "pytest_qt_dev_extra": True,
    "setup_exe_required": True,
    "physical_com_not_blocking": True,
}

NON_CLAIMS = [
    "Not legal-for-trade / Metrc compliance",
    "JSONL remains authoritative for weight records",
    "Capture loop unchanged: scan → settle → lock → confirm → reset",
    "Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only",
    "Not a remote weighing server",
    "Packaged Setup is not Authenticode-signed",
    "Physical COM 100 g remains operator follow-up unless a live scale is connected",
    "pytest-qt is a test extra only — not an operator runtime dependency",
]

SEASONS = [
    ("S01", "scaffold_and_contract_freeze", "Scaffold + contract freeze", "M01",
     "Freeze SR15 contract; baseline tag; Arc artifacts",
     ["ACTIVE_ARC.yaml", "cursor/", "scripts/scaffold_bbws_sr15.py", "reports/"]),
    ("S02", "pytest_sr12_sr14", "pytest SR12–14 + full suite", "M02",
     "Fail closed on SR12/SR13/SR14 tests then full pytest",
     ["tests/", "reports/"]),
    ("S03", "simulator_self_test_smoke", "Simulator self-test + ui-smoke", "M03",
     "--self-test --simulator and --ui-smoke --simulator",
     ["app/best_buds_weight_station/cli.py", "reports/"]),
    ("S04", "pytest_qt_operator_dialogs", "pytest-qt operator dialogs", "M04",
     "Offscreen Qt: duplicate Cancel writes nothing; Station Settings auto-record",
     ["tests/test_sr15_qt_operator_dialogs.py", "pyproject.toml"]),
    ("S05", "bugbot_review", "Bugbot review", "M05",
     "Cursor Bugbot on SR12–SR14 branch changes",
     ["reports/"]),
    ("S06", "defect_pass_or_none", "Defect pass or none", "M06",
     "Fix confirmed defects only; operator-code fixes bump rc10",
     ["app/best_buds_weight_station/", "reports/"]),
    ("S07", "docs_rc9_setup", "Docs + rc9 Setup note", "M07",
     "WINDOWS_BUILD and RELEASE_CANDIDATE note that rc9 has Setup",
     ["docs/WINDOWS_BUILD.md", "docs/RELEASE_CANDIDATE.md"]),
    ("S08", "windows_setup_build", "Windows Setup + zip", "M08",
     "build_windows.ps1; hard fail if ISCC missing",
     ["packaging/windows/", "dist/windows/"]),
    ("S09", "upgrade_smoke", "Packaged upgrade smoke", "M09",
     "Silent upgrade to rc9; data marker and self-test",
     ["packaging/windows/", "reports/"]),
    ("S10", "release_and_closeout", "SR15 series closeout + tags", "M10",
     "series_complete; tag bbws-sr15-complete (keep v2.0.0-rc9 unless S06 forced rc10)",
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
next_action: Execute S01 scaffold + rc9 test-and-package contract freeze
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
        ROOT / "cursor" / f"BBWS_{SRU}_RC9_TEST_AND_WINDOWS_PACKAGE_SERIES_MAP.v{VERSION}.md",
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
                "product_stays_rc9": True,
                "setup_exe_required": True,
                "pytest_fail_closed": True,
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
| pytest SR12–14 | `tests/test_sr12_characterize_stream.py` |
| pytest-qt | `tests/test_sr15_qt_operator_dialogs.py` |
| Windows build | `packaging/windows/build_windows.ps1` |
| Setup | `dist/windows/BestBudsWeightStation-Setup-v2.0.0-rc9.exe` |

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
            "planned_tags": ["bbws-sr15-complete"],
            "updated_at": NOW,
        },
    )
    print(f"BBWS_{SRU} scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
