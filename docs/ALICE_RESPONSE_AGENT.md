# Alice Response Agent

Alice is the operator-facing response, command-proposal, and gatekeeping module. Alice consumes typed application state, operator input, command results, validation receipts, and recovery conditions. Alice produces structured operator guidance; she does not execute persistence or mutate the event ledger.

## Module surfaces

- `response_agent.py`: orchestration entry point.
- `response_models.py`: typed structured response model and truth classes.
- `authority.py`: allowed-action matrix, redaction, and operator-safe errors.
- `state_interpreter.py`: deterministic state-to-guidance mapping.
- `command_builder.py`: AoS envelope command proposals.
- `receipt_interpreter.py`: local commit, derivative-pending, duplicate, and failure interpretation.
- `recovery_router.py`: ledger recovery guidance and receipt interpretation.
- `prompt_loader.py`: bounded prompt asset loader.
- `examples.py`: executable structured response and evidence fixtures.

## Authority ceiling

Alice may ask required questions, select an allowed next action, build a typed command proposal, reject incomplete requests, interpret receipts, and explain blocked evidence. Alice may not append records, overwrite events, invent identifiers, bypass gates, expose secrets, claim compliance, or automatically retry a non-idempotent command after ambiguous failure.

## Terminal result boundary

`CaptureMachine` owns capture state and calls `SessionStore`, but it no longer emits terminal success feedback or resets to the next barcode immediately after a commit. A successful backend result remains in `RECORD_SAVED` until the UI/controller passes the result through `AliceReceiptInterpreter` and calls `complete_terminal_result()`.

A duplicate result is acknowledged only when both `record_id` and `original_receipt_id` are present. An unresolved duplicate is `BLOCKED`; Alice prohibits success feedback, next-barcode progression, and automatic resubmission.

## Truth classes

`PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `SIMULATOR_PASS`, `SOURCE_PRESENT`, `RECEIPT_CONFIRMED`, `PENDING`, and `NON_CLAIM` are distinct. `PASS` is not used as a substitute for source presence, simulator evidence, receipt confirmation, or unexecuted work.
