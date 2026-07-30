from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "packaging/windows/BestBudsWeightStation.spec",
    "packaging/windows/build_windows.ps1",
    "packaging/windows/verify_windows.ps1",
    "packaging/windows/install_windows.ps1",
    "packaging/windows/uninstall_windows.ps1",
    "packaging/windows/launcher_config.json",
    "packaging/windows/README.md",
    "launch_best_buds.bat",
    "launch_best_buds.ps1",
]


def main() -> int:
    failures = [path for path in REQUIRED if not (ROOT / path).is_file()]
    config_path = ROOT / "packaging/windows/launcher_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    if config.get("primary_frontend") != "PySide6":
        failures.append("launcher_config.primary_frontend")
    if config.get("normal_operation_requires_administrator") is not False:
        failures.append("launcher_config.normal_operation_requires_administrator")
    build = (ROOT / "packaging/windows/build_windows.ps1").read_text(encoding="utf-8") if (ROOT / "packaging/windows/build_windows.ps1").exists() else ""
    for marker in ("PyInstaller", "pytest", "verify_windows.ps1", ".[desktop,serial,dev]"):
        if marker not in build:
            failures.append(f"build_windows_missing:{marker}")
    result = {
        "status": "FAIL" if failures else "PASS",
        "truth_class": "WINDOWS_SOURCE_PRESENT" if not failures else "FAIL",
        "native_windows_execution": "NOT_RUN",
        "failures": failures,
        "required_files": REQUIRED,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
