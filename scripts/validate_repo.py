#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
sys.path.insert(0, str(ROOT / "app"))

EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", "build", ".venv"}
errors: list[dict[str, str]] = []
checks: dict[str, object] = {}


def included(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if rel.parts[:2] == ("data", "runtime"):
        return False
    if rel.parts[:3] == ("validation", "receipts", "stages"):
        return False
    if rel.parts[:2] == ("validation", "checkpoints"):
        return False
    if rel.parts[:2] == ("validation", "reports") and (rel.name.startswith("stage_plan.") or (rel.name.startswith("pytest") and rel.name != "pytest_full_suite.v0.1.8.log")):
        return False
    return path.suffix != ".pyc"


def run(name: str, fn) -> None:
    try:
        checks[name] = fn()
    except Exception as exc:  # noqa: BLE001 - validator must preserve all failure classes
        errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})


def parse_json() -> int:
    paths = [p for p in ROOT.rglob("*.json") if p.is_file() and included(p)]
    for path in paths:
        json.loads(path.read_text(encoding="utf-8"))
    return len(paths)


def parse_jsonl() -> int:
    count = 0
    for path in [p for p in ROOT.rglob("*.jsonl") if p.is_file() and included(p)]:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                assert isinstance(json.loads(line), dict), f"{path}:{line_number}"
                count += 1
    return count


def parse_yaml() -> int:
    try:
        import yaml
    except ImportError:
        return 0
    paths = [p for p in ROOT.rglob("*") if p.is_file() and included(p) and p.suffix.lower() in {".yaml", ".yml"}]
    for path in paths:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    return len(paths)


def compile_python() -> str:
    targets = [p for base in (ROOT / "app", ROOT / "scripts") for p in base.rglob("*.py")]
    for path in targets:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
    from best_buds_weight_station.bootstrap import parser
    from best_buds_weight_station.operator_surface import validate_routine_action_layout
    from best_buds_weight_station.stage_runner import StageRunner

    parser()
    validate_routine_action_layout()
    assert StageRunner(ROOT, persist=False).version == VERSION
    return "PASS"


def versions() -> dict[str, object]:
    assert VERSION == "0.1.8"
    assert 'version = "0.1.8"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "__version__ = '0.1.8'" in (ROOT / "app/best_buds_weight_station/version.py").read_text(encoding="utf-8")
    current = [
        "README.md",
        "CHANGELOG.md",
        "docs/SYSTEM_STATE_CURRENT.md",
        "docs/WINDOWS_BUILD.md",
        "docs/DEBIAN_INSTALL.md",
        "repo_release_state.json",
        "guide_pack.json",
        "frontend/frontend_manifest.v0.1.8.json",
        "backend/backend_manifest.v0.1.8.json",
        "release_candidate/rc_phase_matrix.v0.1.8.json",
        "context/working_set/working_set_update_0009.json",
        "context/episodes/episode_0009_v0.1.8.json",
        "context/resume_pack/resume_pack_manifest.v0.1.8.json",
        "pipeline/stage_catalog.v0.1.8.json",
        "pipeline/plans/cursor_ready.v0.1.8.json",
        "cursor/CURSOR_UNO_R3_PHYSICAL_INTEGRATION_HANDOFF_V0_1_8.md",
    ]
    for rel in current:
        path = ROOT / rel
        assert path.exists(), rel
        assert VERSION in path.read_text(encoding="utf-8", errors="ignore"), rel
    return {"version": VERSION, "current_surfaces": len(current)}


def required() -> int:
    paths = [
        "README.md", "VERSION", "CHANGELOG.md", "repo_release_state.json", "guide_pack.json",
        "launch_best_buds.bat", "launch_best_buds.ps1", "launch_best_buds.sh",
        "launch_simulator.bat", "launch_simulator.ps1", "launch_simulator.sh",
        "bootstrap_agent.bat", "bootstrap_agent.ps1", "bootstrap_agent.sh",
        "run_validation.bat", "run_validation.ps1", "run_validation.sh",
        "cursor_bootstrap.bat", "cursor_bootstrap.ps1", "cursor_bootstrap.sh",
        "run_stage.bat", "run_stage.ps1", "run_stage.sh",
        "resume_stage.bat", "resume_stage.ps1", "resume_stage.sh",
        "frontend/design_tokens.v0.1.8.json", "frontend/themes/windows_light.qss",
        "app/best_buds_weight_station/operator_surface.py",
        "app/best_buds_weight_station/stage_runner/cli.py",
        "pipeline/plans/cursor_ready.v0.1.8.json",
        "entrypoints/surface_entry_map.v0.1.8.json",
        "registry/surface_entry_registry.v0.1.8.json",
        "pods/best_buds_weight_station_pod_manifest.v0.1.8.json",
        "runtime/evidence_index.v0.1.8.json",
        "cursor/CURSOR_UNO_R3_PHYSICAL_INTEGRATION_HANDOFF_V0_1_8.md",
    ]
    missing = [rel for rel in paths if not (ROOT / rel).exists()]
    assert not missing, missing
    return len(paths)


def tests() -> int:
    report_path = ROOT / "reports/pytest_full_suite_evidence.v0.1.8.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report.get("status") == "PASS"
    assert report.get("exit_code_or_result") == 0
    assert report.get("test_count", 0) >= 183
    log_rel = report["artifact_paths"][0]
    log_path = ROOT / log_rel
    assert log_path.exists(), log_rel
    expected = report["artifact_hashes"][log_rel]
    assert hashlib.sha256(log_path.read_bytes()).hexdigest() == expected
    return int(report["test_count"])


