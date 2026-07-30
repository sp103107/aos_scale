from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    platform: str
    root: Path
    config: Path
    logs: Path
    runs: Path
    recovery: Path
    exports: Path

    def ensure(self) -> "AppPaths":
        for path in (self.root, self.config, self.logs, self.runs, self.recovery, self.exports):
            path.mkdir(parents=True, exist_ok=True)
        return self


def default_app_paths() -> AppPaths:
    system = platform.system().lower()
    home = Path.home()
    if system == "windows":
        base = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local")) / "BestBudsWeightStation"
        return AppPaths(system, base, base / "config", base / "logs", base / "runs", base / "recovery", base / "exports").ensure()
    if system == "darwin":
        base = home / "Library" / "Application Support" / "BestBudsWeightStation"
        return AppPaths(system, base, base / "config", base / "logs", base / "runs", base / "recovery", base / "exports").ensure()
    data_home = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    state_home = Path(os.environ.get("XDG_STATE_HOME", home / ".local" / "state"))
    root = data_home / "best-buds-weight-station"
    return AppPaths(
        system,
        root,
        config_home / "best-buds-weight-station",
        state_home / "best-buds-weight-station" / "logs",
        root / "runs",
        state_home / "best-buds-weight-station" / "recovery",
        root / "exports",
    ).ensure()
