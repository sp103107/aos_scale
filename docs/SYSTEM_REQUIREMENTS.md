# System requirements

Operator and developer requirements for Best Buds Cultivator Weight Station (`aos_scale`).

## Primary platform (packaged Windows app)

| Item | Requirement |
|------|-------------|
| OS | **Windows 10 or Windows 11**, 64-bit |
| CPU | x64 (Intel/AMD) |
| RAM | **4 GB** minimum (8 GB recommended) |
| Display | **1024×720** or larger |
| Disk | ~500 MB for the installed application |
| Python | **Not required** when using the PyInstaller build / Setup installer |
| Privileges | Normal user; administrator is **not** required for normal operation |
| Network | **Not required** for local weighing, records, or reports |

## Hardware (physical scale)

| Item | Requirement |
|------|-------------|
| Scale interface | USB serial (UNO-class board + HX711 load-cell amp running Best Buds protocol firmware) |
| Port | Free COM port (close Arduino Serial Monitor and other apps that hold the port) |
| Baud | **115200** default (9600 supported for compatibility) |
| Barcode | Optional USB keyboard-wedge / HID scanner (types into the barcode field + Enter) |
| Calibration | Verified reference mass recommended before trusting displayed grams |

## Source / developer install (any supported OS)

| Item | Requirement |
|------|-------------|
| Python | **3.11+** (3.11 or 3.12 recommended) |
| Tools | `pip`, `venv` |
| Desktop UI | PySide6 (`pip install -e ".[desktop,serial]"`) |
| Optional | Tk fallback on Linux if PySide6 is unavailable |

Windows source launch: `launch_best_buds.bat`  
Linux source launch: `./launch_best_buds.sh`

## Secondary platform (Linux)

Linux is supported for **source** runs and packaging experiments. There is no first-class Linux GUI installer in this pass. Use Python 3.11+ and the shell launchers.

## What is not claimed

- No legal-for-trade / NTEP certification
- No production metrology guarantee without station-specific calibration evidence
- Packaged Windows builds in this release are **not Authenticode-signed** (SmartScreen may warn until reputation or signing is added)

## Related docs

- [WINDOWS_BUILD.md](WINDOWS_BUILD.md) — how to build the Windows package
- [CALIBRATION_RUNBOOK.md](CALIBRATION_RUNBOOK.md) — guided calibration
- [RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md) — bring-up RC honesty notes
- [COMMERCIAL.md](../COMMERCIAL.md) — commercial licensing
