"""
Build a clean source zip for BBWS GitHub Release (no .git).

Usage:
  python scripts/make_release_bundle.py --version 2.0.0-rc1
  python scripts/make_release_bundle.py --version 2.0.0-rc1 --ref v2.0.0-rc1

If --ref is omitted, zips the current working tree (excluding .git).
If --ref is set, clones that ref into a temp dir first.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    "dist",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_tree(src: Path, dest: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        skipped = set()
        for name in names:
            if name in EXCLUDE_DIR_NAMES:
                skipped.add(name)
            elif name.endswith(".pyc"):
                skipped.add(name)
        return skipped

    shutil.copytree(src, dest, ignore=ignore)


def _zip_dir(source_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    base = zip_path.with_suffix("")
    shutil.make_archive(str(base), "zip", root_dir=str(source_dir))


def main() -> int:
    parser = argparse.ArgumentParser(description="Make BBWS source release zip without .git")
    parser.add_argument("--version", default="2.0.0-rc1")
    parser.add_argument("--ref", help="Git ref to clone (tag/commit). Default: current tree.")
    parser.add_argument("--remote", default="https://github.com/sp103107/aos_scale.git")
    args = parser.parse_args()

    version = args.version
    out_dir = ROOT / "dist" / "releases"
    zip_name = f"BestBudsWeightStation-source-v{version}.zip"
    zip_path = out_dir / zip_name
    receipt_path = ROOT / "reports" / f"release_bundle_receipt.v{version}.json"

    windows_note = "not_attempted"
    with tempfile.TemporaryDirectory(prefix="bbws-release-") as tmp:
        work = Path(tmp) / f"BestBudsWeightStation-{version}"
        if args.ref:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", args.ref, args.remote, str(work)],
                check=True,
            )
            # Remove .git from clone before zip
            git_dir = work / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
        else:
            _copy_tree(ROOT, work)
        _zip_dir(work, zip_path)

    digest = _sha256(zip_path)
    receipt = {
        "receipt_type": "bbws_release_source_bundle",
        "version": version,
        "ref": args.ref or "working_tree",
        "zip_path": str(zip_path.resolve()),
        "sha256": digest,
        "includes_dot_git": False,
        "windows_binary": windows_note,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "non_claims": [
            "Source zip is not a legal-for-trade or Metrc artifact",
            "Not a production seal",
        ],
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
