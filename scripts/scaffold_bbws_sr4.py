"""
Scaffold BBWS_SR4 operator surface polish 100-arc series (Phase A / S01).

Generates ACTIVE_ARC, blueprint, series map, SR4 superpowers, resume pack,
git_arc pointers, and kickoff. Does not implement product features.

Doctrine cite only (do not mutate Arc Launcher):
- next_ten_episodes_frontend_backend_polish.v0.4.36.json
- s50_operator_ux_graphics_hardening.v0.4.50.json
Salvage design ref: M:/SALVAGE/CAPSULES/front_end_graphics/aos_ks_frontend_flow_graphics_v0_1_43
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR4_operator_surface_polish"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

NON_CLAIMS = [
    "Salvage capsule is design reference only — no React import into BBWS",
    "Visual polish is not legal-for-trade or Metrc compliance",
    "Arc Launcher is cited doctrine, not mutated as Best Buds runtime",
    "Status color aids must remain text-labeled (not color-only)",
    "Capture loop unchanged: scan → settle → lock → confirm → reset",
    "Run artifact polish (CSV/XLSX/DOCX) is BBWS SR5, not this series",
]

SEASONS = [
    {
        "id": "S01",
        "slug": "polish_contract_freeze",
        "title": "Scaffold + polish contract freeze",
        "milestone": "M01",
        "focus": "Freeze polish-vs-capture contract, salvage selection map, non-claims",
        "surfaces": ["ACTIVE_ARC.yaml", "cursor/", "docs/", "scripts/scaffold_bbws_sr4.py"],
        "episodes": [
            ("Intent freeze: polish vs capture", "context"),
            ("Inventory salvage CSS tokens", "context"),
            ("Inventory PySide/Tk surfaces", "context"),
            ("Write selection map receipt", "implement"),
            ("Authorize S02–S03 token scope", "implement"),
            ("Authorize S04–S07 surface scope", "implement"),
            ("Authorize S08 Tk parity scope", "implement"),
            ("Verify no-workflow-change rule", "verify"),
            ("S01 receipt pack", "receipt"),
            ("M01 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S02",
        "slug": "salvage_token_extract",
        "title": "Extract BBWS design tokens from salvage",
        "milestone": "M02",
        "focus": "Colors, radius, eyebrow, pill, metric tokens from salvage CSS",
        "surfaces": ["docs/", "app/best_buds_weight_station/ui_tokens.py"],
        "episodes": [
            ("Intent freeze: token names", "context"),
            ("Map salvage colors/radii", "implement"),
            ("Map eyebrow/pill/metric patterns", "implement"),
            ("Draft BBWS token table", "implement"),
            ("Wire token constants module", "implement"),
            ("Reject React import", "implement"),
            ("Verify token coverage", "verify"),
            ("Non-claim stamp tokens ≠ Metrc", "verify"),
            ("S02 receipt pack", "receipt"),
            ("M02 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S03",
        "slug": "pyside_shell_tokens",
        "title": "Apply token sheet to PySide shell",
        "milestone": "M03",
        "focus": "APP_STYLE: top bar, status, cards, buttons, scroll chrome",
        "surfaces": ["app/best_buds_weight_station/pyside_frontend.py"],
        "episodes": [
            ("Intent freeze: shell tokens only", "context"),
            ("Apply background/card/border tokens", "implement"),
            ("Button hover/focus rings", "implement"),
            ("Menu/status bar chrome", "implement"),
            ("Weight display metric scale", "implement"),
            ("Keep green Confirm", "implement"),
            ("Verify no layout reflow", "verify"),
            ("Verify capture callbacks unchanged", "verify"),
            ("S03 receipt pack", "receipt"),
            ("M03 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S04",
        "slug": "eyebrow_status_hierarchy",
        "title": "Eyebrow + status-pill hierarchy",
        "milestone": "M04",
        "focus": "Eyebrows and text-labeled status pills on cards",
        "surfaces": ["app/best_buds_weight_station/pyside_frontend.py"],
        "episodes": [
            ("Intent freeze: hierarchy language", "context"),
            ("Eyebrow on barcode/Alice/log", "implement"),
            ("Status pill Ready/Stable/Locked/Saved", "implement"),
            ("Metric label hierarchy", "implement"),
            ("objectName hooks for styles", "implement"),
            ("Keep accessibility text", "implement"),
            ("Verify text not color-only", "verify"),
            ("Verify no state-machine change", "verify"),
            ("S04 receipt pack", "receipt"),
            ("M04 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S05",
        "slug": "scan_dialog_polish",
        "title": "Scan capture dialog professional chrome",
        "milestone": "M05",
        "focus": "Capture-mode Scan dialog polish; Enter→submit unchanged",
        "surfaces": ["app/best_buds_weight_station/pyside_frontend.py"],
        "episodes": [
            ("Intent freeze: dialog chrome only", "context"),
            ("Capture dialog eyebrow", "implement"),
            ("Focus field polish", "implement"),
            ("Status line polish", "implement"),
            ("Keep Enter→submit", "implement"),
            ("Menu Test Scanner distinct", "implement"),
            ("Verify gated-until-ready", "verify"),
            ("Verify no workflow change", "verify"),
            ("S05 receipt pack", "receipt"),
            ("M05 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S06",
        "slug": "lock_receipt_polish",
        "title": "Locked-weight + last-saved receipt language",
        "milestone": "M06",
        "focus": "Metric/receipt presentation for lock and last-saved",
        "surfaces": ["app/best_buds_weight_station/pyside_frontend.py"],
        "episodes": [
            ("Intent freeze: presentation only", "context"),
            ("Locked weight metric presentation", "implement"),
            ("Last-saved receipt tone", "implement"),
            ("Confirm-clear lock UI unchanged", "implement"),
            ("Metric scale for locked value", "implement"),
            ("Status pill Locked/Saved", "implement"),
            ("Verify manual loop", "verify"),
            ("Verify lock action wiring", "verify"),
            ("S06 receipt pack", "receipt"),
            ("M06 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S07",
        "slug": "log_dialog_polish",
        "title": "Plant log + run dialog chrome",
        "milestone": "M07",
        "focus": "Plant log list + New Run / Change Strain dialog chrome",
        "surfaces": ["app/best_buds_weight_station/pyside_frontend.py"],
        "episodes": [
            ("Intent freeze: list/dialog chrome", "context"),
            ("Plant log quiet list styling", "implement"),
            ("New Run Cultivator/Strain dialog chrome", "implement"),
            ("Change Strain dialog chrome", "implement"),
            ("About/copy consistency", "implement"),
            ("Eyebrow on plant log card", "implement"),
            ("Verify CSV fields untouched", "verify"),
            ("Verify dialog callbacks", "verify"),
            ("S07 receipt pack", "receipt"),
            ("M07 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S08",
        "slug": "tk_surface_parity",
        "title": "Tk visual parity",
        "milestone": "M08",
        "focus": "Tk colors, eyebrows, Scan dialog, metrics parity",
        "surfaces": ["app/best_buds_weight_station/production_ui.py"],
        "episodes": [
            ("Intent freeze: Tk shared polish language", "context"),
            ("Tk colors/fonts from tokens", "implement"),
            ("Tk Scan popup polish parity", "implement"),
            ("Tk CULTIVATOR/STRAIN metric labels", "implement"),
            ("Tk eyebrows/status text", "implement"),
            ("No new Tk business rules", "implement"),
            ("Dual-UI smoke verify", "verify"),
            ("Non-claim stamp", "verify"),
            ("S08 receipt pack", "receipt"),
            ("M08 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S09",
        "slug": "polish_verify_docs",
        "title": "Tests + dual-UI smoke + non-claims",
        "milestone": "M09",
        "focus": "Style/contract tests and operator polish runbook",
        "surfaces": ["tests/", "docs/"],
        "episodes": [
            ("Intent freeze: verify only", "context"),
            ("Style/contract tests", "implement"),
            ("Operator polish runbook note", "implement"),
            ("BBWS_SR4_ARTIFACTS index", "implement"),
            ("Non-claims page stamp", "implement"),
            ("Dual-UI smoke notes", "implement"),
            ("Pytest green verify", "verify"),
            ("Capture loop unchanged verify", "verify"),
            ("S09 receipt pack", "receipt"),
            ("M09 season closeout + push plan", "closeout"),
        ],
    },
    {
        "id": "S10",
        "slug": "series_closeout",
        "title": "Series closeout + bbws-sr4-complete",
        "milestone": "M10",
        "focus": "ACTIVE_ARC series_complete + tag + push",
        "surfaces": ["ACTIVE_ARC.yaml", "reports/", "git_arc/"],
        "episodes": [
            ("Intent freeze: closeout only", "context"),
            ("Season ledger complete", "implement"),
            ("Closeout report", "implement"),
            ("ACTIVE_ARC series_complete", "implement"),
            ("Tag bbws-sr4-complete", "implement"),
            ("Push origin HEAD + tags", "implement"),
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
    return f"sr4_{season['id'].lower()}_{season['slug']}.v{VERSION}.json"


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
                    "run artifact polish SR5",
                    "React import from salvage",
                    "firmware SET_UNIT kg/lb",
                    "BLE/SPP scanner",
                    "Metrc sync",
                    "Arc Launcher / M: mutation",
                    "auto-push mid-episode",
                ],
                "acceptance": f"{eid} produces context receipt or season closeout when kind is receipt/closeout",
                "runtime_claimed": False,
            }
        )
    return {
        "version": VERSION,
        "schema_version": f"bbws.sr4.{season['slug']}.v1",
        "arc_id": f"SR4_{season['id']}_{season['slug']}",
        "series_id": SERIES_ID,
        "title": season["title"],
        "milestone": season["milestone"],
        "focus": season["focus"],
        "runtime_claimed": False,
        "primary_surfaces": season["surfaces"],
        "episodes": episodes,
        "non_claims": NON_CLAIMS,
        "doctrine_cite": [
            "C:/aos_arc_launcher_v0_4_21/superpowers/next_ten_episodes_frontend_backend_polish.v0.4.36.json",
            "C:/aos_arc_launcher_v0_4_21/superpowers/s50_operator_ux_graphics_hardening.v0.4.50.json",
        ],
        "salvage_graphics_ref": (
            "M:/SALVAGE/CAPSULES/front_end_graphics/aos_ks_frontend_flow_graphics_v0_1_43"
        ),
    }


def main() -> None:
    write_text(
        ROOT / "ACTIVE_ARC.yaml",
        f"""# BBWS SR4 live pointer — product owns truth (Arc Launcher cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: S01
