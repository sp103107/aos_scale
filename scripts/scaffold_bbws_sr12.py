"""
Scaffold BBWS_SR12 Post-Cal Characterize Stream series.

Focus: after Guided Cal Accept, 100 g Stability Test / characterize must restart
the live reading worker so sample collection does not starve.

Doctrine cite only (do not mutate salvage or Arc Launcher):
- C:/aos_arc_launcher_v0_4_21 canonical naming / blueprint factory / git mutation boundary
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR12_post_cal_characterize_stream"
PARENT_SERIES = "BBWS_SR11_live_stream_quiet_window"
PARENT_TAG = "bbws-sr11-complete"
BASELINE_TAG = "bbws-pre-sr12-characterize"
PRODUCT_VERSION = "2.0.0-rc7"
PRODUCT_DURING = "2.0.0-rc6"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
SLUG = "post_cal_characterize_stream"

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
    "Ensure-worker-before-characterize is operational integrity only — not certification",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "scaffold_and_contract_freeze",
        "title": "Scaffold + contract freeze",
        "milestone": "M01",
        "focus": "Freeze SR12 contract; baseline tag; Arc artifacts",
        "surfaces": ["ACTIVE_ARC.yaml", "cursor/", "scripts/scaffold_bbws_sr12.py", "arc_lifecycle/blueprints/", "reports/"],
        "episodes": [
            ("Intent freeze: post-cal characterize stream", "context"),
            ("Inventory collect_weight_samples vs Guided Cal ensure", "context"),
            ("Write contract freeze receipt", "implement"),
            ("Tag bbws-pre-sr12-characterize", "implement"),
            ("Authorize S02–S06 characterize work", "implement"),
            ("Verify non-claims stamped", "verify"),
            ("S01 receipt pack", "receipt"),
            ("Verify ACTIVE_ARC points at S01", "verify"),
            ("S01 closeout notes", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "ensure_worker_for_characterize",
        "title": "Ensure worker before characterize samples",
        "milestone": "M02",
        "focus": "Call ensure_reading_worker at start of collect_weight_samples",
        "surfaces": ["app/best_buds_weight_station/operator_runtime.py", "tests/"],
        "episodes": [
            ("Intent freeze: characterize needs live stream", "context"),
            ("Call ensure_reading_worker from collect_weight_samples", "implement"),
            ("Keep Guided Cal ensure path unchanged", "implement"),
            ("No-op when already running", "implement"),
            ("Fail closed if disconnected", "implement"),
            ("Do not change capture law", "verify"),
            ("Verify worker restarts after Accept-style stop", "verify"),
            ("S02 receipt pack", "receipt"),
            ("S02 closeout notes", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "surface_worker_error_on_collect",
        "title": "Surface worker error on collect fail",
        "milestone": "M03",
        "focus": "Include last_worker_error when characterization samples starve",
        "surfaces": ["app/best_buds_weight_station/operator_runtime.py"],
        "episodes": [
            ("Intent freeze: operator-visible starve reason", "context"),
            ("Append last_worker_error to RuntimeError", "implement"),
            ("Keep soft not-near-100g as reviewable metrics", "implement"),
            ("Do not crash on partial 12–119 samples", "implement"),
            ("Preserve existing timeout/sample floors", "verify"),
            ("No firmware change", "verify"),
            ("S03 receipt pack", "receipt"),
            ("Verify error text still operator-safe after Alice", "verify"),
            ("S03 closeout notes", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "alice_characterize_copy",
        "title": "Alice characterize copy",
        "milestone": "M04",
        "focus": "Operator-safe message for not enough live weight samples",
        "surfaces": ["app/best_buds_weight_station/alice/authority.py"],
        "episodes": [
            ("Intent freeze: Alice characterize starve copy", "context"),
            ("Map not enough live weight samples", "implement"),
            ("Disconnect then Connect recovery wording", "implement"),
            ("Do not claim certification", "verify"),
            ("Keep leftover-ACK Accept copy from SR10", "verify"),
            ("S04 receipt pack", "receipt"),
            ("Verify operator_safe_error unit path", "verify"),
            ("No Metrc/legal-for-trade language", "verify"),
            ("S04 closeout notes", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "scripted_characterize_tests",
        "title": "Scripted characterize tests",
        "milestone": "M05",
        "focus": "Stopped worker recovers; characterize collect does not starve",
        "surfaces": ["tests/", "reports/"],
        "episodes": [
            ("Intent freeze: characterize tests", "context"),
            ("Stopped worker collect recovers", "implement"),
            ("characterize_stability after ensure", "implement"),
            ("Worker error attached on starve", "implement"),
            ("Run pytest green", "verify"),
            ("Write S05 test receipt", "receipt"),
            ("Regression with SR11 quiet tests", "verify"),
            ("S05 receipt pack", "receipt"),
            ("S05 closeout notes", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "physical_characterize_gate",
        "title": "Physical post-cal characterize gate",
        "milestone": "M06",
        "focus": "Accept → 100 g Stability Test with mass on pan",
        "surfaces": ["reports/", "docs/"],
        "episodes": [
            ("Intent freeze: physical gate before rc7", "context"),
            ("Connect + Guided Cal Accept", "verify"),
            ("100 g Stability Test collects samples", "verify"),
            ("Soft not-near-100g is reviewable not crash", "verify"),
            ("Write physical receipt", "receipt"),
            ("Block version bump if collect still starves", "implement"),
            ("Document operator steps", "implement"),
            ("S06 receipt pack", "receipt"),
            ("S06 closeout notes", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "docs_characterize_recovery",
        "title": "Docs + characterize recovery",
        "milestone": "M07",
        "focus": "Bring-up note: 100 g test needs live stream after Accept",
        "surfaces": ["docs/", "docs/OPERATOR_ONBOARDING.md", "docs/WINDOWS_DEVICE_BRINGUP.md", "docs/BBWS_SR12_ARTIFACTS.md"],
        "episodes": [
            ("Intent freeze: docs only", "context"),
            ("Stability test recovery steps", "implement"),
            ("BBWS_SR12_ARTIFACTS.md", "implement"),
            ("Keep non-claims stamped", "implement"),
            ("No capture-law doc drift", "verify"),
            ("Verify docs paths exist", "verify"),
            ("Update CONTINUATION handoff", "implement"),
            ("S07 receipt pack", "receipt"),
            ("S07 closeout notes", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "no_unrelated_churn",
        "title": "No unrelated churn",
        "milestone": "M08",
        "focus": "This bump is characterize-only; SR13/SR14 stay later series",
        "surfaces": ["reports/"],
        "episodes": [
            ("Intent freeze: rc7 contains SR12 only", "context"),
            ("Confirm no duplicate-barcode UI in this bump", "verify"),
            ("Confirm no auto-record-after-lock in this bump", "verify"),
            ("Confirm no firmware bump", "verify"),
            ("Write scope receipt", "receipt"),
            ("S08 receipt pack", "receipt"),
            ("Verify capture law docs unchanged", "verify"),
            ("S08 closeout notes", "receipt"),
            ("Verify ACTIVE_ARC still SR12", "verify"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "rc7_windows_packaging",
        "title": "Bump to 2.0.0-rc7 + Windows packaging",
        "milestone": "M09",
        "focus": "Version/drift/manifest; Setup/zip — only after S06 gate",
        "surfaces": ["VERSION", "app/best_buds_weight_station/version.py", "pyproject.toml", "packaging/windows/", "scripts/", "reports/", "manifests/"],
        "episodes": [
            ("Intent freeze: 2.0.0-rc7 after characterize gate", "context"),
            ("Bump version surfaces", "implement"),
            ("Add drift script v200_rc7", "implement"),
            ("Build Setup + portable zip", "implement"),
            ("rc6→rc7 upgrade smoke", "verify"),
            ("Regenerate file manifest", "implement"),
            ("Leave archival rc6 receipts untouched", "implement"),
            ("S09 receipt pack", "receipt"),
            ("S09 closeout notes", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "release_and_closeout",
        "title": "SR12 series closeout + tags",
        "milestone": "M10",
        "focus": "Docs/release, tag v2.0.0-rc7 + bbws-sr12-complete",
        "surfaces": ["ACTIVE_ARC.yaml", "context/", "git_arc/", "reports/", "docs/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Mark ACTIVE_ARC series_complete", "implement"),
            ("Update resume pack + ledger", "implement"),
            ("Tag v2.0.0-rc7", "implement"),
            ("Tag bbws-sr12-complete", "implement"),
            ("Do not invent SR12 seasons after complete", "verify"),
            ("Verify remote tags optional", "verify"),
            ("S10 receipt pack", "receipt"),
            ("S10 closeout notes", "receipt"),
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
    return f"sr12_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "bump VERSION to rc7 before S06 characterize gate and S09",
                    "duplicate barcode pre-gate (SR13)",
                    "auto_record_after_lock (SR14)",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr12.{season['slug']}.v1",
        "arc_id": f"SR12_{season['id']}_{season['slug']}",
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
        f"""# BBWS SR12 live pointer — product owns truth (salvage cited, not mutated)
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
next_action: Execute S01 scaffold + post-cal characterize contract freeze
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
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr12_{SLUG}.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": PARENT_SERIES,
            "parent_arc_id": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "series_goal": (
                "After Guided Cal Accept, restart the live reader before 100 g "
                "characterization so Stability Test does not starve, then close with "
                f"{PRODUCT_VERSION} after the characterize gate."
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
        ROOT / "manifests" / f"bbws_sr12_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr12_{SLUG}.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR12_POST_CAL_CHARACTERIZE_STREAM_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR12_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR12_POST_CAL_CHARACTERIZE_STREAM_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR12 — Post-Cal Characterize Stream Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `{PARENT_SERIES}` / `{PARENT_TAG}`  
**baseline:** `{BASELINE_TAG}`  
**product version target:** `{PRODUCT_VERSION}`  
**product version during impl:** `{PRODUCT_DURING}` (bump in S09 only after S06 characterize gate)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR12_resume*.json
→ cursor/BBWS_SR12_*_SERIES_MAP*.md
→ superpowers/sr12_sNN_*.json
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
        ROOT / "context" / "resume_pack" / f"BBWS_SR12_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR12_resume",
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
                "ensure_worker_before_characterize": True,
                "rc7_requires_characterize_s06": True,
                "push_cadence": "series_closeout",
                "duplicate_pre_gate": "deferred_to_sr13",
                "auto_record_after_lock": "deferred_to_sr14",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR12_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR12_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR12 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}` toward `{PRODUCT_VERSION}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR12_resume.v{VERSION}.json`
3. `cursor/BBWS_SR12_POST_CAL_CHARACTERIZE_STREAM_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr12_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: capture law/JSONL unchanged; stay on `{PRODUCT_DURING}` until S06 characterize gate then S09 bumps to
`{PRODUCT_VERSION}`; duplicate pre-gate and auto-record-after-lock deferred.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR12 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}  
**Product target:** {PRODUCT_VERSION}  
**During impl:** {PRODUCT_DURING}

