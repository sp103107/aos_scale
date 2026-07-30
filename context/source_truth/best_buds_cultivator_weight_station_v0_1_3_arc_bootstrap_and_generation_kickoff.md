# Best Buds Cultivator Weight Station
## Full-Repository Arc Bootstrap and v0.1.3 Generation Kickoff

---

## Mission

Continue from the attached complete repository:

```text
best_buds_cultivator_weight_station_v0_1_2.zip
```

Verified source repository SHA-256:

```text
811569270d8999054d7a5178b971699b03c1869e26a7af6ffacd17075df2130e
```

Create the next complete full-repository state:

```text
best_buds_cultivator_weight_station_v0_1_3
```

Target version:

```text
0.1.3
```

Bump scope:

```text
full_repo
```

Current internal phase:

```text
rc2_core_operator_loop_crash_safe_frontend_and_device_control
```

Next internal phase:

```text
rc3_physical_scale_integration_and_local_control_bridge
```

This is a complete repository bump. Do not create a detached patch, frontend-only pack, calibration mini-pack, simulator-only replacement, roadmap-only ZIP, or phase-only external archive.

The final deliverable must contain the entire preserved `v0.1.2` repository plus the new `v0.1.3` implementation, contracts, frontend, backend, tests, documentation, manifests, Context Module records, validation reports, Debian package, release state, and continuation handoff.

---

# Source truth and hardware posture

## Current repository truth

Treat `v0.1.2` as the current source repository.

Reported validated state:

- Complete full-repository package.
- Alice executable response-agent module.
- Append-only JSONL authority.
- Individual JSON records.
- Atomic checkpoints.
- Hash-chain and idempotency controls.
- Automatic and manual simulator workflows.
- Alice terminal-receipt validation.
- PySide6 and Tk frontends.
- Debian `0.1.2` installer.
- Windows build workflow with blocked native evidence.
- Firmware source with blocked compile evidence.
- Context Working Set sequences 1–3.
- Immutable Episodes 1–3.
- Context Ledger with 28 events.
- Resume Pack aligned to `0.1.2`.

Verify all claims against the imported repository before preserving them.

## Current Debian artifact

The full repository contains:

```text
dist/debian/best-buds-weight-station_0.1.2_amd64.deb
```

Verified Debian SHA-256:

```text
0a79e752326add399cfaebf6278ad1d6173265f7c18f325e54b15b2e47ee6283
```

Preserve the prior Debian artifact and receipt. Because packaged application source will change, build and validate a new Debian `0.1.3` package.

## Ordered hardware

The following hardware has been ordered for the physical-integration lane:

- 10 kg straight-bar load cell with upper and lower hooks.
- Three HX711 weighing-sensor amplifier modules.
- Breadboards for bench prototyping.
- PC-hosted operation first.
- A later target runtime on Arduino UNO Q.

Treat the ordered hardware as:

```text
ORDERED
```

Do not treat it as:

```text
DELIVERED
WIRED
COMPILED
CALIBRATED
PHYSICAL_DEVICE_PASS
```

No physical success may be claimed until actual evidence exists.

## Deployment sequence

### Current target

```text
10 kg load cell
    ↓
HX711
    ↓
Arduino-compatible controller
    ↓ USB serial
PC
    ↓
Best Buds Cultivator Weight Station
```

The PC remains responsible for:

- Frontend.
- Barcode input.
- Run setup.
- File location.
- Persistence.
- JSONL authority.
- Checkpoints.
- Crash recovery.
- Reports.
- Alice guidance.
- Validation receipts.

The controller remains responsible for:

- HX711 sampling.
- Zeroing.
- Calibration-factor application.
- Weight streaming.
- Device status.
- Bounded command handling.

### Later target

```text
10 kg load cell
    ↓
HX711
    ↓
UNO Q real-time controller side
    ↓ internal bridge
UNO Q Linux side
    ├── application backend
    ├── Alice
    ├── local persistence
    ├── crash recovery
    ├── frontend
    ├── Wi-Fi
    └── Bluetooth
```

Do not implement or claim the UNO Q runtime in `v0.1.3`. Preserve it as a later arc.

---

# Arc series

