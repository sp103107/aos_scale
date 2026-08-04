# BBWS SR4 — Operator Surface Polish Runbook

**series_id:** `BBWS_SR4_operator_surface_polish`  
**parent:** `bbws-sr3-complete` / baseline `bbws-pre-sr4-polish`

## What changed

Visual polish only on PySide (primary) and Tk (fallback):

- Design tokens from salvage CSS (cite-only) in `ui_tokens.py`
- Eyebrow section labels, status pills (Ready / Stable / Locked / Saved — text-labeled)
- Scan capture dialog chrome
- Locked weight metric + last-saved receipt tone
- Plant log and New Run / Change Strain dialog chrome
- Tk parity for the same language

## What did not change

Capture loop remains:

**Scan → settle → Lock → Confirm → reset**

JSONL authority, Metrc/BLE non-claims, and spreadsheet field contracts are unchanged.

## Dual-UI smoke

1. Start a run (Cultivator + Strain).
2. Press **Scan**, enter a barcode, Enter → tag appears on main surface.
3. Wait for stable → **Lock weight** → confirm locked metric text.
4. **Confirm & Record** → last-saved receipt + plant log row.
5. Repeat on Tk fallback (`launch_tk`) for parity.

## Non-claims

- Salvage capsule is design reference only — no React import
- Visual polish is not legal-for-trade or Metrc compliance
- Arc Launcher is cited doctrine only
- Status color aids remain text-labeled

## Follow-on

BBWS SR5 — run artifact polish (CSV/XLSX/DOCX handoff formatting).
