# New Context Build Kickoff — Best Buds Cultivator Weight Station

## Operating role

Act as the AoS application factory, senior desktop engineer, embedded-firmware engineer, release engineer, QA lead, and evidence-bound Judge for a new application repository:

`best_buds_cultivator_weight_station`

Your task is to build the strongest complete initial repository state, package it, validate it, save it to Google Drive, and return the release artifacts in chat.

Do not stop at a design outline. Do not create a detached proof-of-concept archive. Do not create separate phase-only ZIPs.

The required external repository release is:

`best_buds_cultivator_weight_station_v0_1_0`

The source contract hardening addendum is:

`best_buds_cultivator_weight_station_execution_hardening_addendum_v0_1_1.json`

Generated source timestamp: `2026-07-19T15:05:06Z`

---

## Source-of-truth files

Read the uploaded source artifacts before writing code. Use this authority order:

1. `best_buds_cultivator_weight_station_execution_hardening_addendum_v0_1_1.json`
2. `best_buds_cultivator_weight_station_contract_pack_v0_1_0.json`
3. `best_buds_cultivator_weight_station_requirements_and_prompt_pack_v0_1_0.docx`
4. `best_buds_cultivator_weight_station_harvest_alice_sublayer_prompt_v0_1_0.md`
5. `best_buds_cultivator_weight_station_frontend_manifest_v0_1_0.json`
6. `best_buds_cultivator_weight_station_backend_manifest_v0_1_0.json`
7. `best_buds_cultivator_weight_station_new_context_kickoff_prompt.md`
8. `best_buds_cultivator_weight_station_system_compatibility_companion_prompt.md`
9. Operator instructions in this prompt.

Prefer the consolidated contract pack over duplicate prose. Preserve unique requirements from every source.

Record source hashes in the repository. Known source hashes from the preparation context are:

```json
{
  "best_buds_cultivator_weight_station_contract_bundle_v0_1_0.zip": "dfeeae41b0f787dec65b656c354aadc18c1a09edb41ff910eab8671e22ebad5c",
  "best_buds_cultivator_weight_station_contract_pack_v0_1_0.json": "da69715c8621e1267f59e8c70a5f51a955385aee63783b062ad14c7d7aa9f672",
  "best_buds_cultivator_weight_station_requirements_and_prompt_pack_v0_1_0.docx": "f8013887059db1797faa7e166e6f4e411e321546941a2a8e2af9f0d2f86f641d",
  "best_buds_cultivator_weight_station_harvest_alice_sublayer_prompt_v0_1_0.md": "c567568130ad22bcdd486d68bab28c3a1f94024569c03088637c59cf31d5c4b5",
  "best_buds_cultivator_weight_station_frontend_manifest_v0_1_0.json": "19ccecaa24cbec41a15260e2c4a75064fd0675d559ac0fc5a8b9907460486b37",
  "best_buds_cultivator_weight_station_backend_manifest_v0_1_0.json": "24e1cf015374d02b8279de324d972a6a3a659734edd2c9355211dc8827d34c4d",
  "best_buds_cultivator_weight_station_new_context_kickoff_prompt.md": "7ea515e5fcb4c671035cb0ebae4fe84356b50e3eeb2e745b523959cf2947e4b9",
  "best_buds_cultivator_weight_station_system_compatibility_companion_prompt.md": "59c563dde12321a54cd7360481f1f37f0c34355b7f20f5bfb4b873d488a375d5"
}
```

Recalculate hashes from the actual uploaded files and record any mismatch as drift.

---

## Locked product objective

Create a professional, local-first cultivation weight station that:

1. Reads weight from an S-type load cell through an HX711 and Elegoo UNO R3 / ATmega328P.
2. Accepts keyboard-wedge barcode scans.
3. Guides the operator through a new harvest run using Alice.
4. Requires a cultivar/strain roster and run context before capture.
5. Waits for a stable weight.
6. Records automatically after stability or waits for manual confirmation.
7. Emits success feedback only after authoritative local persistence succeeds.
8. Immediately resets for the next barcode.
9. Preserves append-only JSONL, session JSON, individual record JSON, CSV, and XLSX.
10. Continues a compatible spreadsheet without making it authoritative.
11. Compiles reproducible run summaries.
12. Supports disabled-by-default private Git/cloud/network storage adapters.
13. Accepts and emits AoS standard application envelopes.
14. Runs on Windows and Debian Linux.
15. Treats macOS as optional best-effort source compatibility.

This is not a Metrc replacement, full ERP, inventory-ownership authority, regulatory certification engine, or legal-for-trade scale.

---

## Required architecture

