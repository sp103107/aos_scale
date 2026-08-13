"""SR9 regression: calibrated hanging noise never stabilizes under old thresholds."""
from __future__ import annotations

from best_buds_weight_station.models import StabilityProfile
from best_buds_weight_station.stability import StabilityDetector


class Clock:
    def __init__(self) -> None:
        self.v = 0.0

    def __call__(self) -> float:
        return self.v

    def step(self, x: float = 0.2) -> None:
        self.v += x


def _oscillating_samples(n: int = 40) -> list[float]:
    # ±1.5 g around 100 g — typical hanging noise that still passes local 100 g cal bands.
    return [100.0 + (1.5 if i % 2 == 0 else -1.5) for i in range(n)]


def test_old_thresholds_never_stable_with_plus_minus_1_5g():
    profile = StabilityProfile(
        window_size=8,
        minimum_samples=6,
        max_spread_g=0.8,
        max_stddev_g=0.25,
        settle_ms=0,
        timeout_ms=60000,
        max_trend_g=10.0,
        recoverable_timeout=True,
    )
    clock = Clock()
    detector = StabilityDetector(profile, clock=clock)
    for value in _oscillating_samples():
        clock.step(0.1)
        result = detector.add(value)
        assert not result.stable
        assert result.reason in {"collecting", "unstable", "timeout_retry", "trending"}


def test_recommended_hanging_profile_reaches_stable():
    # Plan hanging defaults after characterization (spread 5 / stddev 2 class).
    profile = StabilityProfile(
        profile_id="hanging_recommended",
        window_size=16,
        minimum_samples=12,
        max_spread_g=5.0,
        max_stddev_g=2.0,
        max_trend_g=5.0,
        settle_ms=0,
        timeout_ms=20000,
        recoverable_timeout=True,
    )
    clock = Clock()
    detector = StabilityDetector(profile, clock=clock)
    reached = False
    for value in _oscillating_samples(48):
        clock.step(0.1)
        result = detector.add(value)
        if result.stable:
            reached = True
            break
    assert reached
    assert detector.last_result is not None
    assert detector.last_result.reason == "stable"
