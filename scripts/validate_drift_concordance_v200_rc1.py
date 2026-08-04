"""
BBWS SR6 drift concordance for product version 2.0.0-rc1.

Checks key human/agent doors and packaging version surfaces.
Does not rewrite archival *.v0.1.9 manifests.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = "2.0.0-rc1"
PYPROJECT_PEP440 = "2.0.0rc1"
VERSION = "2.0.0-rc1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    issues: list[dict[str, str]] = []
    checks: list[dict[str, str]] = []

    version_py = ROOT / "app" / "best_buds_weight_station" / "version.py"
    text = _read(version_py)
    if f'__version__ = "{PRODUCT}"' not in text and f"__version__ = '{PRODUCT}'" not in text:
        issues.append({"code": "VERSION_PY_MISMATCH", "path": version_py.as_posix()})
    else:
        checks.append({"code": "VERSION_PY_OK", "path": version_py.as_posix()})

    pyproject = _read(ROOT / "pyproject.toml")
    if f'version = "{PYPROJECT_PEP440}"' not in pyproject:
        issues.append({"code": "PYPROJECT_VERSION_MISMATCH", "path": "pyproject.toml"})
    else:
        checks.append({"code": "PYPROJECT_VERSION_OK", "path": "pyproject.toml"})

    for rel in (
        "README.md",
        "START_HERE.md",
        "START_HERE_CODING_AGENT.md",
        "docs/RELEASE_CANDIDATE.md",
        "docs/OPERATOR_ONBOARDING.md",
        "docs/INTENDED_USER.md",
    ):
        body = _read(ROOT / rel)
        if PRODUCT not in body:
            issues.append({"code": "DOC_VERSION_MISSING", "path": rel})
        else:
            checks.append({"code": "DOC_VERSION_OK", "path": rel})

    for rel in ("START_HERE.md", "START_HERE_CODING_AGENT.md", "docs/OPERATOR_ONBOARDING.md"):
        if not (ROOT / rel).exists():
            issues.append({"code": "ONBOARDING_DOOR_MISSING", "path": rel})

    onboard = ROOT / "app" / "best_buds_weight_station" / "onboard.py"
    if not onboard.exists():
        issues.append({"code": "ONBOARD_MODULE_MISSING", "path": onboard.as_posix()})
    else:
        checks.append({"code": "ONBOARD_MODULE_OK", "path": onboard.as_posix()})

    if "best-buds-weight-station-onboard" not in pyproject:
        issues.append({"code": "ONBOARD_SCRIPT_MISSING", "path": "pyproject.toml"})

    version_file = _read(ROOT / "VERSION").strip()
    if version_file != PRODUCT:
        issues.append({"code": "VERSION_FILE_MISMATCH", "path": "VERSION"})
    else:
        checks.append({"code": "VERSION_FILE_OK", "path": "VERSION"})

    status = "pass" if not issues else "fail"
    report = {
        "gate": "drift_concordance_v200_rc1",
        "status": status,
        "product_version": PRODUCT,
        "pyproject_version": PYPROJECT_PEP440,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checks": checks,
        "issues": issues,
        "non_claims": [
            "Archival v0.1.9 manifests are not rewritten by this gate",
            "Not legal-for-trade / Metrc compliance",
        ],
    }
    out = ROOT / "reports" / f"drift_concordance_report.v{VERSION}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    # Windows-safe filename: avoid ambiguous chars
    out = ROOT / "reports" / "drift_concordance_report.v2.0.0-rc1.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "report": str(out), "issue_count": len(issues)}, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
