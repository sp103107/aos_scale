"""SR14 auto-record after Lock plus operator beep callback.

Covers:
- settings.auto_record_after_lock.set default off keeps Confirm
- when on, capture.weight.lock commits and returns the record
- existing automatic (stable→commit) is unchanged
- duplicate pre-gate still blocks before auto-record-on-lock
- success beep is recorded on the controller feedback list
"""
from __future__ import annotations

from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.operator_beep import play_operator_beep
from tests.test_sr3_capture_ux import feed_stable
from tests.v013_helpers import controller


def test_auto_record_after_lock_commits_on_lock(tmp_path):
    c = controller(tmp_path, "manual")
    updated = c.dispatch(ActionRequest("settings.auto_record_after_lock.set", {"auto_record_after_lock": True}))
    assert updated.status == "completed"
    assert c.settings.auto_record_after_lock is True
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "LOCK-AUTO"}))
    feed_stable(c)
    locked = c.dispatch(ActionRequest("capture.weight.lock"))
    assert locked.status == "completed"
    assert c.state == "WAITING_FOR_BARCODE"
    assert (locked.data or {}).get("record")["barcode_raw"] == "LOCK-AUTO"
    assert "success" in c.feedback_events


def test_lock_without_setting_still_needs_confirm(tmp_path):
    c = controller(tmp_path, "manual")
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "LOCK-MANUAL"}))
    feed_stable(c)
    locked = c.dispatch(ActionRequest("capture.weight.lock"))
    assert locked.status == "completed"
    assert c.state == "MANUAL_CONFIRM"
    assert not (locked.data or {}).get("record")
    assert c.feedback_events == []


def test_auto_record_after_lock_respects_duplicate_gate(tmp_path):
    c = controller(tmp_path, "manual")
    c.dispatch(ActionRequest("settings.auto_record_after_lock.set", {"auto_record_after_lock": True}))
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "LOCK-DUP"}))
    feed_stable(c)
    c.dispatch(ActionRequest("capture.weight.lock"))
    blocked = c.dispatch(ActionRequest("barcode.submit", {"barcode": "LOCK-DUP"}))
    assert blocked.status == "blocked"
    assert c.state == "WAITING_FOR_BARCODE"


def test_automatic_mode_still_records_on_stable(tmp_path):
    c = controller(tmp_path, "automatic")
    c.dispatch(ActionRequest("barcode.submit", {"barcode": "STILL-AUTO"}))
    result = feed_stable(c)
    assert result.truth_class == "RECEIPT_CONFIRMED"
    assert c.state == "WAITING_FOR_BARCODE"


def test_play_operator_beep_is_silent_under_pytest():
    play_operator_beep("success")
