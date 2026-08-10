# Best Buds Cultivator Weight Station (`aos_scale`)

**Version:** `2.0.0-rc2`  
**Public repo:** [https://github.com/sp103107/aos_scale](https://github.com/sp103107/aos_scale)  
**Start here:** [START_HERE.md](START_HERE.md) (operators) · [START_HERE_CODING_AGENT.md](START_HERE_CODING_AGENT.md) (agents)  
**RC notes:** [docs/RELEASE_CANDIDATE.md](docs/RELEASE_CANDIDATE.md)

A Windows-first, local-first, barcode-driven cultivation weighing station. PySide6 is the primary Windows frontend and shared Linux frontend. Tk is the secondary Linux fallback. The PC remains authoritative for run setup, append-only records, crash recovery, reports, Alice guidance, and terminal receipt validation.

## License

- **Personal / noncommercial:** [PolyForm Noncommercial 1.0.0](LICENSE)
- **Commercial / paid:** [COMMERCIAL.md](COMMERCIAL.md)

Third-party dependencies keep their own licenses.

## Honest status

USB connect, live readings, Zero/Tare UX, Guided Calibration, Scan→Lock→Confirm capture, plant log, polished handoff exports, and product onboarding doors are in place for this RC. **Displayed grams are not trustworthy until calibration with a verified reference mass.** This project does **not** claim production-ready or legal-for-trade status.

## System requirements

See [docs/SYSTEM_REQUIREMENTS.md](docs/SYSTEM_REQUIREMENTS.md) for OS, hardware, and packaged-app requirements.

## Launch

Windows:

```text
launch_best_buds.bat
launch_simulator.bat
```

Linux:

```bash
./launch_best_buds.sh
./launch_simulator.sh
```

Operator day-one: [docs/OPERATOR_ONBOARDING.md](docs/OPERATOR_ONBOARDING.md).

## Routine operator loop

```text
Scan → settle → Lock weight → Confirm & Record → next plant
```

New Run uses **Cultivator** (company/grower) and **Strain** (sticky). Exports (Run → Export Report) write CSV / XLSX / DOCX / JSON handoffs; **JSONL remains authoritative**.

## Coding-agent onboarding

```bash
python -m best_buds_weight_station.onboard
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

## Windows packaged install

On a Windows build host:

```powershell
.\packaging\windows\build_windows.ps1
```

Artifacts land in `dist\windows\` when the build succeeds.

## Canonical serial capture

```text
PySerialTransport -> DeviceService -> ScaleReadingWorker -> reading.ingest -> state machine
```

`serial_adapter.py` is retained only as a declared legacy compatibility surface.

## Evidence boundary

Authorized local software, Tk fallback, scripted-device, recovery, stage-runner, and Debian lanes may be executed and claimed only with receipts. Native Windows/PySide execution, firmware compile/upload, physical UNO R3/HX711/load-cell operation, legal-for-trade status, production readiness, and release seal remain unclaimed until direct evidence exists.

See `docs/SYSTEM_STATE_CURRENT.md` and [docs/RELEASE_CANDIDATE.md](docs/RELEASE_CANDIDATE.md).
