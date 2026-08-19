"""Lock sensitivity slider mapping tests."""
from __future__ import annotations

from best_buds_weight_station.models import StabilityProfile
from best_buds_weight_station.stability_sensitivity import apply_lock_sensitivity


def test_neutral_sensitivity_unchanged_spread_order():
    base = StabilityProfile(max_spread_g=4.0, max_stddev_g=1.0, settle_ms=1000)
    tuned = apply_lock_sensitivity(base, 50)
    assert tuned.max_spread_g == 4.0
    assert tuned.max_stddev_g == 1.0
    assert tuned.settle_ms == 1000


def test_strict_sensitivity_tightens_and_slows():
    base = StabilityProfile(max_spread_g=4.0, max_stddev_g=2.0, settle_ms=1000)
    tuned = apply_lock_sensitivity(base, 0)
    assert tuned.max_spread_g < base.max_spread_g
    assert tuned.settle_ms > base.settle_ms


def test_loose_sensitivity_widens_and_speeds():
    base = StabilityProfile(max_spread_g=4.0, max_stddev_g=2.0, settle_ms=1000)
    tuned = apply_lock_sensitivity(base, 100)
    assert tuned.max_spread_g > base.max_spread_g
    assert tuned.settle_ms < base.settle_ms
