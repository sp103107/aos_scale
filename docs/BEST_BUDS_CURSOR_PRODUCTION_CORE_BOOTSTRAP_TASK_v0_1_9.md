# Best Buds Cultivator Weight Station
## Cursor Production-Core Bootstrap and Arc Execution Task

**Source repository:** `best_buds_cultivator_weight_station_v0_1_9`
**Source version:** `0.1.9`
**Initial target version:** `0.1.10`
**Bump scope:** `full_repo`
**Execution posture:** `production_candidate`
**Claim posture:** evidence-gated; no false-green promotion

---

## 1. Mission

Take the complete `v0.1.9` repository and advance it through the next production-core arcs using the repository's Arc Launcher, JSON stage runner, Context Module, validation system, and full-repo bump law.

Do not create detached patches, phase-only ZIPs, validator-only packs, frontend-only packs, or roadmap-only outputs.

The first deliverable is the complete repository state:

```text
best_buds_cultivator_weight_station_v0_1_10/
```

The `v0.1.10` objective is **Judge core hardening and release-truth closure**. Later arcs are mapped below but must not be falsely marked complete.

---

## 2. Source-of-truth order

Inspect these before editing:

1. `VERSION`
2. `repo_release_state.json`
3. `README.md`
4. `CHANGELOG.md`
5. `docs/SYSTEM_STATE_CURRENT.md`
6. `guide_pack.json`
7. `pyproject.toml`
8. `release_candidate/rc_phase_matrix.v0.1.9.json`
9. `pipeline/stage_catalog.v0.1.9.json`
10. `pipeline/plans/cursor_ready.v0.1.9.json`
11. `pipeline/plans/operator_ready.v0.1.9.json`
12. `pipeline/plans/physical_integration_prerequisites.v0.1.9.json`
13. `reports/core_process_audit.v0.1.9.json`
14. `reports/drift_concordance.v0.1.9.json`
15. `context/working_set/`
16. `context/episodes/`
17. `context/ledger/`
18. `context/resume_pack/`
19. `cursor/CURSOR_UNO_R3_PHYSICAL_INTEGRATION_HANDOFF_V0_1_9.md`
20. `contracts/runtime/`, `contracts/pipeline/`, and all persistence/device contracts

Treat `v0.1.9` as the canonical input snapshot. Preserve all historical evidence and phase records.

---

## 3. Known Judge findings to close in v0.1.10

The current `repo_release_state.json` contains two blocking release-truth defects:

```text
final_validation_report = reports/repo_validator.v0.1.8.json
package_validation_status = pending_zip
```

Correct these only after generating current-version evidence.

Also close the following production-core deficiencies where software-only implementation and local evidence are possible:

- Current-version final receipt pointers
- Finalized package-validation state
- Strict no-pending/no-prior-version validator
- Automatic CI triggers and protected-gate documentation
- Dependency vulnerability scan lane
- Secret scan lane
- Static security-analysis lane
- SBOM generation
- Immutable dependency inventory
- Disk-full and low-storage behavior
- Permission-denied behavior
- File-lock contention behavior
- Backup and restore rehearsal
- Ledger-to-export reconciliation
- Calibration lifecycle contracts
- Device identity contracts
- Record correction and void contracts
- Supervisor review contracts
- Operator/auditor role boundaries

Do not claim native Windows, physical device, firmware, production grade, or release seal unless direct evidence is produced.

---

## 4. Arc chain

### ARC P0 — Release Truth Closure

**Target:** `v0.1.10`

**Internal phase:**

```text
rc3c14_judge_core_hardening_and_release_truth_closure
```

**Required implementation:**

- Generate a current `repo_validator.v0.1.10.json`.
- Generate a current package-validation receipt.
- Update `final_validation_report` to the current receipt.
- Change `package_validation_status` only after ZIP verification.
- Add a validator that rejects:
  - `pending*` final states
  - current files pointing to prior-version receipts
  - missing package hashes
  - absent current Context pointers
  - unresolved required Judge blockers
- Add a Judge evidence matrix for all production-core domains.
- Add explicit `accepted`, `rejected`, `blocked`, and `not_run` verdict semantics.

**Exit gate:**

