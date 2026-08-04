# Release candidate notes — v2.0.0-rc1

**Tag intent:** first **product onboarding RC** after SR1–SR5 capability freeze.  
**Not** a production seal or legal-for-trade release.

## What this RC includes

- Windows-first PySide6 operator UI (Tk fallback)
- Capture loop: Scan → settle → Lock → Confirm → reset
- Cultivator vs Strain on New Run and exports
- Plant log (read-only last 50) and Scan capture dialog
- Operator surface polish (SR4 design tokens)
- Handoff artifacts: CSV / XLSX / DOCX / JSON + `handoff_bundle_manifest.json` (SR5)
- Human doors: `START_HERE.md`, `docs/OPERATOR_ONBOARDING.md`, `docs/INTENDED_USER.md`
- Coding-agent door: `START_HERE_CODING_AGENT.md` + `python -m best_buds_weight_station.onboard`
- USB serial connect, Zero/Tare, Guided Calibration, simulator path

## What this RC does **not** claim

- No production-ready weighing seal
- No legal-for-trade / NTEP / Weights & Measures certification
- No Metrc sync or compliance
- No guarantee that displayed grams are accurate until Guided Calibration with a verified reference mass

## Operator bring-up checklist

1. Open [START_HERE.md](../START_HERE.md) or [OPERATOR_ONBOARDING.md](OPERATOR_ONBOARDING.md).
2. Launch `launch_best_buds.bat`.
3. New Run (Cultivator + Strain) → Connect Scale → Guided Calibration → ZERO.
4. Scan → Lock → Confirm plants.
5. Export Report → Reconcile Export ↔ JSONL.

## Coding agents

See [START_HERE_CODING_AGENT.md](../START_HERE_CODING_AGENT.md).

```bash
python -m best_buds_weight_station.onboard
python -m best_buds_weight_station.bootstrap --profile cursor-ready
```

## License

Personal / noncommercial: PolyForm Noncommercial 1.0.0 — `LICENSE`.  
Commercial: separate paid license — `COMMERCIAL.md`.

## Repository

[https://github.com/sp103107/aos_scale](https://github.com/sp103107/aos_scale)
