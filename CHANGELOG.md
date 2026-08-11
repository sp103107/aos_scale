## 2.0.0-rc3 — Scale Face harvest mode (SR8)

- Added PySide **Scale Face (Harvest)** mode (View → Scale Face / Ctrl+Shift+F) sharing OperatorRuntime and capture law.
- Harvest/SETUP toggle: hang-side Lock/Confirm strip plus Connect/Zero/Tare/Calibrate/Test Scanner without leaving the face.
- Hero weight freezes via `frozen_display_weight` while locked; barcode + SCAN and last 1–3 records strip on the face.
- Full desktop `ROUTINE_ACTION_LAYOUT` remains eight actions; Esc exits Scale Face back to MainWindow.
- Bumped product version surfaces to 2.0.0-rc3 with a new drift concordance gate; archival rc2 receipts unchanged.

## 2.0.0-rc2 — Windows installer bring-up and run-lifecycle UX fixes (SR7)

- Finish Run now completes from the post-save idle state and the UI renders a clear RUN FINISHED closeout with an export door.
- The main weight display freezes at the locked value during Confirm & Record; live readings resume after confirm/cancel.
- Added a Resume Run picker (PySide6 dialog + Tk parity) listing in-progress runs under the data root.
- First-run data root now seeds from per-user platform paths so installed/frozen executables never write beside the exe.
- Windows packaging: PyInstaller onedir exe, zip, and Inno Setup 6 per-user Setup.exe with build/install receipts.
- Bumped product version surfaces to 2.0.0-rc2 with a new drift concordance gate; archival v0.1.9 artifacts unchanged.

## 2.0.0-rc1 — Product onboarding release (SR6)

- Human and coding-agent onboarding doors, drift concordance gate, and GitHub Release with clean source zip.

## 0.1.9 — Core-process closure and final Cursor hardening

- Added a deterministic core-process audit covering launch surfaces, run lifecycle, automatic/manual capture, durable commit, recovery, zero, tare, calibration, canonical pyserial boundaries, stage orchestration, and non-claim enforcement.
- Added explicit implementation-status inventory so source-present, simulator-proven, blocked, and physical-not-run surfaces cannot be conflated.
- Hardened current-release concordance and corrected current metadata to 0.1.9 while preserving historical evidence.
- Preserved Windows-first PySide6 source, Linux/Tk runtime evidence, Debian packaging, Context history, and all physical-hardware non-claims.
- USB serial connection hardening (focused): selectable 115200/9600 baud (default 115200), truthful failed-connect error propagation, device-neutral settings/contracts, aligned firmware PING/`A,PONG` handshake, and regressions in `tests/test_usb_serial_settings.py`, `tests/test_device_service.py`, and `tests/test_operator_runtime.py`.

# Changelog

## 0.1.8 - Final frontend polish and drift review

- Corrected the Tk and PySide routine-action grids so `CONFIRM & RECORD`, `CANCEL`, and `FINISH RUN` occupy non-overlapping cells.
- Added an explicit `PLANT OR CONTAINER BARCODE` label, scanner instructions, and accessible descriptions to both frontend paths.
- Changed connected physical-serial status from success coloring to an amber `TESTING REQUIRED` evidence state.
- Added a shared `operator_surface.py` layout contract with executable overlap validation.
- Removed dead callback stubs that existed only to satisfy source-text tests.
- Removed generated Python `.egg-info` content from the repository package.
- Corrected current frontend runtime metadata, release-phase duplication, current test naming, stage references, and generated timestamps.
- Hardened drift validators to distinguish current surfaces, immutable historical evidence, and explicit compatibility references.
- Hardened LLM stage and bootstrap commands with file-backed subprocess output, deterministic termination, and source-copy installation preflight so validation does not leave generated `.egg-info` in the repository.
- Replaced raw evidence-class footer text with operator-facing scale status while preserving engineering truth in receipts and diagnostics.
- Added Context Working Set sequence 9, Episode 9, Ledger events, Resume Pack update, and final Cursor handoff alignment.
- Preserved Windows-native, PySide-native, firmware, physical-scale, certification, production-grade, and release-seal non-claims.

## 0.1.7 — Frontend polish, resumable LLM stages, and final pre-hardware concordance

- Polished the Windows-first PySide6 operator layout and the executable Tk fallback around seven routine scale actions.
- Added persistent simulator truth, large weight hierarchy, operator-language Alice guidance, last-save confirmation, and advanced setup/diagnostic menus.
- Added shared frontend design tokens and Windows-light theme assets.
- Canonicalized physical capture on `PySerialTransport -> DeviceService -> ScaleReadingWorker -> reading.ingest`; marked `SerialScale` as legacy compatibility only.
- Added seven JSON pipeline contract schemas, eleven machine-readable stage definitions, three bootstrap plans, resumable checkpoints, and immutable stage receipts.
- Added `best-buds-weight-station-stage` plus Windows and Linux Cursor bootstrap, run-stage, and resume-stage wrappers.
- Executed the full `cursor_ready` plan: 11/11 stages passed with `CURSOR_READY` and `OPERATOR_SOFTWARE_READY` verdicts.
- Added runtime evidence contracts, claim gates, surface-entry mesh, pod/capsule lineage, candidate VPort/socket cards, and Tree-sitter readiness records.
- Added Tk/Xvfb frontend render evidence; PySide6 and native Windows runtime remain not run in this Linux environment.
- Preserved physical UNO R3, HX711, load-cell, firmware upload, certification, production-grade, and release-seal non-claims.

