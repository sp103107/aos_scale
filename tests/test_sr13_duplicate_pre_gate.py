"""SR13 duplicate barcode pre-gate — warn before recording; cancel writes nothing.

Covers:
- barcode.submit blocks when the barcode is already in the session
- acknowledge_duplicate continues and tags duplicate_status accepted
- automatic mode cannot silently commit a duplicate
"""
from __future__ import annotations

from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.storage import parse_jsonl
from tests.test_sr3_capture_ux import feed_stable
from tests.v013_helpers import controller


def _weight_records(c) -> list[dict]:
    return [
        row
        for row in parse_jsonl(c.loaded_run.store.records_path)
        if row.get("event_type") == "weight_record"
    ]


def test_duplicate_barcode_blocks_before_weigh(tmp_path):
    c = controller(tmp_path, "manual")
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "DUP-1"}))
    feed_stable(c)
    c.dispatch(ActionRequest("capture.weight.lock"))
    done = c.dispatch(ActionRequest("capture.confirm"))
    assert done.status == "completed"
    assert c.state == "WAITING_FOR_BARCODE"
    blocked = c.dispatch(ActionRequest("barcode.submit", {"barcode": "dup-1"}))
    assert blocked.status == "blocked"
    assert blocked.data.get("duplicate_barcode") is True
    assert c.state == "WAITING_FOR_BARCODE"
    assert len(_weight_records(c)) == 1


def test_duplicate_continue_writes_accepted_record(tmp_path):
    c = controller(tmp_path, "manual")
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "DUP-2"}))
    feed_stable(c, 500.0)
    c.dispatch(ActionRequest("capture.weight.lock"))
    c.dispatch(ActionRequest("capture.confirm"))
    accepted = c.dispatch(
        ActionRequest("barcode.submit", {"barcode": "DUP-2", "acknowledge_duplicate": True})
    )
    assert accepted.status == "accepted"
    assert c.state == "WAITING_FOR_STABLE_WEIGHT"
    feed_stable(c, 510.0)
    c.dispatch(ActionRequest("capture.weight.lock"))
    saved = c.dispatch(ActionRequest("capture.confirm"))
    assert saved.status == "completed"
    records = _weight_records(c)
    assert len(records) == 2
    assert records[1]["duplicate_status"] == "accepted"


def test_duplicate_gate_blocks_automatic_before_auto_commit(tmp_path):
    c = controller(tmp_path, "automatic")
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "DUP-AUTO"}))
    result = feed_stable(c)
    assert result.truth_class == "RECEIPT_CONFIRMED"
    blocked = c.dispatch(ActionRequest("barcode.submit", {"barcode": "DUP-AUTO"}))
    assert blocked.status == "blocked"
    assert c.state == "WAITING_FOR_BARCODE"
    assert len(_weight_records(c)) == 1
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "DUP-AUTO", "acknowledge_duplicate": True}))
    second = feed_stable(c, 1260.0)
    assert second.truth_class == "RECEIPT_CONFIRMED"
    records = _weight_records(c)
    assert len(records) == 2
    assert records[1]["duplicate_status"] == "accepted"