Load `ACTIVE_ARC.yaml` and `BBWS_SR12_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "planned_tags": ["v2.0.0-rc7", "bbws-sr12-complete"],
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
        ROOT / "context" / "ledger" / "bbws_sr12_ledger.md",
        f"""# BBWS SR12 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | Phase0/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR12 superpowers, resume pack |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR12_ARTIFACTS.md",
        f"""# BBWS SR12 Artifacts

**series_id:** `{SERIES_ID}`  
**product_version_target:** `{PRODUCT_VERSION}`  
**product_version_during_impl:** `{PRODUCT_DURING}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR12_POST_CAL_CHARACTERIZE_STREAM_SERIES_MAP.v{VERSION}.md` |
| Resume pack | `context/resume_pack/BBWS_SR12_resume.v{VERSION}.json` |
| Characterize collect | `app/best_buds_weight_station/operator_runtime.py` |
| Alice starve copy | `app/best_buds_weight_station/alice/authority.py` |
| Contract freeze | `reports/sr12_s01_contract_freeze.v{VERSION}.json` |
| Characterize tests | `tests/test_sr12_characterize_stream.py` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )

    write_json(
        ROOT / "reports" / f"sr12_s01_contract_freeze.v{VERSION}.json",
        {
            "receipt_id": "sr12_s01_contract_freeze",
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
                "ensure_worker_before_characterize": True,
                "rc7_requires_characterize_s06": True,
                "version_bump_season": "S09",
                "duplicate_pre_gate_deferred": True,
                "auto_record_after_lock_deferred": True,
            },
            "non_claims": NON_CLAIMS,
        },
    )
    print(f"BBWS_SR12 scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
