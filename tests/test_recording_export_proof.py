"""Proof: weigh/record path updates CSV and export produces CSV + DOCX."""

from __future__ import annotations

import csv
from pathlib import Path

from best_buds_weight_station.models import CaptureCommand, RunContext
from best_buds_weight_station.operator_runtime import OperatorRuntime
from best_buds_weight_station.reports import compile_report
from best_buds_weight_station.storage import SessionStore
from tests.v013_helpers import definition


def test_commit_appends_records_csv(tmp_path):
    context = RunContext("S1", "R1", "OP", "F", "ST", "CV", "raw", "Norm Cultivar", "BIN", 10.0)
    store = SessionStore(tmp_path, context)
    # CaptureCommand(barcode, gross_g, sample_count, stability_metrics, mode)
    record, receipt = store.commit(CaptureCommand("PLANT-100", 110.0, 8, {}, "manual"))
    csv_path = store.session_dir / "records.csv"
    assert csv_path.exists()
    assert receipt.derivative_status["csv"] == "updated"
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["barcode_raw"] == "PLANT-100"
    assert float(rows[0]["net_g"]) == 100.0  # 110 gross − 10 tare
    assert rows[0]["record_id"] == record["record_id"]


def test_compile_report_writes_csv_xlsx_docx_json(tmp_path):
    context = RunContext("S2", "R2", "OP", "F", "ST", "CV", "raw", "Alpha", "BIN", 0.0)
    store = SessionStore(tmp_path, context)
    store.commit(CaptureCommand("A-1", 100.0, 8, {}, "manual"))
    store.commit(CaptureCommand("A-2", 50.0, 8, {}, "manual"))
    report = compile_report(store.session_dir)
    assert report["record_count"] == 2
    assert report["total_net_g"] == 150.0
    artifacts = report["artifacts"]
    for key in ("json", "csv", "xlsx", "docx"):
        path = Path(artifacts[key])
        assert path.exists(), key
        assert path.stat().st_size > 0, key
    assert Path(artifacts["docx"]).suffix == ".docx"
    # DOCX is a zip package; PK header proves a real Office Open XML file.
    assert Path(artifacts["docx"]).read_bytes()[:2] == b"PK"


def test_operator_export_copies_handoff_and_session_csv(tmp_path, monkeypatch):
    from tests.test_operator_runtime import wait_state

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "localappdata"))
    runtime = OperatorRuntime(tmp_path / "runs", capture_mode="automatic")
    runtime.dispatch(
        "run.new",
        {
            "definition": definition("automatic"),
            "data_root": str(tmp_path / "runs"),
            "simulator": True,
        },
    )
    runtime.connect_simulator()
    runtime.simulator_set_weight(1250.0)
    runtime.submit_barcode("EXPORT-PROOF-1")
    wait_state(runtime, "WAITING_FOR_BARCODE")
    assert runtime.controller.last_record is not None
    session_csv = runtime.controller.loaded_run.store.session_dir / "records.csv"
    assert session_csv.exists()

    dest = tmp_path / "handoff"
    exported = runtime.dispatch("report.export", {"destination": str(dest)})
    assert exported["status"] == "completed"
    paths = exported["data"]["paths"]
    names = {Path(path).name for path in paths}
    assert "harvest_run_report.csv" in names
    assert "harvest_run_report.docx" in names
    assert "harvest_run_report.json" in names
    assert "records.csv" in names
    assert (dest / "harvest_run_report.docx").read_bytes()[:2] == b"PK"
