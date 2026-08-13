"""
BBWS SR10 drift concordance for product version 2.0.0-rc5.

Checks key human/agent doors and packaging version surfaces, including the
Windows installer fallback version. Does not rewrite archival manifests or the
retired v200_rc1 / v200_rc2 / v200_rc3 gates.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = "2.0.0-rc5"
PYPROJECT_PEP440 = "2.0.0rc5"


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

    iss = _read(ROOT / "packaging" / "windows" / "BestBudsWeightStation.iss")
    if f'#define MyAppVersion "{PRODUCT}"' not in iss:
        issues.append({"code": "ISS_VERSION_MISMATCH", "path": "packaging/windows/BestBudsWeightStation.iss"})
    else:
        checks.append({"code": "ISS_VERSION_OK", "path": "packaging/windows/BestBudsWeightStation.iss"})

    version_file = _read(ROOT / "VERSION").strip()
    if version_file != PRODUCT:
        issues.append({"code": "VERSION_FILE_MISMATCH", "path": "VERSION"})
    else:
        checks.append({"code": "VERSION_FILE_OK", "path": "VERSION"})

    for rel in ("START_HERE.md", "START_HERE_CODING_AGENT.md", "docs/OPERATOR_ONBOARDING.md",
                "docs/WINDOWS_DEVICE_BRINGUP.md"):
        if not (ROOT / rel).exists():
            issues.append({"code": "ONBOARDING_DOOR_MISSING", "path": rel})

    scale_face = ROOT / "app" / "best_buds_weight_station" / "scale_face.py"
    if not scale_face.exists():
        issues.append({"code": "SCALE_FACE_MISSING", "path": scale_face.as_posix()})
    else:
        checks.append({"code": "SCALE_FACE_OK", "path": scale_face.as_posix()})

    scale_profiles = ROOT / "app" / "best_buds_weight_station" / "scale_profiles.py"
    if not scale_profiles.exists():
        issues.append({"code": "SCALE_PROFILES_MISSING", "path": scale_profiles.as_posix()})
    else:
        checks.append({"code": "SCALE_PROFILES_OK", "path": scale_profiles.as_posix()})

    status = "pass" if not issues else "fail"
    # No timestamp: report content stays deterministic so the file manifest
    # remains fresh across repeated gate runs.
    report = {
        "gate": "drift_concordance_v200_rc5",
        "status": status,
        "product_version": PRODUCT,
        "pyproject_version": PYPROJECT_PEP440,
        "checks": checks,
        "issues": issues,
        "non_claims": [
            "Archival v0.1.9 manifests and the v200_rc1/rc2/rc3/rc4 gates are not rewritten",
            "Not legal-for-trade / Metrc compliance",
            "Scale profiles/receipts are local operational evidence only; not legal-for-trade",
        ],
    }
    out = ROOT / "reports" / "drift_concordance_report.v2.0.0-rc5.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "report": str(out), "issue_count": len(issues)}, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