Use the established AoS build order:

`law → kernel → contracts → prompts/operator flows → factory/build → tools → firmware/device adapter → backend → frontend → storage/report adapters → validation → release`

Required implementation stack unless an evidence-backed ADR selects a better compatible alternative:

- Arduino C++ firmware.
- Python 3.11+.
- PySide6 desktop UI.
- `pyserial`.
- Pydantic or equivalent validation.
- `openpyxl`.
- SQLite only as a rebuildable optional index.
- `pytest`.
- PyInstaller for the Windows executable path.
- Native Debian package construction for `.deb`.
- `arduino-cli` for firmware compile where available.

Keep platform differences behind adapters. Do not branch core state-machine logic directly on the operating system.

---

## Hardware contract

Target:

- Elegoo UNO R3 / ATmega328P.
- HX711.
- S-type hanging load cell, nominally 50 kg.
- HX711 DOUT/DT to UNO D2.
- HX711 SCK/CLK to UNO D3.
- HX711 VCC to 5V.
- HX711 GND to GND.
- 9600 baud or a documented higher standard rate.

Load-cell wire colors are not authoritative. Require datasheet verification.

Include mechanical safety and secondary-tether guidance. Do not certify the rig.

---

## Alice-guided harvest startup

Alice is the command-oriented guide and application gatekeeper.

Before the first weight record, Alice must verify:

- Operator identity.
- Facility and station.
- Local data root and write preflight.
- Device connection and firmware identity.
- Calibration status.
- New, Continue, or Recovery mode.
- Harvest-run ID.
- External tracking identifiers when available.
- Room/zone/rack/source context.
- Cultivar or strain roster.
- Raw strain names and normalized cultivar names as separate fields.
- Measurement stage.
- Weight purpose.
- Container/tare policy.
- Automatic or manual capture mode.
- Stability profile.
- Maximum expected capacity.
- Start manifest review.

Alice may block failed application gates. Alice may not declare regulatory compliance, invent missing identifiers, bypass failed persistence, or alter immutable records.

---

## Core state machine

Implement and test:

```text
DISCONNECTED
→ DEVICE_READY
→ SESSION_READY
→ WAITING_FOR_BARCODE
→ BARCODE_CAPTURED
→ WAITING_FOR_STABLE_WEIGHT
→ WEIGHT_STABLE
→ AUTO_RECORD or MANUAL_CONFIRM
→ LOCAL_COMMIT_PENDING
→ RECORD_SAVED
→ SUCCESS_BEEP
→ WAITING_FOR_BARCODE
```

The following must prevent a save acknowledgement:

- HX711 unavailable.
- Device identity mismatch.
- Serial disconnect.
- Unstable weight timeout.
- Out-of-range or invalid weight.
- Required tare failure.
- Missing active cultivar.
- Missing barcode when required.
- JSONL append failure.
- Individual JSON failure.
- Checkpoint/manifest failure.

Remote sync and spreadsheet failures must not lose the locally committed record. Create pending-sync receipts.

---

## Persistence hardening

Authoritative write order:

1. Validate the command/envelope.
2. Construct the record deterministically.
3. Append the JSONL event.
4. Flush and sync where supported.
5. Write the individual record JSON atomically.
6. Update session checkpoint/manifest atomically.
7. Return the local commit receipt.
8. Emit the success beep and reset the UI.
9. Update CSV/XLSX and remote queues asynchronously.

Requirements:

- Append-only correction and void events.
- Hash chain or equivalent continuity.
- Idempotency key handling.
- Crash recovery from JSONL.
- Formula-injection protection in CSV and XLSX.
- Path traversal prevention.
- File-lock handling.
- Deterministic report rebuild.
- Remote sync never blocks capture.

---

## AoS envelope boundary

Implement `aos.application.envelope.v1` ingress and egress.

Support command/event families from the contract pack, including:

- Harvest start/continue/recover.
- Cultivar register/activate.
- Barcode scan.
- Tare request.
- Scale reading.
- Weight record.
- Correction and void.
- Report compile.
- Export.
- Sync.

Every inbound command must produce:

1. Acknowledgement.
2. Terminal success, rejection, or failure receipt.

Validate envelope version, IDs, causality, payload schema, provenance, security context, idempotency key, and content hash.

MCP, VPort, HTTP, socket, and message-bus surfaces remain disabled scaffolds unless actually configured and tested.

---

## UI quality gate

Create a polished operator-first PySide6 interface.

The main capture screen must keep visible:

