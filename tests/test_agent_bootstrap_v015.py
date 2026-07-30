from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from best_buds_weight_station.bootstrap import parser
from best_buds_weight_station.validation.bootstrap import AgentBootstrap, PREHARDWARE_LANES
from best_buds_weight_station.validation.dry_run import run_software_dry_run
from best_buds_weight_station.validation.harness import ValidationHarness

ROOT = Path(__file__).parents[1]


def test_bootstrap_parser_exposes_agent_entrypoint():
    p = parser()
    args = p.parse_args(["--profile", "prehardware", "--skip-ui", "--no-persist"])
    assert args.profile == "prehardware"
    assert args.skip_ui is True
    assert args.no_persist is True


def test_prehardware_profile_loads():
    h = ValidationHarness(ROOT, persist_receipts=False)
    result = h.prepare("prehardware")
    assert result.profile == "prehardware"
    assert result.status in {"PASS", "PASS_WITH_WARNINGS"}


def test_graph_contains_software_bootstrap_lanes():
    h = ValidationHarness(ROOT, persist_receipts=False)
    lanes = h.graph.ordered_lanes()
    for lane in PREHARDWARE_LANES:
        assert lane in lanes
    assert lanes.index("packaging-preflight") < lanes.index("firmware")


def test_software_dry_run_executes_real_controller(tmp_path):
    result = run_software_dry_run(tmp_path)
    assert result["status"] == "PASS"
    assert result["version"] == (ROOT / "VERSION").read_text().strip()
    assert result["automatic_loop"]["truth_class"] == "RECEIPT_CONFIRMED"
    assert result["manual_loop"]["truth_class"] == "RECEIPT_CONFIRMED"
    assert result["automatic_loop"]["load_resume_verified"] is True
    assert result["manual_loop"]["load_resume_verified"] is True
    assert result["physical_device"] == "NOT_RUN"


def test_dry_run_does_not_promote_remote_or_physical_claims(tmp_path):
    result = run_software_dry_run(tmp_path)
    assert result["bluetooth_boundary"] == "VALIDATED_DISABLED_NOT_RUN"
    assert result["wifi_boundary"] == "VALIDATED_DISABLED_NOT_RUN"
    assert result["firmware_upload"] == "NOT_RUN"
    assert result["uno_q"] == "NOT_RUN"


def test_agent_bootstrap_can_run_without_ui_or_persistence(tmp_path, monkeypatch):
    h = ValidationHarness(ROOT, persist_receipts=False)
    bootstrap = AgentBootstrap(ROOT, persist=False)

    def fake_run_lane(lane, profile_name, options=None, prior=None):
        from best_buds_weight_station.validation.models import LaneResult
        return LaneResult(lane, "PASS", "TEST_PASS", profile_name)

    monkeypatch.setattr(bootstrap.harness, "run_lane", fake_run_lane)
    result = bootstrap.run(profile="prehardware", include_ui=False, run_id="test-run")
    assert result.status == "PASS"
    assert result.run_id == "test-run"
    assert result.physical_gates["physical_loop"] == "NOT_RUN"
    assert "frontend-smoke" not in [x["lane"] for x in result.lanes]


def test_module_entrypoint_version():
    cp = subprocess.run(
        [sys.executable, "-m", "best_buds_weight_station.bootstrap", "--version"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={"PYTHONPATH": str(ROOT / "app"), "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert cp.returncode == 0
    assert cp.stdout.strip() == (ROOT / "VERSION").read_text().strip()


def test_validation_cli_bootstrap_help():
    cp = subprocess.run(
        [sys.executable, "-m", "best_buds_weight_station.validation", "bootstrap", "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={"PYTHONPATH": str(ROOT / "app"), "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert cp.returncode == 0
    assert "prehardware" in cp.stdout


def test_bootstrap_schema_parses():
    schema = json.loads((ROOT / "contracts/validation/agent_bootstrap_result.schema.json").read_text())
    assert schema["properties"]["status"]["enum"] == ["PASS", "PASS_WITH_WARNINGS", "FAIL"]


def test_prehardware_physical_lanes_are_not_hard_gates():
    profile = json.loads((ROOT / "validation/profiles/prehardware.profile.json").read_text())
    assert "firmware" not in profile["hard_gate_lanes"]
    assert profile["physical_lanes"]["firmware"] == "NOT_RUN_ALLOWED"
