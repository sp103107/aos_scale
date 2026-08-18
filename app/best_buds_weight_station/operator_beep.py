"""Operator audible feedback for capture terminal results.

Silent under pytest and when BBWS_SILENT_BEEP=1. Windows uses MessageBeep;
other platforms fall back to QApplication.beep when a Qt app exists.
Not a legal-for-trade signal — just an operator cue that a weight was recorded.
"""
from __future__ import annotations

import os


def play_operator_beep(kind: str) -> None:
    """Play a short OS beep for success/warning/error/disconnect."""
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("BBWS_SILENT_BEEP") == "1":
        return
    try:
        import winsound

        codes = {
            "success": winsound.MB_OK,
            "warning": winsound.MB_ICONEXCLAMATION,
            "error": winsound.MB_ICONHAND,
            "disconnect": winsound.MB_ICONASTERISK,
        }
        winsound.MessageBeep(codes.get(kind, winsound.MB_OK))
        return
    except Exception:
        pass
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is not None:
            app.beep()
    except Exception:
        pass
