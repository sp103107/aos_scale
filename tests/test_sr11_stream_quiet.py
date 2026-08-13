"""SR11 live stream quiet window — resume/load quiet apply and skip redundant SET_CAL.

Covers:
- ensure_reading_worker restarting a stopped SimulatedFirmwareTransport worker
- _apply_active_scale_profile skipping SET_CAL when STATUS factor already matches
- resume_run under a running worker leaving worker.running True
"""
from __future__ import annotations

import time

from best_buds_weight_station.operator_runtime import OperatorRuntime


def _definition(run_id: str = "SR11-QUIET-RUN") -> dict:
    return {
        "run_id": run_id,
        "operator_id": "SR11-OP",
        "facility_id": "BEST-BUDS",
        "station_id": "WEIGHT-STATION-01",
        "cultivars": [{"cultivar_id": "CV-001", "name": "Quiet Strain"}],
        "capture_mode": "manual",
        "unit": "g",
        "container_id": "DEFAULT",
        "tare_g": 0.0,
        "maximum_capacity_g": 10000.0,
    }


def test_ensure_reading_worker_restarts_stopped_simulator_worker(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    try:
        result = runtime.connect_simulator()
        assert result["status"] == "completed"
        assert runtime.worker.running
        runtime.worker.stop(stop_stream=True)
        assert not runtime.worker.running
        runtime.last_worker_error = "stale-before-ensure"
        runtime.ensure_reading_worker()
        assert runtime.worker.running
        assert runtime.last_worker_error is None
    finally:
        runtime.close()


def test_apply_active_scale_profile_skips_set_cal_when_factor_matches(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    try:
        assert runtime.connect_simulator()["status"] == "completed"
        # Assign a profile-bound BBWS id; simulator default factor is 103.2.
        assert runtime.set_device_id("BBWS-SCALE-011")["status"] == "completed"
        device = runtime.controller.device
        assert device is not None
        transport = device.transport
        assert transport is not None
        matching = float(device.status.calibration_factor)
        runtime.controller.scale_profiles.create(
            name="SR11 Match Factor",
            device_id="BBWS-SCALE-011",
            calibration_factor=matching,
            activate=True,
        )
        transport.commands.clear()
        applied = runtime.controller._apply_active_scale_profile()
        assert applied is not None
        assert applied["set_cal_applied"] is False
        assert applied["calibration_factor"] == matching
        assert any(cmd == "STATUS" for cmd in transport.commands)
        assert not any(str(cmd).startswith("SET_CAL") for cmd in transport.commands)
    finally:
        runtime.close()


def test_resume_run_under_running_worker_leaves_worker_running(tmp_path):
    data_root = tmp_path / "runs"
    seed = OperatorRuntime(data_root)
    try:
        created = seed.dispatch(
            "run.new",
            {"definition": _definition(), "data_root": str(data_root), "simulator": True},
        )
        assert created["status"] == "completed"
    finally:
        seed.close()

    runtime = OperatorRuntime(data_root)
    try:
        assert runtime.connect_simulator()["status"] == "completed"
        assert runtime.worker.running
        # Give the reader a beat so resume quiet-stop has a live stream to pause.
        deadline = time.time() + 2.0
        while len(runtime.buffer.recent(3)) < 1 and time.time() < deadline:
            time.sleep(0.05)
        result = runtime.resume_run()
        assert result["status"] == "completed"
        assert runtime.worker.running
        assert runtime.last_worker_error is None
    finally:
        runtime.close()