- Connection status.
- Active run.
- Operator.
- Active cultivar.
- Barcode.
- Gross, tare, and net weight.
- Stability state.
- Measurement stage and purpose.
- Automatic/manual mode.
- Confirm & Continue.
- Tare.
- Cancel capture.
- Last saved record.
- Run record count.
- Run total weight.
- Storage status.
- Error banner.

Use layouts, HiDPI support, keyboard navigation, clear focus management, large controls, visible text/icon status, and no critical color-only indicators.

Keep engineering diagnostics out of operator mode.

---

## Firmware deliverables

Create:

```text
firmware/elegoo_uno_r3_hx711/
├── best_buds_scale_firmware.ino
├── firmware_config.example.h
├── SERIAL_PROTOCOL.md
├── calibration_notes.md
├── platform_notes.md
└── compile_receipt.json
```

Firmware must support:

- `PING`
- `STATUS`
- `TARE`
- `READ`
- `STREAM_ON`
- `STREAM_OFF`
- `SET_CAL`
- `SET_UNIT`

Bound serial input length, reject malformed commands, and avoid continuous EEPROM writes.

Compile for `arduino:avr:uno` when `arduino-cli` is available. Record an honest blocked receipt when it is not.

---

## Required complete repository shape

```text
best_buds_cultivator_weight_station_v0_1_0/
├── README.md
├── VERSION
├── CHANGELOG.md
├── pyproject.toml
├── repo_release_state.json
├── contracts/
├── law/
├── kernel/
├── prompts/
├── firmware/
├── app/
├── adapters/
├── frontend/
├── backend/
├── data/
├── docs/
├── scripts/
├── tests/
├── validation/
├── reports/
├── manifests/
├── packaging/
│   ├── windows/
│   └── debian/
├── dist/
│   ├── windows/
│   └── debian/
├── context/
│   ├── working_set/
│   ├── episodes/
│   ├── ledger/
│   └── resume_pack/
├── release_candidate/
└── repo_scaffold/
```

Do not package a phase as a separate external release.

---

## Windows executable — release blocking

The final build must include a real Windows executable produced on Windows.

Preferred artifact:

```text
dist/windows/BestBudsWeightStation-windows-x64.zip
└── BestBudsWeightStation/
    └── BestBudsWeightStation.exe
```

An optional Windows setup executable may also be created.

Requirements:

- Build on a Windows host or native Windows CI runner.
- Do not rename another platform’s binary.
- Include PyInstaller configuration.
- Bundle required Qt resources safely.
- Run:
  - `BestBudsWeightStation.exe --version`
  - `BestBudsWeightStation.exe --self-test --simulator`
- Record:
  - Runner OS and version.
  - Architecture.
  - Python version.
  - Build command.
  - Dependency lock hash.
  - Exit codes.
  - Output SHA-256.
  - Smoke-test result.
- Include a packaging receipt and license inventory.

If the present environment cannot build Windows artifacts, use an available GitHub Actions Windows runner or another native Windows build surface. Do not declare the release complete with only a `.spec` file.

---

## Debian `.deb` installer — release blocking

The final build must include:

```text
dist/debian/best-buds-weight-station_0.1.0_amd64.deb
```

Requirements:

- Build on Debian or an explicitly identified compatible Debian environment.
- Include desktop entry, icon, launcher, runtime dependencies, version metadata, and serial-permission documentation.
- Inspect the package with `dpkg-deb --info`.
- Install in an isolated Debian test environment where feasible.
- Run:
  - `best-buds-weight-station --version`
  - `QT_QPA_PLATFORM=offscreen best-buds-weight-station --self-test --simulator`
- Record environment, commands, exit codes, installed paths, SHA-256, and smoke-test result.
- Do not claim success from filename creation alone.

Select one Debian package path. Do not add AppImage and multiple alternative installers unless they are practically free.

---

## CI and release workflow

Create a native build matrix with at least:

1. `validate-source`
2. `test-linux`
3. `build-debian`
4. `test-windows`
5. `build-windows`
6. `assemble-release`

The assembled release must include:

- Full repository ZIP.
- Repository checksum.
- Windows artifact.
- Windows artifact checksum and receipt.
- Debian `.deb`.
- Debian checksum and receipt.
- Firmware source and compile receipt.
- Validation report.
- Dependency/license inventory.
- Context continuation pack.

Use native runner artifacts as inputs to release assembly.

---

## Required validation

Execute and record:

