"""
Typed per-scale profile store for BBWS SR9.

Persists calibration factor + bounded hanging-load stability parameters under
``config_dir/scale_profiles/`` with atomic JSON writes. Profiles are local
operational evidence — not legal-for-trade certification.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path
from typing import Any, Literal

from .models import StabilityProfile, now_rfc3339
from .storage import atomic_json, safe_component, sha

ProfileStatus = Literal["active", "archived"]

# Prefer BBWS-SCALE-NNN; also accept BBWS-… board IDs (A–Z / digits / hyphen).
_DEVICE_ID_RE = re.compile(r"^(?:BBWS-SCALE-\d{3}|BBWS-[A-Z0-9-]{3,32})$")

_HASH_FIELDS = (
    "profile_id",
    "name",
    "device_id",
    "calibration_factor",
    "calibration_receipt_id",
    "characterization_receipt_id",
    "stability",
    "firmware_version",
    "status",
    "usb_hardware_id",
    "last_port",
)


def validate_device_id(device_id: str) -> str:
    """Validate host-side device identity pattern for profile binding."""
    text = str(device_id or "").strip()
    if not _DEVICE_ID_RE.fullmatch(text):
        raise ValueError(
            "device_id must match BBWS-SCALE-NNN or BBWS-[A-Z0-9-]{3,32}"
        )
    return text


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


@dataclass
class ScaleStabilityParams:
    """Bounded hanging-load stability thresholds for one scale profile."""

    window_size: int = 16
    minimum_samples: int = 12
    max_spread_g: float = 5.0
    max_stddev_g: float = 2.0
    max_trend_g: float = 2.0
    settle_ms: int = 1200
    timeout_ms: int = 20000
    minimum_weight_g: float = 1.0
    maximum_weight_g: float = 50000.0

    def to_stability_profile(self, profile_id: str = "scale_profile") -> StabilityProfile:
        return StabilityProfile(
            profile_id=profile_id,
            window_size=int(self.window_size),
            minimum_samples=int(self.minimum_samples),
            max_spread_g=float(self.max_spread_g),
            max_stddev_g=float(self.max_stddev_g),
            settle_ms=int(self.settle_ms),
            minimum_weight_g=float(self.minimum_weight_g),
            maximum_weight_g=float(self.maximum_weight_g),
            timeout_ms=int(self.timeout_ms),
            max_trend_g=float(self.max_trend_g),
            recoverable_timeout=True,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ScaleStabilityParams":
        raw = dict(data or {})
        allowed = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in raw.items() if k in allowed})


@dataclass
class ScaleProfile:
    """One persisted scale identity + calibration + stability binding."""

    profile_id: str
    name: str
    device_id: str
    calibration_factor: float
    calibration_receipt_id: str | None
    characterization_receipt_id: str | None
    stability: ScaleStabilityParams
    firmware_version: str | None
    created_at: str
    updated_at: str
    status: ProfileStatus
    profile_hash: str
    usb_hardware_id: str | None = None
    last_port: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload

    def to_stability_profile(self) -> StabilityProfile:
        return self.stability.to_stability_profile(profile_id=self.profile_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScaleProfile":
        payload = dict(data)
        payload["stability"] = ScaleStabilityParams.from_dict(payload.get("stability"))
        return cls(**{k: payload[k] for k in (f.name for f in fields(cls)) if k in payload})


def compute_profile_hash(profile: ScaleProfile | dict[str, Any]) -> str:
    """Deterministic SHA256 over canonical profile identity/calibration fields."""
    if isinstance(profile, ScaleProfile):
        data = profile.to_dict()
    else:
        data = dict(profile)
    stability = data.get("stability")
    if isinstance(stability, ScaleStabilityParams):
        stability = asdict(stability)
    canonical_body = {key: data.get(key) for key in _HASH_FIELDS}
    canonical_body["stability"] = stability
    return sha(canonical_body)


def recommend_stability_from_characterization(
    baseline_trimmed_spread_g: float,
    baseline_stddev_g: float,
    baseline_p95_delta_g: float,
    live_weight_g: float = 100.0,
) -> ScaleStabilityParams:
    """Recommend bounded hanging-load thresholds from a 100 g characterization."""
    weight = abs(float(live_weight_g))
    max_spread = _clamp(
        max(2.0, 3.0 * float(baseline_trimmed_spread_g), 0.001 * weight),
        2.0,
        15.0,
    )
    max_stddev = _clamp(
        max(0.75, 3.0 * float(baseline_stddev_g), 0.00035 * weight),
        0.75,
        5.0,
    )
    max_trend = _clamp(
        max(1.0, 2.0 * float(baseline_p95_delta_g), 0.0005 * weight),
        1.0,
        8.0,
    )
    return ScaleStabilityParams(
        window_size=16,
        minimum_samples=12,
        max_spread_g=max_spread,
        max_stddev_g=max_stddev,
        max_trend_g=max_trend,
        settle_ms=1200,
        timeout_ms=20000,
    )


class ScaleProfileStore:
    """Atomic CRUD for scale profiles under ``config_dir/scale_profiles``."""

    def __init__(self, config_dir: str | Path):
        self.config_dir = Path(config_dir).resolve()
        self.root = self.config_dir / "scale_profiles"
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, profile_id: str) -> Path:
        safe = safe_component(profile_id, "profile_id")
        return self.root / f"{safe}.json"

    def _read(self, path: Path) -> ScaleProfile:
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        return ScaleProfile.from_dict(data)

    def list_profiles(self, *, include_archived: bool = False) -> list[ScaleProfile]:
        profiles: list[ScaleProfile] = []
        for path in sorted(self.root.glob("*.json")):
            try:
                profile = self._read(path)
            except Exception:
                continue
            if profile.status == "archived" and not include_archived:
                continue
            profiles.append(profile)
        return profiles

    def get(self, profile_id: str) -> ScaleProfile | None:
        path = self._path(profile_id)
        if not path.exists():
            return None
        return self._read(path)

    def get_active_for_device(self, device_id: str) -> ScaleProfile | None:
        device_id = validate_device_id(device_id)
        for profile in self.list_profiles(include_archived=False):
            if profile.device_id == device_id and profile.status == "active":
                return profile
        return None

    def clear_active_for_device(self, device_id: str) -> int:
        """Clear active status for a device (archive all actives for that device)."""
        device_id = validate_device_id(device_id)
        cleared = 0
        for profile in self.list_profiles(include_archived=False):
            if profile.device_id == device_id and profile.status == "active":
                updated = replace(
                    profile,
                    status="archived",
                    updated_at=now_rfc3339(),
                )
                updated = replace(updated, profile_hash=compute_profile_hash(updated))
                atomic_json(self._path(updated.profile_id), updated.to_dict())
                cleared += 1
        return cleared

    def create(
        self,
        *,
        name: str,
        device_id: str,
        calibration_factor: float,
        stability: ScaleStabilityParams | None = None,
        calibration_receipt_id: str | None = None,
        characterization_receipt_id: str | None = None,
        firmware_version: str | None = None,
        usb_hardware_id: str | None = None,
        last_port: str | None = None,
        activate: bool = True,
        profile_id: str | None = None,
    ) -> ScaleProfile:
        device_id = validate_device_id(device_id)
        name = str(name or "").strip()
        if not name:
            raise ValueError("profile name is required")
        if not isinstance(calibration_factor, (int, float)) or float(calibration_factor) == 0:
            raise ValueError("calibration_factor must be a nonzero number")
        pid = profile_id or f"scale-profile-{uuid.uuid4()}"
        safe_component(pid, "profile_id")
        if self.get(pid) is not None:
            raise ValueError(f"profile already exists: {pid}")
        now = now_rfc3339()
        status: ProfileStatus = "active" if activate else "archived"
        if activate:
            self.clear_active_for_device(device_id)
        profile = ScaleProfile(
            profile_id=pid,
            name=name,
            device_id=device_id,
            calibration_factor=float(calibration_factor),
            calibration_receipt_id=calibration_receipt_id,
            characterization_receipt_id=characterization_receipt_id,
            stability=stability or ScaleStabilityParams(),
            firmware_version=firmware_version,
            created_at=now,
            updated_at=now,
            status=status,
            profile_hash="",
            usb_hardware_id=usb_hardware_id,
            last_port=last_port,
        )
        profile = replace(profile, profile_hash=compute_profile_hash(profile))
        atomic_json(self._path(profile.profile_id), profile.to_dict())
        return profile

    def update(self, profile_id: str, **changes: Any) -> ScaleProfile:
        existing = self.get(profile_id)
        if existing is None:
            raise KeyError(f"unknown profile_id: {profile_id}")
        if "device_id" in changes and changes["device_id"] is not None:
            changes["device_id"] = validate_device_id(str(changes["device_id"]))
        if "stability" in changes and isinstance(changes["stability"], dict):
            changes["stability"] = ScaleStabilityParams.from_dict(changes["stability"])
        blocked = {"profile_id", "created_at", "profile_hash"}
        for key in blocked:
            changes.pop(key, None)
        updated = replace(existing, **changes, updated_at=now_rfc3339())
        updated = replace(updated, profile_hash=compute_profile_hash(updated))
        atomic_json(self._path(updated.profile_id), updated.to_dict())
        return updated

    def rename(self, profile_id: str, name: str) -> ScaleProfile:
        name = str(name or "").strip()
        if not name:
            raise ValueError("profile name is required")
        return self.update(profile_id, name=name)

    def activate(self, profile_id: str) -> ScaleProfile:
        existing = self.get(profile_id)
        if existing is None:
            raise KeyError(f"unknown profile_id: {profile_id}")
        self.clear_active_for_device(existing.device_id)
        return self.update(profile_id, status="active")

    def archive(self, profile_id: str) -> ScaleProfile:
        existing = self.get(profile_id)
        if existing is None:
            raise KeyError(f"unknown profile_id: {profile_id}")
        if existing.status == "active":
            raise ValueError(
                "cannot archive an active profile; activate another profile or "
                "clear_active_for_device first"
            )
        return self.update(profile_id, status="archived")
