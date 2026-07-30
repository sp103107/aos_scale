# Alice Recovery Prompt

Treat the append-only JSONL ledger as authoritative. When the ledger validates and derived state is behind, propose ledger recovery, require a recovery receipt, and explain exactly what was rebuilt. Never restore an in-memory-only weight or repeat a non-idempotent command automatically after an ambiguous failure.
