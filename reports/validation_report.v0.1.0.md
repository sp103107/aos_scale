# Validation Report v0.1.0

Generated: `2026-07-19T15:40:04Z`

**Core implementation:** PASS  
**Complete requested release gate:** BLOCKED

The source runtime, simulator workflow, append-only storage, spreadsheet/report outputs, AoS envelopes, and native Debian package lane passed. The native Windows executable, Arduino compile, and physical hardware lanes remain blocked and are not represented as passing.

## Evidence summary

| Lane | Result | Evidence |
|---|---|---|
| JSON/JSONL/YAML/Python/repo shape | PASS | `validation/static_validation.json` |
| Contract schemas | PASS (22) | `validation/schema_and_export_validation.json` |
| Tests | PASS (17) | `validation/pytest_output.txt` |
| Simulator automatic/manual capture | PASS (simulated) | `validation/persistent_simulator_self_test.json` |
| JSON, JSONL, CSV, XLSX and reports | PASS (simulated fixture) | `validation/fixtures/sessions/SELFTEST-SESSION/` |
| Debian `.deb` native build/install/smoke | PASS | `reports/debian_packaging_receipt.v0.1.0.json` |
| Windows native executable | BLOCKED | `reports/windows_packaging_receipt.v0.1.0.json` |
| Arduino native compile | BLOCKED | `reports/firmware_compile_receipt.v0.1.0.json` |
| UNO/HX711/load-cell physical test | NOT RUN | No hardware receipt |
| Full repo ZIP shape preflight | PASS | `validation/package_zip_validation.json` |
| Google Drive binary delivery | BLOCKED; folder + native receipt Doc created | `reports/drive_delivery_receipt.v0.1.0.json` |

## Drift

- The declared `best_buds_cultivator_weight_station_contract_bundle_v0_1_0.zip` was unavailable. Its expected SHA-256 is preserved; the checksum-valid kickoff pack and Drive transcript were used without claiming full source concordance.

## Non-claims

- No physical hardware success.
- No legal-for-trade certification.
- No Metrc or seed-to-sale integration.
- No Windows packaging pass.
- No Arduino compile pass.
- No production-readiness or release-seal claim.
