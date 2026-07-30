# Frontend

The primary operator UI is Windows-first PySide6. Linux uses the same PySide6 source where available; Tk is a secondary fallback and validation surface.

Design and layout sources:

- `design_tokens.v0.1.8.json`
- `themes/windows_light.qss`
- `app/best_buds_weight_station/operator_surface.py`
- `app/best_buds_weight_station/pyside_frontend.py`
- `app/best_buds_weight_station/production_ui.py`

The routine screen exposes seven non-overlapping actions. Calibration, diagnostics, scale configuration, recovery, and exports remain in menus or setup dialogs.
