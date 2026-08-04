"""
Scaffold BBWS_SR6 product onboarding + 2.0.0-rc1 release 100-arc series.

Doctrine cite only (do not mutate M: salvage):
- KS structured onboarding template
- Book Spine BOOK_ENTRYPOINTS / publication readiness docs
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR6_product_onboarding_release"
PRODUCT_VERSION = "2.0.0-rc1"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

NON_CLAIMS = [
    "Not legal-for-trade / Metrc compliance",
    "Not production-sealed weighing certification",
    "JSONL remains authoritative for records",
    "Salvage/KS/Book Spine are documentation doctrine cites only",
    "Coding-agent onboard entry is guidance/bootstrap routing, not a new capture runtime",
    "Capture loop unchanged: scan → settle → lock → confirm → reset",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "onboarding_contract_freeze",
        "title": "Scaffold + onboarding/release contract freeze",
        "milestone": "M01",
        "focus": "Freeze docs/release contract and non-claims",
        "surfaces": ["ACTIVE_ARC.yaml", "cursor/", "docs/", "scripts/scaffold_bbws_sr6.py"],
        "episodes": [
            ("Intent freeze: onboarding vs capture", "context"),
            ("Inventory human doc gaps", "context"),
            ("Inventory agent entry gaps", "context"),
            ("Write contract freeze receipt", "implement"),
            ("Authorize S02–S04 human docs", "implement"),
            ("Authorize S05 agent entry", "implement"),
            ("Authorize S06–S10 release scope", "implement"),
            ("Verify non-claims stamped", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "salvage_selection_map",
        "title": "Salvage selection map KS + Book Spine",
        "milestone": "M02",
        "focus": "Map onboarding/entrypoint cites to BBWS docs",
        "surfaces": ["docs/BBWS_SR6_SELECTION_MAP.md"],
        "episodes": [
            ("Intent freeze: cite-only", "context"),
            ("Map KS structured onboarding template", "implement"),
            ("Map Book Spine entrypoints", "implement"),
            ("Map publication readiness cites", "implement"),
            ("Draft BBWS target table", "implement"),
            ("Reject salvage runtime import", "implement"),
            ("Verify selection coverage", "verify"),
            ("Verify non-claims", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "human_start_here",
        "title": "Human START_HERE + intended user",
        "milestone": "M03",
        "focus": "Root START_HERE and INTENDED_USER docs",
        "surfaces": ["START_HERE.md", "docs/INTENDED_USER.md"],
        "episodes": [
            ("Intent freeze: operator front door", "context"),
            ("Write START_HERE.md", "implement"),
            ("Write INTENDED_USER.md", "implement"),
            ("Link launchers and runbooks", "implement"),
            ("Stamp JSONL authority", "implement"),
            ("Stamp non-claims", "implement"),
            ("Verify one-page readability", "verify"),
            ("Verify no Metrc claim", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "operator_onboarding",
        "title": "Operator onboarding runbook",
        "milestone": "M04",
        "focus": "Structured OPERATOR_ONBOARDING with capture loop",
        "surfaces": ["docs/OPERATOR_ONBOARDING.md"],
        "episodes": [
            ("Intent freeze: KS template shape", "context"),
            ("Flow map Scan Lock Confirm", "implement"),
            ("Cultivator Strain New Run", "implement"),
            ("Export and reconcile steps", "implement"),
            ("Common confusion callouts", "implement"),
            ("Next action bullets", "implement"),
            ("Verify loop unchanged", "verify"),
            ("Verify non-claims", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "coding_agent_entry",
        "title": "Coding-agent START HERE + onboard.py",
        "milestone": "M05",
        "focus": "Agent front door and Python document router",
        "surfaces": ["START_HERE_CODING_AGENT.md", "app/best_buds_weight_station/onboard.py"],
        "episodes": [
            ("Intent freeze: guidance only", "context"),
            ("Write START_HERE_CODING_AGENT.md", "implement"),
            ("Implement onboard.py CLI", "implement"),
            ("Print version and key paths", "implement"),
            ("Point to bootstrap cursor-ready", "implement"),
            ("Forbidden scopes list", "implement"),
            ("Verify module entry", "verify"),
            ("Verify no capture mutation", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "github_docs_refresh",
        "title": "README + RELEASE_CANDIDATE for 2.0.0-rc1",
        "milestone": "M06",
        "focus": "GitHub-facing honesty for product RC",
        "surfaces": ["README.md", "docs/RELEASE_CANDIDATE.md"],
        "episodes": [
            ("Intent freeze: RC honesty", "context"),
            ("Update README version and START_HERE links", "implement"),
            ("Rewrite RELEASE_CANDIDATE for 2.0.0-rc1", "implement"),
            ("List SR3–SR5 capability highlights", "implement"),
            ("Stamp non-claims", "implement"),
            ("Link operator and agent doors", "implement"),
            ("Verify no production seal claim", "verify"),
            ("Verify launcher section", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "drift_concordance",
        "title": "Drift concordance for 2.0.0-rc1",
        "milestone": "M07",
        "focus": "Version concordance validator and test fixes",
        "surfaces": ["scripts/validate_drift_concordance_v200_rc1.py", "tests/"],
        "episodes": [
            ("Intent freeze: pragmatic drift", "context"),
            ("Add v200_rc1 drift script", "implement"),
            ("Check version.py README RC START_HERE", "implement"),
            ("Fix hard-coded 0.1.9 tests", "implement"),
            ("Write concordance report", "implement"),
            ("Leave archival v0.1.9 manifests", "implement"),
            ("Verify drift pass", "verify"),
            ("Verify pytest green", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "version_bump_rc1",
        "title": "Bump product version to 2.0.0-rc1",
        "milestone": "M08",
        "focus": "version.py and packaging version consumers",
        "surfaces": ["app/best_buds_weight_station/version.py"],
        "episodes": [
            ("Intent freeze: 2.0.0-rc1", "context"),
            ("Set __version__", "implement"),
            ("Align packaging version reads", "implement"),
            ("Align CLI --version", "implement"),
            ("Update core process version tests", "implement"),
            ("Stamp RC non-claims", "implement"),
            ("Verify version print", "verify"),
            ("Verify drift still green", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "clone_zip_bundle",
        "title": "Clean clone source zip bundle",
        "milestone": "M09",
        "focus": "make_release_bundle source zip + receipt",
        "surfaces": ["scripts/make_release_bundle.py", "dist/releases/", "reports/"],
        "episodes": [
            ("Intent freeze: zip without .git", "context"),
            ("Implement make_release_bundle.py", "implement"),
            ("Clone tag and zip source", "implement"),
            ("Write SHA256 receipt", "implement"),
            ("Attempt Windows packaging build", "implement"),
            ("Record binary deferred if needed", "implement"),
            ("Verify zip exists", "verify"),
            ("Verify receipt", "verify"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "series_closeout",
        "title": "GitHub Release + bbws-sr6-complete",
        "milestone": "M10",
        "focus": "gh release, tags, ACTIVE_ARC series_complete",
        "surfaces": ["ACTIVE_ARC.yaml", "reports/", "git_arc/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Tag v2.0.0-rc1", "implement"),
            ("gh release create with notes", "implement"),
            ("Attach source zip", "implement"),
            ("Tag bbws-sr6-complete", "implement"),
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
    return f"sr6_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "claim legal-for-trade or Metrc",
                    "mutate M: salvage",
                    "auto-push mid-episode",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr6.{season['slug']}.v1",
        "arc_id": f"SR6_{season['id']}_{season['slug']}",
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
            "M:/SALVAGE/CAPSULES/aos_knowledge_stack_rc_v5_0_0/docs/onboarding/_STRUCTURED_ONBOARDING_TEMPLATE.md",
            "M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_book_spine_capsule_template_v0_1_10/docs/BOOK_ENTRYPOINTS.md",
        ],
    }


def main() -> None:
    write_text(
        ROOT / "ACTIVE_ARC.yaml",
        f"""# BBWS SR6 live pointer — product owns truth (salvage cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: onboarding_contract_freeze