## v0.1.3 — Current bump

Internal phase:

```text
rc2_core_operator_loop_crash_safe_frontend_and_device_control
```

Implement:

- Simple production frontend.
- New-run creation.
- Configurable data location.
- Load existing run.
- Resume latest run.
- Save-state checkpoint after every committed plant.
- Crash-safe recovery.
- Real application-controller layer.
- Serial-device discovery and connection service.
- Continuous reading controller.
- Functional Zero Scale.
- Functional container-tare workflow.
- Guided calibration workflow.
- Canonical action layer.
- Local test hardware-button adapter.
- Bluetooth and Wi-Fi contract boundaries.
- No physical-success claim without evidence.

## v0.1.4 — Planned

Internal phase:

```text
rc3_physical_scale_integration_and_local_control_bridge
```

Planned scope:

- Delivered hardware inspection.
- Load-cell wire identification.
- HX711 wiring.
- Firmware compilation and upload.
- Physical serial discovery.
- Physical stream validation.
- Reference-weight calibration.
- Repeatability tests.
- Hanging-load tests.
- Full physical barcode-to-record loop.
- Local USB/GPIO/button controller.
- Physical evidence receipts.

## v0.1.5 — Planned

Internal phase:

```text
rc4_uno_q_hybrid_runtime_and_standalone_station_adapter
```

Planned scope:

- UNO Q Linux-side application package.
- UNO Q controller-side weight acquisition.
- Internal RPC or bridge contract.
- Offline local persistence.
- Crash-safe recovery.
- Browser or touchscreen kiosk frontend.
- Local service startup.
- UNO Q Wi-Fi and Bluetooth boundaries.
- Standalone-station evidence.

## v0.1.6 — Planned

Internal phase:

```text
rc5_bluetooth_wifi_transport_adapters_and_remote_command_governance
```

Planned scope:

- Bluetooth transport.
- Wi-Fi transport.
- Pairing and authentication.
- Device identity.
- Canonical-action normalization.
- Idempotency.
- Acknowledgement and terminal-result envelopes.
- Offline-first behavior.
- Remote authority limits.

## v0.1.7 — Planned

Internal phase:

```text
rc6_windows_native_packaging_and_cross_platform_operator_validation
```

Planned scope:

- Native Windows build.
- Windows installer or distributable.
- COM-port discovery.
- Barcode-scanner behavior.
- PySide6 execution.
- Crash recovery.
- Windows-native build and runtime receipts.

## v0.2.0 — Planned

Internal phase:

```text
rc7_integrated_field_release_candidate
```

Planned scope:

- Integrated hardware/software validation.
- Operator runbook.
- Recovery drills.
- Calibration evidence.
- Packaging audit.
- Field workflow.
- Release-candidate determination.
- No production or release seal without complete evidence.

Do not externally package future arcs during `v0.1.3`.

---

# Core product objective

The product must behave like a basic, reliable digital scale application.

The routine operator loop is:

```text
START OR RESUME RUN
        ↓
SCAN PLANT OR CONTAINER BARCODE
        ↓
HANG OR PLACE PLANT
        ↓
READ WEIGHT
        ↓
WAIT FOR STABLE WEIGHT
        ↓
AUTO RECORD
or
CONFIRM & RECORD
        ↓
WRITE AUTHORITATIVE RECORD
        ↓
WRITE CRASH-RECOVERY CHECKPOINT
        ↓
ALICE VALIDATES COMMIT RECEIPT
        ↓
SUCCESS FEEDBACK
        ↓
NEXT BARCODE
```

This loop must be implemented and tested.

Do not satisfy it with:

- Placeholder buttons.
- UI-only messages.
- Dormant schemas.
- Prompt-only documentation.
- Mock production callbacks.
- A simulator-only shell described as a physical application.
- In-memory-only run state.
- Manual Save as the only durability control.

---

# Frontend doctrine

The main weighing screen must remain simple.

The operator should not need to understand:

- JSONL.
- Hash chains.
- AoS envelopes.
- Serial protocol internals.
- Calibration-factor mathematics.
- Checkpoint internals.
- Context Module internals.

## Main screen

Display:

```text
CURRENT STATUS
CURRENT WEIGHT
BARCODE
CULTIVAR
CONTAINER
TARE
NET WEIGHT
LAST SAVED RECORD
```

Primary buttons:

```text
START / RESUME RUN
CONNECT SCALE
ZERO SCALE
SET CONTAINER TARE
CONFIRM & RECORD
CANCEL CURRENT ITEM
FINISH RUN
```

The production screen should not be crowded.

## Visible production states

Use simple operator language:

```text
NO RUN
READY TO SCAN
BARCODE SCANNED
WAITING FOR PLANT
WEIGHING
STABLE
RECORDING
SAVED
NOT SAVED
DEVICE DISCONNECTED
RECOVERY REQUIRED
RUN FINISHED
```

Do not expose every internal state-machine name directly.

## Main weight display

The current weight must be visually dominant.

Example:

```text
12,450.0 g
```

Also show:

```text
Gross: 12,550.0 g
Container tare: 100.0 g
Net: 12,450.0 g
```

## Settings and setup

Keep advanced options behind a Settings or Scale Setup screen:

- Data folder.
- Current run.
- New run.
- Load run.
- Resume latest run.
- Export destination.
- Automatic or manual capture.
- Serial port.
- Baud rate.
- Units.
- Stability settings.
- Container-tare library.
- Calibration.
- Device diagnostics.
- Hardware-button mappings.
- Bluetooth settings.
- Wi-Fi settings.

Bluetooth and Wi-Fi may remain disabled or unconfigured in this bump, but their contracts and configuration models must be real and validated.

## Accessibility

Require:

- Large controls.
- Keyboard access.
- Clear focus order.
- Text labels.
- No critical color-only status.
- High-contrast status messaging.
- Confirmation for destructive or maintenance actions.
- Operator-safe error language.
- Engineering details hidden behind Diagnostics.

---

# Run and file management

## Select data location

Allow the operator to select a writable data directory.

Validate:

- The path exists or can be created.
- The directory is writable.
- No path traversal occurs.
- An unrelated run is not overwritten.
- The location is retained according to settings policy.
- A failed location change does not damage the current run.

## New run

Provide a real New Run workflow.

Required fields may include:

- Harvest-run ID.
- Operator ID.
- Cultivar roster.
- Capture mode.
- Weight unit.
- Container/tare policy.
- Data directory.

The workflow must create actual repository-standard run files and directories.

Do not create an in-memory-only run.

## Load run

Allow the operator to select an existing run through:

- Run manifest.
- Session descriptor.
- Authoritative event ledger.
- Repository-standard run folder.

Validate:

- Schema.
- Run identifier.
- Hash chain.
- Checkpoint relationship.
- Required referenced artifacts.
- Supported version.

Reject invalid files without mutating them.

## Resume latest run

Provide:

```text
RESUME LAST RUN
```

Resolve it through a durable recent-run pointer or settings record.

Do not depend only on an in-memory variable.

## Save behavior

There must be no requirement to press Save after each plant.

Every successfully committed plant must automatically produce:

- Authoritative JSONL event.
- Individual JSON record.
- Updated checkpoint.
- Updated durable current-run pointer.
- Commit receipt.
- Alice validation.
- Success feedback.

A maintenance action such as:

```text
SAVE STATE NOW
```

may exist, but cannot replace commit-time autosave.

## Export

Keep export separate from authority.

Supported exports may include:

- JSON.
- CSV.
- XLSX.
- Reproducible run report.

Export failure after authoritative commit must not invalidate the plant record.

---

# Crash-safe persistence

## Required commit order

Enforce this logical order:

```text
1. Validate current run and action.
2. Build immutable plant-weight event.
3. Append event to authoritative JSONL.
4. Flush and fsync JSONL where supported.
5. Write individual record JSON to a temporary file.
6. Flush and fsync the temporary record.
7. Atomically rename the individual record.
8. Write checkpoint to a temporary file.
9. Flush and fsync the checkpoint.
10. Atomically replace the current checkpoint.
11. Update durable recent-run pointer.
12. Produce local commit receipt.
13. Alice validates the receipt.
14. UI shows SAVED.
15. UI emits success beep or light.
16. UI resets for next barcode.
```

