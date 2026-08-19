"""Auto-record alert setting and operator activity snapshot tests."""
from __future__ import annotations

from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.operator_runtime import OperatorRuntime

from tests.v013_helpers import controller, definition


def test_auto_record_alert_setting_validation(tmp_path):
    c = controller(tmp_path)
    result = c.dispatch(
        ActionRequest(
            "settings.auto_record_alert.set",
            {"auto_record_alert": "voice", "auto_record_alert_phrase": "Weight recorded"},
        )
    )
    assert result.status == "completed"
    assert c.settings.auto_record_alert == "voice"


def test_finish_then_new_run_without_clearing_loaded_run(tmp_path):
    c = controller(tmp_path)
    c.machine.state = __import__(
        "best_buds_weight_station.state_machine", fromlist=["State"]
    ).State.WAITING_FOR_BARCODE
    assert c.dispatch(ActionRequest("run.finish")).status == "completed"
    assert c.state == "RUN_FINISHED"
    second = definition(session_id="HR-2026-TEST-second")
    second["run_id"] = "HR-2026-SECOND"
    created = c.dispatch(
        ActionRequest(
            "run.new",
            {"definition": second, "data_root": str(tmp_path / "data2"), "simulator": True},
        )
    )
    assert created.status == "completed"
    assert c.loaded_run.store.context.run_id == "HR-2026-SECOND"


def test_operator_activity_in_snapshot(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    runtime.set_activity("zeroing", "tare")
    snap = runtime.snapshot()
    assert snap["activity_phase"] == "zeroing"
    assert "Zeroing" in snap["activity_message"]
    runtime.clear_activity()
    assert runtime.snapshot()["activity_phase"] is None


def test_on_record_saved_callback(tmp_path):
    runtime = OperatorRuntime(tmp_path / "runs")
    seen: list[dict] = []
    runtime.on_record_saved = seen.append
    runtime._capture_result({"status": "completed", "data": {"record": {"record_id": "r1"}}})
    assert seen and seen[0]["data"]["record"]["record_id"] == "r1"
