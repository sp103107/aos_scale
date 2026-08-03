"""
Scaffold BBWS_SR2 Tk/Linux + display-units 100-arc series (Phase A).

Generates ACTIVE_ARC, blueprint, series map, SR2 superpowers, resume pack,
git_arc pointers, and kickoff. Does not implement product features.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR2_tk_linux_display_units"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SEASONS = [
    {
        "id": "S01",
        "slug": "tk_gap_audit",
        "title": "Tk/Linux gap audit vs PySide SR1",
        "milestone": "M01",
        "focus": "Freeze parity matrix; no feature inventing",
        "surfaces": ["production_ui.py", "pyside_frontend.py", "docs/"],
        "episodes": [
            ("Intent freeze: Tk/Linux parity goals", "context"),
            ("Inventory PySide SR1 surfaces", "context"),
            ("Inventory Tk production_ui gaps", "context"),
            ("Linux launcher/Debian gap notes", "context"),
            ("Write gap matrix receipt", "implement"),
            ("Authorize S02–S06 Tk port scope", "implement"),
            ("Authorize S07–S08 display-unit scope", "implement"),
            ("Verify non-claims stamped", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "tk_recording_polish",
        "title": "Tk recording polish parity",
        "milestone": "M02",
        "focus": "Confirm pacing, duplicate warning, cancel→focus",
        "surfaces": ["production_ui.py"],
        "episodes": [
            ("Intent freeze: Tk recording polish", "context"),
            ("Soft confirm status pacing", "implement"),
            ("Duplicate warning path", "implement"),
            ("Cancel clears barcode + focus", "implement"),
            ("Empty barcode blocked copy", "implement"),
            ("Saved copy with cultivar", "implement"),
            ("Manual capture verify", "verify"),
            ("Focus reclaim verify", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "tk_hid_scanner",
        "title": "Tk HID scanner + barcode policy",
        "milestone": "M03",
        "focus": "Test Scanner receipts; barcode policy settings",
        "surfaces": ["production_ui.py", "settings.py"],
        "episodes": [
            ("Intent freeze: HID wedge only", "context"),
            ("Test Scanner dialog", "implement"),
            ("Scanner receipt write path", "implement"),
            ("Barcode focus ownership", "implement"),
            ("Station settings barcode policy", "implement"),
            ("Auto ID when policy off", "implement"),
            ("HID-only verify", "verify"),
            ("Policy toggle verify", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "tk_sticky_strain",
        "title": "Tk sticky strain parity",
        "milestone": "M04",
        "focus": "Change Strain + active banner",
        "surfaces": ["production_ui.py"],
        "episodes": [
            ("Intent freeze: sticky until changed", "context"),
            ("Active strain banner", "implement"),
            ("Change Strain dialog", "implement"),
            ("Menu entry for strain", "implement"),
            ("Snapshot cultivar display", "implement"),
            ("Mid-run change verify", "verify"),
            ("Non-claim Metrc stamp", "verify"),
            ("Capture stamp verify", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "tk_csv_recover",
        "title": "Tk CSV rebuild / pending_sync / recover",
        "milestone": "M05",
        "focus": "Rebuild and soft recover paths in Tk",
        "surfaces": ["production_ui.py"],
        "episodes": [
            ("Intent freeze: JSONL authoritative", "context"),
            ("Pending sync banner", "implement"),
            ("Rebuild CSV menu action", "implement"),
            ("Recover soft path", "implement"),
            ("Status copy after rebuild", "implement"),
            ("Menu wiring verify", "verify"),
            ("Pending clear after rebuild verify", "verify"),
            ("Non-destructive recover verify", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "tk_export_reconcile",
        "title": "Tk export + reconcile",
        "milestone": "M06",
        "focus": "Export handoff + reconcile gate messaging",
        "surfaces": ["production_ui.py"],
        "episodes": [
            ("Intent freeze: export derivatives", "context"),
            ("Export copies plant CSV", "implement"),
            ("Reconcile after export", "implement"),
            ("Reconcile menu action", "implement"),
            ("Fail gate messaging", "implement"),
            ("Pass gate verify", "verify"),
            ("JSONL authority copy verify", "verify"),
            ("Windows path safety verify", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "display_unit_core",
        "title": "Display-unit core",
        "milestone": "M07",
        "focus": "g/kg/lb display setting; grams stored",
        "surfaces": ["units.py", "settings.py", "operator_runtime.py", "actions.py"],
        "episodes": [
            ("Intent freeze: display-only units", "context"),
            ("units conversion helper", "implement"),
            ("display_unit on AppSettings", "implement"),
            ("settings.display_unit.set action", "implement"),
            ("Snapshot display fields", "implement"),
            ("Unit conversion tests/smoke", "verify"),
            ("Storage remains grams verify", "verify"),
            ("Firmware unchanged verify", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "display_unit_uis",
        "title": "Display unit in PySide + Tk",
        "milestone": "M08",
        "focus": "Weight/tare/net/cal entry use display unit",
        "surfaces": ["pyside_frontend.py", "production_ui.py"],
        "episodes": [
            ("Intent freeze: dual-UI display unit", "context"),
            ("PySide weight labels", "implement"),
            ("Tk weight labels", "implement"),
            ("Settings picker both UIs", "implement"),
            ("Cal reference convert to grams", "implement"),
            ("Tare known-value convert", "implement"),
            ("PySide display verify", "verify"),
            ("Tk display verify", "verify"),
            ("S08 receipt + M08 tag plan", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "linux_smoke",
        "title": "Linux launchers + Xvfb Tk smoke",
        "milestone": "M09",
        "focus": "Source launch docs + smoke script/receipt",
        "surfaces": ["launch_best_buds.sh", "docs/DEBIAN_INSTALL.md", "scripts/"],
        "episodes": [
            ("Intent freeze: Linux secondary", "context"),
            ("Launcher notes refresh", "implement"),
            ("Debian install notes", "implement"),
            ("Xvfb Tk smoke script", "implement"),
            ("Smoke receipt schema", "implement"),
            ("Windows note: Linux not claimed", "implement"),
            ("Script dry-run verify", "verify"),
            ("Non-claims verify", "verify"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "dual_ui_closeout",
        "title": "Dual-UI regression + series closeout",
        "milestone": "M10",
        "focus": "Parity matrix complete + bbws-sr2-complete tag",
        "surfaces": ["reports/", "context/resume_pack/"],
        "episodes": [
            ("Intent freeze: series end", "context"),
            ("Dual-UI regression matrix", "implement"),
            ("Series closeout report", "implement"),
            ("Resume pack series_complete", "implement"),
            ("Tag policy lock", "implement"),
            ("Final non-claims stamp", "implement"),
            ("Smoke verify", "verify"),
            ("Map complete stamp", "verify"),
            ("S10 receipt pack", "receipt"),
            ("M10 series closeout + tag plan", "closeout"),
        ],
    },
]

NON_CLAIMS = [
    "Display lb/kg ≠ legal-for-trade / NTEP",
    "Tk parity ≠ Windows packaging seal",
    "Linux smoke ≠ Debian production guarantee",
    "Display unit ≠ changing authoritative ledger units",
    "Arc Launcher not claimed as live runtime for Best Buds",
]


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def episode_id(season_id: str, n: int) -> str:
    return f"{season_id}E{n:02d}"


def sp_name(season: dict) -> str:
    return f"sr2_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "firmware SET_UNIT kg/lb",
                    "rename CSV *_g columns",
                    "BLE/SPP scanner",
                    "Arc Launcher / M: mutation",
                    "auto-push mid-episode",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr2.{season['slug']}.v1",
        "arc_id": f"SR2_{season['id']}_{season['slug']}",
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
        f"""# BBWS SR2 live pointer — product owns truth (Arc Launcher cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: tk_gap_audit