When supported, fsync containing directories after atomic renames.

Do not claim durability beyond the actual platform implementation.

## Startup recovery

On application startup:

```text
Locate selected or latest run
→ validate authoritative JSONL
→ validate hash chain
→ inspect checkpoint
→ compare checkpoint with ledger
→ rebuild stale derived state
→ inspect temporary files
→ quarantine or safely remove incomplete artifacts
→ create recovery receipt
→ show last committed plant
→ return to correct state
```

Never restore:

- Uncommitted weight.
- In-memory-only weight.
- Invalid hash-chain data.
- A barcode whose pending state cannot be proven.
- Partial export output as authority.

## Failure-injection requirements

Test interruptions:

- Before JSONL append.
- During JSONL append.
- After JSONL append.
- Before individual JSON commit.
- After individual JSON.
- Before checkpoint.
- During checkpoint replacement.
- After checkpoint but before Alice acknowledgement.
- After receipt but before frontend reset.
- During export.
- During serial disconnect.

After restart:

- No committed plant is lost.
- No duplicate plant record is created.
- The last committed plant is shown.
- The next valid action is clear.
- Uncommitted weight is not invented.

---

# Core state machine

Implement or align these internal states:

```text
NO_RUN
RUN_SETUP
RUN_READY
DEVICE_DISCONNECTED
DEVICE_CONNECTING
DEVICE_READY
WAITING_FOR_BARCODE
BARCODE_CAPTURED
WAITING_FOR_LOAD
WEIGHING
WEIGHT_STABLE
MANUAL_CONFIRM
LOCAL_COMMIT_PENDING
ALICE_RECEIPT_VALIDATION
RECORD_SAVED
RECOVERY_REQUIRED
BLOCKED
ERROR
RUN_FINISHED
```

## Automatic mode

```text
Scan barcode
→ validate barcode
→ read weight
→ detect stability
→ submit record command
→ commit record
→ checkpoint
→ Alice receipt validation
→ success feedback
→ next barcode
```

## Manual mode

```text
Scan barcode
→ read weight
→ detect stability
→ show gross, tare, and net
→ operator presses Confirm & Record
→ commit record
→ checkpoint
→ Alice receipt validation
→ success feedback
→ next barcode
```

## Cancel Current Item

Cancellation may clear only uncommitted current-item state.

It must not delete or mutate a committed plant record.

---

# Device-control implementation

Implement a real device service.

At minimum:

- Enumerate candidate serial ports.
- Allow explicit port selection.
- Open connection.
- Close connection.
- Send `PING`.
- Read `STATUS`.
- Validate expected protocol.
- Start streaming.
- Stop streaming.
- Parse bounded messages.
- Detect malformed messages.
- Detect stale readings.
- Detect disconnect.
- Attempt controlled reconnect.
- Expose status to the frontend.
- Keep simulator mode explicitly separate.

A serial port opening is not by itself physical-device proof.

## Expected firmware command family

Preserve or align:

```text
PING
STATUS
TARE
READ
STREAM_ON
STREAM_OFF
SET_CAL,<factor>
SET_UNIT,g
```

Do not invent incompatible parallel protocols when the existing firmware contract is suitable.

---

# Scale functions

Treat these as separate operations.

## Zero Scale

Implement a real Zero Scale action:

```text
Block active capture
→ require safe zero condition
→ send TARE
→ wait for acknowledgement
→ collect near-zero readings
→ validate zero stability
→ write zero receipt
→ show SCALE ZEROED
```

A button that only changes text does not pass.

## Set Container Tare

Support two workflows.

### Capture tare

```text
Select container
→ hang or place empty container
→ wait for stable reading
→ use reading as container tare
→ store tare record
→ associate with container ID
```

### Enter known tare

```text
Select container
→ enter known tare
→ validate numeric bounds
→ record operator and source
→ save tare record
```

Use:

```text
net_weight = gross_weight - container_tare
```

Prevent invalid negative net values unless handled through an explicit correction workflow.

## Calibration

Implement a guided calibration wizard:

