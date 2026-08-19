from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

CURRENT_JSON_FILES = (
    "repo_release_state.json",
    "guide_pack.json",
)
CURRENT_TEXT_FILES = (
    "README.md",
    "docs/SYSTEM_STATE_CURRENT.md",
    "docs/DEBIAN_INSTALL.md",
    "docs/WINDOWS_BUILD.md",
)
REQUIRED_OPERATOR_PATHS = (
    "launch_best_buds.bat", "launch_best_buds.ps1", "launch_best_buds.sh",
    "launch_simulator.bat", "launch_simulator.ps1", "launch_simulator.sh",
    "bootstrap_agent.bat", "bootstrap_agent.ps1", "bootstrap_agent.sh",
    "run_validation.bat", "run_validation.ps1", "run_validation.sh",
    "app/best_buds_weight_station/operator_runtime.py",
    "app/best_buds_weight_station/pyside_frontend.py",
    "app/best_buds_weight_station/production_ui.py",
    "validation/profiles/operator-ready.profile.json",
)
IMMUTABLE_PREFIXES = (
    "context/episodes/",
    "context/ledger/",
    "context/working_set/",
    "reports/validation_report.v0.1.0",
    "reports/validation_report.v0.1.1",
    "reports/validation_report.v0.1.2",
    "reports/validation_report.v0.1.3",
    "reports/validation_report.v0.1.4",
    "reports/validation_report.v0.1.5",
)
# Must stay concordant with scripts/generate_manifest.py EXCLUDED_DIRS.
EXCLUDED_DIRS = {".git", ".pytest_cache", "__pycache__", "build", ".venv", "logs", "dist"}


def marketing_to_pep440(version: str) -> str:
    """Map marketing tags like 2.0.0-rc10.1 to PEP 440 (2.0.0rc10.post1)."""
    match = re.fullmatch(r"(\d+\.\d+\.\d+)-rc(\d+)\.(\d+)", version.strip())
    if match:
        return f"{match.group(1)}rc{match.group(2)}.post{match.group(3)}"
    return version.replace("-rc", "rc").replace("-a", "a").replace("-b", "b")


def _current_files(repo_root: Path, manifest_path: Path) -> set[str]:
    files: set[str] = set()
    for path in repo_root.rglob("*"):
        if not path.is_file() or path == manifest_path:
            continue
        rel = path.relative_to(repo_root)
        if any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in rel.parts):
            continue
        if rel.parts[:2] == ("data", "runtime") or rel.parts[:3] == ("validation", "receipts", "stages") or rel.parts[:2] == ("validation", "checkpoints") or (rel.parts[:2] == ("validation", "reports") and (rel.name.startswith("stage_plan.") or rel.name.startswith("pytest"))) or path.suffix == ".pyc":
            continue
        files.add(rel.as_posix())
    return files


def _manifest_issue(repo_root: Path, manifest: Path, version: str) -> dict[str, Any] | None:
    rel = manifest.relative_to(repo_root).as_posix()
    if not manifest.exists():
        return {"code": "CURRENT_MANIFEST_MISSING", "path": rel, "repairable": True, "severity": "warning"}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception:
        return {"code": "CURRENT_MANIFEST_INVALID", "path": rel, "repairable": True}
    if data.get("version") != version:
        return {"code": "CURRENT_MANIFEST_VERSION_DRIFT", "path": rel, "repairable": True}
    listed = {item.get("path") for item in data.get("files", [])}
    actual = _current_files(repo_root, manifest)
    if listed != actual:
        return {"code": "CURRENT_MANIFEST_STALE", "path": rel, "repairable": True, "severity": "warning"}
    for item in data.get("files", []):
        path = repo_root / item["path"]
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            return {"code": "CURRENT_MANIFEST_STALE", "path": rel, "repairable": True, "severity": "warning"}
    return None


