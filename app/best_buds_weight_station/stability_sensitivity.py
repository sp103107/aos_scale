"""Map station lock-sensitivity slider (0–100) onto a resolved StabilityProfile.

0 = strict / slower lock; 50 = neutral; 100 = loose / faster lock.
Multiplies spread, stddev, and trend; inversely scales settle_ms. Not legal-for-trade.
"""
from __future__ import annotations

from dataclasses import replace

from .models import StabilityProfile

_SPREAD_CLAMP = (0.5, 15.0)
_STDDEV_CLAMP = (0.25, 5.0)
_TREND_CLAMP = (0.5, 8.0)
_SETTLE_CLAMP = (200, 3000)


def _lerp(low: float, high: float, t: float) -> float:
    return low + (high - low) * t


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def apply_lock_sensitivity(base: StabilityProfile, sensitivity: int) -> StabilityProfile:
    """Return a copy of *base* tuned by operator lock sensitivity (0–100)."""
    level = _clamp(int(sensitivity), 0, 100)
    # 0 -> 0.5x, 50 -> 1.0x (neutral), 100 -> 1.5x spread/stddev/trend
    spread_mult = 1.0 + (level - 50) / 100.0
    settle_mult = 1.5 - (level / 100.0)
    settle_ms = base.settle_ms
    if base.settle_ms > 0:
        settle_ms = int(_clamp(base.settle_ms * settle_mult, *_SETTLE_CLAMP))
    return replace(
        base,
        max_spread_g=_clamp(base.max_spread_g * spread_mult, *_SPREAD_CLAMP),
        max_stddev_g=_clamp(base.max_stddev_g * spread_mult, *_STDDEV_CLAMP),
        max_trend_g=_clamp(base.max_trend_g * spread_mult, *_TREND_CLAMP),
        settle_ms=settle_ms,
    )


def sensitivity_hint(base: StabilityProfile, sensitivity: int) -> str:
    """Short operator hint for the effective spread/settle at a slider position."""
    tuned = apply_lock_sensitivity(base, sensitivity)
    return (
        f"spread≤{tuned.max_spread_g:.1f} g, stddev≤{tuned.max_stddev_g:.2f} g, "
        f"settle {tuned.settle_ms} ms"
    )
