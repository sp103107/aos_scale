"""
Write BBWS SR2 season closeout receipts and advance ACTIVE_ARC / resume pack.

Usage:
  python scripts/bbws_sr2_season_closeout.py S01
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
SERIES_ID = "BBWS_SR2_tk_linux_display_units"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SEASON_META = {
    "S01": ("tk_gap_audit", "M01", "S02", "tk_recording_polish", "Tk/Linux gap audit"),
    "S02": ("tk_recording_polish", "M02", "S03", "tk_hid_scanner", "Tk recording polish"),
    "S03": ("tk_hid_scanner", "M03", "S04", "tk_sticky_strain", "Tk HID scanner"),
    "S04": ("tk_sticky_strain", "M04", "S05", "tk_csv_recover", "Tk sticky strain"),
    "S05": ("tk_csv_recover", "M05", "S06", "tk_export_reconcile", "Tk CSV recover"),
    "S06": ("tk_export_reconcile", "M06", "S07", "display_unit_core", "Tk export reconcile"),
    "S07": ("display_unit_core", "M07", "S08", "display_unit_uis", "Display-unit core"),
    "S08": ("display_unit_uis", "M08", "S09", "linux_smoke", "Display unit UIs"),
    "S09": ("linux_smoke", "M09", "S10", "dual_ui_closeout", "Linux smoke"),
    "S10": ("dual_ui_closeout", "M10", None, None, "Dual-UI series closeout"),
}


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sp_path(season_id: str, slug: str) -> Path:
    return ROOT / "superpowers" / f"sr2_{season_id.lower()}_{slug}.v{VERSION}.json"


def mark_superpower_complete(season_id: str, slug: str) -> None:
    path = sp_path(season_id, slug)
    data = json.loads(path.read_text(encoding="utf-8"))
    for ep in data["episodes"]:
        ep["status"] = "complete"
        ep["runtime_claimed"] = False
        if ep["id"].endswith("E10"):
            ep["evidence_ref"] = f"reports/bbws_sr2_{season_id.lower()}_season_closeout.v{VERSION}.json"
    data["season_status"] = "complete"
    data["closed_at"] = NOW
    write_json(path, data)


def write_episode_receipts(season_id: str, slug: str) -> list[str]:
    refs = []
    for i in range(1, 10):
        eid = f"{season_id}E{i:02d}"
        path = ROOT / "context" / "episodes" / f"SR2_{eid}_{slug}.json"
        write_json(
            path,
            {
                "episode_id": eid,
                "series_id": SERIES_ID,
                "season_id": season_id,
                "slug": slug,
                "status": "complete",
                "updated_at": NOW,
                "runtime_claimed": False,
            },
        )
        refs.append(str(path.relative_to(ROOT)))
    return refs


def update_pointers(season_id: str, slug: str, milestone: str, next_season: str | None, next_slug: str | None) -> None:
    if next_season:
        active_season, active_slug, active_ep, active_ms = next_season, next_slug, f"{next_season}E01", SEASON_META[next_season][1]
        status = "active"
        next_action = f"Execute {active_ep}"
    else:
        active_season, active_slug, active_ep, active_ms = season_id, slug, f"{season_id}E10", milestone
        status = "series_complete"
        next_action = "Series complete — load SR2 closeout report"
    (ROOT / "ACTIVE_ARC.yaml").write_text(
        f"""# BBWS SR2 live pointer — product owns truth (Arc Launcher cited, not mutated)
series_id: {SERIES_ID}
series_version: {VERSION}
season_id: {active_season}
season_slug: {active_slug}
episode_id: {active_ep}
milestone: {active_ms}
status: {status}
parent_series_id: BBWS_SR1_harvest_operator_loop
parent_tag: bbws-sr1-complete
baseline_freeze: v0.1.9-rc2
doctrine_source: C:/aos_arc_launcher_v0_4_21
updated_at: {NOW}
runtime_claimed: false
units_law: display_only_g_kg_lb_storage_grams
next_action: {next_action}
last_closed_season: {season_id}
""",
        encoding="utf-8",
    )
    resume_path = ROOT / "context" / "resume_pack" / f"BBWS_SR2_resume.v{VERSION}.json"
    resume = json.loads(resume_path.read_text(encoding="utf-8"))
    completed = list(resume.get("completed_seasons") or [])
    if season_id not in completed:
        completed.append(season_id)
    resume["completed_seasons"] = completed
    resume["updated_at"] = NOW
    resume["active"] = {
        "season_id": active_season,
        "episode_id": active_ep,
        "milestone": active_ms,
        "status": status,
    }
    write_json(resume_path, resume)
    write_json(
        ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json",
        {
            "season_id": active_season,
            "slug": active_slug,
            "milestone": active_ms,
            "last_closed_season": season_id,
            "push_plan": "git push origin HEAD after season closeout",
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "episode_pointer.v0.1.0.json",
        {
            "episode_id": active_ep,
            "status": "next" if next_season else "series_complete",
            "updated_at": NOW,
        },
    )
    ledger = ROOT / "context" / "ledger" / "bbws_sr2_ledger.md"
    line = f"| {NOW} | {season_id}E10 | {milestone} season closeout; GitHub push point |\n"
    if ledger.exists():
        text = ledger.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        ledger.write_text(text + line, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("season_id", choices=sorted(SEASON_META))
    parser.add_argument("--artifacts", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    season_id = args.season_id
    slug, milestone, next_season, next_slug, title = SEASON_META[season_id]
    refs = write_episode_receipts(season_id, slug)
    mark_superpower_complete(season_id, slug)
    artifacts = [a for a in args.artifacts.split(",") if a] + refs
    closeout = {
        "season_id": season_id,
        "slug": slug,
        "milestone": milestone,
        "title": title,
        "status": "complete",
        "closed_at": NOW,
        "series_id": SERIES_ID,
        "artifacts": artifacts,
        "notes": args.notes,
        "next_season": next_season,
        "runtime_claimed": False,
        "github_push_point": True,
        "non_claims": [
            "Display lb/kg ≠ legal-for-trade / NTEP",
            "Tk parity ≠ Windows packaging seal",
            "Linux smoke ≠ Debian production guarantee",
            "Display unit ≠ changing authoritative ledger units",
            "Arc Launcher not claimed as live runtime for Best Buds",
        ],
    }
    if season_id == "S10":
        closeout["series_status"] = "complete"
        closeout["series_tag_plan"] = "bbws-sr2-complete"
    path = ROOT / "reports" / f"bbws_sr2_{season_id.lower()}_season_closeout.v{VERSION}.json"
    write_json(path, closeout)
    update_pointers(season_id, slug, milestone, next_season, next_slug)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
