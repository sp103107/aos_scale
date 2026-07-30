# Cursor Handoff - UNO R3/HX711 Physical Integration from v0.1.8

## Source truth

Continue the complete repository `best_buds_cultivator_weight_station_v0_1_8`. Do not create a hardware-only mini-pack or detached patch.

First run:

```powershell
.\cursor_bootstrap.ps1 -Plan cursor_ready
```

or:

```bash
python -m best_buds_weight_station.bootstrap --profile cursor-ready
```

Required starting verdicts:

```text
CURSOR_READY
OPERATOR_SOFTWARE_READY
PHYSICAL_HARDWARE_NOT_RUN
WINDOWS_NATIVE_RUNTIME_NOT_RUN
```

## Canonical physical path

```text
PySerialTransport -> DeviceService -> ScaleReadingWorker -> reading.ingest
```

Do not integrate physical capture through the legacy `SerialScale` compatibility adapter.

## Physical sequence

1. Record exact UNO R3, HX711, load-cell, wire-color, hook orientation, and reference-weight inventory.
2. Determine bridge wiring from documentation or measurement; do not assume wire colors.
3. Install `arduino-cli` and the AVR core.
4. Compile and upload firmware.
5. Execute PING and STATUS against the actual COM port.
6. Capture unloaded and loaded raw readings.
7. Execute physical zero and container tare.
8. Calibrate using a verified reference mass.
9. Run repeatability, zero-return, and safe load-range tests.
10. Run physical barcode -> stable weight -> commit -> checkpoint -> Alice receipt -> next barcode.
11. Restart and resume the last committed run.
12. Preserve commands, logs, sample files, hashes, photos, receipts, failures, blocks, and non-claims.

The next complete full-repository bump should implement `rc3d_uno_r3_hx711_physical_scale_bringup`. `PHYSICAL_HARDWARE_NOT_RUN` remains true until direct evidence is recorded.
