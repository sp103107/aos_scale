# Cursor Handoff — Best Buds Cultivator Weight Station v0.1.6

## Source

Use the complete repository:

```text
best_buds_cultivator_weight_station_v0_1_6
```

Do not create a detached patch, UI-only pack, validator-only ZIP, or hardware mini-pack.

## First command

```bash
python -m best_buds_weight_station.bootstrap --profile operator-ready
```

Windows users may run:

```text
bootstrap_agent.bat
bootstrap_agent.ps1
```

## Current implementation truth

- Windows is the primary PC target.
- PySide6 is the primary operator frontend.
- Linux PySide6 parity and Tk fallback are present.
- BAT, PowerShell, and shell launchers are present.
- New/load/resume/finish/export and crash recovery are present.
- Scale Setup is implemented.
- A background reading worker routes device samples through `reading.ingest`.
- Physical-mode Zero Scale does not receive synthetic samples from the UI.
- Known and captured tare flows are present.
- Guided calibration is reachable from the operator UI.
- Automatic and manual operator-runtime flows pass against the simulator.
- Windows packaging source is implemented, but no native Windows pass is claimed.
- UNO R3, HX711, load cell, firmware, and physical calibration remain unexecuted.

## Immediate task

Perform the final naming and drift concordance pass before physical integration.

Check:

1. Current version references.
2. Root and package names.
3. Launcher names and their referenced entry points.
4. README and system-state anchors.
5. PyInstaller and Debian package names.
6. Validation profile and graph names.
7. Current manifests and checksum indexes.
8. Context Working Set, Episode, Ledger, and Resume Pack alignment.
9. Historical evidence immutability.
10. No obsolete placeholder callback remains reachable.

Safe current generated metadata may be repaired. Do not rewrite historical Episodes, prior Working Sets, prior Ledger events, physical evidence, or prior release receipts.

## Operator application acceptance

The following must remain true:

```text
launch
→ new or resume run
→ Scale Setup
→ connect simulator or selected serial device
→ background readings
→ barcode
→ stable weight
→ automatic record or manual confirm
→ authoritative commit
→ checkpoint
→ Alice validation
→ next barcode
```

## Physical boundary

Do not begin physical integration until the operator-ready bootstrap and the final naming/drift pass both succeed.

Do not claim:

- Native Windows executable pass without a Windows receipt.
- Firmware compile or upload pass without tool output.
- Physical UNO/HX711/load-cell pass without actual device evidence.
- Physical calibration, repeatability, or hanging-load pass without recorded samples.
- Legal-for-trade status, production readiness, or release seal.

After the drift pass, continue from the complete corrected repository into the UNO R3/HX711 physical bring-up arc.
