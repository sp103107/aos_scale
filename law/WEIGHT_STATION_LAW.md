# Weight Station Law

1. Local append-only events are authoritative.
2. Success feedback occurs only after JSONL append, individual JSON write, and session checkpoint succeed.
3. Gross, tare, and net are preserved; `net_g = gross_g - tare_g` within decimal tolerance.
4. Corrections and voids append new events and never overwrite the original.
5. Simulator evidence and physical-device evidence are distinct truth classes.
6. Spreadsheet and remote synchronization are derivatives and may fail without losing a committed event.
7. Alice may block incomplete run setup or unsafe capture conditions but may not invent identifiers or declare compliance.
8. Every inbound AoS command receives an acknowledgement and a terminal receipt.
9. Platform and hardware claims require native execution receipts.
10. Report generation is deterministic and read-only against authoritative events.