```text
RELEASE_TRUTH_CLOSED
PRODUCTION_CORE_NOT_YET_CLAIMED
```

---

### ARC P1 — CI, Supply Chain, and Security Baseline

**Proposed target:** `v0.1.11`

**Internal phase:**

```text
rc3c15_ci_supply_chain_and_security_baseline
```

**Required implementation:**

- Trigger CI on pull request and protected release branches.
- Preserve manual dispatch.
- Add pinned tool versions where practicable.
- Add dependency inventory and lock strategy.
- Generate CycloneDX or SPDX SBOM.
- Add secret scanning.
- Add dependency vulnerability scanning.
- Add Python static security analysis.
- Add artifact checksum verification.
- Add signing interfaces as candidates if signing keys are unavailable.
- Add security non-claim report.

**Exit gate:**

```text
SECURITY_BASELINE_PASS
ARTIFACT_SIGNING_NOT_CLAIMED unless proven
```

---

### ARC P2 — Persistence, Durability, and Recovery Qualification

**Proposed target:** `v0.1.12`

**Internal phase:**

```text
rc3c16_persistence_durability_and_recovery_qualification
```

**Required implementation:**

- Long-run simulated record test.
- Disk-full fault injection.
- Permission-denied fault injection.
- File-lock contention test.
- Abrupt termination during each persistence boundary.
- Backup creation and verification.
- Restore into clean application data directory.
- Ledger/record/checkpoint reconciliation.
- Export reconciliation against authoritative ledger.
- Archive/retention policy contracts.
- Low-storage warning and operator instruction.

**Exit gate:**

```text
SOFTWARE_DURABILITY_QUALIFIED
REAL_WINDOWS_POWER_LOSS_NOT_CLAIMED
```

---

### ARC P3 — Operational Governance and Audit Controls

**Proposed target:** `v0.1.13`

**Internal phase:**

```text
rc3c17_operational_governance_calibration_and_audit_controls
```

**Required implementation:**

- Operator, supervisor, and auditor role contracts.
- Non-destructive correction workflow.
- Void/supersede records without deleting history.
- Reason codes and approval receipts.
- Calibration identity, effective date, expiry, and evidence linkage.
- Device identity binding and wrong-device warnings.
- Clock/timestamp governance.
- Shift handoff and audit review reports.
- Incident and support procedures.
- Installation qualification, operational qualification, and performance qualification templates.

**Exit gate:**

```text
OPERATIONAL_GOVERNANCE_IMPLEMENTED
QUALIFICATION_EXECUTION_NOT_CLAIMED
```

---

### ARC P4 — Native Windows Qualification

**Proposed target:** `v0.1.14`

**Internal phase:**

```text
rc3c18_native_windows_runtime_installer_and_device_qualification
```

**Required evidence on an actual Windows host:**

- PySide6 launch and render.
- Barcode keyboard-wedge input.
- Serial-port discovery.
- Disconnect/reconnect behavior.
- Clean shutdown.
- Installer execution.
- Upgrade and uninstall behavior.
- User data path and permissions.
- Sleep/resume.
- USB removal/reinsertion.
- Windows artifact hash and build receipt.

**Exit gate:**

```text
WINDOWS_NATIVE_RUNTIME_PASS
```

Do not complete this arc on Linux-only evidence.

---

### ARC P5 — Physical Scale Bring-Up

**Proposed target:** `v0.1.15`

**Internal phase:**

```text
rc3d_uno_r3_hx711_physical_scale_bringup
```

**Required evidence:**

- Firmware compile.
- Firmware upload.
- UNO R3 identification.
- HX711 communication.
- Raw sample stability.
- Zero and tare.
- Calibration with traceable known mass.
- Protocol conformance.
- USB disconnect/reconnect.
- Power-cycle recovery.

**Exit gate:**

```text
PHYSICAL_SCALE_BRINGUP_PASS
```

---

### ARC P6 — Measurement Qualification

**Proposed target:** `v0.1.16`

**Internal phase:**

```text
rc3e_measurement_repeatability_accuracy_and_load_qualification
```

**Required evidence:**

