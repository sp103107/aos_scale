"""BBWS SR3 capture UX: lock-before-confirm and recent plant log."""
from __future__ import annotations

import os

import pytest

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


def test_capture_scanner_dialog_returns_scanned_barcode():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication, QDialog
    from best_buds_weight_station.pyside_frontend import ScannerTestDialog

    app = QApplication.instance() or QApplication([])
    dialog = ScannerTestDialog(capture=True)
    dialog.field.setText("PLANT-SCAN-42")

    dialog._accepted_scan()

    assert dialog.accepted_barcode == "PLANT-SCAN-42"
    assert dialog.result() == QDialog.Accepted
    app.processEvents()


def test_pyside_scan_is_gated_and_layout_scrolls():
    from pathlib import Path

    source = (
        Path(__file__).parents[1]
        / "app"
        / "best_buds_weight_station"
        / "pyside_frontend.py"
    ).read_text(encoding="utf-8")

    assert "self.scan_btn.setEnabled(ready" in source
    assert "ScannerTestDialog(self, capture=True)" in source
    assert "QScrollArea" in source
    assert "scroll.setWidget(central)" in source
