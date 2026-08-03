# BBWS SR2 S10 — Dual-UI regression matrix

| Check | PySide | Tk | Notes |
|-------|--------|----|-------|
| Soft confirm / duplicate warning | pass | pass | status pacing + warning modal |
| Test Scanner HID receipt | pass | pass | data_root/scanner_test_receipts |
| Sticky Change Strain | pass | pass | run.set_active_cultivar |
| Rebuild CSV / pending sync | pass | pass | spreadsheet.rebuild |
| Export + reconcile | pass | pass | report.reconcile |
| Display unit g/kg/lb | pass | pass | storage remains g |
| Cal reference converts to g | pass | pass | display_to_grams |
| Firmware multi-unit | n/a | n/a | out of scope |

Non-claims: not legal-for-trade; Linux smoke ≠ Debian production guarantee.
