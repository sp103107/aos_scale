# Core Process Implementation — Current

Version: `2.0.0-rc4`

## Implemented software processes

- Cross-platform launch and coding-agent bootstrap surfaces.
- New Run, Load Run, Resume Last Run, Finish Run, and export.
- Automatic and manual barcode-to-weight capture through the authoritative state machine.
- Append-only JSONL, individual JSON, checkpoint, recent-run pointer, receipt, and Alice terminal validation.
- Crash recovery, stale checkpoint reconstruction, duplicate prevention, and interrupted-write handling.
- Simulator and scripted serial transports through `DeviceService` and `ScaleReadingWorker`.
- Zero, known/captured container tare, and guided calibration services.
- Windows-first PySide6 source and Linux/Tk fallback runtime.
- JSON stage plans, resumable stage runner, validation profiles, and evidence receipts.

## Canonical physical serial path

`pyserial -> PySerialTransport -> DeviceService -> ScaleReadingWorker -> reading.ingest`

`serial_adapter.SerialScale` is retained only as a legacy compatibility surface and is not the canonical integration target.

## Evidence boundary

Physical UNO R3, HX711, load cell, firmware upload, native Windows execution, and physical calibration remain `NOT_RUN` or `BLOCKED` until executed.
