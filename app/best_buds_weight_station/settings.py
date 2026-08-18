from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .models import now_rfc3339
from .storage import atomic_json

# Device-neutral USB rates. Additional transports (Bluetooth/Wi-Fi) remain disabled.
ALLOWED_BAUD_RATES = frozenset({115200, 9600})
DEFAULT_BAUD_RATE = 115200


@dataclass
class AppSettings:
    schema_version: str = "1.0.0"
    data_root: str = "data/runtime"
    capture_mode: str = "manual"
    serial_port: str | None = None
    baud_rate: int = DEFAULT_BAUD_RATE
    unit: str = "g"
    stability_profile_id: str = "standard_hanging_grams"
    simulator_enabled: bool = False
    bluetooth_enabled: bool = False
    wifi_enabled: bool = False
    # Soft operator UX (fail-closed only for breaking function elsewhere).
    suggest_calibration_on_new_run: bool = True
    require_calibration_before_capture: bool = False
    warn_on_uncalibrated_weight: bool = True
    default_reference_weight_g: float = 2000.0
    barcode_required_for_capture: bool = True
    # After Lock, skip Confirm and record immediately (manual capture path only).
    auto_record_after_lock: bool = False
    # Operator display unit only; storage/JSONL remains grams via unit="g".
    display_unit: str = "g"
    updated_at: str = ""

    def validate(self) -> None:
        if self.capture_mode not in {"automatic", "manual"}:
            raise ValueError("capture mode must be automatic or manual")
        if self.baud_rate not in ALLOWED_BAUD_RATES:
            raise ValueError(f"unsupported baud rate {self.baud_rate}; allowed: {sorted(ALLOWED_BAUD_RATES)}")
        if self.unit != "g":
            raise ValueError("only grams are supported for authoritative storage in this release")
        if self.display_unit not in {"g", "kg", "lb"}:
            raise ValueError("display_unit must be g, kg, or lb")
        if self.bluetooth_enabled or self.wifi_enabled:
            raise ValueError("remote transports are disabled by default in this release")


class SettingsStore:
    def __init__(self, config_dir: str | Path):
        self.config_dir = Path(config_dir).expanduser().resolve()
        self.path = self.config_dir / "settings.json"
        self.recent_run_path = self.config_dir / "recent_run.json"

    @staticmethod
    def validate_data_root(value: str | Path, *, create: bool = True) -> Path:
        raw = str(value)
        if not raw.strip() or "\x00" in raw:
            raise ValueError("data directory is required")
        path = Path(raw).expanduser().resolve()
        if create:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise ValueError("data directory cannot be created") from exc
        if not path.exists() or not path.is_dir():
            raise ValueError("data directory does not exist")
        probe = path / f".bbws_write_probe_{os.getpid()}"
        try:
            with probe.open("w", encoding="utf-8") as handle:
                handle.write("write-test\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise ValueError("data directory is not writable") from exc
        finally:
            try:
                probe.unlink()
            except OSError:
                pass
        return path

    def load(self) -> AppSettings:
        if not self.path.exists():
            # First run (no settings.json yet): seed data_root with the
            # platform runs directory instead of the repo-relative
            # "data/runtime" default, so a frozen/installed exe never writes
            # run data relative to its install directory or cwd.
            from .platform_paths import default_app_paths

            settings = AppSettings(
                data_root=str(default_app_paths().runs),
                updated_at=now_rfc3339(),
            )
            settings.validate()
            return settings
        data = json.load(self.path.open(encoding="utf-8"))
        settings = AppSettings(**{key: data[key] for key in AppSettings.__dataclass_fields__ if key in data})
        settings.validate()
        return settings

    def save(self, settings: AppSettings) -> AppSettings:
        settings.validate()
        data_root = self.validate_data_root(settings.data_root)
        settings.data_root = str(data_root)
        settings.updated_at = now_rfc3339()
        atomic_json(self.path, asdict(settings))
        return settings

    def update(self, **changes: Any) -> AppSettings:
        settings = self.load()
        for key, value in changes.items():
            if key not in AppSettings.__dataclass_fields__:
                raise ValueError(f"unsupported setting: {key}")
            setattr(settings, key, value)
        return self.save(settings)

    def write_recent_run(self, payload: dict[str, Any]) -> None:
        required = {"session_id", "run_id", "session_manifest", "data_root"}
        if not required.issubset(payload):
            raise ValueError("recent-run pointer is incomplete")
        value = dict(payload)
        value.setdefault("schema_version", "1.0.0")
        value["updated_at"] = now_rfc3339()
        atomic_json(self.recent_run_path, value)

    def read_recent_run(self) -> dict[str, Any]:
        if not self.recent_run_path.exists():
            raise FileNotFoundError("no durable recent-run pointer exists")
        value = json.load(self.recent_run_path.open(encoding="utf-8"))
        required = {"session_id", "run_id", "session_manifest", "data_root"}
        if not required.issubset(value):
            raise ValueError("recent-run pointer is invalid")
        return value
