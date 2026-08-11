from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QDoubleSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .operator_runtime import OperatorRuntime
from .operator_surface import ROUTINE_ACTION_LAYOUT, frozen_display_weight
from .run_manager import facility_id_from_cultivator
from .scale_face import ScaleFaceWindow
from .ui_tokens import (
    COLOR_ACTIVE_BARCODE,
    COLOR_PRIMARY,
    COLOR_WARN_BG,
    COLOR_WARN_BORDER,
    COLOR_WARN_FG,
    build_pyside_stylesheet,
    capture_pill_label,
)
from .units import display_to_grams, format_weight, grams_to_display, unit_label
from .version import __version__


# SR4: stylesheet from salvage-aligned tokens (see docs/BBWS_SR4_DESIGN_TOKENS.md)
APP_STYLE = build_pyside_stylesheet()


def _eyebrow(text: str) -> QLabel:
    """Uppercase section eyebrow — salvage card language, text-labeled."""
    label = QLabel(text)
    label.setObjectName("eyebrow")
    return label


def _show_result(parent: QWidget, result: dict[str, Any], *, success_title: str = "Completed") -> None:
    if result.get("status") in {"failed", "blocked"}:
        QMessageBox.warning(parent, "Action not completed", result.get("message", "Action failed"))
    elif result.get("terminal", True):
        QMessageBox.information(parent, success_title, result.get("message", "Completed"))


class NewRunDialog(QDialog):
    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self.setObjectName("polishDialog")
        self.setWindowTitle("New Harvest Run")
        form = QFormLayout(self)
        form.addRow(_eyebrow("New harvest run"))
        self.run_id = QLineEdit()
        self.operator_id = QLineEdit()
        self.cultivator = QLineEdit("Best Buds")
        self.strain = QLineEdit()
        self.container = QLineEdit("DEFAULT")
        self.mode = QComboBox(); self.mode.addItems(["manual", "automatic"])
        self.data_root = QLineEdit(runtime.controller.settings.data_root)
        choose = QPushButton("Choose…")
        choose.clicked.connect(self.choose_folder)
        folder = QHBoxLayout(); folder.addWidget(self.data_root); folder.addWidget(choose)
        form.addRow("Harvest-run ID", self.run_id)
        form.addRow("Operator ID", self.operator_id)
        form.addRow("Cultivator", self.cultivator)
        form.addRow("Strain", self.strain)
        form.addRow("Container ID", self.container)
        form.addRow("Capture mode", self.mode)
        form.addRow("Run data folder", folder)
        hint = QLabel("Cultivator is the company/grower. Strain is the sticky plant strain for scans.")
        hint.setWordWrap(True)
        hint.setObjectName("dialogTip")
        form.addRow(hint)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.create_run); buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def choose_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Run Data Folder", self.data_root.text())
        if path:
            self.data_root.setText(path)

    def create_run(self) -> None:
        if (
            not self.run_id.text().strip()
            or not self.operator_id.text().strip()
            or not self.cultivator.text().strip()
            or not self.strain.text().strip()
        ):
            QMessageBox.warning(
                self,
                "Missing information",
                "Run ID, operator ID, cultivator, and strain are required.",
            )
            return
        definition = {
            "run_id": self.run_id.text().strip(),
            "operator_id": self.operator_id.text().strip(),
            "facility_id": facility_id_from_cultivator(self.cultivator.text()),
            "station_id": "WEIGHT-STATION-01",
            "cultivars": [{"cultivar_id": "CV-001", "name": self.strain.text().strip()}],
            "capture_mode": self.mode.currentText(),
            "unit": "g",
            "container_id": self.container.text().strip() or "DEFAULT",
            "tare_g": 0.0,
            "maximum_capacity_g": 10000.0,
        }
        result = self.runtime.dispatch("run.new", {
            "definition": definition,
            "data_root": self.data_root.text().strip(),
            "simulator": False,
        })
        if result["status"] == "completed":
            self.accept()
            parent = self.parent()
            if isinstance(parent, MainWindow):
                parent.maybe_suggest_calibration()
        else:
            _show_result(self, result)


class ResumeRunDialog(QDialog):
    """Pick an in-progress run under the data root and load it (run.load).

    Lists unfinished sessions newest-first; the hidden file-dialog load
    remains available via Browse… for runs stored elsewhere.
    """

    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self.setObjectName("polishDialog")
        self.setWindowTitle("Resume Run")
        self.resize(640, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(_eyebrow("Runs in progress"))
        self.sessions = runtime.controller.run_manager.list_sessions()
        self.listing = QListWidget()
        self.listing.setAccessibleName("Runs in progress")
        for entry in self.sessions:
            strain = f" — {entry['strain']}" if entry.get("strain") else ""
            operator = f" — {entry['operator_id']}" if entry.get("operator_id") else ""
            self.listing.addItem(f"{entry['run_id']}{strain}{operator} — {entry['status']}")
        layout.addWidget(self.listing, 1)
        if self.sessions:
            self.listing.setCurrentRow(0)
            hint = QLabel("Newest first. Select a run and press Resume. Finished runs are not listed.")
        else:
            hint = QLabel("No runs in progress under the current data folder. Start a new run or Browse… for one stored elsewhere.")
        hint.setWordWrap(True)
        hint.setObjectName("dialogTip")
        layout.addWidget(hint)
        buttons = QDialogButtonBox()
        resume_btn = buttons.addButton("Resume", QDialogButtonBox.AcceptRole)
        resume_btn.setEnabled(bool(self.sessions))
        new_btn = buttons.addButton("New Run…", QDialogButtonBox.ActionRole)
        browse_btn = buttons.addButton("Browse…", QDialogButtonBox.ActionRole)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.resume_selected)
        buttons.rejected.connect(self.reject)
        new_btn.clicked.connect(self.open_new_run)
        browse_btn.clicked.connect(self.browse)
        self.listing.itemDoubleClicked.connect(lambda _item: self.resume_selected())
        layout.addWidget(buttons)

    def resume_selected(self) -> None:
        row = self.listing.currentRow()
        if row < 0 or row >= len(self.sessions):
            return
        result = self.runtime.dispatch("run.load", {"selection": self.sessions[row]["manifest_path"]})
        if result.get("status") == "completed":
            self.accept()
        else:
            _show_result(self, result)

    def open_new_run(self) -> None:
        self.reject()
        NewRunDialog(self.runtime, self.parent() if isinstance(self.parent(), QWidget) else None).exec()

    def browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Existing Run", self.runtime.controller.settings.data_root,
            "Session manifest (session_manifest.json);;JSON files (*.json)",
        )
        if not path:
            return
        result = self.runtime.dispatch("run.load", {"selection": path})
        if result.get("status") == "completed":
            self.accept()
        else:
            _show_result(self, result)


