"""
Scaffold BBWS_SR9 Scale Profile and Stability Governance series.

Focus: per-scale identity/profiles, post-cal characterization, hanging-load
stability gates with recoverable timeout, then 2.0.0-rc4 closeout.

Doctrine cite only (do not mutate M: salvage or Arc Launcher):
- Arc Launcher canonical naming / blueprint factory / git mutation boundary
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR9_scale_profile_stability_governance"
PARENT_SERIES = "BBWS_SR8_scale_face_harvest_mode"
PARENT_TAG = "bbws-sr8-complete"
BASELINE_TAG = "bbws-pre-sr9-scale-profile"
PRODUCT_VERSION = "2.0.0-rc4"
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
]

SEASONS = [
    {
        "id": "S01",
        "slug": "contract_and_baseline_freeze",
        "title": "Scaffold + identity/profile/stability contract freeze",
        "milestone": "M01",
        "focus": "Freeze: rc3 baseline, SR9 laws, identity/profile/stability non-claims",
        "surfaces": [
            "ACTIVE_ARC.yaml",
            "cursor/",
            "scripts/scaffold_bbws_sr9.py",
            "arc_lifecycle/blueprints/",
            "reports/",
        ],
        "episodes": [
            ("Intent freeze: scale profile governance", "context"),
            ("Inventory hanging-load stability model", "context"),
            ("Inventory identity + profile surfaces", "context"),
            ("Write contract freeze receipt", "implement"),
            ("Authorize S02 device identity", "implement"),
            ("Authorize S03–S06 profile/runtime", "implement"),
            ("Authorize S07–S10 UI/validate/rc4", "implement"),
            ("Verify non-claims stamped", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "device_identity_persistence",
        "title": "Firmware EEPROM device identity",
        "milestone": "M02",
        "focus": "SET_DEVICE_ID EEPROM persist, protocol docs, host validation",
        "surfaces": [
            "firmware/elegoo_uno_r3_hx711/",
            "app/best_buds_weight_station/device_service.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: unique board ID", "context"),
            ("EEPROM layout + load/save", "implement"),
            ("SET_DEVICE_ID command + ack", "implement"),
            ("Update SERIAL_PROTOCOL.md", "implement"),
            ("Host set_device_id + simulator", "implement"),
            ("Validate charset/length", "implement"),
            ("Collision handling at host", "implement"),
            ("Verify STATUS reports ID", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "scale_profile_store",
        "title": "Typed atomic scale profile store",
        "milestone": "M03",
        "focus": "CRUD/archive, hash, active-per-device semantics",
        "surfaces": [
            "app/best_buds_weight_station/scale_profiles.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: typed profile store", "context"),
            ("ScaleStabilityParams + ScaleProfile", "implement"),
            ("Atomic JSON under config/scale_profiles", "implement"),
            ("create/update/rename/activate", "implement"),
            ("Archive rejects active without clear", "implement"),
            ("Deterministic profile_hash", "implement"),
            ("Device ID pattern validation", "implement"),
            ("Verify store unit tests", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "calibration_profile_binding",
        "title": "Calibration binds to device profile",
        "milestone": "M04",
        "focus": "Accept cal creates/updates profile; reconnect apply+verify SET_CAL",
        "surfaces": [
            "app/best_buds_weight_station/scale_control.py",
            "app/best_buds_weight_station/application_controller.py",
            "app/best_buds_weight_station/device_service.py",
        ],
        "episodes": [
            ("Intent freeze: cal binds profile", "context"),
            ("accept_calibration writes profile fields", "implement"),
            ("Reconnect load active by device_id", "implement"),
            ("apply_calibration_factor + STATUS verify", "implement"),
            ("Fail closed on verify mismatch", "implement"),
            ("Require ZERO after apply", "implement"),
            ("Keep receipt API intact", "implement"),
            ("Verify reconnect reapply", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "post_cal_stability_characterization",
        "title": "100 g post-cal stability characterization",
        "milestone": "M05",
        "focus": "120-sample characterization, bounded recommend, operator confirm",
        "surfaces": [
            "app/best_buds_weight_station/scale_control.py",
            "app/best_buds_weight_station/scale_profiles.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: 100 g characterization", "context"),
            ("Collect/trim metrics + p95 delta", "implement"),
            ("recommend_stability clamps", "implement"),
            ("Write characterization receipt", "implement"),
            ("Operator confirmation gate", "implement"),
            ("No silent activate on noisy fail", "implement"),
            ("Caps cannot be exceeded", "implement"),
            ("Verify recommend formulas", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "capture_stability_runtime",
        "title": "Capture stability runtime gates",
        "milestone": "M06",
        "focus": "Trend gate, recoverable timeout, snapshot diagnostics",
        "surfaces": [
            "app/best_buds_weight_station/stability.py",
            "app/best_buds_weight_station/models.py",
            "app/best_buds_weight_station/application_controller.py",
            "app/best_buds_weight_station/operator_runtime.py",
        ],
        "episodes": [
            ("Intent freeze: hanging-load gates", "context"),
            ("max_trend_g + recoverable_timeout fields", "implement"),
            ("Trend reject reason trending", "implement"),
            ("timeout_retry reset path", "implement"),
            ("Install resolved profile on run/connect", "implement"),
            ("Snapshot stability diagnostics", "implement"),
            ("Replace settle_ms=0 hang default", "implement"),
            ("Verify regression noise cases", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "profile_management_ui",
        "title": "Scale Setup profile management UI",
        "milestone": "M07",
        "focus": "Identity, profile CRUD/archive, characterization, diagnostics",
        "surfaces": [
            "app/best_buds_weight_station/pyside_frontend.py",
            "app/best_buds_weight_station/scale_face.py",
        ],
        "episodes": [
            ("Intent freeze: setup manager UI", "context"),
            ("List/activate/archive surfaces", "implement"),
            ("Set device ID from UI", "implement"),
            ("Post-cal test + confirm dialog", "implement"),
            ("Unstable-because diagnostics", "implement"),
            ("Scale Face SETUP entry points", "implement"),
            ("Keep capture law untouched", "implement"),
            ("Verify UI wiring presence", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "physical_and_regression_validation",
        "title": "Physical + regression validation",
        "milestone": "M08",
        "focus": "Unit/integration/simulator tests + COM physical checklist",
        "surfaces": ["tests/", "reports/", "docs/"],
        "episodes": [
            ("Intent freeze: validation receipts", "context"),
            ("Frozen capture noise regression", "implement"),
            ("Profile store archive rejection tests", "implement"),
            ("Recoverable timeout tests", "implement"),
            ("Simulator reconnect path", "implement"),
            ("Physical COM checklist draft", "implement"),
            ("Run targeted pytest green", "verify"),
            ("Capture physical receipt if available", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "rc4_windows_packaging",
        "title": "Bump to 2.0.0-rc4 + Windows packaging",
        "milestone": "M09",
        "focus": "Version/drift/manifest; Setup/zip; rc3→rc4 upgrade smoke",
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
            ("Intent freeze: 2.0.0-rc4", "context"),
            ("Bump version surfaces", "implement"),
            ("Add v200_rc4 drift script", "implement"),
            ("Build Setup + portable zip", "implement"),
            ("rc3→rc4 upgrade smoke", "verify"),
            ("Profile preservation check", "verify"),
            ("Regenerate file manifest", "implement"),
            ("Leave archival rc3 receipts untouched", "implement"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "release_and_closeout",
        "title": "SR9 series closeout + tags",
        "milestone": "M10",
        "focus": "Docs/release, tag v2.0.0-rc4 + bbws-sr9-complete, push",
        "surfaces": ["ACTIVE_ARC.yaml", "context/", "git_arc/", "reports/", "docs/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Mark ACTIVE_ARC series_complete", "implement"),
            ("Update resume pack + ledger", "implement"),
            ("Tag v2.0.0-rc4", "implement"),
            ("Tag bbws-sr9-complete", "implement"),
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
    return f"sr9_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "bump VERSION to rc4 before S09",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr9.{season['slug']}.v1",
        "arc_id": f"SR9_{season['id']}_{season['slug']}",
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
        f"""# BBWS SR9 live pointer — product owns truth (salvage cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: contract_and_baseline_freeze
