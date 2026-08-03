# BBWS SR2 Artifacts

Series `BBWS_SR2_tk_linux_display_units` — Tk/Linux parity + display units.

## Arc

| Path | Purpose |
|------|---------|
| `ACTIVE_ARC.yaml` | Live SR2 pointer |
| `arc_lifecycle/blueprints/series_bbws_sr2_tk_linux_display_units.v0.1.0.json` | Blueprint |
| `cursor/BBWS_SR2_TK_LINUX_DISPLAY_UNITS_SERIES_MAP.v0.1.0.md` | Map |
| `superpowers/sr2_sNN_*.json` | Season packs (distinct from SR1 names) |
| `context/resume_pack/BBWS_SR2_resume.v0.1.0.json` | Resume |

## Product modules

| Path | Purpose |
|------|---------|
| `app/best_buds_weight_station/units.py` | Display g/kg/lb conversion |
| `app/best_buds_weight_station/production_ui.py` | Tk SR1 parity + display unit |
| `scripts/bbws_sr2_xvfb_tk_smoke.sh` | Linux/Xvfb Tk smoke |
| `scripts/bbws_sr2_unit_smoke.py` | Display-unit + action smoke |
