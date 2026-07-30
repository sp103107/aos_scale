from __future__ import annotations

import time
from pathlib import Path

from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.operator_runtime import OperatorRuntime
from best_buds_weight_station.platform_paths import default_app_paths


def definition(mode: str = "automatic") -> dict:
    return {
        "run_id": f"TEST-{mode.upper()}",
        "operator_id": "TEST-OPERATOR",
        "facility_id": "BEST-BUDS",
        "station_id": "WEIGHT-STATION-01",
        "cultivars": [{"cultivar_id": "CV-001", "name": "Test Cultivar"}],
        "capture_mode": mode,
        "unit": "g",
        "container_id": "DEFAULT",
        "tare_g": 0.0,
        "maximum_capacity_g": 10000.0,
    }


def wait_samples(runtime: OperatorRuntime, count: int = 6):
    deadline = time.time() + 10
    while time.time() < deadline:
        if len(runtime.buffer.recent(count)) >= count:
            return
        time.sleep(0.05)
    raise AssertionError("samples not produced")


def wait_state(runtime: OperatorRuntime, state: str):
    deadline = time.time() + 10
    while time.time() < deadline:
        if runtime.controller.state == state:
            return
        time.sleep(0.05)
    raise AssertionError(f"state did not become {state}: {runtime.controller.state}")


