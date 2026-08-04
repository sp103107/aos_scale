"""BBWS SR3 capture UX: lock-before-confirm and recent plant log."""
from __future__ import annotations

from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.operator_runtime import OperatorRuntime
from best_buds_weight_station.simulator import stable_sequence
from tests.v013_helpers import controller


def feed_stable(c, target=1250.0):
    result = None
    for reading in stable_sequence(target):
        result = c.dispatch(
            ActionRequest("reading.ingest", {"weight_g": reading.weight_g, "raw_value": reading.raw_value})
        )
    return result


def test_manual_requires_lock_before_confirm(tmp_path):
    c = controller(tmp_path, "manual")
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "SR3-LOCK"}))
    feed_stable(c)
    assert c.state == "WEIGHT_STABLE"
    blocked = c.dispatch(ActionRequest("capture.confirm"))
    assert blocked.status == "failed"
    assert c.state == "WEIGHT_STABLE"
    locked = c.dispatch(ActionRequest("capture.weight.lock"))
    assert locked.status == "completed"
    assert c.state == "MANUAL_CONFIRM"
    assert float(locked.data["locked_weight_g"]) == 1250.0
    done = c.dispatch(ActionRequest("capture.confirm"))
    assert done.truth_class == "RECEIPT_CONFIRMED"
    assert c.state == "WAITING_FOR_BARCODE"


def test_automatic_mode_still_auto_records(tmp_path):
    c = controller(tmp_path, "automatic")
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "SR3-AUTO"}))
    result = feed_stable(c)
    assert result.truth_class == "RECEIPT_CONFIRMED"
    assert c.state == "WAITING_FOR_BARCODE"
    assert c.last_record["barcode_raw"] == "SR3-AUTO"


def test_recent_plants_snapshot_newest_first(tmp_path):
    c = controller(tmp_path, "manual")
    for barcode in ("P-1", "P-2"):
        c.dispatch(ActionRequest("barcode.submit", {"barcode": barcode}))
        feed_stable(c, 500.0)
        c.dispatch(ActionRequest("capture.weight.lock"))
        c.dispatch(ActionRequest("capture.confirm"))
    runtime = OperatorRuntime(tmp_path / "runs", capture_mode="manual")
    # Bind the already-loaded controller session into a runtime snapshot helper.
    runtime.controller = c
    plants = runtime.recent_plants(50)
    assert len(plants) >= 2
    assert plants[0]["barcode_raw"] == "P-2"
    assert plants[1]["barcode_raw"] == "P-1"
    runtime.close()


def test_cancel_from_weight_stable(tmp_path):
    c = controller(tmp_path, "manual")
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "SR3-CANCEL"}))
    feed_stable(c)
    assert c.state == "WEIGHT_STABLE"
    result = c.dispatch(ActionRequest("capture.cancel"))
    assert result.status == "completed"
    assert c.state == "WAITING_FOR_BARCODE"
