# Transport and Button Boundaries — v0.1.3

Local UI, keyboard, and hardware-button events normalize to the same canonical action family. Green maps to confirm, yellow to zero, red to cancel, and blue to Scale Setup. Buttons never write persistence directly.

Bluetooth and Wi-Fi contracts require authenticated device identity, idempotency keys, acknowledgement and terminal-result separation, and offline local weighing. Both remain disabled by default. Anonymous commands, direct JSONL writes, state bypass, remote success before local commit, and remote calibration acceptance are forbidden.
