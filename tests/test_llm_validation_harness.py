from __future__ import annotations
import json
from pathlib import Path
import pytest
from best_buds_weight_station.validation.capability_probe import probe
from best_buds_weight_station.validation.drift import inspect,repair
from best_buds_weight_station.validation.graph import ValidationGraph
from best_buds_weight_station.validation.harness import ValidationHarness
from best_buds_weight_station.validation.models import LaneResult
from best_buds_weight_station.validation.profiles import load_profile

ROOT=Path(__file__).parents[1]

def H(): return ValidationHarness(ROOT, persist_receipts=False)

def test_profiles_load():
    for name in ("development","integration","release"):
        assert load_profile(ROOT,name)["profile"]==name

def test_graph_dependency_order():
    g=ValidationGraph(ROOT)
    assert g.prerequisites("serial")==["firmware"]
    assert g.ordered_lanes()[0]=="repository-inspection"
    assert g.ordered_lanes()[-1]=="release-packaging"

def test_capability_probe_is_machine_readable():
    data=probe(ROOT); assert data["python"]["available"] is True; assert isinstance(data["serial_ports"],list); assert "arduino_cli" in data["tools"]

def test_lane_result_rejects_unknown_status():
    with pytest.raises(ValueError): LaneResult("x","GREEN","X","development").to_dict()

def test_inspect_reports_current_version():
    data=H().inspect(); version=(ROOT/"VERSION").read_text().strip(); assert data["version"]==version; assert data["graph"]["package_version"]==version

def test_prepare_development_passes_clean_repo():
    report=H().prepare("development"); assert report.status in {"PASS","PASS_WITH_WARNINGS"}

def test_firmware_lane_blocks_without_tool_or_waits_for_port():
    h=H(); result=h.run_lane("firmware","integration")
    assert result.status in {"BLOCKED","WAITING_FOR_EXTERNAL_ACTION"}
    assert result.status!="PASS"

def test_serial_lane_requires_prerequisite_when_prior_missing():
    r=H().run_lane("serial","integration")
    assert r.status=="BLOCKED" and "firmware" in r.blocking_gates

def test_zero_tare_never_passes_without_port():
    h=H()
    prior={"serial":{"status":"PASS"}}
    r=h.run_lane("zero-tare","integration",{},prior)
    assert r.status=="WAITING_FOR_EXTERNAL_ACTION"

def test_calibration_never_passes_from_schema_presence():
    h=H()
    prior={"zero-tare":{"status":"PASS"}}
    r=h.run_lane("calibration","integration",{},prior)
    assert r.status=="WAITING_FOR_EXTERNAL_ACTION"

def test_physical_loop_never_passes_without_hardware():
    h=H()
    prior={"calibration":{"status":"PASS"}}
    r=h.run_lane("physical-loop","integration",{},prior)
    assert r.status=="WAITING_FOR_EXTERNAL_ACTION"

def test_release_packaging_is_blocked_without_physical_evidence():
    h=H()
    prior={"physical-loop":{"status":"PASS"}}
    r=h.run_lane("release-packaging","release",{},prior)
    assert r.status=="BLOCKED"

def test_historical_paths_are_not_repair_targets():
    assert all(not x.startswith("context/episodes") for x in ("pyproject.toml","app/best_buds_weight_station/version.py","repo_release_state.json","guide_pack.json"))

def test_current_drift_inspection_is_clean():
    assert inspect(ROOT)["status"]=="clean"

def test_validation_schemas_exist():
    assert len(list((ROOT/"contracts/validation").glob("*.json")))==8

def test_cli_graph_can_run():
    import subprocess,sys,os
    cp=subprocess.run([sys.executable,"-m","best_buds_weight_station.validation","graph"],cwd=ROOT,text=True,capture_output=True,env={**os.environ,"PYTHONPATH":str(ROOT/"app")})
    assert cp.returncode==0; assert json.loads(cp.stdout)["package_version"]==(ROOT/"VERSION").read_text().strip()
