# Crash-Safe Persistence — v0.1.3

## Commit order

1. Validate run and action.
2. Build immutable weight event.
3. Append JSONL and flush/fsync.
4. Write individual JSON temporary file, flush/fsync, and atomically rename.
5. Write checkpoint temporary file, flush/fsync, and atomically replace.
6. Update the durable recent-run pointer.
7. Attempt non-authoritative CSV/XLSX derivatives.
8. Write local commit receipt.
9. Alice validates the receipt.
10. UI emits feedback and resets.

Parent-directory fsync is best effort and may be unsupported on some platforms; the receipt does not overstate this boundary.

## Startup recovery

The recovery path validates the hash chain, quarantines an invalid final JSONL fragment, quarantines incomplete temporary files, rebuilds missing individual records, reconciles a stale checkpoint, rebuilds missing commit receipts from authoritative evidence, updates the recent-run pointer, and writes a recovery receipt. It never restores an uncommitted weight.
