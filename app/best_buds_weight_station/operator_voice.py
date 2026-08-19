"""Operator text-to-speech cues for auto-record alerts.

Windows uses System.Speech via PowerShell; silent under pytest / BBWS_SILENT_BEEP.
Not legal-for-trade — operator feedback only.
"""
from __future__ import annotations

import os
import subprocess
import sys


def speak_operator_cue(text: str) -> None:
    """Speak a short phrase when TTS is available."""
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("BBWS_SILENT_BEEP") == "1":
        return
    phrase = str(text or "").strip()
    if not phrase or len(phrase) > 120:
        return
    if sys.platform == "win32":
        try:
            escaped = phrase.replace("'", "''")
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        "Add-Type -AssemblyName System.Speech; "
                        f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{escaped}')"
                    ),
                ],
                check=False,
                timeout=8,
                capture_output=True,
            )
            return
        except Exception:
            pass
