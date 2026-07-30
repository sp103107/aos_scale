# Alice Terminal Receipt and UI Flow

## Locked sequence

```text
operator or automatic stable capture
→ CaptureMachine submits typed CaptureCommand
→ SessionStore performs authoritative local commit
→ CaptureMachine returns record/receipt and remains RECORD_SAVED
→ UI controller calls AliceResponseAgent with the terminal result
→ Alice validates receipt fields or duplicate evidence
→ only RECEIPT_CONFIRMED may call complete_terminal_result()
→ success feedback for a new commit, warning feedback for a verified duplicate
→ capture data clears and state advances to WAITING_FOR_BARCODE
```

## Invalid progression

The controller does not advance when Alice returns `FAIL` or `BLOCKED`. This includes:

- missing or malformed local commit receipt fields;
- unresolved duplicate without `original_receipt_id`;
- authoritative JSONL, individual JSON, or checkpoint failure;
- serial disconnect before commit;
- ambiguous terminal result.

## UI parity

PySide6 and Tk use the shared `process_terminal_result()` controller helper. Automatic and manual modes therefore apply the same receipt, feedback, and progression rules.

## Evidence

- `tests/alice/test_alice_terminal_ui_flow.py`
- `tests/test_state_machine.py`
- `validation/simulator_self_test.v0.1.2.json`
- `reports/alice_authority_validation.v0.1.2.json`