def inspect(repo_root: Path) -> dict[str, Any]:
    version_path = repo_root / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "unknown"
    issues: list[dict[str, Any]] = []

    pyproject_path = repo_root / "pyproject.toml"
    # pyproject must use the PEP 440 normalized form (e.g. 2.0.0rc2 for 2.0.0-rc2).
    pep440 = marketing_to_pep440(version)
    if not pyproject_path.exists():
        issues.append({"code": "PYPROJECT_NOT_INSTALLED", "path": "pyproject.toml", "repairable": False, "scope": "installed_package"})
    else:
        pyproject_text = pyproject_path.read_text(encoding="utf-8")
        if f'version = "{version}"' not in pyproject_text and f'version = "{pep440}"' not in pyproject_text:
            issues.append({"code": "PYPROJECT_VERSION_DRIFT", "path": "pyproject.toml", "repairable": True})

    version_module = repo_root / "app/best_buds_weight_station/version.py"
    if not version_module.exists():
        issues.append({"code": "PYTHON_VERSION_MODULE_MISSING", "path": version_module.relative_to(repo_root).as_posix(), "repairable": False})
    elif f"__version__ = '{version}'" not in version_module.read_text(encoding="utf-8"):
        issues.append({"code": "PYTHON_VERSION_DRIFT", "path": version_module.relative_to(repo_root).as_posix(), "repairable": True})

    for rel in CURRENT_JSON_FILES:
        path = repo_root / rel
        if not path.exists():
            issues.append({"code": "REPO_METADATA_NOT_INSTALLED", "path": rel, "repairable": False, "scope": "installed_package"})
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            issues.append({"code": "INVALID_CURRENT_JSON", "path": rel, "repairable": False})
            continue
        if data.get("version") != version:
            issues.append({"code": "CURRENT_JSON_VERSION_DRIFT", "path": rel, "repairable": True})

    for rel in CURRENT_TEXT_FILES:
        path = repo_root / rel
        if not path.exists():
            issues.append({"code": "CURRENT_DOCUMENT_MISSING", "path": rel, "repairable": False})
        elif version not in path.read_text(encoding="utf-8"):
            issues.append({"code": "CURRENT_DOCUMENT_VERSION_DRIFT", "path": rel, "repairable": False})

    for rel in REQUIRED_OPERATOR_PATHS:
        if not (repo_root / rel).exists():
            issues.append({"code": "OPERATOR_RUNTIME_PATH_MISSING", "path": rel, "repairable": False})

    production = repo_root / "app/best_buds_weight_station/production_ui.py"
    pyside = repo_root / "app/best_buds_weight_station/pyside_frontend.py"
    controller = repo_root / "app/best_buds_weight_station/application_controller.py"
    runtime = repo_root / "app/best_buds_weight_station/operator_runtime.py"
    if production.exists() and '"readings_g": [0.0' in production.read_text(encoding="utf-8"):
        issues.append({"code": "SYNTHETIC_PHYSICAL_ZERO_CALLBACK", "path": production.relative_to(repo_root).as_posix(), "repairable": False})
    if pyside.exists() and '"readings_g": [0.0' in pyside.read_text(encoding="utf-8"):
        issues.append({"code": "SYNTHETIC_PHYSICAL_ZERO_CALLBACK", "path": pyside.relative_to(repo_root).as_posix(), "repairable": False})
    if controller.exists() and "Scale Setup may be opened locally" in controller.read_text(encoding="utf-8"):
        issues.append({"code": "SCALE_SETUP_PLACEHOLDER", "path": controller.relative_to(repo_root).as_posix(), "repairable": False})
    if runtime.exists() and "class ScaleReadingWorker" not in runtime.read_text(encoding="utf-8"):
        issues.append({"code": "READING_WORKER_MISSING", "path": runtime.relative_to(repo_root).as_posix(), "repairable": False})

    manifest = repo_root / f"manifests/file_manifest.v{version}.json"
    issue = _manifest_issue(repo_root, manifest, version)
    if issue:
        issues.append(issue)

    only_installed_scope = bool(issues) and all(item.get("scope") == "installed_package" for item in issues)
    return {
        "version": version,
        "issues": issues,
        "status": "clean" if not issues else ("installed_package_limited" if only_installed_scope else "drift"),
    }


def repair(repo_root: Path, profile: dict[str, Any]) -> list[dict[str, Any]]:
    if not profile.get("allow_safe_auto_repair", False):
        return []
    version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    repairs: list[dict[str, Any]] = []

    path = repo_root / "pyproject.toml"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        new = re.sub(r'(?m)^version = "[0-9]+\.[0-9]+\.[0-9]+"$', f'version = "{version}"', text, count=1)
        if new != text:
            path.write_text(new, encoding="utf-8")
            repairs.append({"path": "pyproject.toml", "action": "sync_version"})

    path = repo_root / "app/best_buds_weight_station/version.py"
    expected = f"__version__ = '{version}'\n"
    if path.exists() and path.read_text(encoding="utf-8") != expected:
        path.write_text(expected, encoding="utf-8")
        repairs.append({"path": path.relative_to(repo_root).as_posix(), "action": "sync_version"})

    for rel in CURRENT_JSON_FILES:
        path = repo_root / rel
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("version") != version:
            data["version"] = version
            path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            repairs.append({"path": rel, "action": "sync_version"})

    manifest = repo_root / f"manifests/file_manifest.v{version}.json"
    issue = _manifest_issue(repo_root, manifest, version)
    policy = profile.get("drift_policy", {}).get("generated_manifest", "WARN")
    if issue and policy.startswith("AUTO_REPAIR"):
        cp = subprocess.run([sys.executable, "scripts/generate_manifest.py"], cwd=repo_root, text=True, capture_output=True)
        if cp.returncode:
            raise RuntimeError(f"manifest regeneration failed: {cp.stdout}{cp.stderr}")
        repairs.append({"path": manifest.relative_to(repo_root).as_posix(), "action": "regenerate_manifest"})
    return repairs
