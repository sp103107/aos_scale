# LLM Validation Harness v0.1.4

The harness is a CLI-first machine interface for Cursor, Codex, and similar coding agents. It probes capabilities, applies profile-aware safe drift repair, enforces lane dependencies, executes real commands, writes JSON receipts, and preserves physical truth.

## Profiles

- **development**: safe current metadata repair; historical evidence immutable.
- **integration**: current metadata and software gates are hard; physical gates remain explicit.
- **release**: no unresolved current drift and all required runtime evidence must pass.

## Non-claims

The harness does not convert source presence, schemas, simulator fixtures, or connected serial ports into physical success. Firmware, serial, zero/tare, calibration, and the physical loop require executed evidence.