class ScaleSetupDialog(QDialog):
    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self.setWindowTitle("Scale Setup and Device Status")
        self.resize(700, 560)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.mode = QComboBox(); self.mode.addItems(["Physical serial", "Simulator"])
        self.port = QComboBox(); self.port.setEditable(True)
        settings = runtime.controller.settings
        self.baud = QComboBox()
        for rate in (115200, 9600):
            self.baud.addItem(str(rate), rate)
        preferred = int(getattr(settings, "baud_rate", 115200) or 115200)
        idx = self.baud.findData(preferred)
        self.baud.setCurrentIndex(idx if idx >= 0 else 0)
        if settings.serial_port:
            self.port.setEditText(settings.serial_port)
        self.sim_weight = QDoubleSpinBox(); self.sim_weight.setRange(-1000.0, 10000.0); self.sim_weight.setDecimals(3); self.sim_weight.setValue(1250.0)
        form.addRow("Device mode", self.mode)
        form.addRow("Serial port", self.port)
        form.addRow("Baud", self.baud)
        form.addRow("Simulator test weight (g)", self.sim_weight)
        layout.addLayout(form)
        row = QGridLayout()
        actions = [
            ("Refresh Ports", self.refresh_ports, 0, 0),
            ("Connect", self.connect_device, 0, 1),
            ("Disconnect", self.disconnect_device, 0, 2),
            ("PING", self.ping, 1, 0),
            ("STATUS", self.status, 1, 1),
            ("Apply Simulator Weight", self.apply_sim_weight, 1, 2),
        ]
        for text, callback, r, c in actions:
            button = QPushButton(text); button.clicked.connect(callback); row.addWidget(button, r, c)
        layout.addLayout(row)
        self.output = QPlainTextEdit(); self.output.setReadOnly(True)
        layout.addWidget(self.output)
        buttons = QDialogButtonBox(QDialogButtonBox.Close); buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh_ports(); self.status()

    def write(self, payload: Any) -> None:
        self.output.setPlainText(json.dumps(payload, indent=2, sort_keys=True, default=str))

    def refresh_ports(self) -> None:
        result = self.runtime.dispatch("device.discover")
        current = self.port.currentText()
        self.port.clear()
        for item in result.get("data", {}).get("ports", []):
            self.port.addItem(item["device"])
        if current:
            self.port.setEditText(current)
        self.write(result)

    def connect_device(self) -> None:
        try:
            if self.mode.currentText() == "Simulator":
                result = self.runtime.connect_simulator()
                if result.get("status") == "completed":
                    self.runtime.simulator_set_weight(self.sim_weight.value())
            else:
                port = self.port.currentText().strip()
                if not port:
                    raise ValueError("Select or enter a serial port.")
                baud = int(self.baud.currentData() or self.baud.currentText())
                result = self.runtime.connect_serial(port, baud)
            self.write(result)
            if result.get("status") != "completed":
                detail = result.get("data", {}).get("error_detail") or result.get("message") or "Connection failed"
                QMessageBox.warning(self, "Connection failed", str(detail))
        except Exception as exc:
            QMessageBox.warning(self, "Connection failed", f"{type(exc).__name__}: {exc}")

    def disconnect_device(self) -> None:
        try: self.write(self.runtime.disconnect())
        except Exception as exc: QMessageBox.warning(self, "Disconnect failed", str(exc))

    def ping(self) -> None:
        self.write(self.runtime.dispatch("device.ping"))

    def status(self) -> None:
        self.write(self.runtime.dispatch("device.status"))

    def apply_sim_weight(self) -> None:
        try:
            self.runtime.simulator_set_weight(self.sim_weight.value())
            self.write({"status": "completed", "simulator_weight_g": self.sim_weight.value(), "truth_class": "SIMULATOR_PASS"})
        except Exception as exc:
            QMessageBox.warning(self, "Simulator unavailable", str(exc))


class TareDialog(QDialog):
    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self.setWindowTitle("Container Tare")
        form = QFormLayout(self)
        hint = QLabel(
            "Container tare is for NET = GROSS − TARE only. It does not zero the live scale. "
            "Use ZERO for an empty pan. Large negative live numbers mean calibration is still raw (factor ≈ 1.0)."
        )
        hint.setWordWrap(True)
        form.addRow(hint)
        self.container = QLineEdit("DEFAULT")
        self._display_unit = unit_label(runtime.snapshot().get("display_unit") or "g")
        self.known = QDoubleSpinBox()
        self.known.setRange(0.0, 100000.0)
        self.known.setDecimals(4 if self._display_unit != "g" else 3)
        form.addRow("Container ID", self.container)
        form.addRow(f"Known tare ({self._display_unit})", self.known)
        row = QHBoxLayout()
        entered = QPushButton("Save Known Tare"); entered.clicked.connect(self.save_known)
        captured = QPushButton("Capture Empty Container from Live Scale"); captured.clicked.connect(self.capture_live)
        row.addWidget(entered); row.addWidget(captured)
        form.addRow(row)
        self.result_text = QPlainTextEdit(); self.result_text.setReadOnly(True); form.addRow(self.result_text)
        close = QDialogButtonBox(QDialogButtonBox.Close); close.rejected.connect(self.reject); form.addRow(close)

    def show_result(self, result: dict[str, Any]) -> None:
        self.result_text.setPlainText(json.dumps(result, indent=2, sort_keys=True, default=str))
        if result.get("status") == "completed": self.accept()

    def save_known(self) -> None:
        grams = display_to_grams(float(self.known.value()), self._display_unit)
        self.show_result(self.runtime.set_known_tare(self.container.text().strip(), grams))

    def capture_live(self) -> None:
        try: self.show_result(self.runtime.capture_container_tare(self.container.text().strip()))
        except Exception as exc: QMessageBox.warning(self, "Tare capture blocked", str(exc))


