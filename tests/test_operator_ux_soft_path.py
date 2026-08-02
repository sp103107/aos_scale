"""Operator UX soft-path: cal without run, auto-bind, failed tolerance, auto plant id."""

from __future__ import annotations

import pytest

from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.application_controller import ApplicationController
from best_buds_weight_station.operator_runtime import OperatorRuntime
from best_buds_weight_station.scale_control import ScaleControlService
from tests.v013_helpers import simulated_device


def test_setup_only_connect_binds_scale_and_allows_calibration(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    result = runtime.connect_simulator()
    assert result["status"] == "completed"
    assert result["data"]["setup_only"] is True
    assert runtime.controller.scale is not None
    assert runtime.controller.loaded_run is None
    started = runtime.start_calibration()
    assert started["status"] == "completed"
    assert started["data"]["calibration_session_id"]


def test_run_after_setup_connect_keeps_scale_bound(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.connect_simulator()
    assert runtime.controller.scale is not None
    created = runtime.dispatch(
        "run.new",
        {
            "definition": {
                "run_id": "UX-RUN-1",
                "operator_id": "OP",
                "facility_id": "BEST-BUDS",
                "station_id": "WS-1",
                "cultivars": [{"cultivar_id": "CV-001", "name": "Test"}],
                "capture_mode": "manual",
                "unit": "g",
                "container_id": "DEFAULT",
                "tare_g": 0.0,
                "maximum_capacity_g": 10000.0,
            },
            "data_root": str(tmp_path / "runs"),
            "simulator": True,
        },
    )
    assert created["status"] == "completed"
    assert runtime.controller.scale is not None
    assert runtime.snapshot()["scale_service_bound"] is True
    assert runtime.controller.state == "WAITING_FOR_BARCODE"


def test_failed_tolerance_stays_test_ready_and_blocks_accept(tmp_path):
    service = ScaleControlService(simulated_device(), tmp_path / "session")
    service.start_calibration(active_capture=False, operator_id="OP", maintenance_authorized=True)
    service.add_calibration_samples("zero", [1000, 1001, 999, 1000])
    service.add_calibration_samples(
        "loaded", [101000, 101001, 100999, 101000], reference_weight_g=1000
    )
    service.calculate_calibration()
    # Wrong raw band → should fail local tolerance.
    result = service.test_calibration([1000, 1001, 999, 1000])
    assert result["passed_local_tolerance"] is False
    assert "operator_summary" in result
    assert service.active_calibration["stage"] == "test_ready"
    with pytest.raises(ValueError, match="not saved|not match|Test"):
        service.accept_calibration(maintenance_authorized=True, second_confirmation=True)


def test_zero_without_run(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.connect_simulator()
    runtime.simulator_set_weight(0.0)
    result = runtime.zero_scale()
    assert result["status"] == "completed"


def test_auto_plant_id_helper(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    first = runtime.next_auto_plant_id()
    second = runtime.next_auto_plant_id()
    assert first.startswith("AUTO-")
    assert first != second


def test_missing_scale_returns_friendly_failed_result(tmp_path):
    controller = ApplicationController(tmp_path / "config")
    result = controller.dispatch(ActionRequest("scale.calibration.start", {"maintenance_authorized": True}))
    assert result.status == "failed"
    assert "Connect the scale first" in result.message