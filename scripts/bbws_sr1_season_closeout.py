"""
Write BBWS SR1 season closeout receipts, update ACTIVE_ARC / resume pack / ledger.

Usage:
  python scripts/bbws_sr1_season_closeout.py S01 [--complete-episodes]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

SEASON_META = {
    "S01": ("recording_polish", "M01", "S02", "hid_scanner", "Harvest recording polish"),
    "S02": ("hid_scanner", "M02", "S03", "sticky_strain", "HID scanner integration"),
    "S03": ("sticky_strain", "M03", "S04", "csv_recording_truth", "Sticky strain for scan groups"),
    "S04": ("csv_recording_truth", "M04", "S05", "export_quality", "CSV recording truth"),
    "S05": ("export_quality", "M05", "S06", "export_reconcile_gates", "Export quality"),
    "S06": ("export_reconcile_gates", "M06", "S07", "field_e2e", "Export ↔ JSONL reconcile gates"),
    "S07": ("field_e2e", "M07", "S08", "crash_resume", "Physical field E2E"),
    "S08": ("crash_resume", "M08", "S09", "governance_light", "Crash/resume operator polish"),
    "S09": ("governance_light", "M09", "S10", "package_smoke_closeout", "Light governance"),
    "S10": ("package_smoke_closeout", "M10", None, None, "Windows package smoke + series closeout"),
}


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mark_superpower_complete(season_id: str, slug: str) -> Path:
    path = ROOT / "superpowers" / f"{season_id.lower()}_{slug}.v{VERSION}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for ep in data["episodes"]:
        ep["status"] = "complete"
        ep["runtime_claimed"] = False
        if ep["id"].endswith("E10"):
            ep["evidence_ref"] = f"reports/bbws_{season_id.lower()}_season_closeout.v{VERSION}.json"
    data["runtime_claimed"] = False
    data["season_status"] = "complete"
    data["closed_at"] = NOW
    write_json(path, data)
    return path


def write_episode_receipts(season_id: str, slug: str) -> list[str]:
    refs = []
    for i in range(1, 10):
        eid = f"{season_id}E{i:02d}"
        path = ROOT / "context" / "episodes" / f"{eid}_{slug}.json"
        write_json(
            path,
            {
                "episode_id": eid,
                "season_id": season_id,
                "slug": slug,
                "status": "complete",
                "updated_at": NOW,
                "runtime_claimed": False,
                "notes": f"BBWS SR1 {eid} executed in harvest-operator series pass",
            },
        )
        refs.append(str(path.relative_to(ROOT)))
    return refs


def update_active_and_resume(season_id: str, slug: str, milestone: str, next_season: str | None, next_slug: str | None) -> None:
    if next_season:
        active_season, active_slug, active_ep, active_ms = next_season, next_slug, f"{next_season}E01", SEASON_META[next_season][1]
        status = "active"
        next_action = f"Execute {active_ep}"
    else:
        active_season, active_slug, active_ep, active_ms = season_id, slug, f"{season_id}E10", milestone
        status = "series_complete"
        next_action = "Series complete — load closeout report"
    (ROOT / "ACTIVE_ARC.yaml").write_text(
        f"""# BBWS SR1 live pointer — product owns truth (Arc Launcher cited, not mutated)
series_id: BBWS_SR1_harvest_operator_loop
series_version: {VERSION}
season_id: {active_season}
season_slug: {active_slug}
episode_id: {active_ep}
milestone: {active_ms}
status: {status}
baseline_freeze: v0.1.9-rc2
prequel_arc: context/operator_ux_arc
doctrine_source: C:/aos_arc_launcher_v0_4_21
updated_at: {NOW}
runtime_claimed: false
next_action: {next_action}
last_closed_season: {season_id}
""",
        encoding="utf-8",
    )
    resume_path = ROOT / "context" / "resume_pack" / f"BBWS_SR1_resume.v{VERSION}.json"
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
    handoff = ROOT / "context" / "resume_pack" / "CONTINUATION_HANDOFF_PROMPT.md"
    handoff.write_text(
        f"""# BBWS SR1 Continuation Handoff

Updated: {NOW}

**Last closed:** {season_id} / {milestone}  
**Active:** {active_season} / {active_ep} / {active_ms} ({status})

Load `ACTIVE_ARC.yaml` and `BBWS_SR1_resume.v{VERSION}.json`, then execute the pointed episode.
Do not mutate Arc Launcher. Do not auto-push mid-episode.
""",
        encoding="utf-8",
    )
    git_season = ROOT / "git_arc" / "active" / "season_pointer.v0.1.0.json"
    write_json(
        git_season,
        {
            "season_id": active_season,
            "slug": active_slug,
            "milestone": active_ms,
            "commit_plan": f"Commit {season_id} slice after E10 closeout (done at {NOW})",
            "push_plan": "git push origin HEAD after season closeout receipt",
            "last_closed_season": season_id,
            "updated_at": NOW,
        },
    )
    write_json(
        ROOT / "git_arc" / "active" / "episode_pointer.v0.1.0.json",
        {
            "episode_id": active_ep,
            "status": "next" if next_season else "series_complete",
            "commit_plan": "episode checkpoints are local context only; no mid-episode push",
            "updated_at": NOW,
        },
    )


def append_ledger(season_id: str, milestone: str) -> None:
    ledger = ROOT / "context" / "ledger" / "bbws_sr1_ledger.md"
    line = f"| {NOW} | {season_id}E10 | {milestone} season closeout written; GitHub push point |\n"
    if ledger.exists():
        text = ledger.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        ledger.write_text(text + line, encoding="utf-8")
    else:
        ledger.write_text(
            "# BBWS SR1 Ledger\n\n| When (UTC) | Episode | Note |\n|------------|---------|------|\n" + line,
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("season_id", choices=sorted(SEASON_META))
    parser.add_argument("--artifacts", default="", help="comma-separated artifact paths")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    season_id = args.season_id
    slug, milestone, next_season, next_slug, title = SEASON_META[season_id]
    episode_refs = write_episode_receipts(season_id, slug)
    mark_superpower_complete(season_id, slug)
    artifacts = [a for a in args.artifacts.split(",") if a] + episode_refs
    closeout = {
        "season_id": season_id,
        "slug": slug,
        "milestone": milestone,
        "title": title,
        "status": "complete",
        "closed_at": NOW,
        "series_id": "BBWS_SR1_harvest_operator_loop",
        "baseline_freeze": "v0.1.9-rc2",
        "artifacts": artifacts,
        "notes": args.notes,
        "next_season": next_season,
        "runtime_claimed": False,
        "non_claims": [
            "Not legal-for-trade / metrology certification",
            "Sticky strain UX ≠ Metrc compliance",
            "HID wedge ≠ BLE/SPP barcode protocol",
            "Season push ≠ release seal / Authenticode",
            "Arc Launcher not claimed as live runtime for Best Buds",
        ],
        "github_push_point": True,
    }
    if season_id == "S10":
        closeout["series_status"] = "complete"
        closeout["series_tag_plan"] = "bbws-sr1-complete"
    path = ROOT / "reports" / f"bbws_{season_id.lower()}_season_closeout.v{VERSION}.json"
    write_json(path, closeout)
    update_active_and_resume(season_id, slug, milestone, next_season, next_slug)
    append_ledger(season_id, milestone)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
