"""SR15 offscreen Qt: duplicate Cancel writes nothing; Station Settings auto-record.

Requires pytest-qt (dev extra). Uses QT_QPA_PLATFORM=offscreen so CI/headless
Windows hosts can run the dialogs without a harvest operator at the keyboard.
"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("pytestqt")
pytest.importorskip("PySide6")

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from best_buds_weight_station.operator_runtime import OperatorRuntime
from best_buds_weight_station.pyside_frontend import MainWindow, StationSettingsDialog
from best_buds_weight_station.storage import parse_jsonl
from tests.test_sr3_capture_ux import feed_stable
from tests.v013_helpers import definition


def _weight_records(runtime: OperatorRuntime) -> list[dict]:
    run = runtime.controller.loaded_run
    assert run is not None
    return [
        row
        for row in parse_jsonl(run.store.records_path)
        if row.get("event_type") == "weight_record"
    ]


def _runtime_with_run(tmp_path, monkeypatch) -> OperatorRuntime:
    # Isolate station settings from the operator's live LOCALAPPDATA profile.
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))
    runtime = OperatorRuntime(tmp_path / "runs", capture_mode="manual")
    created = runtime.new_run(
        {"definition": definition("manual"), "data_root": str(tmp_path / "runs"), "simulator": True}
    )
    assert created.get("status") == "completed"
    connected = runtime.connect_simulator()
    assert connected.get("status") == "completed"
    return runtime


def _click_duplicate_button(button_text: str) -> None:
    def _click() -> None:
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMessageBox) and widget.windowTitle() == "Duplicate barcode":
                for button in widget.buttons():
                    if button.text() == button_text:
                        button.click()
                        return

    QTimer.singleShot(0, _click)


def test_duplicate_cancel_writes_nothing(qtbot, tmp_path, monkeypatch):
    runtime = _runtime_with_run(tmp_path, monkeypatch)
    try:
        runtime.submit_barcode("QT-DUP-1")
        feed_stable(runtime.controller)
        runtime.lock_weight()
        runtime.dispatch("capture.confirm")
        assert len(_weight_records(runtime)) == 1

        window = MainWindow(runtime, simulator=True, smoke=False)
        qtbot.addWidget(window)
        window.show()
        window.barcode.setText("QT-DUP-1")
        _click_duplicate_button("Cancel")
        window.submit_barcode()
        qtbot.waitUntil(
            lambda: "Duplicate scan cancelled" in (window.statusBar().currentMessage() or ""),
            timeout=3000,
        )
        assert len(_weight_records(runtime)) == 1
        assert runtime.controller.state == "WAITING_FOR_BARCODE"
    finally:
        runtime.close()


def test_station_settings_sets_auto_record_after_lock(qtbot, tmp_path, monkeypatch):
    runtime = _runtime_with_run(tmp_path, monkeypatch)
    try:
        assert runtime.controller.settings.auto_record_after_lock is False
        dialog = StationSettingsDialog(runtime)
        qtbot.addWidget(dialog)
        dialog.show()
        dialog.auto_record.setCurrentIndex(1)
        dialog.save()
        assert runtime.controller.settings.auto_record_after_lock is True
    finally:
        runtime.close()