episode_id: S01E01
milestone: M01
status: active
parent_series_id: BBWS_SR5_run_artifact_polish
parent_tag: bbws-sr5-complete
baseline_tag: bbws-pre-sr6-onboarding-release
product_version_target: {PRODUCT_VERSION}
doctrine_source: C:/aos_arc_launcher_v0_4_21
ks_onboarding_ref: M:/SALVAGE/CAPSULES/aos_knowledge_stack_rc_v5_0_0/docs/onboarding/_STRUCTURED_ONBOARDING_TEMPLATE.md
book_spine_ref: M:/SALVAGE/KNOWLEDGE/FOUNDATIONS/aos_book_spine_capsule_template_v0_1_10
updated_at: {NOW}
runtime_claimed: false
capture_law: scan_settle_lock_confirm_reset
next_action: Execute S01E01 onboarding/release contract freeze
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
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr6_product_onboarding_release.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": "BBWS_SR5_run_artifact_polish",
            "parent_arc_id": "bbws-sr5-complete",
            "baseline_tag": "bbws-pre-sr6-onboarding-release",
            "product_version_target": PRODUCT_VERSION,
            "series_goal": (
                "Human/operator and coding-agent onboarding front doors, drift concordance, "
                f"product version {PRODUCT_VERSION}, and GitHub Release with source zip."
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
        ROOT / "manifests" / f"bbws_sr6_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr6_product_onboarding_release.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR6_PRODUCT_ONBOARDING_RELEASE_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR6_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR6_PRODUCT_ONBOARDING_RELEASE_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR6 — Product Onboarding + Release Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR5_run_artifact_polish` / `bbws-sr5-complete`  
**baseline:** `bbws-pre-sr6-onboarding-release`  
**product version target:** `{PRODUCT_VERSION}`

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR6_resume*.json
→ cursor/BBWS_SR6_*_SERIES_MAP*.md
→ superpowers/sr6_sNN_*.json
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
        ROOT / "context" / "resume_pack" / f"BBWS_SR6_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR6_resume",
            "version": VERSION,
            "series_id": SERIES_ID,
            "updated_at": NOW,
            "active": {
                "season_id": "S01",
                "episode_id": "S01E01",
                "milestone": "M01",
                "status": "ready_to_execute",
            },
            "parent_series": "BBWS_SR5_run_artifact_polish",
            "parent_tag": "bbws-sr5-complete",
            "baseline_tag": "bbws-pre-sr6-onboarding-release",
            "product_version_target": PRODUCT_VERSION,
            "completed_seasons": [],
            "decision_locks": {
                "capture_loop": "scan_settle_lock_confirm_reset",
                "product_version": PRODUCT_VERSION,
                "source_zip": "without_dot_git",
                "push_cadence": "series_closeout",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR6_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR6_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR6 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}` toward `{PRODUCT_VERSION}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR6_resume.v{VERSION}.json`
3. `cursor/BBWS_SR6_PRODUCT_ONBOARDING_RELEASE_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr6_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: onboarding + release packaging only; capture/JSONL unchanged; salvage cite-only.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR6 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}  
**Product target:** {PRODUCT_VERSION}

