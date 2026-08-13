"""
Scaffold BBWS_SR11 Live Stream Quiet Window series.

Focus: stop Resume/Load from issuing SET_CAL under a live reader, restore live
UI grams and Guided Cal samples, then ship 2.0.0-rc6 after physical proof.

Doctrine cite only (do not mutate M: salvage or Arc Launcher):
- Arc Launcher canonical naming / blueprint factory / git mutation boundary
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR11_live_stream_quiet_window"
PARENT_SERIES = "BBWS_SR10_calibration_handshake_integrity"
PARENT_TAG = "bbws-sr10-complete"
BASELINE_TAG = "bbws-pre-sr11-stream-quiet"
PRODUCT_VERSION = "2.0.0-rc6"
PRODUCT_DURING = "2.0.0-rc5"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

NON_CLAIMS = [
    "Not legal-for-trade / Metrc compliance",
    "100 g characterization is repeatability evidence, not certification",
    "Scale profiles/receipts are local operational evidence only",
    "JSONL remains authoritative for weight records",
    "Capture loop unchanged: scan → settle → lock → confirm → reset",
    "Firmware device identity must be unique; collision requires operator intervention",
    "Archived profiles never erase historical calibration or weight evidence",
    "Salvage/KS/Book Spine and Arc Launcher are documentation doctrine cites only",
    "Not a remote weighing server",
    "Quiet-window resume is operational integrity only — not certification",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "scaffold_and_contract_freeze",
        "title": "Scaffold + contract freeze",
        "milestone": "M01",
        "focus": "Freeze SR11 contract; baseline tag; Arc artifacts",
        "surfaces": [
            "ACTIVE_ARC.yaml",
            "cursor/",
            "scripts/scaffold_bbws_sr11.py",
            "arc_lifecycle/blueprints/",
            "reports/",
        ],
        "episodes": [
            ("Intent freeze: live stream quiet window", "context"),
            ("Inventory resume/SET_CAL race surfaces", "context"),
            ("Write contract freeze receipt", "implement"),
            ("Tag bbws-pre-sr11-stream-quiet", "implement"),
            ("Authorize S02–S06 quiet-window work", "implement"),
            ("Verify non-claims stamped", "verify"),
            ("S01 receipt pack", "receipt"),
            ("Verify ACTIVE_ARC points at S01", "verify"),
            ("S01 closeout notes", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "quiet_resume_load",
        "title": "Quiet window around resume/load",
        "milestone": "M02",
        "focus": "Stop worker before profile apply on run.resume / run.load / new-run-when-connected",
        "surfaces": [
            "app/best_buds_weight_station/operator_runtime.py",
            "app/best_buds_weight_station/pyside_frontend.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: quiet resume", "context"),
            ("Add _with_quiet_profile_apply", "implement"),
            ("Wrap run.resume", "implement"),
            ("Wrap run.load", "implement"),
            ("Wrap new-run when device connected", "implement"),
            ("UI uses runtime wrappers", "implement"),
            ("Keep Zero/Accept quiet windows", "implement"),
            ("Verify resume under stream", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "skip_redundant_set_cal",
        "title": "Skip redundant SET_CAL",
        "milestone": "M03",
        "focus": "If STATUS factor matches active profile, install stability only",
        "surfaces": [
            "app/best_buds_weight_station/application_controller.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: skip matching SET_CAL", "context"),
            ("Read STATUS before apply", "implement"),
            ("isclose skip path", "implement"),
            ("Still SET_CAL when factor differs", "implement"),
            ("Install stability on skip path", "implement"),
            ("Return skipped flag in apply result", "implement"),
            ("Keep reconnect apply path", "implement"),
            ("Verify skip unit test", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "ensure_worker_for_cal",
        "title": "Ensure worker before Guided Cal samples",
        "milestone": "M04",
        "focus": "ensure_reading_worker before collect_raw_samples / start_calibration",
        "surfaces": [
            "app/best_buds_weight_station/operator_runtime.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: cal needs live stream", "context"),
            ("Add ensure_reading_worker", "implement"),
            ("Call from collect_raw_samples", "implement"),
            ("Call from start_calibration", "implement"),
            ("No-op when already running", "implement"),
            ("Fail closed if disconnected", "implement"),
            ("Clear worker error on restart", "implement"),
            ("Verify ensure restarts stopped worker", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "restart_clear_error",
        "title": "Restart worker + clear error",
        "milestone": "M05",
        "focus": "After quiet apply, restart worker and clear last_worker_error on success",
        "surfaces": [
            "app/best_buds_weight_station/operator_runtime.py",
        ],
        "episodes": [
            ("Intent freeze: clear Scale note", "context"),
            ("Restart in finally after quiet apply", "implement"),
            ("Clear last_worker_error on completed", "implement"),
            ("Preserve error if restart fails", "implement"),
            ("Buffer clear optional after apply", "implement"),
            ("Keep status snapshot truthful", "implement"),
            ("Document operator recovery", "implement"),
            ("Verify error cleared after resume", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "scripted_quiet_tests",
        "title": "Scripted quiet-window tests",
        "milestone": "M06",
        "focus": "Resume under stream leaves worker running; skip SET_CAL when matched",
        "surfaces": ["tests/", "reports/"],
        "episodes": [
            ("Intent freeze: quiet tests", "context"),
            ("Resume under stream keeps worker", "implement"),
            ("Skip SET_CAL when factor matches", "implement"),
            ("ensure_reading_worker restart test", "implement"),
            ("Load path uses quiet window", "implement"),
            ("Run pytest green", "verify"),
            ("Write S06 test receipt", "receipt"),
            ("Regression with SR10 handshake tests", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "physical_resume_cal_gate",
        "title": "Physical resume + Guided Cal gate",
        "milestone": "M07",
        "focus": "Connect → Resume → live grams → Guided Cal empty samples",
        "surfaces": ["reports/", "docs/"],
        "episodes": [
            ("Intent freeze: physical gate before rc6", "context"),
            ("Connect COM live grams", "verify"),
            ("Resume Last Run grams still move", "verify"),
            ("Guided Cal empty samples succeed", "verify"),
            ("Optional ZERO + Lock smoke", "verify"),
            ("Write physical receipt", "receipt"),
            ("Block version bump if fail", "implement"),
            ("Document operator steps", "implement"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "docs_resume_recovery",
        "title": "Docs + resume recovery",
        "milestone": "M08",
        "focus": "Bring-up resume recovery; do not reopen stream under SET_CAL",
        "surfaces": [
            "docs/",
            "docs/OPERATOR_ONBOARDING.md",
            "docs/WINDOWS_DEVICE_BRINGUP.md",
            "docs/BBWS_SR11_ARTIFACTS.md",
        ],
        "episodes": [
            ("Intent freeze: docs only", "context"),
            ("Resume recovery steps", "implement"),
            ("Guided Cal needs live stream note", "implement"),
            ("BBWS_SR11_ARTIFACTS.md", "implement"),
            ("Keep non-claims stamped", "implement"),
            ("No capture-law doc drift", "verify"),
            ("Verify docs paths exist", "verify"),
            ("Update CONTINUATION handoff", "implement"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "rc6_windows_packaging",
        "title": "Bump to 2.0.0-rc6 + Windows packaging",
        "milestone": "M09",
        "focus": "Version/drift/manifest; Setup/zip; rc5→rc6 upgrade smoke — only after S07 pass",
        "surfaces": [
            "VERSION",
            "app/best_buds_weight_station/version.py",
            "pyproject.toml",
            "packaging/windows/",
            "scripts/",
            "reports/",
            "manifests/",
        ],
        "episodes": [
            ("Intent freeze: 2.0.0-rc6 after physical pass", "context"),
            ("Bump version surfaces", "implement"),
            ("Add drift script v200_rc6", "implement"),
            ("Build Setup + portable zip", "implement"),
            ("rc5→rc6 upgrade smoke", "verify"),
            ("Profile preservation check", "verify"),
            ("Regenerate file manifest", "implement"),
            ("Leave archival rc5 receipts untouched", "implement"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "release_and_closeout",
        "title": "SR11 series closeout + tags",
        "milestone": "M10",
        "focus": "Docs/release, tag v2.0.0-rc6 + bbws-sr11-complete, push",
        "surfaces": ["ACTIVE_ARC.yaml", "context/", "git_arc/", "reports/", "docs/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Mark ACTIVE_ARC series_complete", "implement"),
            ("Update resume pack + ledger", "implement"),
            ("Tag v2.0.0-rc6", "implement"),
            ("Tag bbws-sr11-complete", "implement"),
            ("Publish GitHub release assets", "implement"),
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
    return f"sr11_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "bump VERSION to rc6 before S07 physical pass and S09",
                    "input-integrity bootstrap as this series",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr11.{season['slug']}.v1",
        "arc_id": f"SR11_{season['id']}_{season['slug']}",
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
        f"""# BBWS SR11 live pointer — product owns truth (salvage cited, not mutated)
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
next_action: Execute S01 scaffold + quiet-window contract freeze
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
        ROOT
        / "arc_lifecycle"
        / "blueprints"
        / f"series_bbws_sr11_live_stream_quiet_window.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": PARENT_SERIES,
            "parent_arc_id": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "series_goal": (
                "Stop Resume/Load from issuing SET_CAL under a live reading worker, "
                "restore live UI grams and Guided Cal samples, and close with "
                f"{PRODUCT_VERSION} only after physical proof."
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
        ROOT / "manifests" / f"bbws_sr11_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": (
                f"arc_lifecycle/blueprints/series_bbws_sr11_live_stream_quiet_window.v{VERSION}.json"
            ),
            "cursor_map_ref": f"cursor/BBWS_SR11_LIVE_STREAM_QUIET_WINDOW_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR11_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR11_LIVE_STREAM_QUIET_WINDOW_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR11 — Live Stream Quiet Window Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `{PARENT_SERIES}` / `{PARENT_TAG}`  
**baseline:** `{BASELINE_TAG}`  
**product version target:** `{PRODUCT_VERSION}`  
**product version during impl:** `{PRODUCT_DURING}` (bump in S09 only after S07 physical pass)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR11_resume*.json
→ cursor/BBWS_SR11_*_SERIES_MAP*.md
→ superpowers/sr11_sNN_*.json
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
        ROOT / "context" / "resume_pack" / f"BBWS_SR11_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR11_resume",
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
            "product_version_during_impl": PRODUCT_DURING,
            "completed_seasons": [],
            "decision_locks": {
                "capture_loop": "scan_settle_lock_confirm_reset",
                "product_version_target": PRODUCT_VERSION,
                "product_version_during_impl": PRODUCT_DURING,
                "quiet_resume": True,
                "skip_matching_set_cal": True,
                "ensure_worker_before_cal_samples": True,
                "rc6_requires_physical_s07": True,
                "push_cadence": "series_closeout",
                "input_integrity": "deferred_to_later_series",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR11_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR11_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR11 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}` toward `{PRODUCT_VERSION}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR11_resume.v{VERSION}.json`
3. `cursor/BBWS_SR11_LIVE_STREAM_QUIET_WINDOW_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr11_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: capture law/JSONL unchanged; stay on `{PRODUCT_DURING}` until S07 physical pass then S09 bumps to
`{PRODUCT_VERSION}`; input-integrity deferred.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR11 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}  
**Product target:** {PRODUCT_VERSION}  
**During impl:** {PRODUCT_DURING}