```text
1. Enter calibration mode.
2. Confirm no active plant capture.
3. Remove all load.
4. Zero scale.
5. Enter verified reference weight.
6. Hang or place reference weight.
7. Collect raw samples.
8. Calculate proposed factor.
9. Display spread, repeatability, and error.
10. Test proposed factor.
11. Require explicit acceptance.
12. Send SET_CAL,<factor>.
13. Read STATUS.
14. Verify accepted factor.
15. Write calibration receipt.
16. Return to device-ready state.
```

The workflow must be implemented in executable code and tests.

Do not claim:

- Legal-for-trade calibration.
- Regulatory certification.
- Physical calibration pass without hardware evidence.

---

# Canonical action layer

Create or complete a transport-neutral action boundary.

Recommended actions:

```text
run.new
run.load
run.resume
run.finish

settings.data_location.set
settings.capture_mode.set

device.discover
device.connect
device.disconnect
device.status

scale.zero
scale.container_tare.capture
scale.container_tare.set
scale.calibration.start
scale.calibration.sample
scale.calibration.test
scale.calibration.accept
scale.calibration.cancel

barcode.submit

capture.confirm
capture.cancel

state.flush
report.export
```

Every adapter must submit actions through the same controller.

The state machine decides whether the action is allowed.

---

# Future hardware controls

Prepare real contracts and a local test adapter for:

```text
Green button  → capture.confirm
Yellow button → scale.zero
Red button    → capture.cancel
Blue button   → open scale setup
```

Required path:

```text
button event
→ adapter
→ canonical action
→ state validation
→ application service
→ acknowledgement
→ terminal result
```

Do not connect buttons directly to persistence.

Calibration acceptance must require maintenance authorization and a second confirmation, long press, keyed mode, or equivalent protection.

---

# Bluetooth and Wi-Fi boundaries

Add validated, disabled-by-default contracts for:

- Device identity.
- Pairing or authentication.
- Bluetooth command input.
- Wi-Fi command input.
- Canonical-action mapping.
- Idempotency key.
- Acknowledgement envelope.
- Terminal-result envelope.
- Error envelope.
- Retry policy.
- Connection status.
- Offline behavior.

Restrictions:

- No anonymous commands.
- No direct JSONL writes.
- No bypass of state validation.
- No network dependency for local weighing.
- No remote calibration acceptance without local authorization.
- No duplicate records after retry.
- No remote success before local commit.
- Do not claim Bluetooth or Wi-Fi activation from scaffolding alone.

---

# Alice responsibilities

Alice remains the operator-facing guidance and truth layer.

Alice must:

- Explain the next action.
- Guide New Run.
- Guide Load Run.
- Guide Resume Last Run.
- Explain data-location errors.
- Guide device connection.
- Guide Zero Scale.
- Guide container tare.
- Guide calibration.
- Interpret stable-weight state.
- Interpret commit receipts.
- Guide recovery.
- Distinguish evidence classes.
- Prevent success language before valid commit and checkpoint evidence.

Alice must not:

- Directly write records.
- Invent identifiers.
- Bypass the state machine.
- Skip required setup.
- Treat simulator evidence as physical evidence.
- Claim certification.
- Claim Bluetooth, Wi-Fi, UNO Q, Windows, or physical hardware operation without evidence.

---

# Implementation rule

Every visible production button must have:

- A real callback.
- A real service invocation.
- State validation.
- Error handling.
- Operator feedback.
- Automated tests.

The following do not count as implementation:

- A button that only changes text.
- A print statement.
- A schema without executable code.
- A disabled placeholder described as complete.
- A test that only asserts a file exists.
- A simulator path labeled physical.
- An in-memory save described as crash proof.

Use the existing repository architecture. Do not create duplicate state machines, stores, envelope families, or disconnected frontends.

---

# Validation requirements

## Existing repository

1. Run the entire existing test suite.
2. Run Alice validators.
3. Run repository validators.
4. Parse all JSON.
5. Parse JSONL line by line.
6. Parse YAML.
7. Compile and import Python.
8. Verify versions.
9. Verify required paths.
10. Verify manifest hashes.
11. Validate full-repository archive shape.

## Run management

12. New-run creation.
13. Data-directory selection.
14. Invalid data-directory rejection.
15. Load existing run.
16. Invalid run rejection.
17. Resume latest run.
18. Durable recent-run pointer.
19. Finish run.
20. Export.

