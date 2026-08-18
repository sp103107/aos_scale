# START HERE — Best Buds Cultivator Weight Station

**Version:** `2.0.0-rc9`  
**Audience:** Harvest-station operators and supervisors  
**Public repo:** [https://github.com/sp103107/aos_scale](https://github.com/sp103107/aos_scale)

## What this is

A **Windows-first, local-first** barcode weighing station for cultivators. You start a harvest run, scan plant tags, lock stable weights, confirm records, and export handoff files (CSV / XLSX / DOCX).

## Who it is for

See [docs/INTENDED_USER.md](docs/INTENDED_USER.md).

> **Next action:** If you are a coding agent or developer, open [START_HERE_CODING_AGENT.md](START_HERE_CODING_AGENT.md) instead.

## Launch (Windows)

```text
launch_best_buds.bat
```

Simulator (no physical scale):

```text
launch_simulator.bat
```

## First-run path

```text
New Run (Cultivator + Strain)
→ Connect Scale
→ Guided Calibration (verified mass)
→ ZERO (empty) → optional SET TARE
→ Scan → settle → Lock weight → Confirm & Record
→ Export Report when the run is done
```

Full walkthrough: [docs/OPERATOR_ONBOARDING.md](docs/OPERATOR_ONBOARDING.md).

**Scale Face (Windows PySide):** View → Scale Face (Harvest) or Ctrl+Shift+F for a large-weight harvest panel (Harvest/SETUP toggle). Esc returns to the full UI.

## Where truth lives

**Session JSONL** is authoritative. CSV / XLSX / DOCX / JSON reports are non-authoritative handoffs. Use **Run → Reconcile Export ↔ JSONL** to check handoffs against the ledger.

## Non-claims

- Not legal-for-trade / Metrc compliance
- Not production-sealed weighing certification
- Displayed grams are not trustworthy until Guided Calibration with a verified reference mass

## Related

| Doc | Use |
|-----|-----|
| [docs/OPERATOR_ONBOARDING.md](docs/OPERATOR_ONBOARDING.md) | Operator day-one |
| [docs/RELEASE_CANDIDATE.md](docs/RELEASE_CANDIDATE.md) | What this RC includes |
| [docs/RECORDING_AND_EXPORT_RUNBOOK.md](docs/RECORDING_AND_EXPORT_RUNBOOK.md) | Recording + export detail |
| [README.md](README.md) | Engineering overview |
