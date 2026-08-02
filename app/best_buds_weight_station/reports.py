"""Non-authoritative harvest reports (JSON / CSV / XLSX / DOCX).

Authoritative truth remains session JSONL + individual record files.
Reports are operator handoff derivatives compiled from accepted weight records.
"""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from .storage import atomic_json, canonical, parse_jsonl


def _accepted_rows(session_dir: Path) -> list[dict[str, Any]]:
    rows = [
        row
        for row in parse_jsonl(session_dir / "records.jsonl")
        if row.get("event_type") == "weight_record" and row.get("record_status") == "accepted"
    ]
    rows.sort(key=lambda row: row["sequence"])
    return rows


def _write_docx(path: Path, report: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    """Write a simple operator harvest summary Word document."""
    try:
        from docx import Document
        from docx.shared import Pt
    except ImportError as exc:  # pragma: no cover - exercised when optional dep missing
        raise RuntimeError(
            "python-docx is required for DOCX reports. Install with: pip install python-docx"
        ) from exc

    doc = Document()
    title = doc.add_heading("Best Buds Harvest Weight Report", level=0)
    title.runs[0].font.size = Pt(18)

    doc.add_paragraph(f"Report ID: {report['report_id']}")
    doc.add_paragraph(f"Session ID: {report['session_id']}")
    doc.add_paragraph(f"Compiled at: {report['compiled_at']}")
    doc.add_paragraph(f"Record count: {report['record_count']}")
    doc.add_paragraph(f"Total net weight: {report['total_net_g']} g")
    doc.add_paragraph(
        "Non-claim: This export is a non-authoritative operator handoff. "
        "Authoritative truth is the local session JSONL ledger."
    )

    doc.add_heading("Cultivar totals", level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    header = table.rows[0].cells
    header[0].text = "Cultivar"
    header[1].text = "Net g"
    for cultivar, net in report["cultivar_totals"].items():
        cells = table.add_row().cells
        cells[0].text = str(cultivar)
        cells[1].text = f"{net}"
    total_row = table.add_row().cells
    total_row[0].text = "TOTAL"
    total_row[1].text = f"{report['total_net_g']}"

    doc.add_heading("Plant records", level=1)
    detail = doc.add_table(rows=1, cols=6)
    detail.style = "Table Grid"
    for idx, name in enumerate(("Seq", "Barcode", "Cultivar", "Gross g", "Tare g", "Net g")):
        detail.rows[0].cells[idx].text = name
    for row in rows:
        cells = detail.add_row().cells
        cells[0].text = str(row.get("sequence", ""))
        cells[1].text = str(row.get("barcode_raw", ""))
        cells[2].text = str(row.get("cultivar_normalized_name", ""))
        cells[3].text = str(row.get("gross_g", ""))
        cells[4].text = str(row.get("tare_g", ""))
        cells[5].text = str(row.get("net_g", ""))

    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)


def compile_report(session_dir: str | Path) -> dict[str, Any]:
    directory = Path(session_dir)
    rows = _accepted_rows(directory)
    total = round(sum(float(row["net_g"]) for row in rows), 3)
    by_cultivar: dict[str, float] = defaultdict(float)
    for row in rows:
        by_cultivar[str(row["cultivar_normalized_name"])] += float(row["net_g"])
    source_hash = hashlib.sha256(("\n".join(canonical(row) for row in rows) + "\n").encode()).hexdigest()
    compiled_at = max([str(row["captured_at"]) for row in rows], default="1970-01-01T00:00:00Z")
    report: dict[str, Any] = {
        "report_id": f"harvest-report-{rows[0]['session_id'] if rows else directory.name}",
        "session_id": rows[0]["session_id"] if rows else directory.name,
        "record_count": len(rows),
        "total_net_g": total,
        "cultivar_totals": {key: round(value, 3) for key, value in sorted(by_cultivar.items())},
        "records_sha256": source_hash,
        "compiled_at": compiled_at,
        "authoritative": False,
        "non_claims": [
            "Non-authoritative operator handoff report.",
            "Authoritative truth remains session JSONL and individual record files.",
        ],
    }

    out = directory / "reports"
    out.mkdir(exist_ok=True)
    json_path = out / "harvest_run_report.json"
    csv_path = out / "harvest_run_report.csv"
    xlsx_path = out / "harvest_run_report.xlsx"
    docx_path = out / "harvest_run_report.docx"

    atomic_json(json_path, report)

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cultivar", "net_g"])
        for cultivar, net in report["cultivar_totals"].items():
            writer.writerow([cultivar, net])
        writer.writerow(["TOTAL", total])

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Summary"
    sheet.append(["Cultivar", "Net g"])
    for cultivar, net in report["cultivar_totals"].items():
        sheet.append([cultivar, net])
    sheet.append(["TOTAL", total])
    detail = workbook.create_sheet("Records")
    detail.append(["sequence", "barcode_raw", "cultivar", "gross_g", "tare_g", "net_g", "record_id"])
    for row in rows:
        detail.append(
            [
                row.get("sequence"),
                row.get("barcode_raw"),
                row.get("cultivar_normalized_name"),
                row.get("gross_g"),
                row.get("tare_g"),
                row.get("net_g"),
                row.get("record_id"),
            ]
        )
    workbook.save(xlsx_path)

    _write_docx(docx_path, report, rows)

    artifacts = {
        "json": str(json_path.resolve()),
        "csv": str(csv_path.resolve()),
        "xlsx": str(xlsx_path.resolve()),
        "docx": str(docx_path.resolve()),
    }
    report["artifacts"] = artifacts
    report["json_path"] = artifacts["json"]
    return report
