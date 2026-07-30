# RC3B — Software Dry Run and Agent Bootstrap Entry-Point Hardening

Status: `PASS` within the software-only evidence boundary.

This internal phase adds:

- `python -m best_buds_weight_station.bootstrap`
- `best-buds-weight-station-bootstrap`
- `prehardware` validation profile
- software-only dry-run execution through the real application controller
- recovery-matrix execution
- Tk UI smoke execution
- isolated package-install preflight
- machine-readable bootstrap receipts and summary

Physical firmware, serial, HX711, zero, tare, calibration, and end-to-end scale gates remain `NOT_RUN` or `BLOCKED` as applicable.
