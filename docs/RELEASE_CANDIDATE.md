# Release candidate notes — v0.1.9-rc1 (USB bring-up)

**Tag intent:** freeze a **USB serial bring-up release candidate**, not a production or legal-for-trade release.

## What this RC includes

- Windows-first PySide6 operator UI (Tk fallback)
- USB serial connect with selectable baud (`115200` default, `9600` supported)
- Protocol handshake (`PING` / `STATUS`) and live weight streaming
- Zero / container tare / guided calibration workflows
- Host display zero + median smoothing for uncalibrated bring-up
- Simulator path for software validation without hardware
- Honest evidence classes (`SOURCE_PRESENT`, `physical_device_pass: false`)

## What this RC does **not** claim

- No production-ready weighing claim
- No legal-for-trade / NTEP / Weights & Measures certification
- No completed physical hanging-load qualification
- No guarantee that displayed grams are accurate until Guided Calibration is completed with a verified reference mass and retained receipts

## Operator bring-up checklist

1. Flash included USB firmware (or compatible protocol firmware) to the UNO-class board.
2. Close Arduino Serial Monitor (port exclusive).
3. Launch `launch_best_buds.bat`, Scale Setup → COM port @ 115200 → Connect.
4. Start/resume a run.
5. Run **Guided Calibration** with a verified reference mass.
6. Empty pan → **ZERO** → optional container **SET TARE** → scan barcodes.

## License

Personal / noncommercial use: PolyForm Noncommercial 1.0.0 — see `LICENSE`.  
Commercial use: requires a separate paid license — see `COMMERCIAL.md`.

## Repository

[https://github.com/sp103107/aos_scale](https://github.com/sp103107/aos_scale)
