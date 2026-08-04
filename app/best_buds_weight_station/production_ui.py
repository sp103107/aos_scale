"""Production operator UI entry: PySide6 primary, Tk secondary fallback.

BBWS SR2 brings Tk to SR1 feature parity and wires display units (g/kg/lb).
Authoritative storage remains grams via OperatorRuntime / JSONL.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .application_controller import ApplicationController
from .operator_runtime import OperatorRuntime
from .operator_surface import ROUTINE_ACTION_LAYOUT
from .units import display_to_grams, format_weight, unit_label
from .version import __version__

KEYBOARD_SHORTCUTS = {
    "Ctrl+N": "new_run",
    "Ctrl+L": "load_run",
    "Ctrl+R": "start_resume",
    "Ctrl+K": "connect_scale",
    "Ctrl+Z": "zero_scale",
    "Ctrl+T": "set_container_tare",
    "Ctrl+Enter": "confirm_record",
    "Escape": "cancel_item",
}

OPERATOR_STATE_LABELS = {
    "NO_RUN": "No run started",
    "RUN_READY": "Run ready",
    "DISCONNECTED": "Scale disconnected",
    "DEVICE_CONNECTING": "Connecting scale",
    "DEVICE_READY": "Scale ready",
    "WAITING_FOR_BARCODE": "Ready to scan",
    "BARCODE_CAPTURED": "Barcode scanned",
    "WAITING_FOR_LOAD": "Hang or place the plant",
    "WEIGHING": "Weighing plant",
    "WAITING_FOR_STABLE_WEIGHT": "Waiting for a stable weight",
    "WEIGHT_STABLE": "Stable - lock weight",
    "MANUAL_CONFIRM": "Locked - confirm record",
    "LOCAL_COMMIT_PENDING": "Saving record",
    "RECORD_SAVED": "Saved safely",
    "RECOVERY_REQUIRED": "Recovery required",
    "ERROR": "Not saved",
    "RUN_FINISHED": "Run finished",
}

BUTTON_ACTIONS = {
    "new_run": "run.new",
    "start_resume": "run.resume",
    "load_run": "run.load",
    "connect_scale": "ui.open_scale_setup",
    "zero_scale": "scale.zero",
    "set_container_tare": "scale.container_tare.set",
    "capture_container_tare": "scale.container_tare.capture",
    "calibrate_scale": "scale.calibration.start",
    "lock_weight": "capture.weight.lock",
    "confirm_record": "capture.confirm",
    "cancel_item": "capture.cancel",
    "finish_run": "run.finish",
    "settings": "settings.data_location.set",
}


@dataclass
class ProductionViewModel:
    controller: ApplicationController
    current_weight_g: float = 0.0
    gross_g: float = 0.0
    tare_g: float = 0.0
    net_g: float = 0.0
    barcode: str = ""

    @property
    def operator_state(self) -> str:
        return OPERATOR_STATE_LABELS.get(self.controller.state, self.controller.state.replace("_", " ").title())

    @property
    def truth_class(self) -> str:
        return str((self.controller.last_alice_response or {}).get("truth_class", "NOT_RUN"))

    @property
    def last_saved(self) -> str:
        record = self.controller.last_record
        return "none" if not record else f"{record['record_id']} - {record['net_g']:.3f} g"


def launch(data_root: str | None = None, simulator: bool = False, smoke: bool = False, capture_mode: str = "manual") -> int:
    runtime = OperatorRuntime(data_root, capture_mode=capture_mode)
    try:
        from .pyside_frontend import launch_pyside
    except ImportError:
        return _launch_tk(runtime, simulator=simulator, smoke=smoke)
    return launch_pyside(runtime, simulator=simulator, smoke=smoke)


def launch_tk(data_root: str | None = None, simulator: bool = False, smoke: bool = False, capture_mode: str = "manual") -> int:
    """Force Tk fallback (Linux smoke / operator preference)."""
    runtime = OperatorRuntime(data_root, capture_mode=capture_mode)
    return _launch_tk(runtime, simulator=simulator, smoke=smoke)


def _launch_tk(runtime: OperatorRuntime, *, simulator: bool, smoke: bool) -> int:
    """Secondary fallback UI. Shares the same runtime and truth gates as PySide6."""

    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk

    root = tk.Tk()
    root.title(f"Best Buds Cultivator Weight Station v{__version__} - Tk fallback")
    root.geometry("1120x920")
    root.minsize(1024, 800)
    root.configure(bg="#F5F7FA")

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Primary.TButton", font=("Segoe UI", 12, "bold"), padding=(14, 12))
    style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=(12, 10))
    style.configure("Danger.TButton", font=("Segoe UI", 11, "bold"), padding=(12, 10))

    shell = tk.Frame(root, bg="#F5F7FA")
    shell.pack(fill="both", expand=True, padx=18, pady=14)

    top = tk.Frame(shell, bg="#FFFFFF", highlightbackground="#CBD4DD", highlightthickness=1)
    top.pack(fill="x")
    tk.Label(top, text="Best Buds Cultivator Weight Station", font=("Segoe UI", 24, "bold"), bg="#FFFFFF", fg="#17212B").pack(side="left", padx=14, pady=10)
    mode_badge = tk.Label(top, text="NO SCALE CONNECTED", font=("Segoe UI", 10, "bold"), bg="#EEF2F6", fg="#5C6975", padx=10, pady=5)
    mode_badge.pack(side="right", padx=14, pady=10)

    status = tk.Label(shell, text="No run started", font=("Segoe UI", 17, "bold"), bg="#FFFFFF", fg="#17212B", anchor="w", padx=14, pady=10, highlightbackground="#CBD4DD", highlightthickness=1)
    status.pack(fill="x", pady=(10, 8))

    weight = tk.Label(shell, text="0.000 g", font=("Segoe UI", 52, "bold"), bg="#FFFFFF", fg="#17212B", padx=14, pady=16, highlightbackground="#17212B", highlightthickness=2)
    weight.pack(fill="x")
    weight_hint = tk.Label(shell, text="", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#8A4B08", wraplength=900)
    weight_hint.pack(fill="x", pady=(2, 0))

    metrics = tk.Frame(shell, bg="#FFFFFF", highlightbackground="#CBD4DD", highlightthickness=1)
    metrics.pack(fill="x", pady=8)
    metric_values: dict[str, tk.Label] = {}
    for idx, key in enumerate(("RUN", "CULTIVAR", "OPERATOR", "CONTAINER", "GROSS", "TARE", "NET", "CAL ID")):
        col = idx % 4
        row = (idx // 4) * 2
        tk.Label(metrics, text=key.title(), font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#5C6975").grid(row=row, column=col, sticky="w", padx=14, pady=(8, 0))
        value = tk.Label(metrics, text="-", font=("Segoe UI", 15, "bold"), bg="#FFFFFF", fg="#17212B", anchor="w")
        value.grid(row=row + 1, column=col, sticky="ew", padx=14, pady=(0, 8))
        metric_values[key] = value
    for col in range(4):
        metrics.grid_columnconfigure(col, weight=1)

    strain_row = tk.Frame(shell, bg="#F5F7FA")
    strain_row.pack(fill="x")
    active_strain = tk.Label(strain_row, text="Active strain (sticky): —", font=("Segoe UI", 11, "bold"), bg="#F5F7FA", fg="#1E6B52", anchor="w")
    active_strain.pack(side="left", fill="x", expand=True)
    change_strain_btn = ttk.Button(strain_row, text="Change Strain")
    change_strain_btn.pack(side="right")

    last_saved = tk.Label(shell, text="No plant has been saved in this run.", font=("Segoe UI", 11, "bold"), bg="#E7F6EC", fg="#176B2C", anchor="w", padx=12, pady=8)
    last_saved.pack(fill="x", pady=(6, 0))
    pending_sync = tk.Label(shell, text="", font=("Segoe UI", 10, "bold"), bg="#F5F7FA", fg="#8A4B08", anchor="w")
    pending_sync.pack(fill="x")

    alice_card = tk.Frame(shell, bg="#FFFFFF", highlightbackground="#CBD4DD", highlightthickness=1)
    alice_card.pack(fill="x", pady=8)
    tk.Label(alice_card, text="Alice - next step", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#5C6975").pack(anchor="w", padx=12, pady=(8, 2))
    alice = tk.Label(alice_card, text="Start a new run or resume the last run.", justify="left", anchor="w", wraplength=1020, font=("Segoe UI", 13, "bold"), bg="#FFFFFF", fg="#17212B", padx=12, pady=8)
    alice.pack(fill="x")

    barcode_card = tk.Frame(shell, bg="#FFFFFF", highlightbackground="#CBD4DD", highlightthickness=1)
    barcode_card.pack(fill="x", pady=(0, 8))
    tk.Label(barcode_card, text="PLANT OR CONTAINER BARCODE", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#5C6975").pack(anchor="w", padx=12, pady=(8, 2))
    barcode_row = tk.Frame(barcode_card, bg="#FFFFFF")
    barcode_row.pack(fill="x", padx=12)
    barcode = tk.Entry(barcode_row, font=("Segoe UI", 18), relief="solid", bd=1, name="barcode_input")
    barcode.pack(side="left", fill="x", expand=True, ipady=8)
    auto_id_btn = ttk.Button(barcode_row, text="Use auto ID")
    auto_id_btn.pack(side="left", padx=(6, 0))
    scan_btn = ttk.Button(barcode_row, text="Scan")
    scan_btn.pack(side="left", padx=(6, 0))
    barcode_hint = tk.Label(
        barcode_card,
        text="USB HID — press Scan, then scan. Tag stays visible until Confirm.",
        font=("Segoe UI", 9),
        bg="#FFFFFF",
        fg="#5C6975",
        anchor="w",
    )
    barcode_hint.pack(fill="x", padx=12, pady=(4, 2))
    active_barcode_banner = tk.Label(
        barcode_card,
        text="Active plant: —",
        font=("Segoe UI", 11, "bold"),
        bg="#FFFFFF",
        fg="#1B69D2",
        anchor="w",
    )
    active_barcode_banner.pack(fill="x", padx=12, pady=(0, 8))

    note_row = tk.Frame(shell, bg="#F5F7FA")
    note_row.pack(fill="x", pady=(0, 6))
    operator_note = tk.Entry(note_row, font=("Segoe UI", 11))
    operator_note.insert(0, "")
    operator_note.pack(side="left", fill="x", expand=True, ipady=4)
    void_var = tk.StringVar(value="void: none")
    void_box = ttk.Combobox(note_row, textvariable=void_var, values=["void: none", "void: mark void"], state="readonly", width=16)
    void_box.pack(side="left", padx=(6, 0))

    controls = tk.Frame(shell, bg="#F5F7FA")
    controls.pack(fill="x")
    locked_weight = tk.Label(shell, text="", font=("Segoe UI", 12, "bold"), bg="#F5F7FA", fg="#1E6B52", anchor="w")
    locked_weight.pack(fill="x", pady=(4, 0))
    plant_log = tk.Listbox(shell, height=6, font=("Consolas", 9))
    plant_log.pack(fill="both", expand=False, pady=(6, 0))
    status_line = tk.Label(shell, text="Scale disconnected", font=("Segoe UI", 9), bg="#F5F7FA", fg="#5C6975", anchor="w")
    status_line.pack(fill="x", pady=(8, 0))

    def show_result(result: dict[str, Any], *, success_title: str = "Completed") -> None:
        if result.get("status") in {"failed", "blocked"}:
            messagebox.showwarning("Action not completed", result.get("message", "Action failed"), parent=root)
        elif result.get("terminal", True) and result.get("status") == "completed" and success_title:
            # Soft path: most successes use status_line; keep modal only when asked.
            pass

    def new_run() -> None:
        run_id = simpledialog.askstring("New Run", "Harvest-run ID", parent=root)
        operator = simpledialog.askstring("New Run", "Operator ID", parent=root)
        cultivar = simpledialog.askstring("New Run", "Cultivar", parent=root)
        if not all((run_id, operator, cultivar)):
            return
        definition = {
            "run_id": run_id.strip(),
            "operator_id": operator.strip(),
            "facility_id": "BEST-BUDS",
            "station_id": "WEIGHT-STATION-01",
            "cultivars": [{"cultivar_id": "CV-001", "name": cultivar.strip()}],
            "capture_mode": runtime.controller.settings.capture_mode,
            "unit": "g",
            "container_id": "DEFAULT",
            "tare_g": 0.0,
            "maximum_capacity_g": 10000.0,
        }
        show_result(runtime.dispatch("run.new", {"definition": definition, "data_root": runtime.controller.settings.data_root, "simulator": False}))

    def start_resume() -> None:
        if runtime.controller.loaded_run:
            show_result(runtime.dispatch("run.resume"))
        else:
            new_run()

    def load_run() -> None:
        path = filedialog.askopenfilename(title="Load Run", filetypes=[("Session manifest", "session_manifest.json"), ("JSON", "*.json")], parent=root)
        if path:
            show_result(runtime.dispatch("run.load", {"selection": path}))

    def change_strain() -> None:
        if not runtime.controller.loaded_run:
            messagebox.showinfo("No run", "Start or resume a run before changing strain.", parent=root)
            return
        current = runtime.snapshot().get("cultivar") or ""
        name = simpledialog.askstring(
            "Change Active Strain",
            "Active strain / cultivar (sticky until changed).\nNot Metrc compliance.",
            initialvalue=str(current),
            parent=root,
        )
        if not name or not name.strip():
            return
        result = runtime.dispatch("run.set_active_cultivar", {"name": name.strip()})
        if result.get("status") != "completed":
            show_result(result)
        else:
            status_line.config(text=result.get("message") or "Active strain updated.")

    def station_settings() -> None:
        win = tk.Toplevel(root)
        win.title("Station Settings")
        win.geometry("480x220")
        body = ttk.Frame(win, padding=12)
        body.pack(fill="both", expand=True)
        required = bool(runtime.controller.settings.barcode_required_for_capture)
        barcode_policy = tk.StringVar(value="required" if required else "optional")
        display = tk.StringVar(value=str(getattr(runtime.controller.settings, "display_unit", "g") or "g"))
        ttk.Label(body, text="Plant barcode policy").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Combobox(body, textvariable=barcode_policy, values=["required", "optional"], state="readonly").grid(row=0, column=1, sticky="ew")
        ttk.Label(body, text="Display unit (storage stays g)").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Combobox(body, textvariable=display, values=["g", "kg", "lb"], state="readonly").grid(row=1, column=1, sticky="ew")
        ttk.Label(body, text="HID keyboard-wedge only. Display lb/kg is not legal-for-trade.").grid(row=2, column=0, columnspan=2, sticky="w", pady=8)

        def save() -> None:
            runtime.dispatch("settings.barcode_policy.set", {"barcode_required_for_capture": barcode_policy.get() == "required"})
            result = runtime.dispatch("settings.display_unit.set", {"display_unit": display.get()})
            if result.get("status") != "completed":
                show_result(result)
            else:
                win.destroy()

        ttk.Button(body, text="Save", command=save).grid(row=3, column=0, pady=10)
        ttk.Button(body, text="Cancel", command=win.destroy).grid(row=3, column=1, pady=10)
        body.grid_columnconfigure(1, weight=1)

    def test_scanner() -> None:
        win = tk.Toplevel(root)
        win.title("Test Barcode Scanner")
        win.geometry("520x220")
        tip = tk.Label(
            win,
            text="Scan with a USB HID keyboard-wedge (or type and press Enter). BLE/SPP/camera not used.",
            wraplength=480,
            justify="left",
        )
        tip.pack(padx=12, pady=10, fill="x")
        field = tk.Entry(win, font=("Segoe UI", 16))
        field.pack(fill="x", padx=12, ipady=6)
        status_lbl = tk.Label(win, text="No scan yet. Keep focus in this field.")
        status_lbl.pack(padx=12, pady=6)

        def accepted(_event=None) -> None:
            value = field.get().strip()
            if not value:
                status_lbl.config(text="Empty scan blocked. Try again.")
                return
            receipt = {
                "receipt_type": "hid_scanner_test",
                "status": "pass",
                "barcode_sample": value,
                "transport": "hid_keyboard_wedge",
                "ui": "tk",
                "non_claims": ["HID wedge only — not BLE/SPP"],
            }
            out = Path(runtime.controller.settings.data_root) / "scanner_test_receipts"
            out.mkdir(parents=True, exist_ok=True)
            path = out / f"scanner_test_{value[:32].replace('/', '_')}.json"
            path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            messagebox.showinfo("Scanner OK", f"Scanner OK — received:\n{value}", parent=win)
            win.destroy()

        field.bind("<Return>", accepted)
        field.focus_set()

    def use_auto_id() -> None:
        if runtime.controller.settings.barcode_required_for_capture:
            messagebox.showinfo(
                "Barcode required",
                "This station requires a scanned or typed barcode. Open Settings → Station Settings to allow auto ID.",
                parent=root,
            )
            return
        value = runtime.next_auto_plant_id()
        barcode.delete(0, "end")
        barcode.insert(0, value)
        submit()

    def scale_setup() -> None:
        win = tk.Toplevel(root)
        win.title("Scale Setup and Connection")
        win.geometry("760x520")
        mode = tk.StringVar(value="Simulator" if simulator else "Physical serial")
        port = tk.StringVar(value=str(runtime.controller.settings.serial_port or ""))
        baud = tk.StringVar(value=str(runtime.controller.settings.baud_rate or 115200))
        body = ttk.Frame(win, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Device mode").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Combobox(body, textvariable=mode, values=["Physical serial", "Simulator"], state="readonly").grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Label(body, text="Serial port").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        ports = [item["device"] for item in runtime.dispatch("device.discover").get("data", {}).get("ports", [])]
        ttk.Combobox(body, textvariable=port, values=ports).grid(row=1, column=1, sticky="ew", padx=6)
        ttk.Label(body, text="Baud").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        ttk.Combobox(body, textvariable=baud, values=["115200", "9600"], state="readonly").grid(row=2, column=1, sticky="ew", padx=6)
        output = tk.Text(body, height=18, width=80, font=("Consolas", 9))
        output.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=6, pady=8)

        def write(value: Any) -> None:
            output.delete("1.0", "end")
            output.insert("1.0", json.dumps(value, indent=2, sort_keys=True, default=str))

        def connect() -> None:
            try:
                if mode.get() == "Simulator":
                    result = runtime.connect_simulator()
                    if result.get("status") == "completed":
                        runtime.simulator_set_weight(1250.0)
                else:
                    selected = port.get().strip()
                    if not selected:
                        raise ValueError("Select or enter a serial port.")
                    result = runtime.connect_serial(selected, int(baud.get()))
                write(result)
                if result.get("status") != "completed":
                    detail = result.get("data", {}).get("error_detail") or result.get("message") or "Connection failed"
                    messagebox.showwarning("Connection failed", str(detail), parent=win)
            except Exception as exc:
                messagebox.showwarning("Connection failed", str(exc), parent=win)

        ttk.Button(body, text="Connect", command=connect).grid(row=3, column=0, padx=6, pady=6)
        ttk.Button(body, text="Disconnect", command=lambda: write(runtime.disconnect())).grid(row=3, column=1, padx=6, pady=6)
        ttk.Button(body, text="PING", command=lambda: write(runtime.dispatch("device.ping"))).grid(row=4, column=0, padx=6, pady=6)
        ttk.Button(body, text="STATUS", command=lambda: write(runtime.dispatch("device.status"))).grid(row=4, column=1, padx=6, pady=6)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(5, weight=1)

    def zero() -> None:
        try:
            result = runtime.zero_scale()
            status_line.config(text=result.get("message") or "Scale zeroed.")
            if result.get("status") in {"failed", "blocked"}:
                show_result(result)
        except Exception as exc:
            messagebox.showwarning("Zero failed", str(exc), parent=root)

    def tare() -> None:
        container = simpledialog.askstring("Container Tare", "Container ID", initialvalue="DEFAULT", parent=root)
        if not container:
            return
        choice = messagebox.askyesnocancel("Container Tare", "Yes: capture empty container from the live scale\nNo: enter a known tare\nCancel: stop", parent=root)
        if choice is None:
            return
        try:
            if choice:
                result = runtime.capture_container_tare(container)
            else:
                du = unit_label(runtime.snapshot().get("display_unit") or "g")
                value = simpledialog.askfloat("Known Tare", f"Tare in {du} (stored as grams)", minvalue=0.0, parent=root)
                if value is None:
                    return
                result = runtime.set_known_tare(container, display_to_grams(value, du))
            show_result(result)
            status_line.config(text=result.get("message") or "Tare saved.")
        except Exception as exc:
            messagebox.showwarning("Tare failed", str(exc), parent=root)

    def calibrate() -> None:
        win = tk.Toplevel(root)
        win.title("Guided Calibration")
        win.geometry("820x620")
        # Calibration reference is always grams — avoids kg/lb display-unit mixups.
        default_g = float(runtime.controller.settings.default_reference_weight_g)
        reference = tk.DoubleVar(value=default_g)
        steps = (
            "Connect the scale. Enter verified reference mass in GRAMS "
            "(even if the main screen display unit is kg/lb).\n"
            "Not legal-for-trade. Leave the same mass on from Loaded through Test.\n"
            "1 Start → 2 Zero samples → 3 Loaded samples → 4 Test → 5 Accept → ZERO."
        )
        tk.Label(win, text=steps, font=("Segoe UI", 10), justify="left", wraplength=780, anchor="w").pack(padx=10, pady=8, fill="x")
        tk.Label(win, text="Reference mass (g) — must match mass on pan", font=("Segoe UI", 11, "bold")).pack(padx=10, anchor="w")
        tk.Entry(win, textvariable=reference, font=("Segoe UI", 12)).pack(fill="x", padx=10)
        output = tk.Text(win, height=18, width=92, font=("Consolas", 9))
        output.pack(fill="both", expand=True, padx=10, pady=10)

        def run_step(fn) -> None:
            try:
                result = fn()
                output.delete("1.0", "end")
                output.insert("1.0", json.dumps(result, indent=2, sort_keys=True, default=str))
                test = (result.get("data") or {}).get("calibration_test") or {}
                summary = test.get("operator_summary") or ""
                if summary and not test.get("passed_local_tolerance", True):
                    messagebox.showwarning("Test did not pass", summary, parent=win)
            except Exception as exc:
                messagebox.showwarning("Calibration step blocked", str(exc), parent=win)

        def loaded() -> dict[str, Any]:
            grams = float(reference.get())
            return runtime.add_calibration_loaded_samples(grams)

        row = tk.Frame(win)
        row.pack(fill="x", padx=8, pady=6)
        for text, fn in [
            ("1 Start", runtime.start_calibration),
            ("2 Zero samples", runtime.add_calibration_zero_samples),
            ("3 Loaded samples", loaded),
            ("4 Test", runtime.test_calibration),
            ("5 Accept", runtime.accept_calibration),
            ("Cancel", runtime.cancel_calibration),
        ]:
            ttk.Button(row, text=text, command=lambda f=fn: run_step(f)).pack(side="left", padx=3)

    def diagnostics() -> None:
        win = tk.Toplevel(root)
        win.title("Diagnostics")
        text = tk.Text(win, height=30, width=110, font=("Consolas", 9))
        text.pack(fill="both", expand=True)
        text.insert("1.0", json.dumps(runtime.snapshot(), indent=2, sort_keys=True, default=str))

    def focus_scan() -> None:
        barcode.focus_set()
        barcode.selection_range(0, "end")
        status_line.config(text="Ready to scan — focus is in the plant barcode field.")

    def lock_weight() -> None:
        result = runtime.lock_weight()
        if result.get("status") in {"failed", "blocked"}:
            show_result(result)
        else:
            status_line.config(text=result.get("message") or "Weight locked — Confirm & Record when ready.")

    def submit(event=None) -> None:
        value = barcode.get().strip()
        if not value:
            status_line.config(text="Empty barcode blocked — scan or type a plant ID, then press Enter.")
            return
        result = runtime.submit_barcode(value)
        if result.get("status") in {"failed", "blocked"}:
            show_result(result)
        else:
            barcode.delete(0, "end")
            barcode.insert(0, value)
            active_barcode_banner.config(text=f"Active plant: {value}")
            status_line.config(text=f"Barcode accepted: {value} — place plant, wait for stable, then Lock weight.")

    def confirm_record() -> None:
        note = operator_note.get().strip() or None
        void_status = "void" if void_var.get().endswith("void") and "mark" in void_var.get() else "none"
        result = runtime.dispatch("capture.confirm", {"operator_note": note, "void_status": void_status})
        if result.get("status") == "completed":
            feedback = (result.get("data") or {}).get("feedback")
            msg = result.get("message") or "Record saved."
            status_line.config(text=msg)
            operator_note.delete(0, "end")
            void_var.set("void: none")
            barcode.delete(0, "end")
            barcode.focus_set()
            if feedback == "warning":
                messagebox.showwarning("Saved with duplicate warning", msg, parent=root)
        else:
            show_result(result)

    def cancel_item() -> None:
        result = runtime.dispatch("capture.cancel")
        barcode.delete(0, "end")
        status_line.config(text=result.get("message") or "Cancelled — scan again when ready.")
        barcode.focus_set()
        if result.get("status") in {"failed", "blocked"}:
            show_result(result)

    def rebuild_csv() -> None:
        result = runtime.dispatch("spreadsheet.rebuild")
        status_line.config(text=result.get("message") or "CSV rebuild finished.")
        if result.get("status") in {"failed", "blocked"}:
            show_result(result)

    def reconcile_export() -> None:
        result = runtime.dispatch("report.reconcile")
        status_line.config(text=result.get("message") or "Reconcile finished.")
        if result.get("status") != "completed":
            show_result(result)
        else:
            messagebox.showinfo("Reconcile pass", result.get("message") or "pass", parent=root)

    def recover() -> None:
        result = runtime.dispatch("state.recover")
        if result.get("status") == "completed":
            receipt = (result.get("data") or {}).get("recovery_receipt") or {}
            msg = result.get("message") or "Recovered."
            if receipt.get("spreadsheet_rebuild"):
                msg += f"\nCSV rebuilt: {receipt['spreadsheet_rebuild'].get('rebuilt_rows')} rows."
            messagebox.showinfo("Recovered", msg, parent=root)
        else:
            rebuild = runtime.dispatch("spreadsheet.rebuild")
            if rebuild.get("status") == "completed":
                messagebox.showinfo("CSV rebuilt", (rebuild.get("message") or "CSV rebuilt from JSONL.") + "\n\nResume and continue scanning.", parent=root)
            else:
                show_result(result)

    def export_report() -> None:
        path = filedialog.askdirectory(title="Export Report", initialdir=str(runtime.paths.exports), parent=root)
        if not path:
            return
        result = runtime.dispatch("report.export", {"destination": path})
        if result.get("status") == "completed":
            paths = (result.get("data") or {}).get("paths") or []
            listing = "\n".join(paths) if paths else path
            reconcile = runtime.dispatch("report.reconcile")
            gate = ((reconcile.get("data") or {}).get("reconcile") or {}).get("status", "n/a")
            messagebox.showinfo(
                "Export completed",
                f"Handoff files written:\n\n{listing}\n\nReconcile gate: {gate}\nSession JSONL remains authoritative.",
                parent=root,
            )
        else:
            show_result(result)

    def finish() -> None:
        if messagebox.askyesno("Finish Run", "Finish the current run? Committed records remain immutable.", parent=root):
            show_result(runtime.dispatch("run.finish"))

    action_callbacks = {
        "start_resume": start_resume,
        "connect_scale": scale_setup,
        "zero_scale": zero,
        "set_tare": tare,
        "lock_weight": lock_weight,
        "confirm_record": confirm_record,
        "cancel_item": cancel_item,
        "finish_run": finish,
    }
    style_names = {"primary": "Primary.TButton", "danger": "Danger.TButton", "default": "Action.TButton"}
    buttons: dict[str, ttk.Button] = {}
    for spec in ROUTINE_ACTION_LAYOUT:
        button = ttk.Button(controls, text=spec.label, command=action_callbacks[spec.action_id], style=style_names[spec.emphasis])
        button.grid(row=spec.row, column=spec.column, columnspan=spec.columnspan, sticky="ew", padx=4, pady=4)
        buttons[spec.label] = button
    for col in range(4):
        controls.grid_columnconfigure(col, weight=1)

    change_strain_btn.config(command=change_strain)
    auto_id_btn.config(command=use_auto_id)
    scan_btn.config(command=focus_scan)

    menubar = tk.Menu(root)
    run_menu = tk.Menu(menubar, tearoff=0)
    run_menu.add_command(label="New Run", command=new_run)
    run_menu.add_command(label="Resume Last Run", command=lambda: show_result(runtime.dispatch("run.resume")))
    run_menu.add_command(label="Load Run...", command=load_run)
    run_menu.add_separator()
    run_menu.add_command(label="Change Active Strain...", command=change_strain)
    run_menu.add_command(label="Recover Run", command=recover)
    run_menu.add_command(label="Rebuild CSV from JSONL", command=rebuild_csv)
    run_menu.add_command(label="Reconcile Export ↔ JSONL", command=reconcile_export)
    run_menu.add_command(label="Export Report...", command=export_report)
    run_menu.add_command(label="Finish Run", command=finish)
    menubar.add_cascade(label="Run", menu=run_menu)
    scale_menu = tk.Menu(menubar, tearoff=0)
    scale_menu.add_command(label="Scale Setup and Connection...", command=scale_setup)
    scale_menu.add_command(label="Zero Scale", command=zero)
    scale_menu.add_command(label="Container Tare...", command=tare)
    scale_menu.add_command(label="Guided Calibration...", command=calibrate)
    scale_menu.add_command(label="Test Scanner...", command=test_scanner)
    scale_menu.add_separator()
    scale_menu.add_command(label="Diagnostics", command=diagnostics)
    menubar.add_cascade(label="Scale", menu=scale_menu)
    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label="Station Settings...", command=station_settings)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    root.config(menu=menubar)

    barcode.bind("<Return>", submit)
    root.bind("<Control-n>", lambda _e: new_run())
    root.bind("<Control-l>", lambda _e: load_run())
    root.bind("<Control-r>", lambda _e: start_resume())
    root.bind("<Control-k>", lambda _e: scale_setup())
    root.bind("<Control-z>", lambda _e: zero())
    root.bind("<Control-t>", lambda _e: tare())
    root.bind("<Control-Return>", lambda _e: confirm_record())
    root.bind("<Control-Shift-L>", lambda _e: lock_weight())
    root.bind("<Escape>", lambda _e: cancel_item())

    capture_states = {"BARCODE_CAPTURED", "WAITING_FOR_LOAD", "WEIGHING", "WAITING_FOR_STABLE_WEIGHT", "WEIGHT_STABLE", "MANUAL_CONFIRM"}

    def refresh() -> None:
        s = runtime.snapshot()
        d = s["device"]
        du = unit_label(s.get("display_unit") or "g")
        status.config(text=s["operator_state"])
        weight.config(text=format_weight(float(s["weight_g"]), du))
        if s.get("weight_uncalibrated"):
            weight_hint.config(text="Uncalibrated raw — open Scale → Guided Calibration with a verified reference mass.")
        else:
            weight_hint.config(text="")
        locked = s.get("locked_weight_g")
        locked_weight.config(text=f"Locked: {format_weight(float(locked), du)}" if locked is not None else "")
        active_bc = s.get("active_barcode")
        if active_bc:
            active_barcode_banner.config(text=f"Active plant: {active_bc}")
            if barcode.get().strip() != str(active_bc) and s["state"] in capture_states:
                barcode.delete(0, "end")
                barcode.insert(0, str(active_bc))
        else:
            active_barcode_banner.config(text="Active plant: —")
        plants = s.get("recent_plants") or []
        log_lines = []
        for row in plants:
            stamp = str(row.get("created_at") or "")[-8:]
            bc = row.get("barcode_raw") or row.get("record_id") or "?"
            net = format_weight(float(row.get("net_g") or 0.0), du)
            cultivar = row.get("cultivar_normalized_name") or ""
            log_lines.append(f"{stamp}  {bc}  {net}  {cultivar}".rstrip())
        current = list(plant_log.get(0, "end"))
        if current != log_lines:
            plant_log.delete(0, "end")
            if not log_lines:
                plant_log.insert("end", "No plants saved in this run yet.")
            else:
                for line in log_lines:
                    plant_log.insert("end", line)
        metric_values["RUN"].config(text=s["run_id"] or "-")
        metric_values["CULTIVAR"].config(text=s["cultivar"] or "-")
        metric_values["OPERATOR"].config(text=s.get("operator_id") or "-")
        metric_values["CONTAINER"].config(text=s["container_id"] or "-")
        metric_values["GROSS"].config(text=format_weight(float(s["weight_g"]), du))
        metric_values["TARE"].config(text=format_weight(float(s["tare_g"]), du))
        metric_values["NET"].config(text=format_weight(float(s["net_g"]), du))
        metric_values["CAL ID"].config(text=s.get("calibration_id") or "-")
        active_strain.config(text=f"Active strain (sticky): {s['cultivar'] or '—'}")
        record = s["last_saved"]
        if record:
            cultivar = record.get("cultivar_normalized_name") or s.get("cultivar") or ""
            dup = record.get("duplicate_status")
            dup_note = " • duplicate barcode warning" if dup and dup != "none" else ""
            last_saved.config(
                text=(
                    f"Saved: {record.get('barcode_raw', record.get('record_id'))} — "
                    f"{format_weight(float(record['net_g']), du)} net ({cultivar}). Ready for next scan.{dup_note}"
                )
            )
        else:
            last_saved.config(text="No plant has been saved in this run yet. Scan, weigh, then Confirm & Record.")
        pending = int(s.get("pending_sync_count") or 0)
        pending_sync.config(
            text=f"CSV/XLSX sync pending for {pending} record(s). Run → Rebuild CSV from JSONL." if pending else ""
        )
        alice.config(text=s["alice_message"])
        mode = d.get("mode") or "none"
        if mode == "serial_simulator":
            mode_badge.config(text="SIMULATOR MODE - NO PHYSICAL SCALE", bg="#FFF1D6", fg="#8A4B08")
        elif d.get("connected"):
            mode_badge.config(text="PHYSICAL SERIAL - TESTING REQUIRED", bg="#FFF1D6", fg="#8A4B08")
        else:
            mode_badge.config(text="NO SCALE CONNECTED", bg="#EEF2F6", fg="#5C6975")
        if mode == "serial_simulator":
            footer_text = f"Simulator • display {du} • storage g • physical scale not in use"
        elif d.get("connected"):
            footer_text = f"Scale connected on {d.get('port') or 'selected port'} • display {du} • storage g"
        else:
            footer_text = f"Scale disconnected • display {du} • open Scale Setup"
        if not status_line.cget("text").startswith("Barcode accepted") and not status_line.cget("text").startswith("Saved"):
            status_line.config(text=footer_text)
        state = s["state"]
        ready = state == "WAITING_FOR_BARCODE"
        barcode.config(state="normal" if ready else "disabled")
        auto_id_btn.state(["!disabled"] if ready and not bool(s.get("barcode_required_for_capture", True)) else ["disabled"])
        focused = root.focus_get()
        if ready and focused not in {barcode, operator_note} and not isinstance(focused, (tk.Toplevel,)):
            try:
                if focused is None or str(focused).endswith("!barcode_input") is False:
                    if focused != barcode:
                        barcode.focus_set()
            except tk.TclError:
                barcode.focus_set()
        connected = bool(d.get("connected"))
        buttons["ZERO"].state(["!disabled"] if connected and state not in capture_states else ["disabled"])
        buttons["SET TARE"].state(["!disabled"] if connected and state in {"WAITING_FOR_BARCODE", "DEVICE_READY"} else ["disabled"])
        buttons["LOCK WEIGHT"].state(["!disabled"] if state == "WEIGHT_STABLE" else ["disabled"])
        buttons["CONFIRM & RECORD"].state(["!disabled"] if state == "MANUAL_CONFIRM" else ["disabled"])
        buttons["CANCEL"].state(["!disabled"] if state in capture_states else ["disabled"])
        root.after(100, refresh)

    def close() -> None:
        runtime.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    if simulator:
        definition = {
            "run_id": "SIMULATOR-TK-RUN",
            "operator_id": "SIMULATOR-OPERATOR",
            "facility_id": "BEST-BUDS",
            "station_id": "WEIGHT-STATION-01",
            "cultivars": [{"cultivar_id": "CV-001", "name": "Simulator Cultivar"}],
            "capture_mode": runtime.controller.settings.capture_mode,
            "unit": "g",
            "container_id": "DEFAULT",
            "tare_g": 0.0,
            "maximum_capacity_g": 10000.0,
        }
        runtime.dispatch("run.new", {"definition": definition, "data_root": runtime.controller.settings.data_root, "simulator": True})
        runtime.connect_simulator()
        runtime.simulator_set_weight(1250.0)
    refresh()
    if smoke:
        root.after(1500, close)
    root.mainloop()
    return 0