Load `ACTIVE_ARC.yaml` and `BBWS_SR6_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "parent_tag": "bbws-sr5-complete",
            "baseline_tag": "bbws-pre-sr6-onboarding-release",
            "planned_tags": ["v2.0.0-rc1", "bbws-sr6-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "onboarding_contract_freeze",
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
        ROOT / "context" / "ledger" / "bbws_sr6_ledger.md",
        f"""# BBWS SR6 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | PhaseA/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR6 superpowers, resume pack |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR6_ARTIFACTS.md",
        f"""# BBWS SR6 Artifacts

**series_id:** `{SERIES_ID}`  
**product_version_target:** `{PRODUCT_VERSION}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR6_PRODUCT_ONBOARDING_RELEASE_SERIES_MAP.v{VERSION}.md` |
| Resume pack | `context/resume_pack/BBWS_SR6_resume.v{VERSION}.json` |
| Selection map | `docs/BBWS_SR6_SELECTION_MAP.md` |
| START HERE | `START_HERE.md` |
| Coding agent START HERE | `START_HERE_CODING_AGENT.md` |
| Operator onboarding | `docs/OPERATOR_ONBOARDING.md` |
| Intended user | `docs/INTENDED_USER.md` |
| Onboard CLI | `app/best_buds_weight_station/onboard.py` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR6_SELECTION_MAP.md",
        f"""# BBWS SR6 — Salvage → BBWS Selection Map

**series_id:** `{SERIES_ID}`  
**generated:** {NOW}

Cite-only. Do not import salvage runtimes into Best Buds.

| Pattern | Salvage cue | BBWS target |
|---------|-------------|-------------|
| Structured onboarding | KS `_STRUCTURED_ONBOARDING_TEMPLATE.md` | `docs/OPERATOR_ONBOARDING.md` |
| Welcome / audience | KS Series20 welcome onboarding | `START_HERE.md`, `docs/INTENDED_USER.md` |
| Entrypoints | Book Spine `BOOK_ENTRYPOINTS.md` | `onboard.py`, `START_HERE_CODING_AGENT.md` |
| Publication readiness | Book Spine publication checklists | GitHub Release notes + source zip |

**Must not change:** capture loop; JSONL authority; Metrc/legal-for-trade non-claims.
""",
    )
    print(f"BBWS_SR6 Phase A scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
