"""
Coding-agent / human documentation router entry for Best Buds Weight Station.

Prints version, key paths, ACTIVE_ARC summary, and bootstrap hints.
Does not launch the operator UI or mutate capture state.

Cite posture: Book Spine BOOK_ENTRYPOINTS (document router, runtime_claimed false).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .version import __version__

REPO_ROOT_MARKERS = ("ACTIVE_ARC.yaml", "START_HERE.md", "pyproject.toml")


def find_repo_root(start: Path | None = None) -> Path:
    """Walk upward from this file or start until repo markers appear."""
    here = (start or Path(__file__).resolve()).resolve()
    if here.is_file():
        here = here.parent
    for candidate in [here, *here.parents]:
        if all((candidate / marker).exists() for marker in ("ACTIVE_ARC.yaml", "pyproject.toml")):
            return candidate
    # Fallback: package lives in app/best_buds_weight_station → repo is parents[2]
    return Path(__file__).resolve().parents[2]


def _read_active_arc(root: Path) -> dict[str, str]:
    path = root / "ACTIVE_ARC.yaml"
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return data


def build_guidance(root: Path | None = None) -> dict[str, Any]:
    repo = find_repo_root(root)
    arc = _read_active_arc(repo)
    paths = {
        "START_HERE": "START_HERE.md",
        "START_HERE_CODING_AGENT": "START_HERE_CODING_AGENT.md",
        "OPERATOR_ONBOARDING": "docs/OPERATOR_ONBOARDING.md",
        "INTENDED_USER": "docs/INTENDED_USER.md",
        "RELEASE_CANDIDATE": "docs/RELEASE_CANDIDATE.md",
        "ACTIVE_ARC": "ACTIVE_ARC.yaml",
        "bootstrap": "python -m best_buds_weight_station.bootstrap --profile cursor-ready",
        "cursor_bootstrap_ps1": "cursor_bootstrap.ps1",
        "launch_operator": "launch_best_buds.bat",
    }
    return {
        "entry": "best_buds_weight_station.onboard",
        "runtime_claimed": False,
        "version": __version__,
        "repo_root": str(repo.resolve()),
        "active_arc": arc,
        "load_order": [
            "ACTIVE_ARC.yaml",
            "context/resume_pack/BBWS_SR*_resume*.json",
            "cursor/*_SERIES_MAP*.md",
            "superpowers/srN_sNN_*.json",
            "next SnnEkk",
        ],
        "paths": paths,
        "next_commands": [
            "python -m best_buds_weight_station.bootstrap --profile cursor-ready",
            "python -m pytest tests/test_sr5_artifact_polish.py tests/test_sr4_polish.py -q",
        ],
        "non_claims": [
            "Coding-agent onboard entry is guidance/bootstrap routing, not a new capture runtime",
            "Not legal-for-trade / Metrc compliance",
            "JSONL remains authoritative for records",
        ],
        "human_door": "START_HERE.md",
        "agent_door": "START_HERE_CODING_AGENT.md",
    }


def print_human(guidance: dict[str, Any]) -> None:
    print(f"Best Buds Weight Station onboard  v{guidance['version']}")
    print(f"repo_root: {guidance['repo_root']}")
    print(f"runtime_claimed: {guidance['runtime_claimed']}")
    arc = guidance.get("active_arc") or {}
    if arc:
        print("--- ACTIVE_ARC ---")
        for key in (
            "series_id",
            "status",
            "season_id",
            "episode_id",
            "product_version_target",
            "next_action",
        ):
            if key in arc:
                print(f"  {key}: {arc[key]}")
    print("--- load order ---")
    for item in guidance["load_order"]:
        print(f"  → {item}")
    print("--- doors ---")
    print(f"  human: {guidance['human_door']}")
    print(f"  agent: {guidance['agent_door']}")
    print("--- next ---")
    for cmd in guidance["next_commands"]:
        print(f"  $ {cmd}")
    print("--- non-claims ---")
    for claim in guidance["non_claims"]:
        print(f"  - {claim}")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="best-buds-weight-station-onboard",
        description="Print coding-agent / human onboarding guidance (no UI launch).",
    )
    p.add_argument("--repo-root", type=Path, help="Override repository root")
    p.add_argument("--json", action="store_true", help="Emit JSON guidance")
    p.add_argument("--version", action="store_true", help="Print product version only")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    guidance = build_guidance(args.repo_root)
    if args.json:
        print(json.dumps(guidance, indent=2, sort_keys=True))
    else:
        print_human(guidance)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
