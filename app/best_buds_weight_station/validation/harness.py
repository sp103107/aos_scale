from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .capability_probe import probe
from .command_runner import run_command
from .drift import inspect as inspect_drift, repair as repair_drift
from .evidence import write_receipt
from .graph import ValidationGraph
from .models import HarnessReport, LaneResult
from .profiles import load_profile


class ValidationHarness:
    def __init__(self, repo_root: Path | None = None, *, persist_receipts: bool = True):
        self.persist_receipts = persist_receipts
        self.repo_root = (repo_root or Path(__file__).resolve().parents[3]).resolve()
        self.version = (self.repo_root / "VERSION").read_text().strip()
        self.graph = ValidationGraph(self.repo_root)

    def inspect(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "capabilities": probe(self.repo_root),
            "drift": inspect_drift(self.repo_root),
            "graph": self.graph.data,
        }

    def prepare(self, profile_name: str) -> HarnessReport:
        profile = load_profile(self.repo_root, profile_name)
        before = inspect_drift(self.repo_root)
        repairs = repair_drift(self.repo_root, profile)
        after = inspect_drift(self.repo_root)
        unresolved = [x for x in after["issues"] if x.get("severity", "error") == "error"]
        if not after["issues"]:
            status = "PASS"
        elif profile_name in {"development", "prehardware", "operator-ready"} and not unresolved:
            status = "PASS_WITH_WARNINGS"
        elif profile_name == "development":
            status = "PASS_WITH_WARNINGS"
        else:
            status = "FAIL"
        return HarnessReport(
            profile_name,
            status,
            self.version,
            [],
            warnings=[x["code"] for x in after["issues"]],
            repairs=repairs,
        )

    def _blocked_by(self, lane: str, prior: dict[str, dict[str, Any]]) -> list[str]:
        accepted = {"PASS", "PASS_WITH_WARNINGS"}
        return [
            req
            for req in self.graph.prerequisites(lane)
            if prior.get(req, {}).get("status") not in accepted
        ]

    def run_lane(
        self,
        lane: str,
        profile_name: str = "integration",
        options: dict[str, Any] | None = None,
        prior: dict[str, dict[str, Any]] | None = None,
    ) -> LaneResult:
        options = options or {}
        prior = prior or {}
        blockers = self._blocked_by(lane, prior)
        if blockers:
            result = LaneResult(
                lane,
                "BLOCKED",
                "PREREQUISITE_NOT_PASSED",
                profile_name,
                blocking_gates=blockers,
                next_action=f"Pass prerequisites: {', '.join(blockers)}",
            )
            self._persist(result)
            return result
        method = getattr(self, f"_lane_{lane.replace('-', '_')}", None)
        if method is None:
            raise ValueError(f"unsupported lane: {lane}")
        result = method(profile_name, options)
        self._persist(result)
        return result

    def _persist(self, result: LaneResult) -> None:
        if not self.persist_receipts:
            return
        path = self.repo_root / f"validation/receipts/{result.lane}.latest.json"
        result.evidence_refs.append(path.relative_to(self.repo_root).as_posix())
        write_receipt(self.repo_root, result.lane, result.to_dict())

    def _lane_repository_inspection(self, profile: str, options: dict[str, Any]) -> LaneResult:
        data = self.inspect()
        return LaneResult("repository-inspection", "PASS", "REPOSITORY_INSPECTED", profile, data=data)

    def _lane_development_hygiene(self, profile: str, options: dict[str, Any]) -> LaneResult:
        report = self.prepare(profile)
        status = "PASS" if report.status in {"PASS", "PASS_WITH_WARNINGS"} else "FAIL"
        return LaneResult(
            "development-hygiene",
            status,
            "SAFE_DRIFT_PREPARED" if status == "PASS" else "UNRESOLVED_CURRENT_DRIFT",
            profile,
            warnings=report.warnings,
            data=report.to_dict(),
        )

    def _lane_software(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [
            run_command([python, "-m", "pytest", "-q", "-p", "no:cacheprovider"], self.repo_root, 900),
            run_command([python, "scripts/validate_repo.py"], self.repo_root, 900),
        ]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "software",
            "FAIL" if failed else "PASS",
            "SOFTWARE_VALIDATION_FAILED" if failed else "SOFTWARE_VALIDATION_PASSED",
            profile,
            commands_executed=commands,
        )

    def _lane_launchers(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [run_command([python, "scripts/validate_launchers.py"], self.repo_root, 300)]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "launchers",
            "FAIL" if failed else "PASS",
            "LAUNCHER_VALIDATION_FAILED" if failed else "LAUNCHER_VALIDATION_PASSED",
            profile,
            commands_executed=commands,
            data={"windows_launchers": "SOURCE_VALIDATED", "linux_launchers": "RUNTIME_VALIDATED" if not failed else "FAIL"},
        )

    def _lane_agent_entrypoint(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [
            run_command([python, "-m", "best_buds_weight_station.bootstrap", "--version"], self.repo_root, 120),
            run_command([python, "-m", "best_buds_weight_station.bootstrap", "--help"], self.repo_root, 120),
            run_command([python, "-m", "best_buds_weight_station.validation", "graph"], self.repo_root, 120),
        ]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "agent-entrypoint",
            "FAIL" if failed else "PASS",
            "AGENT_ENTRYPOINT_FAILED" if failed else "AGENT_ENTRYPOINT_PASSED",
            profile,
            commands_executed=commands,
            data={
                "module_entrypoint": "python -m best_buds_weight_station.bootstrap",
                "console_entrypoint": "best-buds-weight-station-bootstrap",
            },
        )

    def _lane_software_dry_run(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [
            run_command([python, "-m", "best_buds_weight_station.validation.dry_run"], self.repo_root, 300),
            run_command([python, "scripts/run_self_test.py"], self.repo_root, 300),
            run_command([python, "scripts/run_v018_operator_acceptance.py"], self.repo_root, 300),
            run_command([python, "-m", "best_buds_weight_station", "--self-test"], self.repo_root, 300),
        ]
        failed = [c for c in commands if c["exit_code"]]
        parsed: dict[str, Any] = {}
        if commands and not commands[0]["exit_code"]:
            try:
                parsed = json.loads(commands[0]["stdout"])
            except json.JSONDecodeError:
                parsed = {"parse_warning": "dry-run stdout was not JSON"}
        return LaneResult(
            "software-dry-run",
            "FAIL" if failed else "PASS",
            "SOFTWARE_DRY_RUN_FAILED" if failed else "SOFTWARE_DRY_RUN_PASSED",
            profile,
            commands_executed=commands,
            data=parsed,
        )

    def _lane_recovery_matrix(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [
            run_command(
                [
                    python,
                    "-m",
                    "pytest",
                    "-q",
                    "-p",
                    "no:cacheprovider",
                    "tests/test_storage_crash_safety.py",
                    "tests/test_run_management.py",
                ],
                self.repo_root,
                600,
            )
        ]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "recovery-matrix",
            "FAIL" if failed else "PASS",
            "RECOVERY_MATRIX_FAILED" if failed else "RECOVERY_MATRIX_PASSED",
            profile,
            commands_executed=commands,
        )

    def _lane_operator_runtime(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [
            run_command([python, "scripts/run_v018_operator_acceptance.py"], self.repo_root, 600),
            run_command([python, "scripts/validate_frontend_runtime_truth.py"], self.repo_root, 300),
        ]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "operator-runtime",
            "FAIL" if failed else "PASS",
            "OPERATOR_RUNTIME_FAILED" if failed else "OPERATOR_RUNTIME_PASSED",
            profile,
            commands_executed=commands,
            data={"automatic": "SIMULATOR_PASS", "manual": "SIMULATOR_PASS", "physical_device": "NOT_RUN"},
        )

    def _lane_scripted_device(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [
            run_command([python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_operator_runtime.py", "tests/test_device_service.py"], self.repo_root, 600)
        ]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "scripted-device",
            "FAIL" if failed else "PASS",
            "SCRIPTED_DEVICE_FAILED" if failed else "SCRIPTED_DEVICE_PASSED",
            profile,
            commands_executed=commands,
            data={"truth_class": "UNIT_TEST_PASS", "physical_device_pass": False},
        )

    def _lane_frontend_smoke(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [
            run_command([python, "scripts/validate_frontend_runtime_truth.py"], self.repo_root, 300),
            run_command([python, "scripts/validate_frontend_polish_v018.py"], self.repo_root, 300),
        ]
        evidence_path = self.repo_root / "reports/frontend_render_evidence.v0.1.8.json"
        evidence_valid = False
        evidence_data: dict[str, Any] = {}
        if evidence_path.exists():
            try:
                import hashlib
                evidence_data = json.loads(evidence_path.read_text(encoding="utf-8"))
                artifact_rel = evidence_data["artifact_paths"][0]
                artifact = self.repo_root / artifact_rel
                expected = evidence_data["artifact_hashes"][artifact_rel]
                evidence_valid = (
                    evidence_data.get("status") == "PASS"
                    and artifact.is_file()
                    and hashlib.sha256(artifact.read_bytes()).hexdigest() == expected
                )
            except Exception:
                evidence_valid = False
        failed = [c for c in commands if c["exit_code"]] or ([] if evidence_valid else [{"evidence": "frontend render receipt invalid"}])
        return LaneResult(
            "frontend-smoke",
            "FAIL" if failed else "PASS",
            "FRONTEND_RENDER_EVIDENCE_INVALID" if failed else "FRONTEND_RENDER_EVIDENCE_VALIDATED",
            profile,
            commands_executed=commands,
            data={
                "tk_runtime": "PASS" if evidence_valid else "FAIL",
                "render_evidence": evidence_path.relative_to(self.repo_root).as_posix(),
                "pyside6_runtime": "NOT_RUN_DEPENDENCY_UNAVAILABLE",
                "native_windows_runtime": "NOT_RUN",
            },
        )

    def _lane_windows_packaging_source(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [run_command([python, "scripts/validate_windows_source.py"], self.repo_root, 300)]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "windows-packaging-source",
            "FAIL" if failed else "PASS",
            "WINDOWS_SOURCE_VALIDATION_FAILED" if failed else "WINDOWS_SOURCE_VALIDATED",
            profile,
            commands_executed=commands,
            warnings=[] if failed else ["WINDOWS_NATIVE_RUNTIME_NOT_RUN"],
            data={"truth_class": "WINDOWS_SOURCE_PRESENT", "native_runtime": "NOT_RUN"},
        )

    def _lane_linux_parity(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        commands = [
            run_command(["sh", "-n", "launch_best_buds.sh"], self.repo_root, 120),
            run_command(["sh", "-n", "launch_simulator.sh"], self.repo_root, 120),
            run_command([python, "scripts/launcher.py", "simulator", "--direct", "--dry-run", "--ui-smoke"], self.repo_root, 120),
        ]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "linux-parity",
            "FAIL" if failed else "PASS",
            "LINUX_PARITY_FAILED" if failed else "LINUX_PARITY_PASSED",
            profile,
            commands_executed=commands,
            data={"linux_launcher": "PASS" if not failed else "FAIL", "tk_fallback": "SOURCE_PRESENT", "pyside_primary": "SOURCE_PRESENT"},
        )

    def _lane_packaging_preflight(self, profile: str, options: dict[str, Any]) -> LaneResult:
        python = shutil.which("python3") or "python3"
        with tempfile.TemporaryDirectory(prefix="bbws-install-preflight-") as td:
            target = Path(td) / "site"
            source = Path(td) / "source"
            shutil.copytree(
                self.repo_root,
                source,
                ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "*.pyc", "*.egg-info", "build", ".venv"),
            )
            commands = [
                run_command(
                    [python, "-m", "pip", "install", "--no-deps", "--no-build-isolation", "--no-index", "--disable-pip-version-check", "--target", str(target), "."],
                    source,
                    600,
                ),
                run_command(
                    [
                        python,
                        "-c",
                        (
                            "import sys; sys.path.insert(0, r'%s'); "
                            "from best_buds_weight_station.version import __version__; "
                            "from best_buds_weight_station.bootstrap import parser; "
                            "assert __version__ == '%s'; parser(); print(__version__)"
                        ) % (target, self.version),
                    ],
                    self.repo_root,
                    120,
                ),
            ]
        failed = [c for c in commands if c["exit_code"]]
        return LaneResult(
            "packaging-preflight",
            "FAIL" if failed else "PASS",
            "PACKAGING_PREFLIGHT_FAILED" if failed else "PACKAGING_PREFLIGHT_PASSED",
            profile,
            commands_executed=commands,
            data={"isolated_install": "PASS" if not failed else "FAIL"},
        )

    def _lane_firmware(self, profile: str, options: dict[str, Any]) -> LaneResult:
        caps = probe(self.repo_root)
        tool = caps["tools"]["arduino_cli"]
        if not tool["available"]:
            return LaneResult(
                "firmware",
                "BLOCKED",
                "ARDUINO_CLI_UNAVAILABLE",
                profile,
                next_action="Install arduino-cli and the Arduino AVR core, then rerun the firmware lane.",
                data={"capability": tool},
            )
        fqbn = options.get("fqbn", "arduino:avr:uno")
        sketch = str(self.repo_root / "firmware/elegoo_uno_r3_hx711")
        c = run_command([tool["path"], "compile", "--fqbn", fqbn, sketch], self.repo_root, 600)
        if c["exit_code"]:
            return LaneResult("firmware", "FAIL", "FIRMWARE_COMPILE_FAILED", profile, commands_executed=[c])
        port = options.get("port")
        if not port:
            return LaneResult(
                "firmware",
                "WAITING_FOR_EXTERNAL_ACTION",
                "FIRMWARE_COMPILED_UPLOAD_PORT_REQUIRED",
                profile,
                commands_executed=[c],
                required_action={"type": "CONNECT_CONTROLLER_AND_PROVIDE_PORT"},
                next_action="Rerun with --port <serial-port> to upload.",
            )
        u = run_command([tool["path"], "upload", "-p", port, "--fqbn", fqbn, sketch], self.repo_root, 600)
        return LaneResult(
            "firmware",
            "PASS" if not u["exit_code"] else "FAIL",
            "FIRMWARE_COMPILE_UPLOAD_PASSED" if not u["exit_code"] else "FIRMWARE_UPLOAD_FAILED",
            profile,
            commands_executed=[c, u],
            data={"port": port, "fqbn": fqbn},
        )

    def _physical_device(self, options: dict[str, Any]):
        port = options.get("port")
        if not port:
            return None, LaneResult(
                "serial",
                "WAITING_FOR_EXTERNAL_ACTION",
                "SERIAL_PORT_REQUIRED",
                "integration",
                required_action={"type": "CONNECT_CONTROLLER_AND_PROVIDE_PORT"},
                next_action="Rerun with --port <serial-port>.",
            )
        from ..device_service import DeviceMode, DeviceService

        service = DeviceService(mode=DeviceMode.PHYSICAL_SERIAL)
        service.connect(port)
        return service, None

    def _lane_serial(self, profile: str, options: dict[str, Any]) -> LaneResult:
        service, blocked = self._physical_device(options)
        if blocked:
            blocked.profile = profile
            return blocked
        try:
            ping = service.ping()
            status = service.read_status()
            return LaneResult(
                "serial",
                "PASS",
                "PHYSICAL_SERIAL_PROTOCOL_PASSED",
                profile,
                data={"port": options["port"], "ping": ping, "status": status, "device": service.status.to_dict()},
            )
        except Exception as exc:
            return LaneResult(
                "serial",
                "FAIL",
                "PHYSICAL_SERIAL_PROTOCOL_FAILED",
                profile,
                data={"error": f"{type(exc).__name__}: {exc}", "port": options.get("port")},
            )
        finally:
            if service:
                service.disconnect(silent=True)

    def _lane_zero_tare(self, profile: str, options: dict[str, Any]) -> LaneResult:
        port = options.get("port")
        if not port:
            return LaneResult(
                "zero-tare",
                "WAITING_FOR_EXTERNAL_ACTION",
                "ZERO_CONDITION_AND_PORT_REQUIRED",
                profile,
                required_action={"type": "REMOVE_LOAD_AND_PROVIDE_PORT"},
                next_action="Remove all load and rerun with --port.",
            )
        from ..device_service import DeviceMode, DeviceService

        service = DeviceService(mode=DeviceMode.PHYSICAL_SERIAL)
        try:
            service.connect(port)
            ack = service.tare()
            samples = [service.read_weight() for _ in range(int(options.get("samples", 5)))]
            values = [float(x["grams"]) for x in samples]
            tolerance = float(options.get("zero_tolerance_g", 2.0))
            stable = max(abs(x) for x in values) <= tolerance
            return LaneResult(
                "zero-tare",
                "PASS" if stable else "FAIL",
                "PHYSICAL_ZERO_PASSED" if stable else "ZERO_STABILITY_OUT_OF_TOLERANCE",
                profile,
                data={"ack": ack, "samples_g": values, "tolerance_g": tolerance},
            )
        except Exception as exc:
            return LaneResult(
                "zero-tare",
                "FAIL",
                "ZERO_TARE_EXECUTION_FAILED",
                profile,
                data={"error": f"{type(exc).__name__}: {exc}"},
            )
        finally:
            service.disconnect(silent=True)

    def _lane_calibration(self, profile: str, options: dict[str, Any]) -> LaneResult:
        ref = options.get("reference_weight_g")
        port = options.get("port")
        if not port or not ref:
            return LaneResult(
                "calibration",
                "WAITING_FOR_EXTERNAL_ACTION",
                "REFERENCE_WEIGHT_AND_PORT_REQUIRED",
                profile,
                required_action={"type": "APPLY_REFERENCE_WEIGHT", "reference_weight_g": ref},
                next_action="Provide --port and --reference-weight-g after applying the known mass.",
            )
        return LaneResult(
            "calibration",
            "WAITING_FOR_EXTERNAL_ACTION",
            "CALIBRATION_REQUIRES_PHYSICAL_SAMPLE_SEQUENCE",
            profile,
            required_action={"type": "RUN_CALIBRATION_SEQUENCE", "port": port, "reference_weight_g": float(ref)},
            next_action="Use the application calibration service or Cursor-controlled sequence, then attach the generated calibration receipt.",
        )

    def _lane_physical_loop(self, profile: str, options: dict[str, Any]) -> LaneResult:
        if not options.get("port"):
            return LaneResult(
                "physical-loop",
                "WAITING_FOR_EXTERNAL_ACTION",
                "PHYSICAL_LOOP_PORT_REQUIRED",
                profile,
                required_action={"type": "CONNECT_SCALE_AND_PREPARE_TEST_LOAD"},
                next_action="Connect the scale and rerun with --port plus run/barcode inputs.",
            )
        return LaneResult(
            "physical-loop",
            "WAITING_FOR_EXTERNAL_ACTION",
            "PHYSICAL_LOAD_AND_BARCODE_REQUIRED",
            profile,
            required_action={"type": "SCAN_BARCODE_AND_APPLY_TEST_LOAD", "barcode": options.get("barcode")},
            next_action="Run the production application through one physical commit and provide its receipt path.",
        )

    def _lane_release_packaging(self, profile: str, options: dict[str, Any]) -> LaneResult:
        return LaneResult(
            "release-packaging",
            "BLOCKED",
            "PHYSICAL_EVIDENCE_NOT_CLOSED",
            profile,
            blocking_gates=["calibration", "physical-loop"],
            next_action="Complete physical calibration and end-to-end loop before release packaging.",
        )

    def evaluate(self, profile_name: str, receipt_dir: Path | None = None) -> HarnessReport:
        profile = load_profile(self.repo_root, profile_name)
        receipt_dir = receipt_dir or self.repo_root / "validation/receipts"
        lanes = []
        for lane in self.graph.ordered_lanes():
            p = receipt_dir / f"{lane}.latest.json"
            lanes.append(json.loads(p.read_text()) if p.exists() else {"lane": lane, "status": "NOT_RUN", "reason_code": "NO_RECEIPT"})
        hard = set(profile.get("hard_gate_lanes", []))
        failures = [x for x in lanes if x["lane"] in hard and x["status"] not in {"PASS", "PASS_WITH_WARNINGS"}]
        status = "PASS" if not failures else "FAIL"
        return HarnessReport(
            profile_name,
            status,
            self.version,
            lanes,
            warnings=[f"{x['lane']}={x['status']}" for x in failures],
        )
