"""
Scaffold BBWS_SR7 Windows installer bring-up + 2.0.0-rc2 release 100-arc series.

Focus: run-lifecycle/capture-display UX fixes, path/device install hygiene,
native Windows exe + Inno Setup installer, version 2.0.0-rc2, GitHub Release.

Doctrine cite only (do not mutate M: salvage or Arc Launcher):
- Arc Launcher canonical naming / blueprint factory / git mutation boundary
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR7_windows_installer_bringup"
PARENT_SERIES = "BBWS_SR6_product_onboarding_release"
PARENT_TAG = "bbws-sr6-complete"
BASELINE_TAG = "bbws-pre-sr7-windows-installer"
PRODUCT_VERSION = "2.0.0-rc2"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

NON_CLAIMS = [
    "Not legal-for-trade / Metrc compliance",
    "Not production-sealed weighing certification",
    "JSONL remains authoritative for records",
    "Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only",
    "Installer ships a USB bring-up product; calibration with a verified reference mass is required for accurate grams",
    "Capture loop unchanged: scan → settle → lock → confirm → reset",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "installer_contract_freeze",
        "title": "Scaffold + installer/release contract freeze",
        "milestone": "M01",
        "focus": "Freeze SR7 scope: UX fixes, hygiene, installer, rc2 release",
        "surfaces": ["ACTIVE_ARC.yaml", "cursor/", "scripts/scaffold_bbws_sr7.py", "arc_lifecycle/blueprints/"],
        "episodes": [
            ("Intent freeze: installer vs capture law", "context"),
            ("Inventory run UX bug evidence", "context"),
            ("Inventory packaging host gaps", "context"),
            ("Write contract freeze receipt", "implement"),
            ("Authorize S02 run UX fixes", "implement"),
            ("Authorize S03 hygiene scope", "implement"),
            ("Authorize S04-S10 build/release scope", "implement"),
            ("Verify non-claims stamped", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "run_lifecycle_ux_fixes",
        "title": "Run lifecycle + capture display UX fixes",
        "milestone": "M02",
        "focus": "Finish Run closeout, locked-weight display freeze, resume-run picker",
        "surfaces": [
            "app/best_buds_weight_station/pyside_frontend.py",
            "app/best_buds_weight_station/application_controller.py",
            "app/best_buds_weight_station/alice/authority.py",
            "app/best_buds_weight_station/production_ui.py",
            "tests/",
        ],
        "episodes": [
            ("Reproduce Finish Run dead-end with evidence", "context"),
            ("Widen run.finish authority for idle states", "implement"),
            ("Render RUN_FINISHED end state in refresh", "implement"),
            ("Freeze main weight display while locked", "implement"),
            ("Unfreeze display after confirm/cancel", "implement"),
            ("Add Resume Run picker over run.load", "implement"),
            ("Tk parity where cheap", "implement"),
            ("Contract tests for all three fixes", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "path_device_hygiene",
        "title": "Path + device install hygiene",
        "milestone": "M03",
        "focus": "Frozen-exe path truth and runtime COM enumeration only",
        "surfaces": [
            "app/best_buds_weight_station/settings.py",
            "app/best_buds_weight_station/platform_paths.py",
            "docs/",
        ],
        "episodes": [
            ("Audit data_root default in frozen exe", "context"),
            ("Prove config/runs land under LOCALAPPDATA", "context"),
            ("Fix relative data_root leak if proven", "implement"),
            ("Verify COM enumeration has no hardcoded port", "implement"),
            ("Driver notes FTDI/CH340 in docs", "implement"),
            ("Keep USB-serial-only transport law", "implement"),
            ("Verify dev-repo paths unchanged", "verify"),
            ("Verify hygiene tests green", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "build_host_prep",
        "title": "Build host prep (Inno Setup 6 + env)",
        "milestone": "M04",
        "focus": "Install/verify Inno Setup 6 and PyInstaller build env",
        "surfaces": ["packaging/windows/", "reports/"],
        "episodes": [
            ("Intent freeze: host tooling only", "context"),
            ("Detect existing ISCC install", "implement"),
            ("Install Inno Setup 6 via winget", "implement"),
            ("Verify ISCC on PATH or default dir", "verify"),
            ("Prepare venv with desktop/serial/dev extras", "implement"),
            ("Install PyInstaller in build env", "implement"),
            ("Write host prep receipt", "implement"),
            ("Verify tooling receipt", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "pyinstaller_build_green",
        "title": "PyInstaller exe + zip build green",
        "milestone": "M05",
        "focus": "build_windows.ps1 through exe, verify, zip",
        "surfaces": ["packaging/windows/build_windows.ps1", "packaging/windows/BestBudsWeightStation.spec", "dist/"],
        "episodes": [
            ("Intent freeze: native build evidence", "context"),
            ("Run packaging-critical pytest", "implement"),
            ("Run PyInstaller build", "implement"),
            ("Fix build breaks if any", "implement"),
            ("Run verify_windows.ps1", "verify"),
            ("Produce windows zip", "implement"),
            ("Write windows_build_receipt", "implement"),
            ("Verify exe launches --version", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "installer_smoke",
        "title": "Setup.exe build + install/uninstall smoke",
        "milestone": "M06",
        "focus": "Inno installer, per-user install, launch, uninstall preserves runs",
        "surfaces": ["packaging/windows/BestBudsWeightStation.iss", "dist/windows/", "reports/"],
        "episodes": [
            ("Intent freeze: per-user no-admin install", "context"),
            ("Build Setup.exe via ISCC", "implement"),
            ("Install to LOCALAPPDATA app dir", "implement"),
            ("Launch installed exe smoke", "verify"),
            ("New Run simulator smoke", "verify"),
            ("Uninstall preserves runs data", "verify"),
            ("Write install smoke receipt", "implement"),
            ("Verify receipts complete", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "version_bump_rc2",
        "title": "Bump product version to 2.0.0-rc2",
        "milestone": "M07",
        "focus": "version.py, VERSION, pyproject, iss, README, RC docs",
        "surfaces": [
            "app/best_buds_weight_station/version.py",
            "VERSION",
            "pyproject.toml",
            "packaging/windows/BestBudsWeightStation.iss",
            "README.md",
            "docs/RELEASE_CANDIDATE.md",
        ],
        "episodes": [
            ("Intent freeze: 2.0.0-rc2", "context"),
            ("Set __version__ and VERSION", "implement"),
            ("Set pyproject 2.0.0rc2", "implement"),
            ("Set iss fallback define", "implement"),
            ("Update README version surfaces", "implement"),
            ("Rewrite RELEASE_CANDIDATE for rc2", "implement"),
            ("Verify version print", "verify"),
            ("Verify no stale rc1 claims", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "drift_concordance_rc2",
        "title": "Drift concordance for 2.0.0-rc2",
        "milestone": "M08",
        "focus": "rc2 concordance validator, report, version-pinned tests",
        "surfaces": ["scripts/", "reports/", "tests/"],
        "episodes": [
            ("Intent freeze: pragmatic drift", "context"),
            ("Add v200_rc2 drift script", "implement"),
            ("Check version surfaces concordance", "implement"),
            ("Fix version-pinned tests", "implement"),
            ("Write concordance report", "implement"),
            ("Leave archival manifests untouched", "implement"),
            ("Verify drift pass", "verify"),
            ("Verify pytest green", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "release_artifacts",
        "title": "Release artifacts: source zip + windows zip + Setup.exe",
        "milestone": "M09",
        "focus": "make_release_bundle source zip, staged Windows artifacts, SHA256 receipts",
        "surfaces": ["scripts/make_release_bundle.py", "dist/releases/", "dist/windows/", "reports/"],
        "episodes": [
            ("Intent freeze: three-artifact release", "context"),
            ("Tag v2.0.0-rc2 plan", "implement"),
            ("Build source zip from tag", "implement"),
            ("Stage windows zip + Setup.exe", "implement"),
            ("Write SHA256 receipts", "implement"),
            ("Draft gh release notes", "implement"),
            ("Verify artifacts exist", "verify"),
            ("Verify receipts", "verify"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "series_closeout",
        "title": "GitHub Release + bbws-sr7-complete",
        "milestone": "M10",
        "focus": "gh release v2.0.0-rc2, tags, ACTIVE_ARC series_complete",
        "surfaces": ["ACTIVE_ARC.yaml", "reports/", "git_arc/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Tag v2.0.0-rc2", "implement"),
            ("gh release create with notes", "implement"),
            ("Attach source + windows zips + Setup.exe", "implement"),
            ("Tag bbws-sr7-complete", "implement"),
            ("ACTIVE_ARC series_complete", "implement"),
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
    return f"sr7_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr7.{season['slug']}.v1",
        "arc_id": f"SR7_{season['id']}_{season['slug']}",
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
        f"""# BBWS SR7 live pointer — product owns truth (salvage cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: installer_contract_freeze
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
next_action: Execute S01E01 installer/release contract freeze
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
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr7_windows_installer_bringup.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": PARENT_SERIES,
            "parent_arc_id": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "series_goal": (
                "Run lifecycle/capture display UX fixes, frozen-exe path and device hygiene, "
                f"native Windows exe + Inno Setup installer, product version {PRODUCT_VERSION}, "
                "and GitHub Release with source zip, Windows zip, and Setup.exe."
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
        ROOT / "manifests" / f"bbws_sr7_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr7_windows_installer_bringup.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR7_WINDOWS_INSTALLER_BRINGUP_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR7_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR7_WINDOWS_INSTALLER_BRINGUP_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR7 — Windows Installer Bring-up Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `{PARENT_SERIES}` / `{PARENT_TAG}`  
**baseline:** `{BASELINE_TAG}`  
**product version target:** `{PRODUCT_VERSION}`

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR7_resume*.json
→ cursor/BBWS_SR7_*_SERIES_MAP*.md
→ superpowers/sr7_sNN_*.json
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
        ROOT / "context" / "resume_pack" / f"BBWS_SR7_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR7_resume",
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
                "installer": "inno_setup_6_per_user_no_admin",
                "source_zip": "without_dot_git",
                "push_cadence": "series_closeout",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR7_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR7_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR7 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}` toward `{PRODUCT_VERSION}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR7_resume.v{VERSION}.json`
3. `cursor/BBWS_SR7_WINDOWS_INSTALLER_BRINGUP_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr7_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: run UX fixes + install hygiene + packaging/release only; capture law/JSONL unchanged; salvage cite-only.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR7 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}  
**Product target:** {PRODUCT_VERSION}