def test_background_worker_drives_automatic_commit(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs", capture_mode="automatic")
    runtime.dispatch("run.new", {"definition": definition(), "data_root": str(tmp_path / "runs"), "simulator": True})
    runtime.connect_simulator()
    runtime.simulator_set_weight(1250)
    runtime.submit_barcode("PLANT-001")
    wait_state(runtime, "WAITING_FOR_BARCODE")
    assert runtime.controller.last_record["net_g"] == 1250.0
    assert runtime.snapshot()["alice_truth_class"] == "RECEIPT_CONFIRMED"
    runtime.close()
    assert not runtime.worker.running


def test_physical_zero_path_omits_synthetic_readings(tmp_path, monkeypatch):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.dispatch("run.new", {"definition": definition("manual"), "data_root": str(tmp_path / "runs"), "simulator": True})
    runtime.connect_simulator()
    captured = {}
    original = runtime.controller.dispatch
    def spy(request):
        if request.action_type == "scale.zero": captured.update(request.payload)
        return original(request)
    monkeypatch.setattr(runtime.controller, "dispatch", spy)
    runtime.zero_scale()
    assert "readings_g" not in captured
    runtime.close()


def test_worker_stop_does_not_surface_stream_off_error(tmp_path, monkeypatch):
    from best_buds_weight_station.device_service import DeviceProtocolError

    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.dispatch("run.new", {"definition": definition("manual"), "data_root": str(tmp_path / "runs"), "simulator": True})
    runtime.connect_simulator()
    wait_samples(runtime, 3)
    assert runtime.worker.running

    def boom_stop_stream():
        raise DeviceProtocolError("stream stop was not acknowledged")

    monkeypatch.setattr(runtime.controller.device, "stop_stream", boom_stop_stream)
    runtime.worker.stop(stop_stream=True)
    assert runtime.last_worker_error is None
    runtime.close()


def test_zero_scale_survives_worker_restart_failure(tmp_path, monkeypatch):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.dispatch("run.new", {"definition": definition("manual"), "data_root": str(tmp_path / "runs"), "simulator": True})
    runtime.connect_simulator()
    wait_samples(runtime, 3)

    def boom_start():
        raise RuntimeError("stream restart failed")

    monkeypatch.setattr(runtime.worker, "start", boom_start)
    result = runtime.zero_scale()
    assert result["status"] == "completed"
    assert runtime.last_worker_error is not None
    assert "stream restart failed" in runtime.last_worker_error
    runtime.close()


def test_display_weight_uses_median_of_recent_samples():
    from best_buds_weight_station.operator_runtime import ReadingBuffer, ReadingSample
    from best_buds_weight_station.models import now_rfc3339

    buf = ReadingBuffer()
    for weight in (10.0, 100.0, 12.0):
        buf.append(
            ReadingSample(
                weight_g=weight,
                raw_value=int(weight),
                ready=True,
                device_ms=1,
                received_at=now_rfc3339(),
                truth_class="SIMULATOR_PASS",
            )
        )
    assert buf.display_weight_g(3) == 12.0


def test_calibration_dialog_steps_cover_walkthrough():
    from best_buds_weight_station.pyside_frontend import CalibrationDialog

    for key in ("before", "start", "zero", "loaded", "test", "accept", "after", "cancelled"):
        assert key in CalibrationDialog.STEPS
        assert len(CalibrationDialog.STEPS[key]) > 20


def test_live_tare_capture_uses_reading_buffer(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.dispatch("run.new", {"definition": definition("manual"), "data_root": str(tmp_path / "runs"), "simulator": True})
    runtime.connect_simulator(); runtime.simulator_set_weight(100.0); runtime.buffer.clear(); wait_samples(runtime, 8)
    result = runtime.capture_container_tare("SLING", 8)
    assert result["status"] == "completed"
    assert runtime.controller.loaded_run.store.context.tare_g == 100.0
    runtime.close()


def test_calibration_workflow_reachable_from_operator_runtime(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.dispatch("run.new", {"definition": definition("manual"), "data_root": str(tmp_path / "runs"), "simulator": True})
    runtime.connect_simulator()
    runtime.start_calibration()
    runtime.simulator_set_weight(0); runtime.buffer.clear(); wait_samples(runtime, 8); runtime.add_calibration_zero_samples()
    runtime.simulator_set_weight(2000); runtime.buffer.clear(); wait_samples(runtime, 8)
    proposal = runtime.add_calibration_loaded_samples(2000)
    tested = runtime.test_calibration()
    accepted = runtime.accept_calibration()
    assert proposal["status"] == tested["status"] == accepted["status"] == "completed"
    assert accepted["data"]["calibration_receipt"]["physical_device_pass"] is False
    runtime.close()


def test_new_canonical_device_actions(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.dispatch("run.new", {"definition": definition("manual"), "data_root": str(tmp_path / "runs"), "simulator": True})
    runtime.connect_simulator()
    assert runtime.dispatch("device.ping")["status"] == "completed"
    assert runtime.dispatch("device.status")["data"]["device_status"]["connected"] is True
    runtime.close()


def test_platform_paths_are_durable_and_separated():
    paths = default_app_paths()
    assert paths.config.exists() and paths.logs.exists() and paths.runs.exists()
    assert paths.config != paths.runs


def test_failed_connect_does_not_start_reading_worker(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.dispatch("run.new", {"definition": definition("manual"), "data_root": str(tmp_path / "runs")})

    def failing_dispatch(request: ActionRequest):
        from best_buds_weight_station.actions import ActionResult

        if request.action_type != "device.connect":
            return runtime.controller.__class__.dispatch(runtime.controller, request)
        return ActionResult(
            action_id=request.action_id,
            action_type=request.action_type,
            status="failed",
            truth_class="BLOCKED",
            state=runtime.controller.state,
            message="OSError: Access is denied",
            data={"error_class": "OSError"},
        )

    runtime.controller.dispatch = failing_dispatch  # type: ignore[method-assign]
    result = runtime.connect_serial("COM99", 115200)
    assert result["status"] == "failed"
    assert "Access is denied" in result["message"]
    assert not runtime.worker.running
    runtime.close()


def test_validated_connect_starts_reading_worker(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.dispatch("run.new", {"definition": definition("manual"), "data_root": str(tmp_path / "runs"), "simulator": True})
    result = runtime.connect_simulator()
    assert result["status"] == "completed"
    assert runtime.worker.running
    assert runtime.controller.device is not None
    assert runtime.controller.device.status.protocol_validated
    runtime.close()


def test_setup_connect_allowed_without_loaded_run(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    assert runtime.controller.state == "NO_RUN"
    result = runtime.connect_simulator()
    assert result["status"] == "completed"
    assert result["data"].get("setup_only") is True
    assert runtime.controller.device is not None
    assert runtime.controller.device.status.protocol_validated
    assert runtime.worker.running
    runtime.close()