- JSON parse.
- JSONL parse.
- Schema validation.
- YAML parse if present.
- Python static/import checks.
- Unit tests.
- State-machine tests.
- Serial simulator.
- Automatic capture.
- Manual capture.
- Stable-weight detection.
- Duplicate handling.
- Tare math.
- Gross/net reconciliation.
- Hash-chain verification.
- Crash recovery.
- Spreadsheet import/append/backup.
- CSV/XLSX formula-injection checks.
- Report reproducibility.
- Device-disconnect recovery.
- Local-write failure preventing beep.
- Remote failure preserving local data.
- Secret scan.
- Dependency/license inventory.
- Firmware compile if toolchain available.
- Native Windows build and smoke receipt.
- Native Debian build and smoke receipt.
- Required paths.
- Version alignment.
- ZIP exact membership.
- No forbidden detached release paths.

Simulator evidence must never be labeled as physical-device evidence.

---

## Context Module

Create the initial Context Module state:

- Working Set update sequence 1.
- Immutable episode checkpoint.
- Append-only ledger.
- Resume Pack.
- Source hashes.
- Continuation handoff.
- Context validation.

Do not claim Context Module runtime execution unless it actually ran.

---

## Google Drive delivery

Use the connected Google Drive.

1. Search for an existing folder named:
   - `Best Buds Cultivator Weight Station`
   - and reasonable naming variants.
2. Inspect matching folder metadata and parent paths.
3. Reuse the canonical project folder when one exists, even if it was moved.
4. Create one folder only when no suitable project folder exists.
5. Upload:
   - Full repository ZIP.
   - Repository checksum.
   - Windows executable distribution and checksum.
   - Windows packaging receipt.
   - Debian `.deb` and checksum.
   - Debian packaging receipt.
   - Validation report.
   - Contract/source bundle or a manifest pointing to it.
6. Verify every uploaded file through Drive metadata.
7. Record file IDs and Drive URLs in:
   - `reports/drive_delivery_receipt.v0.1.0.json`
   - `repo_release_state.json`
8. Do not claim Drive delivery for files whose upload did not return metadata.
9. If the connector rejects local generated files, report the exact limitation and still provide all chat download links. Do not hide the failure.

Do not create duplicate Drive folders during retry.

---

## Final chat delivery

Return direct chat download links for:

- Full repo ZIP.
- Repo checksum.
- Windows artifact.
- Windows checksum.
- Debian `.deb`.
- Debian checksum.
- Validation report.
- Optional source/installer bundle.

Final response must state:

1. New version.
2. What was implemented.
3. What was preserved from the contract pack.
4. Hardware assumptions.
5. Simulator tests performed.
6. Physical hardware tests performed or withheld.
7. Windows build result.
8. Debian build result.
9. Drive delivery result.
10. Drift found.
11. Non-claims.
12. Validation result.
13. Context Module update status.
14. Download links.

---

## Release-state requirements

`repo_release_state.json` must include:

```json
{
  "package_name": "best_buds_cultivator_weight_station",
  "previous_version": null,
  "version": "0.1.0",
  "bump_scope": "full_repo",
  "current_internal_phase": "rc0_initial_application_build",
  "next_internal_phase": "rc1_physical_hardware_calibration_and_dual_platform_pilot",
  "source_of_truth": [],
  "drift_check_status": "pending",
  "validation_status": "pending",
  "context_update_status": "pending",
  "platform_support": {
    "windows": {"required": true, "status": "pending"},
    "debian_linux": {"required": true, "status": "pending"},
    "macos": {"required": false, "status": "best_effort"},
    "arduino_uno_r3_atmega328p": {"required": true, "status": "pending"}
  },
  "packaging_status": {
    "windows_exe": "pending",
    "debian_deb": "pending"
  },
  "drive_delivery_status": "pending",
  "non_claims": []
}
```

Replace pending values with evidence-backed final statuses.

---

## Non-claims

Do not claim:

- Legal-for-trade certification.
- Regulatory compliance certification.
- Metrc synchronization.
- Seed-to-sale completeness.
- Genetic truth from a strain label.
- Physical hardware success from the simulator.
- Windows support from a Linux-only build.
- Debian support from a source-only launch.
- Installer success without smoke execution.
- Drive upload without returned metadata.
- Remote storage success without a provider receipt.
- MCP, VPort, HTTP, socket, or message-bus activation without execution.
- Production readiness or release seal.
- macOS packaged support.

---

## Execution directive

Proceed without asking the operator to restate information already present in the source pack.

Use the simulator for development and workflow validation when physical hardware is absent.

Use native Windows and Debian build surfaces for final installers.

Do not finish with scaffolding alone.

Do not omit required packaging artifacts silently.

Do not fabricate evidence to satisfy the requested final polish.

The desired outcome is a complete, professional `v0.1.0` repository with a functioning simulator-tested application, firmware, Windows executable, Debian `.deb`, validation receipts, Drive delivery, and chat downloads.
