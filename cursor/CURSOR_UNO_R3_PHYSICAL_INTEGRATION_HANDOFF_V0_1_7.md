# Cursor Handoff - UNO R3/HX711 Physical Integration from v0.1.7

## Gate before hardware work

```bash
python -m best_buds_weight_station.bootstrap --profile cursor-ready
```

Required verdicts:

```text
CURSOR_READY
OPERATOR_SOFTWARE_READY
PHYSICAL_HARDWARE_NOT_RUN
WINDOWS_NATIVE_RUNTIME_NOT_RUN
```

## Canonical capture path

```text
UNO R3 -> USB serial -> pyserial -> PySerialTransport -> DeviceService -> ScaleReadingWorker -> reading.ingest
```

Do not integrate new work through `serial_adapter.py`; it is a legacy compatibility adapter.

## Physical sequence

1. Record exact UNO R3, HX711, load-cell, wiring, and reference-mass inventory.
2. Install and verify Arduino CLI and AVR core.
3. Compile and upload firmware.
4. Run PING, STATUS, and raw stream evidence.
5. Execute physical zero, container tare, calibration, repeatability, and zero-return.
6. Execute barcode -> physical stable weight -> commit -> checkpoint -> Alice receipt -> next barcode.
7. Restart and resume the last committed run.
8. Preserve actual logs, samples, receipts, hashes, and non-claims.

The next complete repository bump should be `v0.1.8`. Do not create a hardware-only mini-pack.