season_slug: polish_contract_freeze
episode_id: S01E01
milestone: M01
status: active
parent_series_id: BBWS_SR3_station_capture_ux
parent_tag: bbws-sr3-complete
baseline_tag: bbws-pre-sr4-polish
baseline_freeze: v0.1.9-rc2
doctrine_source: C:/aos_arc_launcher_v0_4_21
salvage_graphics_ref: M:/SALVAGE/CAPSULES/front_end_graphics/aos_ks_frontend_flow_graphics_v0_1_43
updated_at: {NOW}
runtime_claimed: false
capture_law: scan_settle_lock_confirm_reset
polish_law: styles_labels_dialogs_only
next_action: Execute S01E01 polish contract freeze
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
        ROOT / "arc_lifecycle" / "blueprints" / f"series_bbws_sr4_operator_surface_polish.v{VERSION}.json",
        {
            "blueprint_type": "series",
            "blueprint_id": SERIES_ID,
            "parent_series_id": "BBWS_SR3_station_capture_ux",
            "parent_arc_id": "bbws-sr3-complete",
            "baseline_tag": "bbws-pre-sr4-polish",
            "series_goal": (
                "Polish Best Buds operator surface using salvage design tokens "
                "(eyebrow, status pills, metric hierarchy, dialog chrome) without "
                "changing capture workflow. Run-artifact polish deferred to SR5."
            ),
            "runtime_claimed": False,
            "version": VERSION,
            "shape": "10 seasons × 10 episodes = 100",
            "capture_law": "scan_settle_lock_confirm_reset",
            "polish_law": "styles_labels_dialogs_only",
            "github_push_cadence": "after_series_closeout",
            "seasons": seasons_bp,
            "total_episodes": 100,
            "non_claims": NON_CLAIMS,
            "doctrine_cite": [
                "C:/aos_arc_launcher_v0_4_21/superpowers/next_ten_episodes_frontend_backend_polish.v0.4.36.json",
                "C:/aos_arc_launcher_v0_4_21/superpowers/s50_operator_ux_graphics_hardening.v0.4.50.json",
            ],
            "salvage_graphics_ref": (
                "M:/SALVAGE/CAPSULES/front_end_graphics/aos_ks_frontend_flow_graphics_v0_1_43"
            ),
        },
    )

    write_json(
        ROOT / "manifests" / f"bbws_sr4_series_map.v{VERSION}.json",
        {
            "manifest_type": "series_map",
            "series_id": SERIES_ID,
            "version": VERSION,
            "generated_at": NOW,
            "blueprint_ref": f"arc_lifecycle/blueprints/series_bbws_sr4_operator_surface_polish.v{VERSION}.json",
            "cursor_map_ref": f"cursor/BBWS_SR4_OPERATOR_SURFACE_POLISH_SERIES_MAP.v{VERSION}.md",
            "active_arc_ref": "ACTIVE_ARC.yaml",
            "resume_pack_ref": f"context/resume_pack/BBWS_SR4_resume.v{VERSION}.json",
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
        ROOT / "cursor" / f"BBWS_SR4_OPERATOR_SURFACE_POLISH_SERIES_MAP.v{VERSION}.md",
        f"""# BBWS SR4 — Operator Surface Polish Series Map

**series_id:** `{SERIES_ID}`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR3_station_capture_ux` / `bbws-sr3-complete`  
**baseline:** `bbws-pre-sr4-polish`  
**polish law:** styles / eyebrows / pills / dialog chrome only  
**capture law (unchanged):** scan → settle → lock → confirm → reset

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR4_resume*.json
→ cursor/BBWS_SR4_*_SERIES_MAP*.md
→ superpowers/sr4_sNN_*.json (current season)
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
{rows}

## Salvage selection map (cite-only)

| Pattern | Salvage source | BBWS target |
|---------|----------------|-------------|
| Eyebrow label | professional-business-components.css | Card section titles |
| Status pill | cockpit status-pill patterns | Ready/Stable/Locked/Saved text |
| Metric hierarchy | metric / readout CSS | Weight + CULTIVATOR/STRAIN |
| Card chrome | card border/radius/bg | PySide QFrame cards |
| Dialog chrome | modal/panel patterns | Scan / New Run / Change Strain |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}
""",
    )

    for s in SEASONS:
        write_json(ROOT / "superpowers" / sp_name(s), build_superpower(s))

    write_json(
        ROOT / "context" / "resume_pack" / f"BBWS_SR4_resume.v{VERSION}.json",
        {
            "pack_id": "BBWS_SR4_resume",
            "version": VERSION,
            "series_id": SERIES_ID,
            "updated_at": NOW,
            "active": {
                "season_id": "S01",
                "episode_id": "S01E01",
                "milestone": "M01",
                "status": "ready_to_execute",
            },
            "parent_series": "BBWS_SR3_station_capture_ux",
            "parent_tag": "bbws-sr3-complete",
            "baseline_tag": "bbws-pre-sr4-polish",
            "completed_seasons": [],
            "decision_locks": {
                "capture_loop": "scan_settle_lock_confirm_reset",
                "polish_scope": "styles_labels_dialogs_only",
                "salvage": "design_tokens_cite_only_no_react",
                "push_cadence": "series_closeout",
                "follow_on": "BBWS_SR5_run_artifact_polish",
            },
            "non_claims": NON_CLAIMS,
            "continuation_handoff": "kickoff_prompts/BBWS_SR4_HUMAN_CHAT_KICKOFF.md",
        },
    )

    write_text(
        ROOT / "kickoff_prompts" / "BBWS_SR4_HUMAN_CHAT_KICKOFF.md",
        f"""# BBWS SR4 — Human Chat Kickoff

Continue **Best Buds Weight Station** series `{SERIES_ID}`.

1. `ACTIVE_ARC.yaml`
2. `context/resume_pack/BBWS_SR4_resume.v{VERSION}.json`
3. `cursor/BBWS_SR4_OPERATOR_SURFACE_POLISH_SERIES_MAP.v{VERSION}.md`
4. Current `superpowers/sr4_sNN_*.json`
5. Execute next `SnnEkk` only

Locks: polish styles/labels/dialogs only; capture loop unchanged; salvage cite-only (no React); no SR5 artifact polish in this series.
""",
    )

    write_text(
        ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md",
        f"""# BBWS SR4 Continuation Handoff

Updated: {NOW}

**Active:** S01 / S01E01 / M01  
**Series:** {SERIES_ID}

Load `ACTIVE_ARC.yaml` and `BBWS_SR4_resume.v{VERSION}.json`, then execute the pointed episode.
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
            "parent_tag": "bbws-sr3-complete",
            "baseline_tag": "bbws-pre-sr4-polish",
            "planned_tags": ["bbws-sr4-complete"],
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": "S01",
            "slug": "polish_contract_freeze",
            "milestone": "M01",
            "commit_plan": "Commit S01 scaffold/contract after E10 closeout",
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
        ROOT / "context" / "ledger" / "bbws_sr4_ledger.md",
        f"""# BBWS SR4 Ledger

| When (UTC) | Episode | Note |
|------------|---------|------|
| {NOW} | PhaseA/S01 | Scaffold ACTIVE_ARC, blueprint, maps, SR4 superpowers, resume pack, git_arc |
""",
    )
    write_text(
        ROOT / "docs" / "BBWS_SR4_ARTIFACTS.md",
        f"""# BBWS SR4 Artifacts

**series_id:** `{SERIES_ID}`  
**generated:** {NOW}

| Artifact | Path |
|----------|------|
| Active arc | `ACTIVE_ARC.yaml` |
| Series map | `cursor/BBWS_SR4_OPERATOR_SURFACE_POLISH_SERIES_MAP.v{VERSION}.md` |
| Blueprint | `arc_lifecycle/blueprints/series_bbws_sr4_operator_surface_polish.v{VERSION}.json` |
| Resume pack | `context/resume_pack/BBWS_SR4_resume.v{VERSION}.json` |
| Ledger | `context/ledger/bbws_sr4_ledger.md` |
| Design tokens | `app/best_buds_weight_station/ui_tokens.py` |
| Token note | `docs/BBWS_SR4_DESIGN_TOKENS.md` |

## Non-claims

{chr(10).join(f'- {c}' for c in NON_CLAIMS)}

Follow-on (not this series): BBWS SR5 run artifact polish (CSV/XLSX/DOCX).
""",
    )

    write_text(
        ROOT / "docs" / "BBWS_SR4_SELECTION_MAP.md",
        f"""# BBWS SR4 — Salvage → BBWS Selection Map

**series_id:** `{SERIES_ID}`  
**generated:** {NOW}  
**salvage:** `M:/SALVAGE/CAPSULES/front_end_graphics/aos_ks_frontend_flow_graphics_v0_1_43`

Cite-only. No React/component import into Best Buds.

| Pattern | Salvage cue | BBWS surface |
|---------|-------------|--------------|
| Eyebrow | `.eyebrow` / section label uppercase tracking | Card eyebrows (barcode, Alice, plant log) |
| Status pill | cockpit status pill | Ready / Stable / Locked / Saved (text + style) |
| Metric | large readout + small unit label | Live weight + locked weight |
| Card | bordered panel, soft radius | QFrame / Tk LabelFrame |
| Dialog | modal chrome, focus field | Scan capture, New Run, Change Strain |

**Must not change:** Scan → settle → Lock → Confirm → reset; JSONL; Metrc/BLE claims.
""",
    )
    print(f"BBWS_SR4 Phase A scaffold complete series={SERIES_ID}")


if __name__ == "__main__":
    main()
