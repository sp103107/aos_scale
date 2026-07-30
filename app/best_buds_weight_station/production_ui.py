from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .application_controller import ApplicationController
from .operator_runtime import OperatorRuntime
from .operator_surface import ROUTINE_ACTION_LAYOUT
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
    "WEIGHT_STABLE": "Weight stable",
    "MANUAL_CONFIRM": "Weight stable - confirm record",
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


def _launch_tk(runtime: OperatorRuntime, *, simulator: bool, smoke: bool) -> int:
    """Secondary fallback UI. It shares the same runtime and truth gates as PySide6."""

    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk

    root = tk.Tk()
    root.title(f"Best Buds Cultivator Weight Station v{__version__} - Tk fallback")
    root.geometry("1120x850")
    root.minsize(1024, 760)
    root.configure(bg="#F5F7FA")

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Card.TFrame", background="#FFFFFF", relief="solid", borderwidth=1)
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
    for idx, key in enumerate(("RUN", "CULTIVAR", "CONTAINER", "GROSS", "TARE", "NET")):
        col = idx % 3
        row = (idx // 3) * 2
        tk.Label(metrics, text=key.title(), font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#5C6975").grid(row=row, column=col, sticky="w", padx=14, pady=(8, 0))
        value = tk.Label(metrics, text="-", font=("Segoe UI", 15, "bold"), bg="#FFFFFF", fg="#17212B", anchor="w")
        value.grid(row=row + 1, column=col, sticky="ew", padx=14, pady=(0, 8))
        metric_values[key] = value
    for col in range(3):
        metrics.grid_columnconfigure(col, weight=1)

    last_saved = tk.Label(shell, text="No plant has been saved in this run.", font=("Segoe UI", 11, "bold"), bg="#E7F6EC", fg="#176B2C", anchor="w", padx=12, pady=8)
    last_saved.pack(fill="x")

    alice_card = tk.Frame(shell, bg="#FFFFFF", highlightbackground="#CBD4DD", highlightthickness=1)
    alice_card.pack(fill="x", pady=8)
    tk.Label(alice_card, text="Alice - next step", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#5C6975").pack(anchor="w", padx=12, pady=(8, 2))
    alice = tk.Label(alice_card, text="Start a new run or resume the last run.", justify="left", anchor="w", wraplength=1020, font=("Segoe UI", 13, "bold"), bg="#FFFFFF", fg="#17212B", padx=12, pady=8)
    alice.pack(fill="x")

    barcode_card = tk.Frame(shell, bg="#FFFFFF", highlightbackground="#CBD4DD", highlightthickness=1)
    barcode_card.pack(fill="x", pady=(0, 8))
    tk.Label(
        barcode_card,
        text="PLANT OR CONTAINER BARCODE",
        font=("Segoe UI", 9, "bold"),
        bg="#FFFFFF",
        fg="#5C6975",
    ).pack(anchor="w", padx=12, pady=(8, 2))
    barcode = tk.Entry(
        barcode_card,
        font=("Segoe UI", 18),
        relief="solid",
        bd=1,
        name="barcode_input",
    )
    barcode.pack(fill="x", padx=12, ipady=8)
    barcode_hint = tk.Label(
        barcode_card,
        text="Scan or type the barcode, then press Enter.",
        font=("Segoe UI", 9),
        bg="#FFFFFF",
        fg="#5C6975",
        anchor="w",
    )
    barcode_hint.pack(fill="x", padx=12, pady=(4, 8))

    controls = tk.Frame(shell, bg="#F5F7FA")
    controls.pack(fill="x")
    status_line = tk.Label(shell, text="Scale disconnected", font=("Segoe UI", 9), bg="#F5F7FA", fg="#5C6975", anchor="w")
    status_line.pack(fill="x", pady=(8, 0))

    def show_result(result: dict[str, Any]) -> None:
        if result.get("status") in {"failed", "blocked"}:
            messagebox.showwarning("Action not completed", result.get("message", "Action failed"), parent=root)

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
            show_result(runtime.zero_scale())
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
                value = simpledialog.askfloat("Known Tare", "Tare in grams", minvalue=0.0, maxvalue=10000.0, parent=root)
                if value is None:
                    return
                result = runtime.set_known_tare(container, value)
            show_result(result)
        except Exception as exc:
            messagebox.showwarning("Tare failed", str(exc), parent=root)

    def calibrate() -> None:
        win = tk.Toplevel(root)
        win.title("Guided Calibration")
        win.geometry("820x620")
        reference = tk.DoubleVar(value=2000.0)
        steps = (
            "Before you start: Connect the scale, start/resume a run, empty the pan, enter a verified reference mass. "
            "Not legal-for-trade.\n"
            "1 Start — begin maintenance calibration; do not scan plants mid-flow.\n"
            "2 Zero samples — pan empty; wait for live readings; capture raw zero samples.\n"
            "3 Loaded samples — place the reference mass; reference (g) must match; capture raw loaded samples.\n"
            "4 Test — keep/re-place reference mass; review proposed factor and error %.\n"
            "5 Accept — second confirmation writes SET_CAL; live weight should near the reference in grams.\n"
            "After — empty pan → ZERO → optional SET TARE → normal scanning."
        )
        tk.Label(win, text=steps, font=("Segoe UI", 10), justify="left", wraplength=780, anchor="w").pack(padx=10, pady=8, fill="x")
        tk.Label(win, text="Maintenance workflow - not legal-for-trade certification.", font=("Segoe UI", 11, "bold"), wraplength=760, fg="#8A4B08").pack(padx=10, pady=4)
        tk.Entry(win, textvariable=reference, font=("Segoe UI", 12)).pack(fill="x", padx=10)
        output = tk.Text(win, height=18, width=92, font=("Consolas", 9))
        output.pack(fill="both", expand=True, padx=10, pady=10)

        def run_step(fn) -> None:
            try:
                result = fn()
                output.delete("1.0", "end")
                output.insert("1.0", json.dumps(result, indent=2, sort_keys=True, default=str))
            except Exception as exc:
                messagebox.showwarning("Calibration step blocked", str(exc), parent=win)

        row = tk.Frame(win)
        row.pack(fill="x", padx=8, pady=6)
        for text, fn in [
            ("1 Start", runtime.start_calibration),
            ("2 Zero samples", runtime.add_calibration_zero_samples),
            ("3 Loaded samples", lambda: runtime.add_calibration_loaded_samples(reference.get())),
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

    def submit(event=None) -> None:
        value = barcode.get().strip()
        if not value:
            return
        result = runtime.submit_barcode(value)
        show_result(result)
        if result.get("status") not in {"failed", "blocked"}:
            barcode.delete(0, "end")

    def export_report() -> None:
        path = filedialog.askdirectory(title="Export Report", initialdir=str(runtime.paths.exports), parent=root)
        if path:
            show_result(runtime.dispatch("report.export", {"destination": path}))

    def finish() -> None:
        if messagebox.askyesno("Finish Run", "Finish the current run? Committed records remain immutable.", parent=root):
            show_result(runtime.dispatch("run.finish"))

    action_callbacks = {
        "start_resume": start_resume,
        "connect_scale": scale_setup,
        "zero_scale": zero,
        "set_tare": tare,
        "confirm_record": lambda: show_result(runtime.dispatch("capture.confirm")),
        "cancel_item": lambda: show_result(runtime.dispatch("capture.cancel")),
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

    menubar = tk.Menu(root)
    run_menu = tk.Menu(menubar, tearoff=0)
    run_menu.add_command(label="New Run", command=new_run)
    run_menu.add_command(label="Resume Last Run", command=lambda: show_result(runtime.dispatch("run.resume")))
    run_menu.add_command(label="Load Run...", command=load_run)
    run_menu.add_separator()
    run_menu.add_command(label="Recover Run", command=lambda: show_result(runtime.dispatch("state.recover")))
    run_menu.add_command(label="Export Report...", command=export_report)
    run_menu.add_command(label="Finish Run", command=finish)
    menubar.add_cascade(label="Run", menu=run_menu)
    scale_menu = tk.Menu(menubar, tearoff=0)
    scale_menu.add_command(label="Scale Setup and Connection...", command=scale_setup)
    scale_menu.add_command(label="Zero Scale", command=zero)
    scale_menu.add_command(label="Container Tare...", command=tare)
    scale_menu.add_command(label="Guided Calibration...", command=calibrate)
    scale_menu.add_separator()
    scale_menu.add_command(label="Diagnostics", command=diagnostics)
    menubar.add_cascade(label="Scale", menu=scale_menu)
    root.config(menu=menubar)

    barcode.bind("<Return>", submit)
    root.bind("<Control-n>", lambda _e: new_run())
    root.bind("<Control-l>", lambda _e: load_run())
    root.bind("<Control-r>", lambda _e: start_resume())
    root.bind("<Control-k>", lambda _e: scale_setup())
    root.bind("<Control-z>", lambda _e: zero())
    root.bind("<Control-t>", lambda _e: tare())
    root.bind("<Escape>", lambda _e: show_result(runtime.dispatch("capture.cancel")))

    capture_states = {"BARCODE_CAPTURED", "WAITING_FOR_LOAD", "WEIGHING", "WAITING_FOR_STABLE_WEIGHT", "WEIGHT_STABLE", "MANUAL_CONFIRM"}

    def refresh() -> None:
        s = runtime.snapshot()
        d = s["device"]
        status.config(text=s["operator_state"])
        weight.config(text=f"{s['weight_g']:,.3f} g")
        if s.get("weight_uncalibrated"):
            weight_hint.config(text="Uncalibrated raw — open Scale → Guided Calibration with a verified reference mass.")
        else:
            weight_hint.config(text="")
        metric_values["RUN"].config(text=s["run_id"] or "-")
        metric_values["CULTIVAR"].config(text=s["cultivar"] or "-")
        metric_values["CONTAINER"].config(text=s["container_id"] or "-")
        metric_values["GROSS"].config(text=f"{s['weight_g']:,.3f} g")
        metric_values["TARE"].config(text=f"{s['tare_g']:,.3f} g")
        metric_values["NET"].config(text=f"{s['net_g']:,.3f} g")
        record = s["last_saved"]
        last_saved.config(text=f"Saved safely: {record['record_id']} - {record['net_g']:.3f} g" if record else "No plant has been saved in this run.")
        alice.config(text=s["alice_message"])
        mode = d.get("mode") or "none"
        if mode == "serial_simulator":
            mode_badge.config(text="SIMULATOR MODE - NO PHYSICAL SCALE", bg="#FFF1D6", fg="#8A4B08")
        elif d.get("connected"):
            mode_badge.config(text="PHYSICAL SERIAL - TESTING REQUIRED", bg="#FFF1D6", fg="#8A4B08")
        else:
            mode_badge.config(text="NO SCALE CONNECTED", bg="#EEF2F6", fg="#5C6975")
        if mode == "serial_simulator":
            footer_text = "Simulator connected • live readings active • physical scale not in use"
        elif d.get("connected"):
            footer_text = f"Scale connected on {d.get('port') or 'selected port'} • readings {'active' if s['worker_running'] else 'stopped'} • physical testing evidence pending"
        else:
            footer_text = "Scale disconnected • open Scale Setup to connect"
        status_line.config(text=footer_text)
        state = s["state"]
        ready = state == "WAITING_FOR_BARCODE"
        barcode.config(state="normal" if ready else "disabled")
        if ready and root.focus_get() is not barcode:
            barcode.focus_set()
        connected = bool(d.get("connected"))
        buttons["ZERO"].state(["!disabled"] if connected and state in {"WAITING_FOR_BARCODE", "DEVICE_READY"} else ["disabled"])
        buttons["SET TARE"].state(["!disabled"] if connected and state in {"WAITING_FOR_BARCODE", "DEVICE_READY"} else ["disabled"])
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
