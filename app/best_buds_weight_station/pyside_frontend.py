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
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .operator_runtime import OperatorRuntime
from .operator_surface import ROUTINE_ACTION_LAYOUT
from .version import __version__


APP_STYLE = """
QWidget { color: #17212B; font-family: "Segoe UI"; font-size: 14px; }
QMainWindow, QDialog { background: #F5F7FA; }
QFrame#topBar, QFrame#card, QGroupBox { background: #FFFFFF; border: 1px solid #CBD4DD; border-radius: 8px; }
QLabel#appTitle { font-size: 28px; font-weight: 700; }
QLabel#modeBadge { padding: 5px 10px; border-radius: 10px; font-weight: 700; background: #EEF2F6; }
QLabel#statusBanner { font-size: 19px; font-weight: 700; padding: 12px 16px; background: #FFFFFF; border: 2px solid #CBD4DD; border-radius: 8px; }
QLabel#weightDisplay { font-size: 72px; font-weight: 800; padding: 18px; background: #FFFFFF; border: 2px solid #17212B; border-radius: 10px; }
QLabel#metricValue { font-size: 20px; font-weight: 700; }
QLabel#instruction { font-size: 17px; font-weight: 600; }
QLabel#lastSaved { color: #176B2C; font-weight: 700; padding: 8px; background: #E7F6EC; border-radius: 6px; }
QLineEdit#barcodeInput { min-height: 52px; font-size: 20px; padding: 4px 10px; border: 2px solid #CBD4DD; border-radius: 6px; }
QLineEdit#barcodeInput:focus { border-color: #1B69D2; }
QPushButton { min-height: 44px; font-size: 14px; font-weight: 600; padding: 6px 14px; border: 1px solid #AAB7C3; border-radius: 6px; background: #FFFFFF; }
QPushButton:hover { background: #EEF2F6; }
QPushButton#primaryAction { min-height: 58px; font-size: 16px; color: #FFFFFF; background: #1E6B52; border-color: #1E6B52; }
QPushButton#dangerAction { color: #B42318; border-color: #DCA7A2; }
QPushButton:disabled { color: #8A969F; background: #EDF0F2; }
QMenuBar { background: #FFFFFF; border-bottom: 1px solid #CBD4DD; }
QStatusBar { background: #FFFFFF; border-top: 1px solid #CBD4DD; }
"""


def _show_result(parent: QWidget, result: dict[str, Any], *, success_title: str = "Completed") -> None:
    if result.get("status") in {"failed", "blocked"}:
        QMessageBox.warning(parent, "Action not completed", result.get("message", "Action failed"))
    elif result.get("terminal", True):
        QMessageBox.information(parent, success_title, result.get("message", "Completed"))