Load `ACTIVE_ARC.yaml` and `BBWS_SR7_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "planned_tags": ["v2.0.0-rc2", "bbws-sr7-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "installer_contract_freeze",
            "milestone": "M01",
            "commit_plan": "Commit S01 scaffold after E10 closeout",
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
        ROOT / "context" / "ledger" / "bbws_sr7_ledger.md",
        f"""# BBWS SR7 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | Phase0/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR7 superpowers, resume pack |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR7_ARTIFACTS.md",
        f"""# BBWS SR7 Artifacts

**series_id:** `{SERIES_ID}`  
**product_version_target:** `{PRODUCT_VERSION}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR7_WINDOWS_INSTALLER_BRINGUP_SERIES_MAP.v{VERSION}.md` |
| Resume pack | `context/resume_pack/BBWS_SR7_resume.v{VERSION}.json` |
| Run UX fixes | `app/best_buds_weight_station/pyside_frontend.py`, `alice/authority.py` |
| Path/device hygiene | `app/best_buds_weight_station/settings.py`, `platform_paths.py` |
| Windows build | `packaging/windows/` |
| Installer | `dist/windows/BestBudsWeightStation-Setup-v{PRODUCT_VERSION}.exe` |
| Drift concordance | `scripts/validate_drift_concordance_v200_rc2.py` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )
    print(f"BBWS_SR7 scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
