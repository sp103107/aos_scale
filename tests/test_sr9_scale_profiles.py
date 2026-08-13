"""SR9 scale profile store, recommend clamps, and StabilityDetector governance tests."""
from __future__ import annotations

import pytest

from best_buds_weight_station.models import StabilityProfile
from best_buds_weight_station.scale_profiles import (
    ScaleProfileStore,
    recommend_stability_from_characterization,
)
from best_buds_weight_station.stability import StabilityDetector


class Clock:
    def __init__(self) -> None:
        self.v = 0.0

    def __call__(self) -> float:
        return self.v

    def step(self, x: float = 0.2) -> None:
        self.v += x


def test_recommend_stability_clamps_low_and_high():
    low = recommend_stability_from_characterization(0.01, 0.01, 0.01, live_weight_g=100.0)
    assert low.max_spread_g == 2.0
    assert low.max_stddev_g == 0.75
    assert low.max_trend_g == 1.0
    assert low.window_size == 16
    assert low.minimum_samples == 12
    assert low.settle_ms == 1200
    assert low.timeout_ms == 20000

    high = recommend_stability_from_characterization(20.0, 10.0, 20.0, live_weight_g=100000.0)
    assert high.max_spread_g == 15.0
    assert high.max_stddev_g == 5.0
    assert high.max_trend_g == 8.0


def test_profile_create_hash_activate_archive_rejects_active(tmp_path):
    store = ScaleProfileStore(tmp_path)
    first = store.create(
        name="Scale A",
        device_id="BBWS-SCALE-001",
        calibration_factor=123.45,
        firmware_version="0.1.4",
    )
    assert first.status == "active"
    assert first.profile_hash
    again = store.get(first.profile_id)
    assert again is not None
    assert again.profile_hash == first.profile_hash

    second = store.create(
        name="Scale A v2",
        device_id="BBWS-SCALE-001",
        calibration_factor=130.0,
        activate=True,
    )
    assert second.status == "active"
    assert store.get(first.profile_id).status == "archived"

    with pytest.raises(ValueError, match="cannot archive an active"):
        store.archive(second.profile_id)

    store.clear_active_for_device("BBWS-SCALE-001")
    archived = store.archive(second.profile_id)
    assert archived.status == "archived"


def test_stability_recoverable_timeout_and_trend_reject():
    clock = Clock()
    profile = StabilityProfile(
        window_size=6,
        minimum_samples=4,
        max_spread_g=5.0,
        max_stddev_g=2.0,
        max_trend_g=0.5,
        settle_ms=0,
        timeout_ms=1000,
        recoverable_timeout=True,
    )
    detector = StabilityDetector(profile, clock=clock)

    # Large adjacent jumps → trending
    for value in (100.0, 102.0, 100.0, 102.0):
        clock.step(0.05)
        result = detector.add(value)
    assert result.reason == "trending"
    assert detector.last_result is not None
    assert detector.last_result.reason == "trending"

    # Advance past timeout → recoverable retry, not permanent timeout
    clock.step(1.2)
    result = detector.add(100.1)
    assert result.reason == "timeout_retry"
    assert detector.last_result.reason == "timeout_retry"
    assert len(detector.samples) == 1


def test_frozen_capture_noise_passes_recommended_profile():
    """Noise that fails old 0.8/0.25 still becomes stable under recommended hanging profile."""
    # Oscillation amplitude that blows past 0.8 spread / 0.25 stddev.
    samples = []
    for i in range(24):
        samples.append(100.0 + (1.2 if i % 2 == 0 else -1.2))

    old = StabilityProfile(
        window_size=8,
        minimum_samples=6,
        max_spread_g=0.8,
        max_stddev_g=0.25,
        settle_ms=0,
        timeout_ms=30000,
        max_trend_g=10.0,
    )
    clock_old = Clock()
    det_old = StabilityDetector(old, clock=clock_old)
    old_stable = False
    for value in samples:
        clock_old.step(0.1)
        if det_old.add(value).stable:
            old_stable = True
            break
    assert not old_stable

    recommended = recommend_stability_from_characterization(
        baseline_trimmed_spread_g=2.4,
        baseline_stddev_g=1.2,
        baseline_p95_delta_g=2.4,
        live_weight_g=100.0,
    )
    # Recommend should land near hanging allowances used in the field.
    assert recommended.max_spread_g >= 5.0
    assert recommended.max_stddev_g >= 2.0

    hanging = recommended.to_stability_profile("hanging_test")
    hanging = StabilityProfile(
        **{
            **hanging.__dict__,
            "settle_ms": 0,
            "max_trend_g": 10.0,
        }
    )
    clock_new = Clock()
    det_new = StabilityDetector(hanging, clock=clock_new)
    reached = False
    for value in samples:
        clock_new.step(0.1)
        result = det_new.add(value)
        if result.stable:
            reached = True
            break
    assert reached
