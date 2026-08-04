# BBWS SR3 Series Closeout

**series_id:** `BBWS_SR3_station_capture_ux`  
**status:** series_complete  
**parent:** `BBWS_SR2_tk_linux_display_units` / `bbws-sr2-complete`

## Delivered

- Active barcode stays visible after scan until Confirm/Cancel
- Main-row **Scan** focuses barcode; Test Scanner remains under Scale menu
- Manual capture stops at `WEIGHT_STABLE`; **Lock weight** (`capture.weight.lock`) required before Confirm
- Run plant log (last 50, read-only) on PySide and Tk
- Snapshot fields: `active_barcode`, `locked_weight_g`, `recent_plants`
- Tests in `tests/test_sr3_capture_ux.py` plus updated state/controller/frontend contracts

## Follow-on

BBWS SR4 — polished professional formatting of generated run artifacts (CSV/XLSX/DOCX/export pack).
