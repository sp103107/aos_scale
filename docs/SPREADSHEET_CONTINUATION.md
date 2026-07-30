# Spreadsheet Continuation

A spreadsheet is compatible when its first-row headers match the canonical export header sequence. Compatible workbooks are appended atomically. Incompatible workbooks are backed up and rejected for manual mapping; JSONL remains authoritative. Cells beginning with `=`, `+`, `-`, or `@` are escaped to prevent formula execution.
