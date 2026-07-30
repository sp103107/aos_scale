# LLM Software Dry Run and Coding-Agent Bootstrap

## Purpose

`v0.1.5` adds a deterministic Python bootstrap that Cursor, Codex, CI, or another coding agent can execute before any UNO R3, HX711, or load-cell integration.

The bootstrap runs real repository software gates. It does not convert simulator evidence into physical evidence.

## Entry points

From the repository root:

```bash
python -m best_buds_weight_station.bootstrap --profile prehardware
```

Installed console entry point:

```bash
best-buds-weight-station-bootstrap --profile prehardware
```

Equivalent validation command:

```bash
python -m best_buds_weight_station.validation bootstrap --profile prehardware
```

## Executed lanes

1. Repository inspection
2. Development hygiene and safe current-metadata repair
3. Full automated test suite and repository validator
4. Python/module entry-point smoke
5. Real software-only dry run through the application controller
6. Crash-recovery test matrix
7. Tk manual and automatic UI smoke under Xvfb when available
8. Isolated Python package installation preflight

## Software-only dry run

The dry run executes:

```text
new run
→ simulator connection
→ zero
→ known container tare
→ barcode submit
→ stable-weight ingestion
→ automatic or manual commit
→ JSONL + individual JSON + checkpoint
→ Alice receipt confirmation
→ durable recent-run pointer
→ load existing run
→ resume latest run
```

It also executes the guided calibration service with simulator samples and validates canonical local-button mappings plus disabled Bluetooth and Wi-Fi boundaries.

## Evidence boundary

A successful prehardware bootstrap means:

- Core Python software gates passed.
- Automatic and manual simulator loops passed.
- Recovery tests passed.
- Tk runtime smoke passed when Xvfb is available.
- The package can be installed into an isolated Python target.

It does **not** mean:

- Firmware compiled or uploaded.
- A physical serial device connected.
- HX711 readings passed.
- Zero, tare, calibration, or weighing passed on physical hardware.
- Bluetooth, Wi-Fi, physical buttons, UNO Q, or Windows-native execution passed.

## Next command

After the controller is wired and a serial port is available:

```bash
python -m best_buds_weight_station.validation run \
  --lane firmware \
  --profile integration \
  --port <serial-port>
```