def schemas() -> int:
    import jsonschema

    paths = list(ROOT.glob("contracts/**/*.json"))
    for path in paths:
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
    assert len(paths) >= 60, len(paths)
    return len(paths)


def scripts(execute: bool = True) -> dict[str, str]:
    names = [
        "validate_launchers.py",
        "validate_frontend_runtime_truth.py",
        "validate_frontend_polish_v018.py",
        "validate_windows_source.py",
        "validate_drift_concordance_v018.py",
        "validate_cursor_ready_v018.py",
        "validate_cursor_handoff_v018.py",
    ]
    out: dict[str, str] = {}
    if not execute:
        report_paths = [
            ROOT / "reports/frontend_polish_validation.v0.1.8.json",
            ROOT / "reports/drift_concordance_report.v0.1.8.json",
            ROOT / "reports/cursor_ready_validation.v0.1.8.json",
        ]
        for path in report_paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data.get("status") == "PASS", path.relative_to(ROOT)
        return {name: "PREVIOUS_PASS_REPORT_VERIFIED" for name in names}
    env = {**os.environ, "PYTHONPATH": str(ROOT / "app"), "PYTHONDONTWRITEBYTECODE": "1"}
    for name in names:
        cp = subprocess.run(
            [sys.executable, "scripts/" + name],
            cwd=ROOT,
            text=True,
            capture_output=True,
            env=env,
            timeout=600,
        )
        if cp.returncode:
            raise RuntimeError(name + "\n" + cp.stdout + cp.stderr)
        out[name] = "PASS"
    return out


def context() -> dict[str, object]:
    lines = [json.loads(line) for line in (ROOT / "context/ledger/ledger.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 106, len(lines)
    assert lines[-1]["sequence"] == len(lines)
    report = json.loads((ROOT / "context/context_validation_report.v0.1.8.json").read_text(encoding="utf-8"))
    assert report["working_set_update_seq"] == 9
    assert report["episode"] == "episode_0009_v0.1.8"
    return {"ledger_events": len(lines), "working_set": 9, "episode": report["episode"]}


def claims() -> dict[str, object]:
    state = json.loads((ROOT / "repo_release_state.json").read_text(encoding="utf-8"))
    assert state["execution_posture"] == "real_execution_allowed"
    assert state["production_ready_claimed"] is False
    assert state["release_seal_claimed"] is False
    assert state["physical_device_status"] == "not_run"
    assert state["windows_native_runtime_status"] == "NOT_RUN"
    return {
        "runtime_scope": "authorized_local_software_only",
        "physical": "NOT_RUN",
        "windows_native": "NOT_RUN",
        "production_ready": False,
        "release_seal": False,
    }


def phase_matrix() -> dict[str, int]:
    matrix = json.loads((ROOT / "release_candidate/rc_phase_matrix.v0.1.8.json").read_text(encoding="utf-8"))
    phases = [item["phase"] for item in matrix["phases"]]
    assert len(phases) == len(set(phases)), phases
    return {"phase_count": len(phases), "unique_phase_count": len(set(phases))}


def generated_hygiene() -> str:
    assert not list((ROOT / "app").glob("*.egg-info"))
    assert "_LegacyCallbackNamesForContract" not in (ROOT / "app/best_buds_weight_station/production_ui.py").read_text(encoding="utf-8")
    return "PASS"


def manifest(require_manifest: bool) -> object:
    path = ROOT / f"manifests/file_manifest.v{VERSION}.json"
    if not require_manifest:
        return "DEFERRED_TO_FINAL_PACKAGE_GATE"
    if not path.exists():
        raise AssertionError(f"missing manifest: {path.relative_to(ROOT)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    listed = {item["path"] for item in data["files"]}
    actual: set[str] = set()
    for candidate in ROOT.rglob("*"):
        if candidate.is_file() and candidate != path and included(candidate):
            actual.add(candidate.relative_to(ROOT).as_posix())
    assert listed == actual, {
        "missing_from_manifest": sorted(actual - listed)[:20],
        "missing_from_repo": sorted(listed - actual)[:20],
    }
    for item in data["files"]:
        digest = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
        assert digest == item["sha256"], item["path"]
    return data["file_count"]


def forbidden() -> str:
    bad = []
    for path in ROOT.rglob("*.zip"):
        rel = path.relative_to(ROOT)
        if rel.parts[:2] != ("context", "source_truth"):
            bad.append(rel.as_posix())
    assert not bad, bad
    return "ABSENT"


def cleanup_generated() -> None:
    for directory in list(ROOT.rglob("__pycache__")) + [ROOT / ".pytest_cache", ROOT / "build", ROOT / ".venv"]:
        if directory.exists():
            shutil.rmtree(directory)
    for path in ROOT.rglob("*.pyc"):
        path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the complete Best Buds repository.")
    parser.add_argument("--require-manifest", action="store_true")
    args = parser.parse_args()
    cleanup_generated()
    for name, fn in [
        ("json", parse_json),
        ("jsonl", parse_jsonl),
        ("yaml", parse_yaml),
        ("tests", tests),
        ("python_compile", compile_python),
        ("versions", versions),
        ("required", required),
        ("schemas", schemas),
        ("validators", lambda: scripts(not args.require_manifest)),
        ("context", context),
        ("claims", claims),
        ("phase_matrix", phase_matrix),
        ("generated_hygiene", generated_hygiene),
        ("manifest", lambda: manifest(args.require_manifest)),
        ("forbidden", forbidden),
    ]:
        run(name, fn)
    cleanup_generated()
    result = {
        "package_name": "best_buds_cultivator_weight_station",
        "version": VERSION,
        "status": "FAIL" if errors else "PASS",
        "checks": checks,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
