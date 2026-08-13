"""
Scaffold BBWS_SR10 Calibration Handshake Integrity series.

Focus: flash 0.1.4+, host matched-ACK for SET_CAL, quiet Accept window,
Alice error split, firmware 0.1.5 stream-interrupt, then 2.0.0-rc5 closeout.

Doctrine cite only (do not mutate M: salvage or Arc Launcher):
- Arc Launcher canonical naming / blueprint factory / git mutation boundary
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR10_calibration_handshake_integrity"
PARENT_SERIES = "BBWS_SR9_scale_profile_stability_governance"
PARENT_TAG = "bbws-sr9-complete"
BASELINE_TAG = "bbws-pre-sr10-cal-handshake"
PRODUCT_VERSION = "2.0.0-rc5"
PRODUCT_DURING = "2.0.0-rc4"
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
    "Matched-ACK handshake is operational integrity only — not certification",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "scaffold_and_flash_014",
        "title": "Scaffold + flash firmware 0.1.4",
        "milestone": "M01",
        "focus": "Freeze SR10 contract; baseline tag; flash 0.1.4; STATUS receipt",
        "surfaces": [
            "ACTIVE_ARC.yaml",
            "cursor/",
            "scripts/scaffold_bbws_sr10.py",
            "arc_lifecycle/blueprints/",
            "firmware/elegoo_uno_r3_hx711/",
            "reports/",
        ],
        "episodes": [
            ("Intent freeze: calibration handshake integrity", "context"),
            ("Inventory Accept/SET_CAL race surfaces", "context"),
            ("Write contract freeze receipt", "implement"),
            ("Tag bbws-pre-sr10-cal-handshake", "implement"),
            ("Flash firmware 0.1.4 on operator COM", "implement"),
            ("Verify STATUS reports 0.1.4", "verify"),
            ("Write physical flash STATUS receipt", "receipt"),
            ("Authorize S02–S06 host/fw work", "implement"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "matched_ack_reader",
        "title": "Host matched-ACK reader",
        "milestone": "M02",
        "focus": "Wait for A,SET_CAL / A,SET_DEVICE_ID / A,STREAM_OFF; skip W and unmatched A",
        "surfaces": [
            "app/best_buds_weight_station/device_service.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: matched ACK", "context"),
            ("Add _read_ack(command)", "implement"),
            ("Wire set_calibration matched ACK", "implement"),
            ("Wire set_device_id matched ACK", "implement"),
            ("Wire start_stream/stop_stream matched ACK", "implement"),
            ("Distinct timeout vs unmatched ACK errors", "implement"),
            ("Keep simulator A,CAL_SET compatible", "implement"),
            ("Verify unit tests for matcher", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "quiet_accept_window",
        "title": "Quiet Accept command window",
        "milestone": "M03",
        "focus": "Worker stays stopped through SET_CAL + STATUS verify; longer STREAM_OFF drain",
        "surfaces": [
            "app/best_buds_weight_station/operator_runtime.py",
            "app/best_buds_weight_station/device_service.py",
        ],
        "episodes": [
            ("Intent freeze: quiet Accept window", "context"),
            ("Increase post-STREAM_OFF drain", "implement"),
            ("Keep worker stopped through Accept", "implement"),
            ("STATUS verify before worker restart", "implement"),
            ("Same quiet window for set_device_id", "implement"),
            ("Flush input after stop_stream", "implement"),
            ("Preserve reconnect profile apply path", "implement"),
            ("Verify Accept quiet path", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "alice_error_split",
        "title": "Alice error message split",
        "milestone": "M04",
        "focus": "Split leftover ACK vs raw HX711 dump vs BAD_CAL — stop calling all streaming",
        "surfaces": [
            "app/best_buds_weight_station/alice/authority.py",
            "tests/",
        ],
        "episodes": [
            ("Intent freeze: Alice copy split", "context"),
            ("Leftover ACK / unmatched command message", "implement"),
            ("Keep raw HX711 dump message", "implement"),
            ("BAD_CAL / calibration rejected message", "implement"),
            ("Drop blanket set_cal → streaming rewrite", "implement"),
            ("Preserve serial/permission messages", "implement"),
            ("Add authority unit coverage", "implement"),
            ("Verify Alice mapping cases", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "firmware_015_stream_interrupt",
        "title": "Firmware 0.1.5 stream interrupt",
        "milestone": "M05",
        "focus": "Abort waitHx711Ready when Serial.available; bump protocol to 0.1.5",
        "surfaces": [
            "firmware/elegoo_uno_r3_hx711/",
        ],
        "episodes": [
            ("Intent freeze: interruptible HX711 wait", "context"),
            ("Serial.available abort in waitHx711Ready", "implement"),
            ("Bump firmwareVersion to 0.1.5", "implement"),
            ("Update SERIAL_PROTOCOL.md", "implement"),
            ("Keep SET_CAL/SET_DEVICE_ID behavior", "implement"),
            ("Keep non-blocking setup", "implement"),
            ("Document flash side-effect (RAM cal reset)", "implement"),
            ("Verify sketch compiles or syntax-check", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "scripted_handshake_tests",
        "title": "Scripted handshake regression tests",
        "milestone": "M06",
        "focus": "Interleaved W + STREAM_OFF ACK then SET_CAL ACK must succeed",
        "surfaces": ["tests/", "reports/"],
        "episodes": [
            ("Intent freeze: handshake tests", "context"),
            ("ScriptedTransport interleaved W case", "implement"),
            ("Unmatched ACK distinct failure", "implement"),
            ("Simulator A,CAL_SET still accepted", "implement"),
            ("STREAM_OFF matched ACK test", "implement"),
            ("SET_DEVICE_ID matched ACK test", "implement"),
            ("Run pytest green", "verify"),
            ("Write S06 test receipt", "receipt"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "physical_accept_characterize",
        "title": "Physical Accept + characterize",
        "milestone": "M07",
        "focus": "Flash 0.1.5; Connect/profile apply; Guided Cal Accept; 100 g Confirm",
        "surfaces": ["firmware/", "reports/", "docs/"],
        "episodes": [
            ("Intent freeze: physical validation", "context"),
            ("Flash firmware 0.1.5", "implement"),
            ("Connect and re-apply profile SET_CAL", "verify"),
            ("Guided Cal Accept succeeds", "verify"),
            ("100 g characterize Confirm", "verify"),
            ("ZERO then Lock path smoke", "verify"),
            ("Write physical receipt", "receipt"),
            ("Document operator recovery if blocked", "implement"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "docs_and_operator_recovery",
        "title": "Docs + operator Accept recovery",
        "milestone": "M08",
        "focus": "Bring-up flash steps, SERIAL_PROTOCOL 0.1.5, Accept recovery copy",
        "surfaces": [
            "docs/",
            "firmware/elegoo_uno_r3_hx711/SERIAL_PROTOCOL.md",
            "docs/OPERATOR_ONBOARDING.md",
            "docs/WINDOWS_DEVICE_BRINGUP.md",
        ],
        "episodes": [
            ("Intent freeze: docs only", "context"),
            ("Bring-up flash 0.1.5 steps", "implement"),
            ("SERIAL_PROTOCOL notes for interruptible wait", "implement"),
            ("Operator Accept recovery steps", "implement"),
            ("BBWS_SR10_ARTIFACTS.md", "implement"),
            ("Keep non-claims stamped", "implement"),
            ("No capture-law doc drift", "verify"),
            ("Verify docs paths exist", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "rc5_windows_packaging",
        "title": "Bump to 2.0.0-rc5 + Windows packaging",
        "milestone": "M09",
        "focus": "Version/drift/manifest; Setup/zip; rc4→rc5 upgrade smoke",
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
            ("Intent freeze: 2.0.0-rc5", "context"),
            ("Bump version surfaces", "implement"),
            ("Add/refresh drift script if needed", "implement"),
            ("Build Setup + portable zip", "implement"),
            ("rc4→rc5 upgrade smoke", "verify"),
            ("Profile preservation check", "verify"),
            ("Regenerate file manifest", "implement"),
            ("Leave archival rc4 receipts untouched", "implement"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "release_and_closeout",
        "title": "SR10 series closeout + tags",
        "milestone": "M10",
        "focus": "Docs/release, tag v2.0.0-rc5 + bbws-sr10-complete, push",
        "surfaces": ["ACTIVE_ARC.yaml", "context/", "git_arc/", "reports/", "docs/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Mark ACTIVE_ARC series_complete", "implement"),
            ("Update resume pack + ledger", "implement"),
            ("Tag v2.0.0-rc5", "implement"),
            ("Tag bbws-sr10-complete", "implement"),
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
    return f"sr10_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "bump VERSION to rc5 before S09",
                    "input-integrity bootstrap as SR8/SR10",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr10.{season['slug']}.v1",
        "arc_id": f"SR10_{season['id']}_{season['slug']}",
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
        f"""# BBWS SR10 live pointer — product owns truth (salvage cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: scaffold_and_flash_014
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
next_action: Execute S01 scaffold + flash firmware 0.1.4
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
        / f"series_bbws_sr10_calibration_handshake_integrity.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": PARENT_SERIES,
            "parent_arc_id": PARENT_TAG,
            "baseline_tag": BASELINE_TAG,
            "product_version_target": PRODUCT_VERSION,
            "series_goal": (
                "Fix Guided Calibration Accept failures caused by interleaved stream ACKs, "
                "align firmware to 0.1.4/0.1.5, split Alice error copy, and close with "
                f"{PRODUCT_VERSION}."
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
        ROOT / "manifests" / f"bbws_sr10_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": (
                f"arc_lifecycle/blueprints/series_bbws_sr10_calibration_handshake_integrity.v{VERSION}.json"
            ),
            "cursor_map_ref": f"cursor/BBWS_SR10_CALIBRATION_HANDSHAKE_INTEGRITY_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR10_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR10_CALIBRATION_HANDSHAKE_INTEGRITY_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR10 — Calibration Handshake Integrity Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `{PARENT_SERIES}` / `{PARENT_TAG}`  
**baseline:** `{BASELINE_TAG}`  
**product version target:** `{PRODUCT_VERSION}`  
**product version during impl:** `{PRODUCT_DURING}` (bump in S09)

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR10_resume*.json
→ cursor/BBWS_SR10_*_SERIES_MAP*.md
→ superpowers/sr10_sNN_*.json
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
        ROOT / "context" / "resume_pack" / f"BBWS_SR10_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR10_resume",
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
                "matched_ack": "SET_CAL_SET_DEVICE_ID_STREAM_OFF",
                "firmware_flash_s01": "0.1.4",
                "firmware_target": "0.1.5",
                "push_cadence": "series_closeout",
                "input_integrity": "deferred_to_later_series",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR10_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR10_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR10 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}` toward `{PRODUCT_VERSION}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR10_resume.v{VERSION}.json`
3. `cursor/BBWS_SR10_CALIBRATION_HANDSHAKE_INTEGRITY_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr10_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: capture law/JSONL unchanged; stay on `{PRODUCT_DURING}` until S09 bumps to
`{PRODUCT_VERSION}`; flash 0.1.4 in S01 then 0.1.5 in S05/S07; input-integrity deferred.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR10 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}  
**Product target:** {PRODUCT_VERSION}  
**During impl:** {PRODUCT_DURING}

