"""In-process operator activity for long-running maintenance and run-install work.

Surfaces progress to Alice / status bar via OperatorRuntime.snapshot — no WebSockets.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorActivity:
    phase: str
    step: str
    message: str
    progress: tuple[int, int] | None = None

    def to_dict(self) -> dict:
        out: dict = {
            "phase": self.phase,
            "step": self.step,
            "message": self.message,
        }
        if self.progress is not None:
            out["progress_current"] = self.progress[0]
            out["progress_total"] = self.progress[1]
        return out


MAINTENANCE_MESSAGES: dict[tuple[str, str], str] = {
    ("zeroing", "tare"): "Zeroing — hold the pan empty. Sending TARE to the scale…",
    ("zeroing", "sampling"): "Zeroing — sampling empty pan (keep still)…",
    ("connecting", "validate"): "Connecting scale — validating PING and STATUS…",
    ("characterizing", "collecting"): "100 g stability test — collecting live samples…",
    ("run_install", "quiet"): "Loading run — pausing live stream briefly…",
}


def activity_message(phase: str, step: str, *, progress: tuple[int, int] | None = None) -> str:
    base = MAINTENANCE_MESSAGES.get((phase, step), f"{phase.replace('_', ' ').title()}…")
    if progress is not None:
        current, total = progress
        return f"{base} ({current}/{total})"
    return base