- Accuracy at multiple known masses.
- Repeatability.
- Hysteresis.
- Creep.
- Drift over time.
- Off-axis/corner loading where applicable.
- Overload behavior.
- Calibration persistence.
- Recalibration workflow.
- Environmental notes.

**Exit gate:**

```text
MEASUREMENT_QUALIFICATION_PASS
LEGAL_FOR_TRADE_NOT_CLAIMED
```

---

### ARC P7 — End-to-End Production Candidate

**Proposed target:** `v0.1.17`

**Internal phase:**

```text
rc3f_end_to_end_scan_weigh_record_recover_and_audit_candidate
```

**Required evidence:**

- Barcode scan.
- Stable physical weight.
- Correct tare/net calculation.
- Authoritative commit.
- Receipt generation.
- Application restart.
- Run resume.
- Last record restoration.
- Export reconciliation.
- Supervisor correction/void.
- Backup and restore.
- Operator acceptance script.

**Exit gate:**

```text
PRODUCTION_CANDIDATE_PASS
PRODUCTION_READY_NOT_YET_CLAIMED
```

---

### ARC P8 — Production-Grade Judge Gate

**Proposed target:** `v0.1.18`

**Internal phase:**

```text
rc3g_production_grade_evidence_matrix_and_judge_acceptance
```

**Judge must inspect:**

- Release truth
- Current receipts
- CI/security
- SBOM and dependency state
- Durability and recovery
- Operational governance
- Native Windows evidence
- Physical-scale evidence
- Measurement qualification
- End-to-end operator evidence
- Documentation
- Context continuity
- Package integrity
- Non-claims

**Possible verdicts:**

```text
PRODUCTION_GRADE_ACCEPTED
PRODUCTION_GRADE_REJECTED
PRODUCTION_GRADE_BLOCKED
```

Do not generate a release seal in this arc unless every required gate passes.

---

### ARC P9 — Release Seal and Controlled Deployment

**Proposed target:** `v0.2.0`

**Internal phase:**

```text
rc4_release_seal_controlled_deployment_and_support_readiness
```

**Required evidence:**

- Explicit Judge acceptance.
- Immutable package inventory.
- Final ZIP and installer hashes.
- Signed artifacts where authorized and available.
- Installation, rollback, backup, and support instructions.
- Known limitations.
- Deployment checklist.
- Release-state finalization.

**Exit gate:**

```text
RELEASE_SEAL_PASS
```

---

## 5. Cursor bootstrap order of operations

Execute in this order.

### Step 1 — Establish immutable source intake

```powershell
Get-FileHash .\best_buds_cultivator_weight_station_v0_1_9.zip -Algorithm SHA256
Expand-Archive .\best_buds_cultivator_weight_station_v0_1_9.zip -DestinationPath .\work
Set-Location .\work\best_buds_cultivator_weight_station_v0_1_9
```

Record the input hash in:

- `repo_release_state.json`
- bump Working Set
- bump Episode
- Ledger
- source-intake report

### Step 2 — Run repository preflight before mutation

```powershell
.\cursor_bootstrap.ps1 -Plan cursor_ready
python -m best_buds_weight_station.stage_runner status --json
python -m best_buds_weight_station.stage_runner validate-receipts
```

Stop on any unexpected failure. Do not edit around a failing source-truth gate without recording the defect.

### Step 3 — Create the v0.1.10 full-repo working state

Copy the complete repository to:

```text
best_buds_cultivator_weight_station_v0_1_10/
```

Update current-version surfaces only. Preserve historical versioned records.

### Step 4 — Add the Arc Launcher plan

Create:

```text
pipeline/plans/production_core_bootstrap.v0.1.10.json
pipeline/stage_catalog.v0.1.10.json
release_candidate/rc_phase_matrix.v0.1.10.json
```

Add stages for:

```text
110_release_truth_closure
120_ci_policy_validation
130_security_baseline
140_sbom_dependency_inventory
150_storage_fault_injection
160_backup_restore_reconciliation
170_operational_governance_contracts
180_judge_production_core_gate
190_full_repo_package_validation
```

Each stage must declare dependencies, allowed mutations, forbidden mutations, commands, pass conditions, evidence paths, resume behavior, and non-claims.

### Step 5 — Implement ARC P0 completely