Load `ACTIVE_ARC.yaml` and `BBWS_SR11_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "planned_tags": ["v2.0.0-rc6", "bbws-sr11-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "scaffold_and_contract_freeze",
            "milestone": "M01",
            "commit_plan": "Commit S01 scaffold after contract freeze",
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
        ROOT / "context" / "ledger" / "bbws_sr11_ledger.md",
        f"""# BBWS SR11 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | Phase0/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR11 superpowers, resume pack |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR11_ARTIFACTS.md",
        f"""# BBWS SR11 Artifacts

**series_id:** `{SERIES_ID}`  
**product_version_target:** `{PRODUCT_VERSION}`  
**product_version_during_impl:** `{PRODUCT_DURING}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR11_LIVE_STREAM_QUIET_WINDOW_SERIES_MAP.v{VERSION}.md` |
| Resume pack | `context/resume_pack/BBWS_SR11_resume.v{VERSION}.json` |
| Operator quiet window | `app/best_buds_weight_station/operator_runtime.py` |
| Profile apply skip SET_CAL | `app/best_buds_weight_station/application_controller.py` |
| Contract freeze | `reports/sr11_s01_contract_freeze.v{VERSION}.json` |
| Quiet tests | `tests/test_sr11_stream_quiet.py` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )

    write_json(
        ROOT / "reports" / f"sr11_s01_contract_freeze.v{VERSION}.json",
        {
            "receipt_id": "sr11_s01_contract_freeze",
            "series_id": SERIES_ID,
            "season_id": "S01",
            "version": VERSION,
            "status": "accepted",
            "runtime_claimed": False,
            "baseline_tag": BASELINE_TAG,
            "parent_tag": PARENT_TAG,
            "product_version_during_impl": PRODUCT_DURING,
            "product_version_target": PRODUCT_VERSION,
            "acceptance": {
                "capture_law": "scan_settle_lock_confirm_reset",
                "jsonl_authoritative": True,
                "quiet_resume_load": True,
                "skip_matching_set_cal": True,
                "ensure_worker_before_cal_samples": True,
                "rc6_requires_physical_s07": True,
                "version_bump_season": "S09",
                "input_integrity_deferred": True,
            },
            "non_claims": NON_CLAIMS,
        },
    )
    print(f"BBWS_SR11 scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
