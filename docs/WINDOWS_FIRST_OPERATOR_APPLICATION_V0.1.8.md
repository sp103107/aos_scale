# Windows-First Operator Application - v0.1.8

PySide6 is the primary UI. The design system is defined in `frontend/design_tokens.v0.1.8.json` and `frontend/themes/windows_light.qss`.

The routine screen uses the shared `operator_surface.py` layout contract, exposes seven non-overlapping actions, labels the plant-barcode field, and displays physical serial as `TESTING REQUIRED` until direct evidence exists.

Windows-specific native execution remains unproven until a Windows runner builds and executes the packaged application.
