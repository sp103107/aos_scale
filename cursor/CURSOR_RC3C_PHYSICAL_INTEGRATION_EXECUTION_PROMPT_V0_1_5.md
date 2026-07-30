# Cursor Kickoff — Best Buds Weight Station Physical Integration from v0.1.5

## Mission

Continue the complete repository:

```text
best_buds_cultivator_weight_station_v0_1_5
```

Do not create a detached patch or hardware-only mini-pack.

First execute the coding-agent bootstrap:

```bash
python -m best_buds_weight_station.bootstrap --profile prehardware
```

The bootstrap must return `PASS` or an evidence-backed `PASS_WITH_WARNINGS` before physical work begins.

## Current software truth

- Full software tests pass.
- Automatic and manual simulator loops pass.
- Crash recovery passes.
- Tk manual and automatic smoke pass when Xvfb is present.
- Python package installation preflight passes.
- Firmware, physical serial, HX711, physical zero/tare/calibration, and physical weighing remain unproven.

## Next physical sequence

1. Record exact UNO R3, HX711, load-cell, wire-color, and reference-weight inventory.
2. Confirm wiring from documentation or bridge measurement; do not assume color conventions.
3. Install `arduino-cli` and AVR core.
4. Compile firmware.
5. Upload firmware.
6. Run `PING` and `STATUS`.
7. Capture unloaded and loaded raw readings.
8. Execute physical zero.
9. Execute container tare.
10. Execute known-weight calibration.
11. Run repeatability and zero-return tests.
12. Run physical barcode → weigh → commit → Alice receipt → next barcode.
13. Restart and resume the last committed run.
14. Preserve logs, receipts, sample files, hashes, and non-claims.

## Validation commands

```bash
python -m best_buds_weight_station.validation run --lane firmware --profile integration --port <port>
python -m best_buds_weight_station.validation run --lane serial --profile integration --port <port>
python -m best_buds_weight_station.validation run --lane zero-tare --profile integration --port <port>
python -m best_buds_weight_station.validation run --lane calibration --profile integration --port <port> --reference-weight-g <grams>
python -m best_buds_weight_station.validation run --lane physical-loop --profile integration --port <port> --barcode <test-barcode>
```

## Required next repository state

Create the next complete full-repository bump only after actual work is recorded. Preserve all `v0.1.5` software receipts and historical evidence.

Do not claim physical success from source presence, simulator fixtures, or serial-port availability alone.
