"""
BBWS SR8 Scale Face — harvest-mode UI shell for the PySide operator app.

Presentation-only window that shares ``MainWindow``'s ``OperatorRuntime``.
Capture law, Alice gating, and JSONL authority stay on the host; this module
renders a bench-scale face (Harvest / SETUP toggle) and forwards actions to
existing ``MainWindow`` methods.

Not a separate process, not a remote weighing server, not legal-for-trade.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence, QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .operator_surface import (
    SCALE_FACE_HARVEST_ACTIONS,
    SCALE_FACE_SETUP_ACTIONS,
    frozen_display_weight,
)
from .ui_tokens import (
    COLOR_PRIMARY,
    COLOR_TEXT_MUTED,
    build_pyside_stylesheet,
    capture_pill_label,
)
from .units import format_weight, unit_label

if TYPE_CHECKING:
    from .pyside_frontend import MainWindow


class ScaleFaceWindow(QMainWindow):
    """Fullscreen-friendly Scale Face mode backed by the host MainWindow."""

    CAPTURE_STATES = {
        "BARCODE_CAPTURED",
        "WAITING_FOR_LOAD",
        "WEIGHING",
        "WAITING_FOR_STABLE_WEIGHT",
        "WEIGHT_STABLE",
        "MANUAL_CONFIRM",
        "LOCAL_COMMIT_PENDING",
    }

    def __init__(self, host: MainWindow):
        super().__init__(host)
        self.host = host
        self.runtime = host.runtime
        self._mode = "harvest"  # harvest | setup
        self.setWindowTitle("Best Buds — Scale Face (Harvest)")
        self.setStyleSheet(build_pyside_stylesheet())
        self.resize(1024, 768)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(14)

        header = QHBoxLayout()
        self.run_meta = QLabel("RUN —  ·  STRAIN —")
        self.run_meta.setStyleSheet(f"color:{COLOR_TEXT_MUTED};font-size:14px;font-weight:600")
        self.run_meta.setAccessibleName("Run and strain")
        header.addWidget(self.run_meta, 1)

        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(0)
        self.harvest_btn = QPushButton("HARVEST")
        self.setup_btn = QPushButton("SETUP")
        for btn in (self.harvest_btn, self.setup_btn):
            btn.setCheckable(True)
            btn.setMinimumHeight(36)
            btn.setStyleSheet(
                "QPushButton { padding: 6px 18px; font-weight: 700; border: 1px solid #D8DEE8; }"
                "QPushButton:checked { background: #1B6B52; color: white; border-color: #1B6B52; }"
            )
        self.harvest_btn.setChecked(True)
        self._mode_group = QButtonGroup(self)
        self._mode_group.setExclusive(True)
        self._mode_group.addButton(self.harvest_btn)
        self._mode_group.addButton(self.setup_btn)
        self.harvest_btn.clicked.connect(lambda: self.set_mode("harvest"))
        self.setup_btn.clicked.connect(lambda: self.set_mode("setup"))
        toggle_row.addWidget(self.harvest_btn)
        toggle_row.addWidget(self.setup_btn)
        header.addLayout(toggle_row)
        layout.addLayout(header)

        self.weight = QLabel("0.000 g")
        self.weight.setObjectName("weightDisplay")
        self.weight.setAlignment(Qt.AlignCenter)
        self.weight.setAccessibleName("Current weight in grams")
        self.weight.setStyleSheet("font-size: 96px; font-weight: 700; letter-spacing: -1px;")
        layout.addWidget(self.weight, 3)

        pill_row = QHBoxLayout()
        pill_row.addStretch(1)
        self.capture_pill = QLabel("Idle")
        self.capture_pill.setObjectName("statusPill")
        self.capture_pill.setAccessibleName("Capture status")
        self.capture_pill.setProperty("pill", "ready")
        self.capture_pill.setAlignment(Qt.AlignCenter)
        pill_row.addWidget(self.capture_pill)
        pill_row.addStretch(1)
        layout.addLayout(pill_row)

        self.alice_message = QLabel("Start a new run or resume the last run.")
        self.alice_message.setAlignment(Qt.AlignCenter)
        self.alice_message.setWordWrap(True)
        self.alice_message.setStyleSheet(f"color:{COLOR_TEXT_MUTED};font-size:15px;padding:4px 12px")
        self.alice_message.setAccessibleName("Alice next step")
        layout.addWidget(self.alice_message)

        barcode_row = QHBoxLayout()
        barcode_label = QLabel("BARCODE")
        barcode_label.setStyleSheet(f"color:{COLOR_TEXT_MUTED};font-weight:700;letter-spacing:1px")
        self.barcode = QLineEdit()
        self.barcode.setObjectName("barcodeInput")
        self.barcode.setPlaceholderText("Scan or type plant barcode")
        self.barcode.setAccessibleName("Plant barcode")
        self.barcode.returnPressed.connect(self.submit_barcode)
        self.scan_btn = QPushButton("SCAN")
        self.scan_btn.clicked.connect(self.open_scan)
        barcode_row.addWidget(barcode_label)
        barcode_row.addWidget(self.barcode, 1)
        barcode_row.addWidget(self.scan_btn)
        layout.addLayout(barcode_row)

        self.recent_strip = QLabel("Last: —")
        self.recent_strip.setStyleSheet(f"color:{COLOR_TEXT_MUTED};font-size:13px")
        self.recent_strip.setWordWrap(True)
        self.recent_strip.setAccessibleName("Recent saved plants")
        layout.addWidget(self.recent_strip)

        self.action_stack = QStackedWidget()
        self.harvest_buttons: dict[str, QPushButton] = {}
        self.setup_buttons: dict[str, QPushButton] = {}
        self.action_stack.addWidget(self._build_action_page(SCALE_FACE_HARVEST_ACTIONS, self.harvest_buttons, "harvest"))
        self.action_stack.addWidget(self._build_action_page(SCALE_FACE_SETUP_ACTIONS, self.setup_buttons, "setup"))
        layout.addWidget(self.action_stack)

        footer = QHBoxLayout()
        footer.addStretch(1)
        exit_btn = QPushButton("Exit Scale Face")
        exit_btn.clicked.connect(self.exit_to_host)
        footer.addWidget(exit_btn)
        layout.addLayout(footer)

        self.setCentralWidget(central)

        exit_action = QAction(self)
        exit_action.setShortcut(QKeySequence("Escape"))
        exit_action.triggered.connect(self.exit_to_host)
        self.addAction(exit_action)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(100)
        self.refresh()

    def _build_action_page(
        self,
        specs: tuple,
        store: dict[str, QPushButton],
        mode: str,
    ) -> QWidget:
        page = QFrame()
        page.setObjectName("card")
        grid = QGridLayout(page)
        grid.setContentsMargins(16, 14, 16, 14)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)
        callbacks = {
            "zero_scale": self.host.zero_scale,
            "set_tare": self.host.container_tare,
            "lock_weight": self.host.lock_weight,
            "confirm_record": self.host.confirm_record,
            "cancel_item": self.host.cancel_item,
            "start_resume": self.host.start_resume,
            "connect_scale": self.host.scale_setup,
            "calibrate": self.host.calibrate,
            "test_scanner": self.host.test_scanner,
        }
        object_names = {"primary": "primaryAction", "danger": "dangerAction"}
        for spec in specs:
            button = QPushButton(spec.label)
            button.clicked.connect(callbacks[spec.action_id])
            if spec.emphasis in object_names:
                button.setObjectName(object_names[spec.emphasis])
            if mode == "harvest" and spec.action_id == "start_resume":
                button.setStyleSheet("font-size: 12px; padding: 8px 12px; min-height: 36px;")
            else:
                button.setMinimumHeight(52)
            grid.addWidget(button, spec.row, spec.column, 1, spec.columnspan)
            store[spec.action_id] = button
        return page

    def set_mode(self, mode: str) -> None:
        self._mode = "setup" if mode == "setup" else "harvest"
        self.harvest_btn.setChecked(self._mode == "harvest")
        self.setup_btn.setChecked(self._mode == "setup")
        self.action_stack.setCurrentIndex(0 if self._mode == "harvest" else 1)
        self.refresh()

    def open_scale_face(self) -> None:
        """Show this face (usually called from the host)."""
        self.showMaximized()
        self.raise_()
        self.activateWindow()
        self.refresh()

    def exit_to_host(self) -> None:
        self.hide()
        self.host.show()
        self.host.raise_()
        self.host.activateWindow()
        self.host.refresh()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        event.ignore()
        self.exit_to_host()

    def open_scan(self) -> None:
        self.host.open_scan_dialog()
        self.barcode.setText(self.host.barcode.text())
        self.refresh()

    def submit_barcode(self) -> None:
        value = self.barcode.text().strip()
        self.host.barcode.setText(value)
        self.host.submit_barcode()
        self.refresh()

    def _refresh_capture_pill(self, state: str, has_saved: bool) -> None:
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
        if state == "WEIGHT_STABLE":
            label = "STABLE — LOCK WEIGHT"
        elif state == "MANUAL_CONFIRM":
            label = "LOCKED — CONFIRM"
        self.capture_pill.setText(label)
        self.capture_pill.setProperty("pill", pill)
        self.capture_pill.style().unpolish(self.capture_pill)
        self.capture_pill.style().polish(self.capture_pill)

    def _recent_lines(self, plants: list[dict[str, Any]], du: str) -> str:
        if not plants:
            return "Last: —"
        parts: list[str] = []
        for row in plants[:3]:
            barcode = row.get("barcode_raw") or row.get("record_id") or "?"
            net = format_weight(float(row.get("net_g") or 0.0), du)
            parts.append(f"{barcode}  {net}")
        return "Last: " + " · ".join(parts)

    def refresh(self) -> None:
        if not self.isVisible():
            return
        s = self.runtime.snapshot()
        device = s["device"]
        du = unit_label(s.get("display_unit") or "g")
        locked = s.get("locked_weight_g")
        display_g = frozen_display_weight(float(s["weight_g"]), locked)
        self.weight.setText(format_weight(display_g, du))
        if locked is not None:
            self.weight.setStyleSheet(
                f"font-size: 96px; font-weight: 700; letter-spacing: -1px; color:{COLOR_PRIMARY};"
            )
        else:
            self.weight.setStyleSheet("font-size: 96px; font-weight: 700; letter-spacing: -1px;")

        run_id = s.get("run_id") or "—"
        strain = s.get("strain") or s.get("cultivar") or "—"
        self.run_meta.setText(f"RUN {run_id}  ·  STRAIN {strain}")
        self.alice_message.setText(str(s.get("alice_message") or ""))
        record = s.get("last_saved")
        self._refresh_capture_pill(s["state"], bool(record))
        self.recent_strip.setText(self._recent_lines(list(s.get("recent_plants") or []), du))

        active_bc = s.get("active_barcode")
        if active_bc and self.barcode.text().strip() != str(active_bc) and s["state"] in self.CAPTURE_STATES:
            self.barcode.setText(str(active_bc))

        state = s["state"]
        ready = state == "WAITING_FOR_BARCODE"
        connected = bool(device.get("connected"))
        calibration_open = bool(getattr(self.host, "_calibration_open", False))
        self.barcode.setEnabled(ready and not calibration_open)
        self.scan_btn.setEnabled(ready and not calibration_open)

        # Mirror MainWindow.refresh enable rules for shared actions.
        start_enabled = state in {"NO_RUN", "RUN_FINISHED", "DEVICE_READY", "WAITING_FOR_BARCODE"}
        zero_enabled = connected and state not in self.CAPTURE_STATES
        tare_enabled = connected and state in {"WAITING_FOR_BARCODE", "DEVICE_READY"}
        self.harvest_buttons["zero_scale"].setEnabled(zero_enabled)
        self.harvest_buttons["set_tare"].setEnabled(tare_enabled)
        self.harvest_buttons["lock_weight"].setEnabled(state == "WEIGHT_STABLE")
        self.harvest_buttons["confirm_record"].setEnabled(state == "MANUAL_CONFIRM")
        self.harvest_buttons["cancel_item"].setEnabled(state in self.CAPTURE_STATES)
        start_btn = self.harvest_buttons["start_resume"]
        start_btn.setEnabled(start_enabled)
        # Compact START/RESUME only when a run is missing or finished.
        need_start = state in {"NO_RUN", "RUN_FINISHED"} or not s.get("run_id")
        start_btn.setVisible(need_start)

        self.setup_buttons["connect_scale"].setEnabled(state not in self.CAPTURE_STATES)
        self.setup_buttons["zero_scale"].setEnabled(zero_enabled)
        self.setup_buttons["set_tare"].setEnabled(tare_enabled)
        self.setup_buttons["calibrate"].setEnabled(state not in self.CAPTURE_STATES)
        self.setup_buttons["test_scanner"].setEnabled(True)

        active = QApplication.activeModalWidget()
        if (
            ready
            and not calibration_open
            and active is None
            and self._mode == "harvest"
            and not self.barcode.hasFocus()
        ):
            self.barcode.setFocus()