class ScannerTestDialog(QDialog):
    """Quick check that a USB HID keyboard-wedge scanner reaches the app (no BLE/SPP)."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        runtime: OperatorRuntime | None = None,
        capture: bool = False,
    ):
        super().__init__(parent)
        self.runtime = runtime
        self.capture = capture
        self.accepted_barcode: str | None = None
        self.setObjectName("polishDialog")
        self.setWindowTitle("Scan Plant Barcode" if capture else "Test Barcode Scanner")
        self.resize(520, 260)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.addWidget(_eyebrow("Scan capture" if capture else "Scanner test"))
        tip = QLabel(
            (
                "Scan the plant tag now. The barcode will be copied into the "
                "station and accepted when you press Enter."
            )
            if capture
            else (
                "Scan any barcode now with a USB HID keyboard-wedge scanner "
                "(or type a code and press Enter). BLE/SPP/camera are not used."
            )
        )
        tip.setWordWrap(True)
        tip.setObjectName("dialogTip")
        layout.addWidget(tip)
        self.field = QLineEdit()
        self.field.setObjectName("barcodeInput")
        self.field.setPlaceholderText("Waiting for scan…")
        self.field.setAccessibleName("Scan capture barcode field")
        self.field.returnPressed.connect(self._accepted_scan)
        layout.addWidget(self.field)
        self.status = QLabel("Waiting for barcode scanner input…")
        self.status.setObjectName("dialogStatus")
        layout.addWidget(self.status)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        QTimer.singleShot(0, self.field.setFocus)

    def _accepted_scan(self) -> None:
        value = self.field.text().strip()
        if not value:
            self.status.setText("Empty scan blocked. Focus this field and try again.")
            return
        if self.capture:
            self.accepted_barcode = value
            self.status.setText(f"Barcode received: {value}")
            self.accept()
            return
        receipt = {
            "receipt_type": "hid_scanner_test",
            "status": "pass",
            "barcode_sample": value,
            "transport": "hid_keyboard_wedge",
            "non_claims": ["HID wedge only — not BLE/SPP barcode protocol"],
        }
        if self.runtime is not None:
            out = Path(self.runtime.controller.settings.data_root) / "scanner_test_receipts"
            out.mkdir(parents=True, exist_ok=True)
            path = out / f"scanner_test_{value[:32].replace('/', '_')}.json"
            path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            receipt["path"] = str(path)
        self.status.setText(f"Scanner OK — received: {value}")
        QMessageBox.information(self, "Scanner OK", f"Scanner OK — received:\n{value}")
        self.accept()


class ChangeStrainDialog(QDialog):
    """Sticky active strain until the operator changes it again."""

    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self.setObjectName("polishDialog")
        self.setWindowTitle("Change Active Strain")
        form = QFormLayout(self)
        form.addRow(_eyebrow("Active strain"))
        current = runtime.snapshot().get("strain") or runtime.snapshot().get("cultivar") or ""
        tip = QLabel(
            "New scans use this strain until you change it again. "
            "This is operator sticky strain — not Metrc compliance."
        )
        tip.setWordWrap(True)
        tip.setObjectName("dialogTip")
        form.addRow(tip)
        self.strain = QLineEdit(str(current))
        form.addRow("Active strain", self.strain)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.apply)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def apply(self) -> None:
        name = self.strain.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing strain", "Enter a strain name.")
            return
        result = self.runtime.dispatch("run.set_active_cultivar", {"name": name})
        if result.get("status") == "completed":
            self.accept()
        else:
            _show_result(self, result)


class StationSettingsDialog(QDialog):
    """Light station settings for barcode policy and display unit."""

    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self.setWindowTitle("Station Settings")
        form = QFormLayout(self)
        self.require_barcode = QComboBox()
        self.require_barcode.addItems(["required (scan/type barcode)", "optional (auto ID allowed)"])
        required = bool(runtime.controller.settings.barcode_required_for_capture)
        self.require_barcode.setCurrentIndex(0 if required else 1)
        form.addRow("Plant barcode policy", self.require_barcode)
        self.display_unit = QComboBox()
        self.display_unit.addItems(["g", "kg", "lb"])
        current = unit_label(getattr(runtime.controller.settings, "display_unit", "g") or "g")
        self.display_unit.setCurrentText(current)
        form.addRow("Display unit (storage stays g)", self.display_unit)
        hint = QLabel("Scanners: USB HID only. Display lb/kg is not legal-for-trade; JSONL stays grams.")
        hint.setStyleSheet("color:#5C6975")
        hint.setWordWrap(True)
        form.addRow(hint)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def save(self) -> None:
        required = self.require_barcode.currentIndex() == 0
        result = self.runtime.dispatch(
            "settings.barcode_policy.set",
            {"barcode_required_for_capture": required},
        )
        if result.get("status") not in {"completed"}:
            _show_result(self, result)
            return
        unit_result = self.runtime.dispatch(
            "settings.display_unit.set",
            {"display_unit": self.display_unit.currentText()},
        )
        if unit_result.get("status") == "completed":
            self.accept()
        else:
            _show_result(self, unit_result)


class CalibrationDialog(QDialog):
    """Step-by-step guided calibration with casual employee instructions."""

    STEPS = {
        "before": (
            "Connect the scale first. A harvest run is optional for calibration. "
            "Empty the pan, enter your verified reference mass in GRAMS below, then follow steps 1–5. "
            "Calibration always uses grams (even if the main screen display unit is kg/lb)."
        ),
        "start": "Step 1 — Start calibration. Do not scan plants until you finish or cancel.",
        "zero": "Step 2 — Empty pan only (no mass). Wait for live weight, then Capture empty samples.",
        "loaded": "Step 3 — Place the verified mass on the pan. For light weights (100 g), wait extra until the live number fully stops climbing — then Capture loaded. Reference must match that mass in grams.",
        "test": "Step 4 — Leave the SAME mass on the pan (do not remove it). Wait one beat, press Test. Pass is required before Accept.",
        "accept": "Step 5 — Accept writes the factor to the scale. Then empty pan → ZERO.",
        "after": "Done. Empty the pan → ZERO → optional SET TARE → resume scanning. Large wild numbers before Accept were uncalibrated.",
        "cancelled": "Calibration cancelled. You can start again when ready.",
        "failed_test": (
            "Test did not pass — calibration was not saved. "
            "Most common cause: the reference mass was not on the pan during Test. "
            "Put the same mass back on, wait, run Test again."
        ),
    }

    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self._test_passed = False
        self.setWindowTitle("Guided Scale Calibration")
        self.resize(780, 640)
        layout = QVBoxLayout(self)

        self.instructions = QLabel(self.STEPS["before"])
        self.instructions.setWordWrap(True)
        self.instructions.setObjectName("instruction")
        self.instructions.setStyleSheet("background:#F7FAFC;border:1px solid #D9E2EC;padding:12px;border-radius:8px;")
        layout.addWidget(self.instructions)

        warning = QLabel("Maintenance only — not legal-for-trade. Use a verified reference mass.")
        warning.setWordWrap(True)
        warning.setStyleSheet("color:#8A4B08;font-weight:600")
        layout.addWidget(warning)

        form = QFormLayout()
        default_ref = float(getattr(runtime.controller.settings, "default_reference_weight_g", 2000.0) or 2000.0)
        # Calibration reference is always grams — avoids kg/lb display-unit mixups.
        self._display_unit = "g"
        self.reference = QDoubleSpinBox()
        self.reference.setRange(1.0, 100000.0)
        self.reference.setDecimals(3)
        self.reference.setValue(default_ref)
        self.samples = QSpinBox(); self.samples.setRange(3, 32); self.samples.setValue(8)
        form.addRow("Reference weight (g) — must match mass on pan", self.reference)
        form.addRow("Live sample count", self.samples)
        layout.addLayout(form)

        self.summary = QLabel("")
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet("font-weight:700;padding:8px;")
        layout.addWidget(self.summary)

        grid = QGridLayout()
        self.accept_btn = QPushButton("5. Accept (after Test Pass)")
        self.accept_btn.setEnabled(False)
        self.accept_btn.clicked.connect(self.accept_factor)
        actions = [
            ("1. Start", self.start, 0, 0),
            ("2. Capture empty samples", self.zero_samples, 0, 1),
            ("3. Capture loaded samples", self.loaded_samples, 1, 0),
            ("4. Test", self.test_factor, 1, 1),
            (None, None, 2, 0),
            ("Cancel", self.cancel_calibration, 2, 1),
        ]
        for text, callback, r, c in actions:
            if text is None:
                grid.addWidget(self.accept_btn, r, c)
                continue
            button = QPushButton(text); button.clicked.connect(callback); grid.addWidget(button, r, c)
        layout.addLayout(grid)
        self.output = QPlainTextEdit(); self.output.setReadOnly(True); layout.addWidget(self.output)
        close = QDialogButtonBox(QDialogButtonBox.Close); close.rejected.connect(self.reject); layout.addWidget(close)

    def set_step(self, key: str) -> None:
        self.instructions.setText(self.STEPS.get(key, self.STEPS["before"]))

    def write(self, result: dict[str, Any], *, next_step: str | None = None) -> None:
        self.output.setPlainText(json.dumps(result, indent=2, sort_keys=True, default=str))
        if result.get("status") in {"failed", "blocked"}:
            _show_result(self, result)
            return
        if next_step:
            self.set_step(next_step)

    def start(self) -> None:
        self._test_passed = False
        self.accept_btn.setEnabled(False)
        self.summary.setText("")
        self.set_step("start")
        self.write(self.runtime.start_calibration(), next_step="zero")

    def zero_samples(self) -> None:
        self.set_step("zero")
        try:
            self.write(self.runtime.add_calibration_zero_samples(self.samples.value()), next_step="loaded")
        except Exception as exc:
            QMessageBox.warning(self, "Samples unavailable", str(exc))

    def loaded_samples(self) -> None:
        self.set_step("loaded")
        try:
            ref_g = float(self.reference.value())
            self.runtime.controller.settings_store.update(default_reference_weight_g=ref_g)
            self.write(
                self.runtime.add_calibration_loaded_samples(ref_g, self.samples.value()),
                next_step="test",
            )
        except Exception as exc:
            QMessageBox.warning(self, "Samples unavailable", str(exc))

    def test_factor(self) -> None:
        self.set_step("test")
        try:
            # Runtime clears the buffer and waits for fresh stream samples.
            result = self.runtime.test_calibration(self.samples.value())
            test = (result.get("data") or {}).get("calibration_test") or {}
            summary = test.get("operator_summary") or result.get("message") or ""
            self.summary.setText(summary)
            self._test_passed = bool(test.get("passed_local_tolerance"))
            self.accept_btn.setEnabled(self._test_passed)
            next_step = "accept" if self._test_passed else "failed_test"
            self.write(result, next_step=next_step)
            if not self._test_passed:
                QMessageBox.warning(self, "Test did not pass", summary or result.get("message", "Run Test again."))
        except Exception as exc:
            self._test_passed = False
            self.accept_btn.setEnabled(False)
            QMessageBox.warning(self, "Test unavailable", str(exc))

    def accept_factor(self) -> None:
        if not self._test_passed:
            QMessageBox.warning(
                self,
                "Not ready",
                "Run Test until you see Pass first. Calibration is not saved until Accept succeeds.",
            )
            return
        self.set_step("accept")
        if QMessageBox.question(self, "Confirm calibration", "Save this calibration to the scale?") == QMessageBox.Yes:
            result = self.runtime.accept_calibration()
            self.write(result, next_step="after")
            if result.get("status") in {"failed", "blocked"}:
                self._test_passed = False
                self.accept_btn.setEnabled(False)
                self.summary.setText(
                    (result.get("message") or "")
                    + " Large numbers can stay wrong until calibration is saved, then press ZERO."
                )

    def cancel_calibration(self) -> None:
        self._test_passed = False
        self.accept_btn.setEnabled(False)
        self.write(self.runtime.cancel_calibration(), next_step="cancelled")


class MainWindow(QMainWindow):
    """Windows-first operator surface with advanced workflows moved out of the routine loop."""

    CAPTURE_STATES = {"BARCODE_CAPTURED", "WAITING_FOR_LOAD", "WEIGHING", "WAITING_FOR_STABLE_WEIGHT", "WEIGHT_STABLE", "MANUAL_CONFIRM"}

    def __init__(self, runtime: OperatorRuntime, *, simulator: bool = False, smoke: bool = False):
        super().__init__()
        self.runtime = runtime
        self.simulator_requested = simulator
        self._calibration_open = False
        self._scale_face: ScaleFaceWindow | None = None
        self.setWindowTitle(f"Best Buds Cultivator Weight Station v{__version__}")
        self.resize(1180, 820)
        self.setMinimumSize(1024, 720)
        self.setStyleSheet(APP_STYLE)
        self._build_menus()

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        top = QFrame(); top.setObjectName("topBar")
        top_layout = QHBoxLayout(top); top_layout.setContentsMargins(14, 10, 14, 10)
        title = QLabel("Best Buds Cultivator Weight Station"); title.setObjectName("appTitle")
        self.mode_badge = QLabel("NO SCALE"); self.mode_badge.setObjectName("modeBadge")
        self.mode_badge.setAccessibleName("Scale evidence mode")
        top_layout.addWidget(title); top_layout.addStretch(1); top_layout.addWidget(self.mode_badge)
        layout.addWidget(top)

        status_row = QHBoxLayout()
        self.status = QLabel("No run started")
        self.status.setObjectName("statusBanner")
        self.status.setAccessibleName("Current station status")
        self.capture_pill = QLabel("Idle")
        self.capture_pill.setObjectName("statusPill")
        self.capture_pill.setAccessibleName("Capture status")
        self.capture_pill.setProperty("pill", "ready")
        status_row.addWidget(self.status, 1)
        status_row.addWidget(self.capture_pill)
        layout.addLayout(status_row)

        self.weight = QLabel("0.000 g")
        self.weight.setObjectName("weightDisplay")
        self.weight.setAlignment(Qt.AlignCenter)
        self.weight.setAccessibleName("Current weight in grams")
        layout.addWidget(self.weight, 2)
        self.weight_hint = QLabel("")
        self.weight_hint.setAlignment(Qt.AlignCenter)
        self.weight_hint.setStyleSheet(f"color:{COLOR_WARN_FG};font-size:13px;font-weight:600")
        self.weight_hint.setWordWrap(True)
        layout.addWidget(self.weight_hint)
        self.locked_weight_label = QLabel("")
        self.locked_weight_label.setObjectName("lockedMetric")
        self.locked_weight_label.setAlignment(Qt.AlignCenter)
        self.locked_weight_label.setAccessibleName("Locked weight")
        layout.addWidget(self.locked_weight_label)

        metrics = QFrame(); metrics.setObjectName("card")
        grid = QGridLayout(metrics); grid.setContentsMargins(16, 12, 16, 12); grid.setHorizontalSpacing(20); grid.setVerticalSpacing(8)
        self.fields: dict[str, QLabel] = {}
        for idx, key in enumerate(
            ("RUN", "CULTIVATOR", "STRAIN", "OPERATOR", "CONTAINER", "GROSS", "TARE", "NET")
        ):
            label = QLabel(key); label.setObjectName("metricLabel")
            value = QLabel("—"); value.setObjectName("metricValue"); value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            row, col = divmod(idx, 4)
            grid.addWidget(label, row * 2, col)
            grid.addWidget(value, row * 2 + 1, col)
            self.fields[key] = value
        layout.addWidget(metrics)

        strain_row = QHBoxLayout()
        self.active_strain_banner = QLabel("Active strain: —")
        self.active_strain_banner.setStyleSheet(f"font-weight:700;color:{COLOR_PRIMARY};padding:6px 0")
        change_strain_btn = QPushButton("Change Strain")
        change_strain_btn.clicked.connect(self.change_strain)
        strain_row.addWidget(self.active_strain_banner, 1)
        strain_row.addWidget(change_strain_btn)
        layout.addLayout(strain_row)

        self.last_saved = QLabel("No plant has been saved in this run.")
        self.last_saved.setObjectName("lastSaved")
        self.last_saved.setAccessibleName("Last saved plant receipt")
        layout.addWidget(self.last_saved)
        self.pending_sync_label = QLabel("")
        self.pending_sync_label.setStyleSheet(f"color:{COLOR_WARN_FG};font-weight:600")
        layout.addWidget(self.pending_sync_label)

        alice_card = QFrame(); alice_card.setObjectName("card")
        alice_layout = QVBoxLayout(alice_card); alice_layout.setContentsMargins(14, 10, 14, 10)
        alice_layout.addWidget(_eyebrow("Alice — next step"))
        self.alice_message = QLabel("Start a new run or resume the last run.")
        self.alice_message.setObjectName("instruction"); self.alice_message.setWordWrap(True)
        alice_layout.addWidget(self.alice_message)
        layout.addWidget(alice_card)

        barcode_card = QFrame(); barcode_card.setObjectName("card")
        barcode_layout = QVBoxLayout(barcode_card); barcode_layout.setContentsMargins(14, 10, 14, 10); barcode_layout.setSpacing(4)
        barcode_layout.addWidget(_eyebrow("Plant or container barcode"))
        self.barcode = QLineEdit()
        self.barcode.setObjectName("barcodeInput")
        self.barcode.setPlaceholderText("Scan or type the barcode, then press Enter")
        self.barcode.setAccessibleName("Plant barcode")
        self.barcode.setAccessibleDescription("Scan or type a plant barcode and press Enter")
        self.barcode.returnPressed.connect(self.submit_barcode)
        barcode_row = QHBoxLayout()
        barcode_row.addWidget(self.barcode, 1)
        self.auto_id_btn = QPushButton("Use auto ID")
        self.auto_id_btn.clicked.connect(self.use_auto_plant_id)
        barcode_row.addWidget(self.auto_id_btn)
        self.scan_btn = QPushButton("Scan")
        self.scan_btn.clicked.connect(self.open_scan_dialog)
        barcode_row.addWidget(self.scan_btn)
        barcode_hint = QLabel(
            "Press Scan to open the scanner window. The accepted tag stays "
            "visible here until Confirm."
        )
        barcode_hint.setObjectName("dialogTip")
        barcode_layout.addLayout(barcode_row)
        barcode_layout.addWidget(barcode_hint)
        self.active_barcode_banner = QLabel("Active plant: —")
        self.active_barcode_banner.setStyleSheet(f"font-weight:700;color:{COLOR_ACTIVE_BARCODE};padding:4px 0")
        barcode_layout.addWidget(self.active_barcode_banner)
        layout.addWidget(barcode_card)
        note_row = QHBoxLayout()
        self.operator_note = QLineEdit()
        self.operator_note.setPlaceholderText("Optional note for next Confirm (governance light)")
        self.void_next = QComboBox()
        self.void_next.addItems(["void: none", "void: mark void"])
        note_row.addWidget(self.operator_note, 1)
        note_row.addWidget(self.void_next)
        layout.addLayout(note_row)

        actions = QGridLayout(); actions.setHorizontalSpacing(10); actions.setVerticalSpacing(10)
        action_callbacks = {
            "start_resume": self.start_resume,
            "connect_scale": self.scale_setup,
            "zero_scale": self.zero_scale,
            "set_tare": self.container_tare,
            "lock_weight": self.lock_weight,
            "confirm_record": self.confirm_record,
            "cancel_item": self.cancel_item,
            "finish_run": self.finish_run,
        }
        object_names = {"primary": "primaryAction", "danger": "dangerAction"}
        self.buttons: dict[str, QPushButton] = {}
        for spec in ROUTINE_ACTION_LAYOUT:
            button = QPushButton(spec.label); button.clicked.connect(action_callbacks[spec.action_id])
            if spec.emphasis in object_names: button.setObjectName(object_names[spec.emphasis])
            actions.addWidget(button, spec.row, spec.column, 1, spec.columnspan)
            self.buttons[spec.label] = button
        layout.addLayout(actions)

        log_card = QFrame(); log_card.setObjectName("card")
        log_layout = QVBoxLayout(log_card); log_layout.setContentsMargins(14, 10, 14, 10)
        log_layout.addWidget(_eyebrow("Run plant log (read-only)"))
        self.plant_log = QListWidget()
        self.plant_log.setMinimumHeight(120)
        self.plant_log.setMaximumHeight(180)
        self.plant_log.setAccessibleName("Run plant log")
        self.plant_log.setObjectName("plantLog")
        log_layout.addWidget(self.plant_log)
        layout.addWidget(log_card)

        central.setMinimumWidth(980)
        central.setMinimumHeight(layout.sizeHint().height())
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(central)
        self.setCentralWidget(scroll)

        self.device_status = QLabel("Scale disconnected")
        self.statusBar().addPermanentWidget(self.device_status, 1)
        self.statusBar().showMessage("Ready")

        shortcuts = {
            "Ctrl+N": self.new_run, "Ctrl+L": self.load_run, "Ctrl+R": self.start_resume,
            "Ctrl+K": self.scale_setup, "Ctrl+Z": self.zero_scale, "Ctrl+T": self.container_tare,
            "Ctrl+Shift+L": self.lock_weight,
            "Ctrl+Enter": self.confirm_record, "Escape": self.cancel_item,
            "Ctrl+Shift+F": self.open_scale_face,
        }
        for shortcut, callback in shortcuts.items():
            action = QAction(self); action.setShortcut(QKeySequence(shortcut)); action.triggered.connect(callback); self.addAction(action)

        self.timer = QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(100)
        if simulator: QTimer.singleShot(50, self.bootstrap_simulator)
        if smoke: QTimer.singleShot(1400, self.close)
        self.refresh()

    def _add_menu_action(self, menu, text: str, callback, shortcut: str | None = None) -> None:
        action = QAction(text, self)
        if shortcut: action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback); menu.addAction(action)

    def _build_menus(self) -> None:
        run_menu = self.menuBar().addMenu("Run")
        self._add_menu_action(run_menu, "New Run", self.new_run, "Ctrl+N")
        self._add_menu_action(run_menu, "Resume Last Run", self.resume_run, "Ctrl+R")
        self._add_menu_action(run_menu, "Resume Run (Choose)...", self.choose_run)
        self._add_menu_action(run_menu, "Load Run...", self.load_run, "Ctrl+L")
        run_menu.addSeparator()
        self._add_menu_action(run_menu, "Change Active Strain...", self.change_strain)
        self._add_menu_action(run_menu, "Recover Run", self.recover)
        self._add_menu_action(run_menu, "Rebuild CSV from JSONL", self.rebuild_csv)
        self._add_menu_action(run_menu, "Reconcile Export ↔ JSONL", self.reconcile_export)
        self._add_menu_action(run_menu, "Export Report...", self.export_report)
        self._add_menu_action(run_menu, "Finish Run", self.finish_run)

        scale_menu = self.menuBar().addMenu("Scale")
        self._add_menu_action(scale_menu, "Scale Setup and Connection...", self.scale_setup, "Ctrl+K")
        self._add_menu_action(scale_menu, "Zero Scale", self.zero_scale, "Ctrl+Z")
        self._add_menu_action(scale_menu, "Container Tare...", self.container_tare, "Ctrl+T")
        self._add_menu_action(scale_menu, "Guided Calibration...", self.calibrate)
        self._add_menu_action(scale_menu, "Test Scanner...", self.test_scanner)
        scale_menu.addSeparator()
        self._add_menu_action(scale_menu, "Diagnostics", self.diagnostics)

        view_menu = self.menuBar().addMenu("View")
        self._add_menu_action(view_menu, "Scale Face (Harvest)", self.open_scale_face, "Ctrl+Shift+F")

        settings_menu = self.menuBar().addMenu("Settings")
        self._add_menu_action(settings_menu, "Station Settings...", self.station_settings)

        help_menu = self.menuBar().addMenu("Help")
        self._add_menu_action(help_menu, "About", self.about)

    def bootstrap_simulator(self) -> None:
        if not self.runtime.controller.loaded_run:
            definition = {
                "run_id": "SIMULATOR-UI-RUN", "operator_id": "SIMULATOR-OPERATOR",
                "facility_id": "BEST-BUDS", "station_id": "WEIGHT-STATION-01",
                "cultivars": [{"cultivar_id": "CV-001", "name": "Simulator Strain"}],
                "capture_mode": self.runtime.controller.settings.capture_mode,
                "unit": "g", "container_id": "DEFAULT", "tare_g": 0.0, "maximum_capacity_g": 10000.0,
            }
            self.runtime.dispatch("run.new", {"definition": definition, "data_root": self.runtime.controller.settings.data_root, "simulator": True})
        if not self.runtime.controller.device:
            self.runtime.connect_simulator(); self.runtime.simulator_set_weight(1250.0)

    def refresh(self) -> None:
        s = self.runtime.snapshot(); device = s["device"]
        du = unit_label(s.get("display_unit") or "g")
        self.status.setText(s["operator_state"].title())
        locked = s.get("locked_weight_g")
        # While locked, the big display freezes at the locked value until
        # Confirm & Record or Cancel releases it (display-only; capture law unchanged).
        self.weight.setText(format_weight(frozen_display_weight(float(s["weight_g"]), locked), du))
        if locked is not None:
            self.weight_hint.setText(
                "Weight locked — Confirm & Record to save, or Cancel to release."
            )
            self.locked_weight_label.setText(f"Locked  {format_weight(float(locked), du)}")
        else:
            if s.get("warn_on_uncalibrated_weight") and s.get("weight_uncalibrated"):
                self.weight_hint.setText(
                    "Uncalibrated — open Scale → Guided Calibration with a verified mass. "
                    "Large wild numbers are normal until calibration is saved, then press ZERO."
                )
            else:
                self.weight_hint.setText("")
            self.locked_weight_label.setText("")
        active_bc = s.get("active_barcode")
        if active_bc:
            self.active_barcode_banner.setText(f"Active plant: {active_bc}")
            if self.barcode.text().strip() != str(active_bc) and s["state"] in self.CAPTURE_STATES:
                self.barcode.setText(str(active_bc))
        else:
            self.active_barcode_banner.setText("Active plant: —")
        self._refresh_plant_log(s.get("recent_plants") or [], du)
        self.fields["RUN"].setText(s["run_id"] or "—")
        self.fields["CULTIVATOR"].setText(s.get("cultivator") or s.get("facility_id") or "—")
        self.fields["STRAIN"].setText(s.get("strain") or s.get("cultivar") or "—")
        self.fields["OPERATOR"].setText(s.get("operator_id") or "—")
        self.fields["CONTAINER"].setText(s["container_id"] or "—")
        self.fields["GROSS"].setText(format_weight(float(s["weight_g"]), du))
        self.fields["TARE"].setText(format_weight(float(s["tare_g"]), du))
        self.fields["NET"].setText(format_weight(float(s["net_g"]), du))
        self.active_strain_banner.setText(
            f"Active strain (sticky): {s.get('strain') or s.get('cultivar') or '—'}"
        )
        record = s["last_saved"]
        if s["state"] == "RUN_FINISHED":
            self.last_saved.setText(
                "Run finished — records are immutable. Export the report (Run → Export Report…) "
                "or press START / RESUME for another run."
            )
        elif record:
            csv_note = ""
            run = self.runtime.controller.loaded_run
            if run and (run.store.session_dir / "records.csv").exists():
                csv_note = f" • CSV: {run.store.session_dir / 'records.csv'}"
            dup = record.get("duplicate_status")
            dup_note = " • duplicate barcode warning" if dup and dup != "none" else ""
            strain = record.get("cultivar_normalized_name") or s.get("strain") or s.get("cultivar") or ""
            self.last_saved.setText(
                f"Saved: {record.get('barcode_raw', record.get('record_id'))} — "
                f"{format_weight(float(record['net_g']), du)} net ({strain}). Ready for next scan.{dup_note}{csv_note}"
            )
        else:
            self.last_saved.setText("No plant has been saved in this run yet. Scan a barcode, weigh, then Confirm & Record.")
        pending = int(s.get("pending_sync_count") or 0)
        if pending:
            self.pending_sync_label.setText(
                f"CSV/XLSX sync pending for {pending} record(s). Run → Rebuild CSV from JSONL (JSONL stays authoritative)."
            )
        else:
            self.pending_sync_label.setText("")
        self.alice_message.setText(str(s["alice_message"]))
        self._refresh_capture_pill(s["state"], bool(record))

        mode = device.get("mode") or "none"
        warn_pill = (
            f"background:{COLOR_WARN_BG};color:{COLOR_WARN_FG};border:1px solid {COLOR_WARN_BORDER};"
            "padding:6px 10px;border-radius:999px;font-weight:700;font-size:12px"
        )
        if mode == "serial_simulator":
            self.mode_badge.setText("SIMULATOR MODE - NO PHYSICAL SCALE")
            self.mode_badge.setStyleSheet(warn_pill)
        elif device.get("connected"):
            self.mode_badge.setText("PHYSICAL SERIAL - TESTING REQUIRED")
            self.mode_badge.setStyleSheet(warn_pill)
        else:
            self.mode_badge.setText("NO SCALE CONNECTED")
            self.mode_badge.setStyleSheet("")

        port = device.get("port") or "none"
        worker = "reading" if s["worker_running"] else "stopped"
        stale = "stale" if device.get("stale", True) else "live"
        self.device_status.setText(f"Scale: {'connected' if device.get('connected') else 'disconnected'} | {mode} | {port} | {worker} | {stale}")
        if s["worker_error"]:
            self.statusBar().showMessage(f"Scale note: {s['worker_error']}")
        elif mode == "serial_simulator":
            self.statusBar().showMessage("Simulator connected • live readings active • physical scale not in use")
        elif device.get("connected"):
            self.statusBar().showMessage(f"Scale connected on {port} • readings {worker} • physical testing evidence pending")
        else:
            self.statusBar().showMessage("Scale disconnected • open Scale Setup to connect")

        state=s["state"]; ready=state=="WAITING_FOR_BARCODE"; connected=bool(device.get("connected"))
        self.barcode.setEnabled(ready and not self._calibration_open)
        self.scan_btn.setEnabled(ready and not self._calibration_open)
        self.auto_id_btn.setEnabled(ready and not self._calibration_open and not bool(s.get("barcode_required_for_capture", True)))
        self.auto_id_btn.setVisible(not bool(s.get("barcode_required_for_capture", True)))
        # Focus ownership: reclaim barcode focus only when ready and no modal owns focus.
        active = QApplication.activeModalWidget()
        if ready and not self._calibration_open and active is None and not self.barcode.hasFocus():
            if not self.operator_note.hasFocus():
                self.barcode.setFocus()
        self.buttons["START / RESUME"].setEnabled(state in {"NO_RUN", "RUN_FINISHED", "DEVICE_READY", "WAITING_FOR_BARCODE"})
        self.buttons["CONNECT SCALE"].setEnabled(state not in self.CAPTURE_STATES)
        # Zero is maintenance: allowed whenever the scale is connected (run optional).
        self.buttons["ZERO"].setEnabled(connected and state not in self.CAPTURE_STATES)
        self.buttons["SET TARE"].setEnabled(connected and state in {"WAITING_FOR_BARCODE", "DEVICE_READY"})
        self.buttons["LOCK WEIGHT"].setEnabled(state == "WEIGHT_STABLE")
        self.buttons["CONFIRM & RECORD"].setEnabled(state == "MANUAL_CONFIRM")
        self.buttons["CANCEL"].setEnabled(state in self.CAPTURE_STATES)
        self.buttons["FINISH RUN"].setEnabled(bool(s["run_id"]) and state not in {"LOCAL_COMMIT_PENDING", "RUN_FINISHED"})

    def _refresh_capture_pill(self, state: str, has_saved: bool) -> None:
        """Text-labeled capture status pill (Ready / Stable / Locked / Saved)."""
        label = capture_pill_label(state)
        if state == "WAITING_FOR_BARCODE" and has_saved:
            label = "Saved"
            pill = "saved"
        elif state == "MANUAL_CONFIRM":
            pill = "locked"
        elif state == "WEIGHT_STABLE":
            pill = "stable"
        elif state in {"RECORD_SAVED", "RUN_FINISHED"}:
            pill = "saved"
        elif state in {"WAITING_FOR_LOAD", "WEIGHING", "WAITING_FOR_STABLE_WEIGHT"}:
            pill = "warn"
        else:
            pill = "ready"
        self.capture_pill.setText(label)
        self.capture_pill.setProperty("pill", pill)
        self.capture_pill.setToolTip(f"Capture status: {label} ({state})")
        # Force QSS property refresh
        self.capture_pill.style().unpolish(self.capture_pill)
        self.capture_pill.style().polish(self.capture_pill)

    def _refresh_plant_log(self, plants: list[dict[str, Any]], du: str) -> None:
        lines: list[str] = []
        for row in plants:
            stamp = str(row.get("created_at") or "")[-8:]
            barcode = row.get("barcode_raw") or row.get("record_id") or "?"
            net = format_weight(float(row.get("net_g") or 0.0), du)
            cultivar = row.get("cultivar_normalized_name") or ""
            flags = []
            if row.get("void_status") and row.get("void_status") != "none":
                flags.append("void")
            if row.get("duplicate_status") and row.get("duplicate_status") != "none":
                flags.append("dup")
            flag_txt = f" [{' '.join(flags)}]" if flags else ""
            lines.append(f"{stamp}  {barcode}  {net}  {cultivar}{flag_txt}".rstrip())
        current = [self.plant_log.item(i).text() for i in range(self.plant_log.count())]
        if current == lines:
            return
        self.plant_log.clear()
        if not lines:
            self.plant_log.addItem("No plants saved in this run yet.")
            return
        for line in lines:
            self.plant_log.addItem(line)

    def maybe_suggest_calibration(self) -> None:
        snap = self.runtime.snapshot()
        if not snap.get("suggest_calibration_on_new_run"):
            return
        if not snap.get("device", {}).get("connected"):
            QMessageBox.information(
                self,
                "Next step",
                "Run started. Connect the scale (Scale Setup), then consider Guided Calibration before weighing plants.",
            )
            return
        if not snap.get("weight_uncalibrated"):
            return
        box = QMessageBox(self)
        box.setWindowTitle("Calibrate scale?")
        box.setText(
            "The scale looks uncalibrated (readings may look like huge or negative numbers). "
            "Calibrate now with a verified mass?"
        )
        calibrate = box.addButton("Calibrate now", QMessageBox.AcceptRole)
        skip = box.addButton("Skip for now", QMessageBox.RejectRole)
        box.setDefaultButton(skip)
        box.exec()
        if box.clickedButton() is calibrate:
            self.calibrate()

    def open_scale_face(self) -> None:
        """Enter Scale Face harvest mode (SR8); Esc / Exit returns here."""
        if self._scale_face is None:
            self._scale_face = ScaleFaceWindow(self)
        self.hide()
        self._scale_face.open_scale_face()

    def start_resume(self) -> None:
        state = self.runtime.controller.state
        if self.runtime.controller.loaded_run and state != "RUN_FINISHED":
            self.resume_run()
            return
        # No active run (or the loaded run is finished): offer the in-progress
        # picker; it falls through to New Run / Browse when nothing is listed.
        self.choose_run()
    def new_run(self) -> None: NewRunDialog(self.runtime, self).exec()
    def resume_run(self) -> None: _show_result(self, self.runtime.dispatch("run.resume"))
    def choose_run(self) -> None: ResumeRunDialog(self.runtime, self).exec()
    def load_run(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Existing Run", self.runtime.controller.settings.data_root, "Session manifest (session_manifest.json);;JSON files (*.json)")
        if path: _show_result(self, self.runtime.dispatch("run.load", {"selection": path}))
    def scale_setup(self) -> None: ScaleSetupDialog(self.runtime, self).exec()
    def zero_scale(self) -> None:
        try:
            result = self.runtime.zero_scale()
            if result.get("status") == "completed":
                note = self.runtime.last_worker_error
                _show_result(self, result, success_title="Scale Zeroed")
                if note:
                    self.statusBar().showMessage(f"Scale zeroed; live stream note: {note}")
            else:
                _show_result(self, result, success_title="Scale Zeroed")
        except Exception as exc:
            QMessageBox.warning(self, "Zero failed", str(exc))
    def container_tare(self) -> None: TareDialog(self.runtime, self).exec()
    def calibrate(self) -> None:
        self._calibration_open = True
        try:
            CalibrationDialog(self.runtime, self).exec()
        finally:
            self._calibration_open = False
    def test_scanner(self) -> None:
        ScannerTestDialog(self, runtime=self.runtime).exec()

    def open_scan_dialog(self) -> None:
        """Capture one HID barcode visibly, then submit it to the active run."""
        dialog = ScannerTestDialog(self, capture=True)
        if dialog.exec() != QDialog.Accepted or not dialog.accepted_barcode:
            return
        self.barcode.setText(dialog.accepted_barcode)
        self.submit_barcode()

    def focus_scan(self) -> None:
        """Legacy helper: focus barcode field for HID wedge entry."""
        self.barcode.setFocus()
        self.barcode.selectAll()
        self.statusBar().showMessage("Ready to scan — focus is in the plant barcode field.")

    def lock_weight(self) -> None:
        result = self.runtime.lock_weight()
        if result.get("status") in {"failed", "blocked"}:
            _show_result(self, result)
        else:
            self.statusBar().showMessage(result.get("message") or "Weight locked — Confirm & Record when ready.")

    def change_strain(self) -> None:
        if not self.runtime.controller.loaded_run:
            QMessageBox.information(self, "No run", "Start or resume a run before changing strain.")
            return
        ChangeStrainDialog(self.runtime, self).exec()
    def station_settings(self) -> None:
        StationSettingsDialog(self.runtime, self).exec()
    def rebuild_csv(self) -> None:
        _show_result(self, self.runtime.dispatch("spreadsheet.rebuild"), success_title="CSV rebuilt")
    def reconcile_export(self) -> None:
        result = self.runtime.dispatch("report.reconcile")
        _show_result(self, result, success_title="Reconcile pass")
    def use_auto_plant_id(self) -> None:
        if self.runtime.controller.settings.barcode_required_for_capture:
            QMessageBox.information(
                self,
                "Barcode required",
                "This station requires a scanned or typed barcode. Open Settings → Station Settings "
                "to allow auto ID for casual/demo mode.",
            )
            return
        value = self.runtime.next_auto_plant_id()
        self.barcode.setText(value)
        self.submit_barcode()
    def submit_barcode(self) -> None:
        if self._calibration_open:
            QMessageBox.information(self, "Finish calibration first", "Finish or cancel Guided Calibration before scanning plants.")
            return
        value=self.barcode.text().strip()
        if not value:
            self.statusBar().showMessage("Empty barcode blocked — scan or type a plant ID, then press Enter.")
            return
        result=self.runtime.submit_barcode(value)
        if result.get("status") in {"failed", "blocked"}:
            _show_result(self, result)
        else:
            self.barcode.setText(value)
            self.active_barcode_banner.setText(f"Active plant: {value}")
            self.statusBar().showMessage(
                f"Barcode accepted: {value} — place plant, wait for stable, then Lock weight."
            )
    def confirm_record(self) -> None:
        note = self.operator_note.text().strip() or None
        void_status = "void" if self.void_next.currentIndex() == 1 else "none"
        result = self.runtime.dispatch(
            "capture.confirm",
            {"operator_note": note, "void_status": void_status},
        )
        if result.get("status") == "completed":
            record = (result.get("data") or {}).get("record") or self.runtime.controller.last_record or {}
            feedback = (result.get("data") or {}).get("feedback")
            msg = result.get("message") or "Record saved."
            run = self.runtime.controller.loaded_run
            if run and (run.store.session_dir / "records.csv").exists():
                msg += f" CSV: {run.store.session_dir / 'records.csv'}"
            # Soft pacing: status + last_saved carry the proof; modal only on duplicate warning.
            self.statusBar().showMessage(msg)
            self.operator_note.clear()
            self.void_next.setCurrentIndex(0)
            self.barcode.clear()
            QTimer.singleShot(0, self.barcode.setFocus)
            if feedback == "warning":
                QMessageBox.warning(self, "Saved with duplicate warning", msg)
        else:
            _show_result(self, result)

    def cancel_item(self) -> None:
        result = self.runtime.dispatch("capture.cancel")
        self.barcode.clear()
        self.statusBar().showMessage(result.get("message") or "Cancelled — scan again when ready.")
        QTimer.singleShot(0, self.barcode.setFocus)
        if result.get("status") in {"failed", "blocked"}:
            _show_result(self, result)
    def recover(self) -> None:
        result = self.runtime.dispatch("state.recover")
        if result.get("status") == "completed":
            receipt = (result.get("data") or {}).get("recovery_receipt") or {}
            msg = result.get("message") or "Recovered."
            if receipt.get("spreadsheet_rebuild"):
                msg += f"\nCSV rebuilt: {receipt['spreadsheet_rebuild'].get('rebuilt_rows')} rows."
            QMessageBox.information(self, "Recovered", msg)
        else:
            # Soft path: allow rebuild even when machine is not in RECOVERY_REQUIRED.
            rebuild = self.runtime.dispatch("spreadsheet.rebuild")
            if rebuild.get("status") == "completed":
                QMessageBox.information(
                    self,
                    "CSV rebuilt",
                    (rebuild.get("message") or "CSV rebuilt from JSONL.")
                    + "\n\nIf the run was interrupted, resume and continue scanning.",
                )
            else:
                _show_result(self, result)
    def finish_run(self) -> None:
        if QMessageBox.question(self,"Finish Run","Finish the current run? Committed records remain immutable.")==QMessageBox.Yes:
            _show_result(self,self.runtime.dispatch("run.finish"),success_title="Run Finished")
    def export_report(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Export Report To", str(self.runtime.paths.exports))
        if not path:
            return
        result = self.runtime.dispatch("report.export", {"destination": path})
        if result.get("status") == "completed":
            paths = (result.get("data") or {}).get("paths") or []
            listing = "\n".join(paths) if paths else path
            reconcile = self.runtime.dispatch("report.reconcile")
            gate = ((reconcile.get("data") or {}).get("reconcile") or {}).get("status", "n/a")
            QMessageBox.information(
                self,
                "Export completed",
                "Handoff files written (plain plant CSV / XLSX / DOCX / JSON):\n\n"
                f"{listing}\n\n"
                f"Reconcile gate: {gate}\n"
                "Session JSONL remains the authoritative ledger.",
            )
        else:
            _show_result(self, result)
    def diagnostics(self) -> None:
        QMessageBox.information(self,"Diagnostics",json.dumps(self.runtime.snapshot(),indent=2,sort_keys=True,default=str))
    def about(self) -> None:
        QMessageBox.information(
            self,
            "About",
            f"Best Buds Cultivator Weight Station v{__version__}\n"
            "Harvest weight capture for cultivators.\n"
            "Authoritative records stay in local session JSONL.\n"
            "Operator surface polish uses design tokens (cite-only).\n"
            "Not legal-for-trade or Metrc compliance.",
        )
    def closeEvent(self,event:QCloseEvent)->None:
        self.runtime.close(); event.accept()

def launch_pyside(runtime: OperatorRuntime, *, simulator: bool = False, smoke: bool = False) -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(runtime, simulator=simulator, smoke=smoke)
    window.show()
    return int(app.exec())
