# Validation Plan — v0.1.3

## Repository and contracts

- Parse every JSON and JSONL record.
- Parse YAML when present.
- Compile/import Python.
- Validate all JSON Schemas.
- Verify version alignment, required paths, prior evidence preservation, manifest hashes, and forbidden detached-package absence.

## Run management and operator loop

- New Run, writable data location, invalid location rejection, Load Run, invalid run rejection, Resume Last Run, durable recent pointer, Finish Run, and export.
- Automatic and manual barcode-to-record loops, stability, confirm, cancel, next-barcode reset, duplicate/idempotency, and gross/tare/net reconciliation.

## Persistence and recovery

- JSONL, individual JSON, checkpoint, recent pointer, receipt, and Alice gate.
- Interruptions before/during/after JSONL, individual JSON, checkpoint, pointer, and receipt.
- Invalid final JSONL fragment quarantine, temporary-file quarantine, stale checkpoint rebuild, receipt rebuild, hash-chain rejection, and no invented uncommitted weight.

## Device, scale, and adapters

- Serial protocol handshake, stream, parsing bounds, malformed lines, stale readings, disconnect, reconnect, and simulator/physical evidence separation.
- Zero acknowledgement/stability, captured and known tare, calibration factor calculation/test/protected acceptance/rejection.
- UI/keyboard/test-button canonical mapping and disabled Bluetooth/Wi-Fi authentication/idempotency boundaries.

## Platform evidence

- Source and installed Tk UI smoke in automatic and manual modes.
- Native Debian build, package inspection, install, version, self-test, and UI smoke.
- Firmware compile attempt and blocked receipt when toolchain is unavailable.
- Windows and physical hardware remain blocked/not run without matching evidence.