class NewRunDialog(QDialog):
    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self.setWindowTitle("New Harvest Run")
        form = QFormLayout(self)
        self.run_id = QLineEdit()
        self.operator_id = QLineEdit()
        self.cultivar = QLineEdit()
        self.container = QLineEdit("DEFAULT")
        self.mode = QComboBox(); self.mode.addItems(["manual", "automatic"])
        self.data_root = QLineEdit(runtime.controller.settings.data_root)
        choose = QPushButton("Choose…")
        choose.clicked.connect(self.choose_folder)
        folder = QHBoxLayout(); folder.addWidget(self.data_root); folder.addWidget(choose)
        form.addRow("Harvest-run ID", self.run_id)
        form.addRow("Operator ID", self.operator_id)
        form.addRow("Cultivar", self.cultivar)
        form.addRow("Container ID", self.container)
        form.addRow("Capture mode", self.mode)
        form.addRow("Run data folder", folder)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.create_run); buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def choose_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Run Data Folder", self.data_root.text())
        if path:
            self.data_root.setText(path)

    def create_run(self) -> None:
        if not self.run_id.text().strip() or not self.operator_id.text().strip() or not self.cultivar.text().strip():
            QMessageBox.warning(self, "Missing information", "Run ID, operator ID, and cultivar are required.")
            return
        definition = {
            "run_id": self.run_id.text().strip(),
            "operator_id": self.operator_id.text().strip(),
            "facility_id": "BEST-BUDS",
            "station_id": "WEIGHT-STATION-01",
            "cultivars": [{"cultivar_id": "CV-001", "name": self.cultivar.text().strip()}],
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
        self.known = QDoubleSpinBox(); self.known.setRange(0.0, 10000.0); self.known.setDecimals(3)
        form.addRow("Container ID", self.container)
        form.addRow("Known tare (g)", self.known)
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
        self.show_result(self.runtime.set_known_tare(self.container.text().strip(), self.known.value()))

    def capture_live(self) -> None:
        try: self.show_result(self.runtime.capture_container_tare(self.container.text().strip()))
        except Exception as exc: QMessageBox.warning(self, "Tare capture blocked", str(exc))


class CalibrationDialog(QDialog):
    """Step-by-step guided calibration with operator-facing instructions."""

    STEPS = {
        "before": (
            "Before you start: Connect the scale, start or resume a run, empty the pan, and enter the "
            "verified reference mass (grams) below. This is maintenance calibration only — not legal-for-trade."
        ),
        "start": (
            "Step 1 — Start: Begins a maintenance calibration session. Do not scan plant barcodes until this "
            "walkthrough is finished or cancelled."
        ),
        "zero": (
            "Step 2 — Zero samples: Keep the pan empty (no container, no reference mass). Wait until live "
            "readings are updating, then click Capture Zero Raw Samples. Samples use raw HX711 values from the live buffer."
        ),
        "loaded": (
            "Step 3 — Loaded samples: Place the verified reference mass on the empty pan. Wait for settle, "
            "confirm the Reference weight (g) matches the physical mass, then click Capture Loaded Raw Samples."
        ),
        "test": (
            "Step 4 — Test: Keep the reference mass on the pan (or re-place it), then click Test Proposed Factor. "
            "Review the proposed factor and error percent in the output panel before accepting."
        ),
        "accept": (
            "Step 5 — Accept: Confirm to write the factor to the device (SET_CAL). After accept, live weight should "
            "read near the reference mass in real grams."
        ),
        "after": (
            "After calibration: Empty the pan → press ZERO → optional container SET TARE → resume normal scanning. "
            "Large swings labeled as grams before accept were uncalibrated raw counts."
        ),
        "cancelled": "Calibration cancelled. You can start again when ready.",
    }

    def __init__(self, runtime: OperatorRuntime, parent: QWidget | None = None):
        super().__init__(parent)
        self.runtime = runtime
        self.setWindowTitle("Guided Scale Calibration")
        self.resize(780, 640)
        layout = QVBoxLayout(self)

        self.instructions = QLabel(self.STEPS["before"])
        self.instructions.setWordWrap(True)
        self.instructions.setObjectName("instruction")
        self.instructions.setStyleSheet("background:#F7FAFC;border:1px solid #D9E2EC;padding:12px;border-radius:8px;")
        layout.addWidget(self.instructions)

        warning = QLabel("Maintenance workflow. No legal-for-trade certification is implied. Use a verified reference mass.")
        warning.setWordWrap(True)
        warning.setStyleSheet("color:#8A4B08;font-weight:600")
        layout.addWidget(warning)

        form = QFormLayout()
        self.reference = QDoubleSpinBox(); self.reference.setRange(1.0, 10000.0); self.reference.setDecimals(3); self.reference.setValue(2000.0)
        self.samples = QSpinBox(); self.samples.setRange(3, 32); self.samples.setValue(8)
        form.addRow("Reference weight (g)", self.reference)
        form.addRow("Live sample count", self.samples)
        layout.addLayout(form)

        grid = QGridLayout()
        actions = [
            ("1. Start Maintenance Calibration", self.start, 0, 0),
            ("2. Capture Zero Raw Samples", self.zero_samples, 0, 1),
            ("3. Capture Loaded Raw Samples", self.loaded_samples, 1, 0),
            ("4. Test Proposed Factor", self.test_factor, 1, 1),
            ("5. Accept with Second Confirmation", self.accept_factor, 2, 0),
            ("Cancel Calibration", self.cancel_calibration, 2, 1),
        ]
        for text, callback, r, c in actions:
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
            self.write(
                self.runtime.add_calibration_loaded_samples(self.reference.value(), self.samples.value()),
                next_step="test",
            )
        except Exception as exc:
            QMessageBox.warning(self, "Samples unavailable", str(exc))

    def test_factor(self) -> None:
        self.set_step("test")
        try:
            self.write(self.runtime.test_calibration(self.samples.value()), next_step="accept")
        except Exception as exc:
            QMessageBox.warning(self, "Test unavailable", str(exc))

    def accept_factor(self) -> None:
        self.set_step("accept")
        if QMessageBox.question(self, "Confirm calibration", "Apply the proposed factor to the connected device?") == QMessageBox.Yes:
            self.write(self.runtime.accept_calibration(), next_step="after")

    def cancel_calibration(self) -> None:
        self.write(self.runtime.cancel_calibration(), next_step="cancelled")


class MainWindow(QMainWindow):
    """Windows-first operator surface with advanced workflows moved out of the routine loop."""

    CAPTURE_STATES = {"BARCODE_CAPTURED", "WAITING_FOR_LOAD", "WEIGHING", "WAITING_FOR_STABLE_WEIGHT", "WEIGHT_STABLE", "MANUAL_CONFIRM"}

    def __init__(self, runtime: OperatorRuntime, *, simulator: bool = False, smoke: bool = False):
        super().__init__()
        self.runtime = runtime
        self.simulator_requested = simulator
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

        self.status = QLabel("No run started")
        self.status.setObjectName("statusBanner")
        self.status.setAccessibleName("Current station status")
        layout.addWidget(self.status)

        self.weight = QLabel("0.000 g")
        self.weight.setObjectName("weightDisplay")
        self.weight.setAlignment(Qt.AlignCenter)
        self.weight.setAccessibleName("Current weight in grams")
        layout.addWidget(self.weight, 2)
        self.weight_hint = QLabel("")
        self.weight_hint.setAlignment(Qt.AlignCenter)
        self.weight_hint.setStyleSheet("color:#8A4B08;font-size:13px;font-weight:600")
        self.weight_hint.setWordWrap(True)
        layout.addWidget(self.weight_hint)

        metrics = QFrame(); metrics.setObjectName("card")
        grid = QGridLayout(metrics); grid.setContentsMargins(16, 12, 16, 12); grid.setHorizontalSpacing(20); grid.setVerticalSpacing(8)
        self.fields: dict[str, QLabel] = {}
        for idx, key in enumerate(("RUN", "CULTIVAR", "CONTAINER", "GROSS", "TARE", "NET")):
            label = QLabel(key.title()); label.setStyleSheet("font-weight:600;color:#5C6975")
            value = QLabel("—"); value.setObjectName("metricValue"); value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            row, col = divmod(idx, 3)
            grid.addWidget(label, row * 2, col)
            grid.addWidget(value, row * 2 + 1, col)
            self.fields[key] = value
        layout.addWidget(metrics)

        self.last_saved = QLabel("No plant has been saved in this run.")
        self.last_saved.setObjectName("lastSaved")
        layout.addWidget(self.last_saved)

        alice_card = QFrame(); alice_card.setObjectName("card")
        alice_layout = QVBoxLayout(alice_card); alice_layout.setContentsMargins(14, 10, 14, 10)
        alice_header = QLabel("Alice - next step"); alice_header.setStyleSheet("font-weight:700;color:#5C6975")
        self.alice_message = QLabel("Start a new run or resume the last run.")
        self.alice_message.setObjectName("instruction"); self.alice_message.setWordWrap(True)
        alice_layout.addWidget(alice_header); alice_layout.addWidget(self.alice_message)
        layout.addWidget(alice_card)

        barcode_card = QFrame(); barcode_card.setObjectName("card")
        barcode_layout = QVBoxLayout(barcode_card); barcode_layout.setContentsMargins(14, 10, 14, 10); barcode_layout.setSpacing(4)
        barcode_label = QLabel("PLANT OR CONTAINER BARCODE"); barcode_label.setStyleSheet("font-weight:700;color:#5C6975")
        self.barcode = QLineEdit()
        self.barcode.setObjectName("barcodeInput")
        self.barcode.setPlaceholderText("Scan or type the barcode, then press Enter")
        self.barcode.setAccessibleName("Plant barcode")
        self.barcode.setAccessibleDescription("Scan or type a plant barcode and press Enter")
        self.barcode.returnPressed.connect(self.submit_barcode)
        barcode_hint = QLabel("Barcode scanners normally submit automatically with Enter.")
        barcode_hint.setStyleSheet("color:#5C6975;font-size:12px")
        barcode_layout.addWidget(barcode_label); barcode_layout.addWidget(self.barcode); barcode_layout.addWidget(barcode_hint)
        layout.addWidget(barcode_card)

        actions = QGridLayout(); actions.setHorizontalSpacing(10); actions.setVerticalSpacing(10)
        action_callbacks = {
            "start_resume": self.start_resume,
            "connect_scale": self.scale_setup,
            "zero_scale": self.zero_scale,
            "set_tare": self.container_tare,
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
        self.setCentralWidget(central)

        self.device_status = QLabel("Scale disconnected")
        self.statusBar().addPermanentWidget(self.device_status, 1)
        self.statusBar().showMessage("Ready")

        shortcuts = {
            "Ctrl+N": self.new_run, "Ctrl+L": self.load_run, "Ctrl+R": self.start_resume,
            "Ctrl+K": self.scale_setup, "Ctrl+Z": self.zero_scale, "Ctrl+T": self.container_tare,
            "Ctrl+Enter": self.confirm_record, "Escape": self.cancel_item,
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
        self._add_menu_action(run_menu, "Load Run...", self.load_run, "Ctrl+L")
        run_menu.addSeparator()
        self._add_menu_action(run_menu, "Recover Run", self.recover)
        self._add_menu_action(run_menu, "Export Report...", self.export_report)
        self._add_menu_action(run_menu, "Finish Run", self.finish_run)

        scale_menu = self.menuBar().addMenu("Scale")
        self._add_menu_action(scale_menu, "Scale Setup and Connection...", self.scale_setup, "Ctrl+K")
        self._add_menu_action(scale_menu, "Zero Scale", self.zero_scale, "Ctrl+Z")
        self._add_menu_action(scale_menu, "Container Tare...", self.container_tare, "Ctrl+T")
        self._add_menu_action(scale_menu, "Guided Calibration...", self.calibrate)
        scale_menu.addSeparator()
        self._add_menu_action(scale_menu, "Diagnostics", self.diagnostics)

        help_menu = self.menuBar().addMenu("Help")
        self._add_menu_action(help_menu, "About", self.about)

    def bootstrap_simulator(self) -> None:
        if not self.runtime.controller.loaded_run:
            definition = {
                "run_id": "SIMULATOR-UI-RUN", "operator_id": "SIMULATOR-OPERATOR",
                "facility_id": "BEST-BUDS", "station_id": "WEIGHT-STATION-01",
                "cultivars": [{"cultivar_id": "CV-001", "name": "Simulator Cultivar"}],
                "capture_mode": self.runtime.controller.settings.capture_mode,
                "unit": "g", "container_id": "DEFAULT", "tare_g": 0.0, "maximum_capacity_g": 10000.0,
            }
            self.runtime.dispatch("run.new", {"definition": definition, "data_root": self.runtime.controller.settings.data_root, "simulator": True})
        if not self.runtime.controller.device:
            self.runtime.connect_simulator(); self.runtime.simulator_set_weight(1250.0)

    def refresh(self) -> None:
        s = self.runtime.snapshot(); device = s["device"]
        self.status.setText(s["operator_state"].title())
        self.weight.setText(f"{s['weight_g']:,.3f} g")
        if s.get("weight_uncalibrated"):
            self.weight_hint.setText("Uncalibrated raw — open Scale → Guided Calibration with a verified reference mass.")
        else:
            self.weight_hint.setText("")
        self.fields["RUN"].setText(s["run_id"] or "—")
        self.fields["CULTIVAR"].setText(s["cultivar"] or "—")
        self.fields["CONTAINER"].setText(s["container_id"] or "—")
        self.fields["GROSS"].setText(f"{s['weight_g']:,.3f} g")
        self.fields["TARE"].setText(f"{s['tare_g']:,.3f} g")
        self.fields["NET"].setText(f"{s['net_g']:,.3f} g")
        record = s["last_saved"]
        self.last_saved.setText(f"Saved safely: {record['record_id']} - {record['net_g']:.3f} g" if record else "No plant has been saved in this run.")
        self.alice_message.setText(str(s["alice_message"]))

        mode = device.get("mode") or "none"
        if mode == "serial_simulator":
            self.mode_badge.setText("SIMULATOR MODE - NO PHYSICAL SCALE")
            self.mode_badge.setStyleSheet("background:#FFF1D6;color:#8A4B08;border:1px solid #D69E2E;padding:5px 10px;border-radius:10px;font-weight:700")
        elif device.get("connected"):
            self.mode_badge.setText("PHYSICAL SERIAL - TESTING REQUIRED")
            self.mode_badge.setStyleSheet("background:#FFF1D6;color:#8A4B08;border:1px solid #D69E2E;padding:5px 10px;border-radius:10px;font-weight:700")
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
        self.barcode.setEnabled(ready)
        if ready and not self.barcode.hasFocus(): self.barcode.setFocus()
        self.buttons["START / RESUME"].setEnabled(state in {"NO_RUN", "RUN_FINISHED", "DEVICE_READY", "WAITING_FOR_BARCODE"})
        self.buttons["CONNECT SCALE"].setEnabled(state not in self.CAPTURE_STATES)
        self.buttons["ZERO"].setEnabled(connected and state in {"WAITING_FOR_BARCODE", "DEVICE_READY"})
        self.buttons["SET TARE"].setEnabled(connected and state in {"WAITING_FOR_BARCODE", "DEVICE_READY"})
        self.buttons["CONFIRM & RECORD"].setEnabled(state == "MANUAL_CONFIRM")
        self.buttons["CANCEL"].setEnabled(state in self.CAPTURE_STATES)
        self.buttons["FINISH RUN"].setEnabled(bool(s["run_id"]) and state not in {"LOCAL_COMMIT_PENDING"})

    def start_resume(self) -> None:
        if self.runtime.controller.loaded_run: self.resume_run()
        else: self.new_run()
    def new_run(self) -> None: NewRunDialog(self.runtime, self).exec()
    def resume_run(self) -> None: _show_result(self, self.runtime.dispatch("run.resume"))
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
    def calibrate(self) -> None: CalibrationDialog(self.runtime, self).exec()
    def submit_barcode(self) -> None:
        value=self.barcode.text().strip()
        if not value: return
        result=self.runtime.submit_barcode(value)
        if result.get("status") in {"failed", "blocked"}: _show_result(self,result)
        else: self.barcode.clear()
    def confirm_record(self) -> None: _show_result(self, self.runtime.dispatch("capture.confirm"))
    def cancel_item(self) -> None: _show_result(self, self.runtime.dispatch("capture.cancel"))
    def recover(self) -> None: _show_result(self, self.runtime.dispatch("state.recover"))
    def finish_run(self) -> None:
        if QMessageBox.question(self,"Finish Run","Finish the current run? Committed records remain immutable.")==QMessageBox.Yes:
            _show_result(self,self.runtime.dispatch("run.finish"))
    def export_report(self) -> None:
        path=QFileDialog.getExistingDirectory(self,"Export Report To",str(self.runtime.paths.exports))
        if path: _show_result(self,self.runtime.dispatch("report.export",{"destination":path}),success_title="Export completed")
    def diagnostics(self) -> None:
        QMessageBox.information(self,"Diagnostics",json.dumps(self.runtime.snapshot(),indent=2,sort_keys=True,default=str))
    def about(self) -> None:
        QMessageBox.information(self,"About",f"Best Buds Cultivator Weight Station v{__version__}\nWindows-first PySide6 operator application.\nPhysical scale and native Windows runtime require evidence before claims.")
    def closeEvent(self,event:QCloseEvent)->None:
        self.runtime.close(); event.accept()

def launch_pyside(runtime: OperatorRuntime, *, simulator: bool = False, smoke: bool = False) -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(runtime, simulator=simulator, smoke=smoke)
    window.show()
    return int(app.exec())
