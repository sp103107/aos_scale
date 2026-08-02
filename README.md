# Best Buds Cultivator Weight Station (`aos_scale`)

**Version:** `0.1.9`  
**Public repo:** [https://github.com/sp103107/aos_scale](https://github.com/sp103107/aos_scale)  
**Current freeze:** USB bring-up release candidate — see [docs/RELEASE_CANDIDATE.md](docs/RELEASE_CANDIDATE.md)

A Windows-first, local-first, barcode-driven cultivation weighing station. PySide6 is the primary Windows frontend and shared Linux frontend. Tk is the secondary Linux fallback. The PC remains authoritative for run setup, append-only records, crash recovery, reports, Alice guidance, and terminal receipt validation.

## License

- **Personal / noncommercial:** [PolyForm Noncommercial 1.0.0](LICENSE)
- **Commercial / paid:** [COMMERCIAL.md](COMMERCIAL.md)

Third-party dependencies keep their own licenses.

## Honest status

USB connect, live readings, Zero/Tare UX, and Guided Calibration are in place for bring-up. **Displayed grams are not trustworthy until calibration with a verified reference mass.** This project does **not** claim production-ready or legal-for-trade status.

## System requirements

See [docs/SYSTEM_REQUIREMENTS.md](docs/SYSTEM_REQUIREMENTS.md) for OS, hardware, and packaged-app requirements.

## Windows packaged install

On a Windows build host:

```powershell
.\packaging\windows\build_windows.ps1
```

Artifacts land in `dist\windows\` (zip + Setup `.exe` when Inno Setup is installed). Zip-only fallback:

```powershell
.\packaging\windows\install_windows.ps1
```

## Routine operator screen

The routine weighing screen exposes seven actions only:

```text
START / RESUME
CONNECT SCALE
ZERO
SET TARE
CONFIRM & RECORD
CANCEL
FINISH RUN
```

The current screen includes a labeled barcode capture card, a large weight display, gross/tare/net values, cultivar and container context, last-safe-save confirmation, Alice's next action, and an explicit simulator or physical-testing badge. Calibration, diagnostics, recovery, exports, and serial engineering details remain in menus or dedicated dialogs.

Each saved plant updates session `records.csv` / `records.xlsx`. **Run → Export Report…** writes handoff **CSV, XLSX, DOCX, and JSON** (non-authoritative). See [`docs/RECORDING_AND_EXPORT_RUNBOOK.md`](docs/RECORDING_AND_EXPORT_RUNBOOK.md).

## Launch

Windows primary:

```text
launch_best_buds.bat
launch_best_buds.ps1
launch_simulator.bat
launch_simulator.ps1
```

Linux parity:

```bash
./launch_best_buds.sh
./launch_simulator.sh
```

## Coding-agent bootstrap

```bash
python -m best_buds_weight_station.bootstrap --profile cursor-ready
```

Windows wrapper:

```powershell
.\cursor_bootstrap.ps1 -Plan cursor_ready
```

Stage runner:

```bash
python -m best_buds_weight_station.stage_runner list
python -m best_buds_weight_station.stage_runner run-plan --plan cursor_ready
python -m best_buds_weight_station.stage_runner status
```

Stage commands use bounded file-backed subprocess output and atomic receipts/checkpoints. This prevents GUI, pytest, or tracing descendants from retaining orchestration pipes and makes Cursor/Codex runs resumable and deterministic.

## Canonical serial capture

```text
PySerialTransport -> DeviceService -> ScaleReadingWorker -> reading.ingest -> state machine
```

`serial_adapter.py` is retained only as a declared legacy compatibility surface. It is not the physical-integration target.

## Evidence boundary

Authorized local software, Tk fallback, scripted-device, recovery, stage-runner, and Debian lanes may be executed and claimed only with receipts. Native Windows/PySide execution, firmware compile/upload, physical UNO R3/HX711/load-cell operation, legal-for-trade status, production readiness, and release seal remain unclaimed until direct evidence exists.

See `docs/SYSTEM_STATE_CURRENT.md`, `pipeline/plans/cursor_ready.v0.1.9.json`, and `cursor/CURSOR_UNO_R3_PHYSICAL_INTEGRATION_HANDOFF_V0_1_8.md`.
