"""
Build a clean source zip for BBWS GitHub Release (no .git).

Preferred path: `git archive` from a local ref (Windows-safe).
Fallback: copy working tree excluding .git / dist / caches.
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
    def ignore(_directory: str, names: list[str]) -> set[str]:
        skipped = set()
        for name in names:
            if name in EXCLUDE_DIR_NAMES or name.endswith(".pyc"):
                skipped.add(name)
        return skipped

    shutil.copytree(src, dest, ignore=ignore)


def _archive_ref(ref: str, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    prefix = f"BestBudsWeightStation-{ref.lstrip('v')}/"
    subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "archive",
            "--format=zip",
            f"--prefix={prefix}",
            "-o",
            str(zip_path),
            ref,
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Make BBWS source release zip without .git")
    parser.add_argument("--version", default="2.0.0-rc4")
    parser.add_argument("--ref", help="Git ref to archive (tag/commit). Default: HEAD working tree copy.")
    args = parser.parse_args()

    version = args.version
    out_dir = ROOT / "dist" / "releases"
    zip_path = out_dir / f"BestBudsWeightStation-source-v{version}.zip"
    receipt_path = ROOT / "reports" / f"release_bundle_receipt.v{version}.json"
    method = "git_archive" if args.ref else "working_tree_copy"

    if args.ref:
        _archive_ref(args.ref, zip_path)
    else:
        with tempfile.TemporaryDirectory(prefix="bbws-release-") as tmp:
            work = Path(tmp) / f"BestBudsWeightStation-{version}"
            _copy_tree(ROOT, work)
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            if zip_path.exists():
                zip_path.unlink()
            base = zip_path.with_suffix("")
            shutil.make_archive(str(base), "zip", root_dir=str(work))

    digest = _sha256(zip_path)
    receipt = {
        "receipt_type": "bbws_release_source_bundle",
        "version": version,
        "ref": args.ref or "working_tree",
        "method": method,
        "zip_path": str(zip_path.resolve()),
        "sha256": digest,
        "includes_dot_git": False,
        "windows_binary": "deferred_not_blocking",
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
