from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).parents[1]


def test_root_launchers_exist():
    for base in ("launch_best_buds", "launch_simulator", "bootstrap_agent", "run_validation"):
        for ext in ("bat", "ps1", "sh"):
            assert (ROOT / f"{base}.{ext}").is_file()


def test_launcher_validator_passes():
    cp = subprocess.run([sys.executable, "scripts/validate_launchers.py"], cwd=ROOT, text=True, capture_output=True)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    assert json.loads(cp.stdout)["status"] == "PASS"


def test_windows_source_validator_passes_without_claiming_runtime():
    cp = subprocess.run([sys.executable, "scripts/validate_windows_source.py"], cwd=ROOT, text=True, capture_output=True)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    result = json.loads(cp.stdout)
    assert result["truth_class"] == "WINDOWS_SOURCE_PRESENT"
    assert result["native_windows_execution"] == "NOT_RUN"


def test_frontend_runtime_truth_validator_passes():
    cp = subprocess.run([sys.executable, "scripts/validate_frontend_runtime_truth.py"], cwd=ROOT, text=True, capture_output=True)
    assert cp.returncode == 0, cp.stdout + cp.stderr