Load `ACTIVE_ARC.yaml` and `BBWS_SR10_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "planned_tags": ["v2.0.0-rc5", "bbws-sr10-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "scaffold_and_flash_014",
            "milestone": "M01",
            "commit_plan": "Commit S01 scaffold after flash receipt",
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
        ROOT / "context" / "ledger" / "bbws_sr10_ledger.md",
        f"""# BBWS SR10 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | Phase0/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR10 superpowers, resume pack |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR10_ARTIFACTS.md",
        f"""# BBWS SR10 Artifacts

**series_id:** `{SERIES_ID}`  
**product_version_target:** `{PRODUCT_VERSION}`  
**product_version_during_impl:** `{PRODUCT_DURING}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR10_CALIBRATION_HANDSHAKE_INTEGRITY_SERIES_MAP.v{VERSION}.md` |
| Resume pack | `context/resume_pack/BBWS_SR10_resume.v{VERSION}.json` |
| Device service (matched ACK) | `app/best_buds_weight_station/device_service.py` |
| Operator Accept quiet window | `app/best_buds_weight_station/operator_runtime.py` |
| Alice authority | `app/best_buds_weight_station/alice/authority.py` |
| Firmware | `firmware/elegoo_uno_r3_hx711/best_buds_scale_firmware.ino` |
| Contract freeze | `reports/sr10_s01_contract_freeze.v{VERSION}.json` |
| Handshake tests | `tests/test_sr10_calibration_handshake.py` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )

    write_json(
        ROOT / "reports" / f"sr10_s01_contract_freeze.v{VERSION}.json",
        {
            "receipt_id": "sr10_s01_contract_freeze",
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
                "matched_ack_commands": ["SET_CAL", "SET_DEVICE_ID", "STREAM_ON", "STREAM_OFF"],
                "skip_kinds_during_ack_wait": ["W"],
                "firmware_flash_s01": "0.1.4",
                "firmware_target": "0.1.5",
                "quiet_accept_window": True,
                "alice_error_split": ["leftover_ack", "raw_hx711_dump", "bad_cal"],
                "version_bump_season": "S09",
                "input_integrity_deferred": True,
            },
            "non_claims": NON_CLAIMS,
        },
    )
    print(f"BBWS_SR10 scaffold complete series={SERIES_ID} product={PRODUCT_VERSION}")


if __name__ == "__main__":
    main()