## Core loop

21. Automatic barcode-to-record loop.
22. Manual barcode-to-record loop.
23. Stable-weight detection.
24. Confirm & Record.
25. Cancel uncommitted item.
26. Next-barcode reset.
27. Duplicate rejection.
28. Gross/tare/net calculation.

## Persistence and recovery

29. Autosave after every plant.
30. JSONL commit.
31. Individual JSON commit.
32. Checkpoint commit.
33. Durable recent-run pointer update.
34. No success before Alice validation.
35. Crash before JSONL.
36. Crash during JSONL.
37. Crash after JSONL.
38. Crash after individual JSON.
39. Crash before checkpoint.
40. Crash after checkpoint.
41. Restart after receipt but before frontend reset.
42. Stale checkpoint rebuild.
43. Temporary-file handling.
44. Hash-chain recovery.
45. Duplicate prevention after restart.
46. Export failure after authoritative commit.

## Device control

47. Serial-port enumeration fixture.
48. Connect.
49. Disconnect.
50. PING.
51. STATUS.
52. Stream start.
53. Stream stop.
54. Bounded message parsing.
55. Malformed-line handling.
56. Stale-reading handling.
57. Disconnect handling.
58. Reconnect handling.
59. Simulator and physical mode separation.

## Zero, tare, and calibration

60. Zero command invocation.
61. Zero acknowledgement.
62. Zero stability validation.
63. Captured container tare.
64. Entered container tare.
65. Tare persistence.
66. Tare reload.
67. Net calculation.
68. Calibration-factor calculation.
69. Calibration sampling.
70. Calibration test.
71. Calibration acceptance.
72. Calibration rejection.
73. Calibration receipt.
74. Calibration blocked during active capture.

## Frontend

75. PySide6 New Run.
76. Tk New Run.
77. PySide6 Load/Resume.
78. Tk Load/Resume.
79. PySide6 automatic production loop.
80. Tk automatic production loop.
81. PySide6 manual production loop.
82. Tk manual production loop.
83. Every visible button callback.
84. Keyboard accessibility.
85. No critical color-only state.
86. Settings persistence.
87. Simple-screen usability review.

## Canonical actions

88. UI action mapping.
89. Keyboard action mapping.
90. Test-button action mapping.
91. Invalid-state action rejection.
92. Bluetooth contract validation.
93. Wi-Fi contract validation.
94. Idempotent remote-command model.

Do not weaken existing gates to obtain a pass.

---

# Evidence classes

Use:

```text
SOURCE_PRESENT
UNIT_TEST_PASS
SIMULATOR_PASS
UI_SMOKE_PASS
NATIVE_PLATFORM_PASS
PHYSICAL_DEVICE_PASS
BLOCKED
NOT_RUN
FAIL
NON_CLAIM
```

Examples:

- Serial service implemented: `SOURCE_PRESENT`
- Port fixtures pass: `UNIT_TEST_PASS`
- Simulator loop passes: `SIMULATOR_PASS`
- Real load cell streams correctly: `PHYSICAL_DEVICE_PASS`
- Arduino toolchain unavailable: `BLOCKED`
- UNO Q runtime not attempted: `NOT_RUN`

---

# Context Module update

Preserve:

- Working Set sequences 1–3.
- Episodes 1–3.
- All existing Ledger events.
- Resume Pack history.
- Existing source hashes.
- Existing continuation handoffs.

For `v0.1.3`:

- Add Working Set update sequence `4`.
- Add immutable Episode `episode_0004_v0.1.3.json`.
- Append Ledger events for:
  - Source inspection.
  - Drift review.
  - Core implementation.
  - Frontend implementation.
  - Persistence testing.
  - Recovery testing.
  - Device-service testing.
  - Calibration testing.
  - Packaging.
  - Final validation.
- Update Resume Pack to `0.1.3`.
- Update continuation handoff.
- Record source artifact hashes.
- Validate JSON and JSONL.
- Confirm context version alignment.

Do not claim Context Module runtime execution unless it actually ran.

---

# Repository metadata

Update `repo_release_state.json` with at least:

