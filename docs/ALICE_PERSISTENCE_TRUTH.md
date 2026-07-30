# Alice Persistence Truth Boundary

Alice must never treat the UI as persistence authority. The success sequence is: operator/automatic request → Alice validates visible context → typed command proposal → backend validation → JSONL append and sync → individual JSON atomic write → checkpoint atomic write → local commit receipt → Alice receipt validation → saved message and success feedback → next barcode.

A spreadsheet failure after local commit becomes pending sync and does not block the weighing loop. A failure before the complete local commit receipt blocks success feedback. An ambiguous failure is not automatically retried.