episode_id: S01E01
milestone: M01
status: active
parent_series_id: BBWS_SR1_harvest_operator_loop
parent_tag: bbws-sr1-complete
baseline_freeze: v0.1.9-rc2
doctrine_source: C:/aos_arc_launcher_v0_4_21
updated_at: {NOW}
runtime_claimed: false
units_law: display_only_g_kg_lb_storage_grams
next_action: Execute S01E01 Tk/Linux gap audit
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
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr2_tk_linux_display_units.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": "BBWS_SR1_harvest_operator_loop",
            "parent_arc_id": "bbws-sr1-complete",
            "series_goal": (
                "Tk/Linux operator parity with SR1 features plus display-unit selection "
                "(g/kg/lb) while keeping grams authoritative in JSONL."
            ),
            "runtime_claimed": False,
            "version": VERSION,
            "shape": "10 seasons × 10 episodes = 100",
            "units_law": "display_only",
            "tk_law": "secondary_fallback_shared_runtime",
            "linux_law": "source_plus_xvfb_smoke_no_new_gui_installer",
            "github_push_cadence": "after_each_season_closeout",
            "seasons": seasons_bp,
            "total_episodes": 100,
            "non_claims": NON_CLAIMS,
        },
    )

    write_json(
        ROOT / "manifests" / f"bbws_sr2_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr2_tk_linux_display_units.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR2_TK_LINUX_DISPLAY_UNITS_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR2_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR2_TK_LINUX_DISPLAY_UNITS_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR2 — Tk/Linux + Display Units Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR1_harvest_operator_loop` / `bbws-sr1-complete`  
**units law:** display-only g/kg/lb; JSONL stays grams

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR2_resume*.json
→ cursor/BBWS_SR2_*_SERIES_MAP*.md
→ superpowers/sr2_sNN_*.json (current season)
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
        ROOT / "context" / "resume_pack" / f"BBWS_SR2_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR2_resume",
            "version": VERSION,
            "series_id": SERIES_ID,
            "updated_at": NOW,
            "active": {
                "season_id": "S01",
                "episode_id": "S01E01",
                "milestone": "M01",
                "status": "ready_to_execute",
            },
            "parent_series": "BBWS_SR1_harvest_operator_loop",
            "completed_seasons": [],
            "decision_locks": {
                "units": "display_only_g_kg_lb",
                "storage": "grams_authoritative",
                "tk": "secondary_shared_runtime",
                "linux": "source_xvfb_smoke",
                "push_cadence": "season_closeout_only",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR2_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR2_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR2 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR2_resume.v{VERSION}.json`
3. `cursor/BBWS_SR2_TK_LINUX_DISPLAY_UNITS_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr2_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: display units only; grams in JSONL; Tk shares OperatorRuntime; no firmware multi-unit; push after E10 only.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR2 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}

Load `ACTIVE_ARC.yaml` and `BBWS_SR2_resume.v{VERSION}.json`, then execute the pointed episode.
""",
    )

    write_json(
        ROOT / "git_arc" / "active" / "series_pointer.v0.1.0.json",
        {
            "series_id": SERIES_ID,
            "branch_plan": "main",
            "remote_plan": "origin",
            "push_policy": "after_season_closeout_only",
            "auto_push": False,
            "parent_tag": "bbws-sr1-complete",
            "planned_tags": ["v0.1.9-bbws-sr2-s08", "bbws-sr2-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "tk_gap_audit",
            "milestone": "M01",
            "commit_plan": "Commit S01 gap audit after E10 closeout",
            "push_plan": "git push origin HEAD after season closeout",
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

    ledger = ROOT / "context" / "ledger" / "bbws_sr2_ledger.md"
    write_text(
        ledger,
        f"""# BBWS SR2 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | PhaseA | Scaffold ACTIVE_ARC, blueprint, maps, SR2 superpowers, resume pack, git_arc |
""",
    )
    print(f"BBWS_SR2 Phase A scaffold complete series={SERIES_ID}")


if __name__ == "__main__":
    main()