```json
{
  "package_name": "best_buds_cultivator_weight_station",
  "previous_version": "0.1.2",
  "version": "0.1.3",
  "bump_scope": "full_repo",
  "current_internal_phase": "rc2_core_operator_loop_crash_safe_frontend_and_device_control",
  "next_internal_phase": "rc3_physical_scale_integration_and_local_control_bridge",
  "source_of_truth": [],
  "drift_check_status": "pending",
  "validation_status": "pending",
  "context_update_status": "pending",
  "core_operator_loop_status": "pending",
  "frontend_status": "pending",
  "crash_recovery_status": "pending",
  "device_control_status": "pending",
  "tare_status": "pending",
  "calibration_status": "pending",
  "physical_device_status": "pending",
  "non_claims": []
}
```

Replace `pending` only with evidence-backed results.

---

# Required non-claims

Preserve or add:

- No physical UNO success unless executed.
- No physical HX711 success unless executed.
- No physical load-cell success unless executed.
- No physical calibration or hanging-load success unless executed.
- No legal-for-trade certification.
- No firmware compile pass without toolchain evidence.
- No native Windows pass without Windows evidence.
- No UNO Q runtime claim.
- No Bluetooth activation claim.
- No Wi-Fi activation claim.
- No physical-button activation claim.
- No Metrc integration.
- No seed-to-sale replacement.
- No production-readiness claim.
- No release seal.
- No Context Module runtime claim unless executed.
- No Google Drive upload claim without returned connector evidence.

---

# Packaging

Produce:

```text
best_buds_cultivator_weight_station_v0_1_3.zip
best_buds_cultivator_weight_station_v0_1_3.zip.sha256
```

Also build, when the Debian packaging lane remains available:

```text
best-buds-weight-station_0.1.3_amd64.deb
best-buds-weight-station_0.1.3_amd64.deb.sha256
```

The ZIP must contain the full repository.

Preserve prior packages, receipts, contracts, reports, Context records, and release phases.

Do not fabricate:

- Windows executables.
- Firmware binaries.
- Physical-device receipts.
- UNO Q receipts.
- Bluetooth evidence.
- Wi-Fi evidence.
- Release seals.

---

# Final acceptance gate

Before packaging, verify:

1. Version is consistently `0.1.3`.
2. The package is a full repository.
3. No detached subpackage exists.
4. Prior repository state is preserved.
5. The frontend is a real operator application.
6. New Run works.
7. Data-location selection works.
8. Load Run works.
9. Resume Last Run works.
10. Every committed plant writes crash-recovery state.
11. Startup recovery works.
12. Automatic capture works.
13. Manual capture works.
14. Zero Scale invokes the device service.
15. Container tare works.
16. Guided calibration works.
17. Serial device service is integrated.
18. Canonical actions route correctly.
19. Test hardware-button mapping works.
20. Bluetooth boundaries validate.
21. Wi-Fi boundaries validate.
22. Alice gates success.
23. JSON, JSONL, YAML, and Python validation pass.
24. All tests pass.
25. Manifest verification passes.
26. Final ZIP membership and CRC pass.
27. Evidence classes match actual execution.
28. Context records align to `0.1.3`.

---

# Final response format

State:

- New version.
- Full-repository bump status.
- Core loop implementation.
- Frontend implementation.
- New Run result.
- Data-location result.
- Load result.
- Resume result.
- Autosave result.
- Crash-recovery result.
- Automatic capture result.
- Manual capture result.
- Zero Scale result.
- Container-tare result.
- Calibration result.
- Serial-device result.
- Canonical-action result.
- Hardware-button boundary result.
- Bluetooth boundary result.
- Wi-Fi boundary result.
- Simulator result.
- Physical-device result.
- Firmware result.
- Windows result.
- Debian result.
- Drift found.
- Working Set update.
- Episode added.
- Ledger events appended.
- Resume Pack update.
- Context validation.
- Non-claims.
- ZIP SHA-256.
- Download links.

Do not describe schemas, placeholders, disabled adapters, simulator fixtures, or unexecuted hardware as completed runtime capability.

Begin by inspecting the attached complete `v0.1.2` repository.