episode_id: S01E01
milestone: M01
status: active
parent_series_id: {PARENT_SERIES}
parent_tag: {PARENT_TAG}
baseline_tag: {BASELINE_TAG}
product_version_target: {PRODUCT_VERSION}
product_version_during_impl: 2.0.0-rc3
doctrine_source: C:/aos_arc_launcher_v0_4_21
updated_at: {NOW}
runtime_claimed: false
capture_law: scan_settle_lock_confirm_reset
next_action: Execute S01E01 contract and baseline freeze
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
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr9_scale_profile_stability_governance.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": PARENT_SERIES,
            "parent_arc_id": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "series_goal": (
                "Fix unrecoverable/over-strict capture stability, add 100 g post-calibration "
                "characterization, and persist calibration plus bounded hanging-load stability "
                f"settings per uniquely identified physical scale; close with {PRODUCT_VERSION}."
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
        ROOT / "manifests" / f"bbws_sr9_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": (
                f"arc_lifecycle/blueprints/series_bbws_sr9_scale_profile_stability_governance.v{VERSION}.json"
            ),
            "cursor_map_ref": f"cursor/BBWS_SR9_SCALE_PROFILE_STABILITY_GOVERNANCE_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR9_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR9_SCALE_PROFILE_STABILITY_GOVERNANCE_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR9 — Scale Profile and Stability Governance Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `{PARENT_SERIES}` / `{PARENT_TAG}`  
**baseline:** `{BASELINE_TAG}`  
**product version target:** `{PRODUCT_VERSION}`  
**product version during impl:** `2.0.0-rc3` (bump in S09)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR9_resume*.json
→ cursor/BBWS_SR9_*_SERIES_MAP*.md
→ superpowers/sr9_sNN_*.json
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
        ROOT / "context" / "resume_pack" / f"BBWS_SR9_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR9_resume",
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
            "product_version_during_impl": "2.0.0-rc3",
            "completed_seasons": [],
            "decision_locks": {
                "capture_loop": "scan_settle_lock_confirm_reset",
                "product_version_target": PRODUCT_VERSION,
                "product_version_during_impl": "2.0.0-rc3",
                "reference_mass_g": 100.0,
                "characterization": "post_cal_100g_120_samples_bounded_recommend",
                "stability_model": "spread_stddev_trend_hold_recoverable_timeout",
                "profile_store": "config/scale_profiles typed atomic CRUD archive",
                "device_identity": "EEPROM SET_DEVICE_ID unique board id",
                "push_cadence": "series_closeout",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR9_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR9_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR9 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}` toward `{PRODUCT_VERSION}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR9_resume.v{VERSION}.json`
3. `cursor/BBWS_SR9_SCALE_PROFILE_STABILITY_GOVERNANCE_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr9_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: capture law/JSONL unchanged; 100 g characterization is not certification; stay on
`2.0.0-rc3` until S09 bumps to `{PRODUCT_VERSION}`; unique firmware device ID required.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR9 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}  
**Product target:** {PRODUCT_VERSION}  
**During impl:** 2.0.0-rc3

