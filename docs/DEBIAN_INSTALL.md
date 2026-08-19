# Debian Install - v2.0.0-rc10.1

Install `dist/debian/best-buds-weight-station_2.0.0-rc10.1_amd64.deb` when present. Debian is the secondary platform. Tk is the guaranteed fallback; `python3-serial` is required for physical serial capture. PySide6 remains the primary shared frontend source but is not guaranteed by the Debian package.

## BBWS SR2 Linux notes

- Source launch: `PYTHONPATH=app python -m best_buds_weight_station --ui tk` (or auto → PySide when installed).
- Xvfb Tk smoke: `bash scripts/bbws_sr2_xvfb_tk_smoke.sh` (requires `xvfb-run` on Linux).
- Display unit g/kg/lb is operator UX only; session JSONL remains grams.
- Non-claim: Linux smoke ≠ Debian production guarantee; no first-class Linux GUI installer in SR2.