## 0.1.6 — Windows-first operator application implementation

- Added Windows-primary `.bat` and PowerShell launchers plus Linux shell parity for application, simulator, coding-agent bootstrap, and validation.
- Added platform-aware Windows `%LOCALAPPDATA%` and Linux XDG storage paths.
- Implemented a PySide6 primary operator application and a functional Tk fallback.
- Replaced the placeholder Scale Setup route with serial discovery, explicit connection, PING, STATUS, disconnect, simulator controls, and device truth display.
- Added a background reading worker that routes samples through canonical `reading.ingest` without writing persistence directly.
- Removed synthetic zero samples from physical-mode UI actions.
- Added known and captured container tare workflows and a guided calibration dialog.
- Added Windows PyInstaller build, verify, install, and uninstall source.
- Added `operator-ready` validation profile, launcher validation, frontend runtime-truth validation, Windows source validation, and scripted operator-runtime acceptance.
- Preserved all prior persistence, recovery, Alice receipt, Context Module, Debian, firmware, and non-claim evidence.
- Native Windows execution, firmware, and physical hardware remain unclaimed.

## 0.1.5

- Added `python -m best_buds_weight_station.bootstrap` and the `best-buds-weight-station-bootstrap` console entry point.
- Added the `prehardware` validation profile and software-only bootstrap graph.
- Added executable software dry runs for automatic/manual capture, load/resume, zero, tare, calibration, Alice receipt gating, and canonical adapters.
- Added recovery-matrix, Tk runtime smoke, and isolated package-install preflight lanes.
- Fixed run manifests to derive `application_version` from the current package version instead of a stale literal.
- Added machine-readable bootstrap and dry-run schemas, tests, receipts, Context Module sequence 6, Episode 6, and continuation handoff.
- Preserved all physical, firmware, Windows, Bluetooth, Wi-Fi, UNO Q, certification, production, and release-seal non-claims.

## 0.1.4

- Added LLM-native validation harness, validation profiles, dependency graph, safe current-metadata repair, machine-readable receipts, and explicit physical evidence gates.
- Added RC3 internal arc map for Cursor-executed firmware and physical integration.
- Preserved all v0.1.3 implementation and evidence.


## 0.1.3 — Core operator loop, crash-safe frontend, and device control

### Added

- Production `ApplicationController` with a transport-neutral canonical action layer.
- Durable New Run, Load Run, Resume Last Run, Finish Run, data-location, and recent-run-pointer services.
- Full production operator UI entrypoint for PySide6 and Tk with large controls, keyboard routes, text status, Alice guidance, and real callbacks.
- Serial-device service for discovery, connection, PING, STATUS, READ, streaming, bounded parsing, stale readings, disconnect, and controlled reconnect.
- Functional zero, captured/known container tare, and guided calibration services.
- Local hardware-button test adapter and protected calibration-acceptance boundary.
- Disabled-by-default Bluetooth and Wi-Fi identity/authentication/idempotency contracts.
- Run, settings, action, device, zero, tare, calibration, remote transport, and button schemas.
- Working Set update 4, Episode 4, additional Ledger events, Resume Pack `0.1.3`, and continuation handoff.

### Hardened

- Commit order now includes a durable recent-run pointer before receipt acknowledgement.
- Atomic rename paths perform best-effort parent-directory fsync and record the platform boundary.
- Startup recovery quarantines interrupted final JSONL fragments and incomplete temporary files.
- Recovery rebuilds missing individual records, stale checkpoints, and receipts for authoritative commits interrupted before Alice acknowledgement.
- Automatic and manual loops continue to require Alice terminal-receipt validation before feedback and progression.

### Preserved

- Complete `0.1.2` source, contracts, reports, packages, release-candidate history, validation evidence, and Context records.
- Native Debian `0.1.2` artifact with verified SHA-256 `0a79e752326add399cfaebf6278ad1d6173265f7c18f325e54b15b2e47ee6283`.
- Blocked Windows, firmware-compile, and physical-hardware evidence.

### Non-claims

No physical scale, firmware compile, Windows-native, UNO Q, Bluetooth, Wi-Fi, legal-for-trade, production-readiness, or release-seal pass is claimed without execution evidence.

## 0.1.2

Alice terminal-receipt/UI progression and evidence-hygiene hardening.

## 0.1.1

Alice response-agent implementation and persistence-truth hardening.

## 0.1.0

Initial full repository, simulator, and native Debian package.
