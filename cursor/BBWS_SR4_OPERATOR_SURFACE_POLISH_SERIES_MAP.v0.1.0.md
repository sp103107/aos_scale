# BBWS SR4 — Operator Surface Polish Series Map

**series_id:** `BBWS_SR4_operator_surface_polish`  
**shape:** 10 × 10 = 100  
**parent:** `BBWS_SR3_station_capture_ux` / `bbws-sr3-complete`  
**baseline:** `bbws-pre-sr4-polish`  
**polish law:** styles / eyebrows / pills / dialog chrome only  
**capture law (unchanged):** scan → settle → lock → confirm → reset

## Context load order

```text
ACTIVE_ARC.yaml
→ context/resume_pack/BBWS_SR4_resume*.json
→ cursor/BBWS_SR4_*_SERIES_MAP*.md
→ superpowers/sr4_sNN_*.json (current season)
→ next SnnEkk
```

## Season map

| Season | Milestone | Title | Focus | Superpower |
|--------|-----------|-------|-------|------------|
| **S01** | M01 | Scaffold + polish contract freeze | Freeze polish-vs-capture contract, salvage selection map, non-claims | `sr4_s01_polish_contract_freeze.v0.1.0.json` |
| **S02** | M02 | Extract BBWS design tokens from salvage | Colors, radius, eyebrow, pill, metric tokens from salvage CSS | `sr4_s02_salvage_token_extract.v0.1.0.json` |
| **S03** | M03 | Apply token sheet to PySide shell | APP_STYLE: top bar, status, cards, buttons, scroll chrome | `sr4_s03_pyside_shell_tokens.v0.1.0.json` |
| **S04** | M04 | Eyebrow + status-pill hierarchy | Eyebrows and text-labeled status pills on cards | `sr4_s04_eyebrow_status_hierarchy.v0.1.0.json` |
| **S05** | M05 | Scan capture dialog professional chrome | Capture-mode Scan dialog polish; Enter→submit unchanged | `sr4_s05_scan_dialog_polish.v0.1.0.json` |
| **S06** | M06 | Locked-weight + last-saved receipt language | Metric/receipt presentation for lock and last-saved | `sr4_s06_lock_receipt_polish.v0.1.0.json` |
| **S07** | M07 | Plant log + run dialog chrome | Plant log list + New Run / Change Strain dialog chrome | `sr4_s07_log_dialog_polish.v0.1.0.json` |
| **S08** | M08 | Tk visual parity | Tk colors, eyebrows, Scan dialog, metrics parity | `sr4_s08_tk_surface_parity.v0.1.0.json` |
| **S09** | M09 | Tests + dual-UI smoke + non-claims | Style/contract tests and operator polish runbook | `sr4_s09_polish_verify_docs.v0.1.0.json` |
| **S10** | M10 | Series closeout + bbws-sr4-complete | ACTIVE_ARC series_complete + tag + push | `sr4_s10_series_closeout.v0.1.0.json` |

## Salvage selection map (cite-only)

| Pattern | Salvage source | BBWS target |
|---------|----------------|-------------|
| Eyebrow label | professional-business-components.css | Card section titles |
| Status pill | cockpit status-pill patterns | Ready/Stable/Locked/Saved text |
| Metric hierarchy | metric / readout CSS | Weight + CULTIVATOR/STRAIN |
| Card chrome | card border/radius/bg | PySide QFrame cards |
| Dialog chrome | modal/panel patterns | Scan / New Run / Change Strain |

## Non-claims

- Salvage capsule is design reference only — no React import into BBWS
- Visual polish is not legal-for-trade or Metrc compliance
- Arc Launcher is cited doctrine, not mutated as Best Buds runtime
- Status color aids must remain text-labeled (not color-only)
- Capture loop unchanged: scan → settle → lock → confirm → reset
- Run artifact polish (CSV/XLSX/DOCX) is BBWS SR5, not this series
