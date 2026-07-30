# Cursor Execution Kickoff — Best Buds Weight Station v0.1.4 RC3 Physical Integration

## Mission

Continue from the complete `best_buds_cultivator_weight_station_v0_1_4` repository. Do not create a detached test pack. Use the included LLM-native validation harness to execute RC3B through RC3G against the connected PC-first controller, HX711, and 10 kg load cell.

## Truth lock

- RC3A validation harness is implemented.
- Hardware availability is operator-reported, not independently proven by the repository build environment.
- Firmware compile/upload, physical serial, zero, tare, calibration, repeatability, hanging-load, and physical barcode loop are not yet passed.
- No physical pass may be inferred from schemas, source, simulator results, or an opened serial port.

## Start commands

```bash
python -m best_buds_weight_station.validation inspect
python -m best_buds_weight_station.validation prepare --profile development
python -m best_buds_weight_station.validation run --lane repository-inspection --profile development
python -m best_buds_weight_station.validation run --lane development-hygiene --profile development
python -m best_buds_weight_station.validation run --lane software --profile development
```

Then execute the physical lanes in dependency order:

```text
firmware → serial → zero-tare → calibration → physical-loop → release-packaging
```

## Internal arc sequence

1. `rc3b_hardware_inventory_and_wiring_contract`
2. `rc3c_firmware_compile_upload_and_protocol_bringup`
3. `rc3d_physical_stream_zero_and_tare_validation`
4. `rc3e_calibration_repeatability_and_load_validation`
5. `rc3f_physical_scan_weigh_record_validate_resume`
6. `rc3g_local_control_bridge_and_evidence_closure`

## Required execution behavior

- Inspect the exact controller, HX711 labels, load-cell wires, mechanical orientation, serial port, and known reference mass.
- Compile with a real Arduino toolchain.
- Upload to the connected controller.
- Capture PING, STATUS, raw unloaded readings, loaded readings, zero return, tare, calibration, repeatability, and end-to-end receipts.
- Use machine-readable `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, or `WAITING_FOR_EXTERNAL_ACTION` results.
- Do not auto-repair historical evidence.
- Do not weaken physical gates.
- Package only a complete full-repository next version after evidence closure.

## Next version rule

This repository is the completed `v0.1.4` harness/preflight state. Physical integration results must be preserved in the next complete repository bump, recommended `v0.1.5`, unless the operator explicitly directs an in-place release-candidate continuation policy.