Load `ACTIVE_ARC.yaml` and `BBWS_SR9_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "planned_tags": ["v2.0.0-rc4", "bbws-sr9-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "contract_and_baseline_freeze",
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
        ROOT / "context" / "ledger" / "bbws_sr9_ledger.md",
        f"""# BBWS SR9 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | Phase0/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR9 superpowers, resume pack |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR9_ARTIFACTS.md",
        f"""# BBWS SR9 Artifacts

**series_id:** `{SERIES_ID}`  
**product_version_target:** `{PRODUCT_VERSION}`  
**product_version_during_impl:** `2.0.0-rc3`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR9_SCALE_PROFILE_STABILITY_GOVERNANCE_SERIES_MAP.v{VERSION}.md` |
| Resume pack | `context/resume_pack/BBWS_SR9_resume.v{VERSION}.json` |
| Scale profiles | `app/best_buds_weight_station/scale_profiles.py` |
| Stability detector | `app/best_buds_weight_station/stability.py` |
| Firmware identity | `firmware/elegoo_uno_r3_hx711/best_buds_scale_firmware.ino` |
| Contract freeze | `reports/sr9_s01_contract_freeze.v{VERSION}.json` |
| Profile tests | `tests/test_sr9_scale_profiles.py` |
| Stability regression | `tests/test_sr9_stability_regression.py` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )

    write_json(
        ROOT / "reports" / f"sr9_s01_contract_freeze.v{VERSION}.json",
        {
            "receipt_id": "sr9_s01_contract_freeze",
            "series_id": SERIES_ID,
            "season_id": "S01",
            "version": VERSION,
            "status": "accepted",
            "runtime_claimed": False,
            "baseline_tag": BASELINE_TAG,
            "parent_tag": PARENT_TAG,
            "product_version_during_impl": "2.0.0-rc3",
            "product_version_target": PRODUCT_VERSION,
            "acceptance": {
                "capture_law": "scan_settle_lock_confirm_reset",
                "jsonl_authoritative": True,
                "reference_mass_g": 100.0,
                "characterization_samples": 120,
                "characterization_window_s": 6,
                "settle_discard_s": 2,
                "stability_gates": ["max_spread_g", "max_stddev_g", "max_trend_g", "settle_ms", "timeout_ms"],
                "recoverable_timeout": True,
                "profile_caps": {
                    "max_spread_g": [2.0, 15.0],
                    "max_stddev_g": [0.75, 5.0],
                    "max_trend_g": [1.0, 8.0],
                },
                "recommend_formulas": {
                    "max_spread_g": "clamp(max(2.0, 3×baseline_trimmed_spread_g, 0.001×live_weight_g), 2.0, 15.0)",
                    "max_stddev_g": "clamp(max(0.75, 3×baseline_stddev_g, 0.00035×live_weight_g), 0.75, 5.0)",
                    "max_trend_g": "clamp(max(1.0, 2×baseline_p95_delta_g, 0.0005×live_weight_g), 1.0, 8.0)",
                    "minimum_samples": 12,
                    "window_size": 16,
                    "settle_ms": 1200,
                    "timeout_ms": 20000,
                },
                "device_identity": "EEPROM SET_DEVICE_ID unique board id via STATUS",
                "profile_store": "config/scale_profiles typed atomic CRUD with safe archive",
                "reconnect": "identify → load active profile → SET_CAL verify → install StabilityProfile → require ZERO",
                "no_silent_profile_selection": True,
                "version_bump_season": "S09",
            },
            "non_claims": NON_CLAIMS,
        },
    )
    print(f"BBWS_SR9 scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