Correct release-state drift and add strict validators. Do not merely edit the JSON fields; generate current evidence first and bind the fields to that evidence.

### Step 6 — Implement software-only portions of P1 through P3

Implement contracts, validators, tests, CI configuration, security lanes, durability tests, backup/restore, reconciliation, calibration lifecycle, device identity, correction/void, and supervisor review.

Do not mark Windows-native or hardware arcs complete.

### Step 7 — Run tests and evidence lanes

Minimum commands:

```powershell
python -m pytest -q
python -m best_buds_weight_station.stage_runner run-plan --plan production_core_bootstrap
python -m best_buds_weight_station.stage_runner validate-receipts
python scripts\validate_release_truth.py
python scripts\validate_context_module.py
python scripts\validate_package_shape.py
```

Run all newly added security and durability commands. Capture stdout, stderr, exit code, timestamps, and artifact hashes.

### Step 8 — Update Context Module

- Preserve prior Working Sets.
- Add the next Working Set sequence.
- Add an immutable episode checkpoint.
- Append Ledger events.
- Update Resume Pack pointers.
- Add continuation handoff.
- Record source and output hashes.
- Do not claim Context runtime execution unless actually executed.

### Step 9 — Judge gate

The Judge must reject the bump if any of the following remain in a finalized current release state:

- `pending`
- prior-version final receipt pointer
- absent current package hash
- missing Context pointer
- missing stage receipt
- simulator result labeled physical
- Linux result labeled Windows-native
- source presence labeled runtime proof
- skipped security gate labeled pass

### Step 10 — Package the complete repo

Produce:

```text
best_buds_cultivator_weight_station_v0_1_10.zip
best_buds_cultivator_weight_station_v0_1_10.zip.sha256
```

The ZIP must contain the full repository state, not only new arc files.

### Step 11 — Validate the extracted ZIP independently

Extract the final ZIP into a clean directory and rerun:

- version concordance
- JSON/JSONL parsing
- manifest hashes
- exact membership
- forbidden-path scan
- current release-state truth
- Context alignment
- stage-plan validation
- repository validator

### Step 12 — Produce the next Cursor handoff

The handoff must state:

- Completed version and phase
- Added implementation
- Preserved history
- Drift found and corrected
- Validation evidence
- Remaining blockers
- Explicit non-claims
- Exact next arc
- Exact bootstrap command

---

## 6. Required v0.1.10 release-state posture

At package finalization, use evidence-backed values equivalent to:

```json
{
  "previous_version": "0.1.9",
  "version": "0.1.10",
  "bump_scope": "full_repo",
  "current_internal_phase": "rc3c14_judge_core_hardening_and_release_truth_closure",
  "next_internal_phase": "rc3c15_ci_supply_chain_and_security_baseline",
  "execution_posture": "production_candidate",
  "execution_authorized": true,
  "evidence_required": true,
  "claim_gate_required": true,
  "package_validation_status": "pass",
  "production_ready_claimed": false,
  "production_grade_status": "not_run_or_rejected",
  "release_seal_claimed": false,
  "windows_native_runtime_status": "NOT_RUN",
  "physical_device_status": "not_run"
}
```

Do not copy this mechanically. Bind every final status to generated evidence.

---

## 7. Forbidden claims

Until the corresponding arc is executed with direct evidence, do not claim:

- Native Windows pass
- PySide6 native pass
- Firmware compile or upload pass
- UNO R3 pass
- HX711 pass
- Physical calibration pass
- Measurement accuracy pass
- Legal-for-trade status
- Production readiness
- Production-grade acceptance
- Release seal
- Artifact signing
- Live VPort, socket, message bus, or MCP activation

---

## 8. Definition of success for this Cursor task

The first Cursor execution is successful when it returns a complete `v0.1.10` repository with:

```text
RELEASE_TRUTH_CLOSED
CORE_HARDENING_IMPLEMENTED
CURRENT_RECEIPTS_BOUND
CONTEXT_UPDATED
PACKAGE_VALIDATED
CURSOR_CONTINUATION_READY
PRODUCTION_READY_FALSE
PHYSICAL_HARDWARE_NOT_RUN
WINDOWS_NATIVE_RUNTIME_NOT_RUN
```

