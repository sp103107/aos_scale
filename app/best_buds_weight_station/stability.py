"""Capture-window stability detector with trend and recoverable timeout.

SR9 adds adjacent-sample trend rejection (`max_trend_g`) and optional
recoverable timeouts that restart the observation window (`timeout_retry`)
instead of permanently sticking on `timeout`.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from statistics import pstdev
from time import monotonic

from .models import StabilityProfile


@dataclass(frozen=True)
class StabilityResult:
    stable: bool
    weight_g: float | None
    sample_count: int
    spread_g: float | None
    stddev_g: float | None
    reason: str
    trend_g: float | None = None


def _p95ish_adjacent_delta(values: list[float]) -> float:
    """Return a p95-ish (or max for tiny windows) adjacent absolute delta."""
    if len(values) < 2:
        return 0.0
    deltas = sorted(abs(values[i] - values[i - 1]) for i in range(1, len(values)))
    if not deltas:
        return 0.0
    # ceil(0.95 * n) - 1, clamped — for small n this leans toward max.
    index = min(len(deltas) - 1, max(0, int(math.ceil(0.95 * len(deltas)) - 1)))
    return float(deltas[index])


class StabilityDetector:
    def __init__(self, profile: StabilityProfile, clock=monotonic):
        self.profile = profile
        self.clock = clock
        self.samples: deque[float] = deque(maxlen=profile.window_size)
        self.started = clock()
        self.candidate_since = None
        self.last_result: StabilityResult | None = None

    def reset(self):
        self.samples.clear()
        self.started = self.clock()
        self.candidate_since = None

    def _store(self, result: StabilityResult) -> StabilityResult:
        self.last_result = result
        return result

    def add(self, weight_g: float, ready: bool = True) -> StabilityResult:
        now = self.clock()
        if not ready:
            return self._store(StabilityResult(False, None, len(self.samples), None, None, "device_not_ready"))
        if weight_g < self.profile.minimum_weight_g:
            return self._store(StabilityResult(False, None, len(self.samples), None, None, "below_minimum"))
        if weight_g > self.profile.maximum_weight_g:
            return self._store(StabilityResult(False, None, len(self.samples), None, None, "above_capacity"))
        self.samples.append(float(weight_g))
        elapsed_ms = (now - self.started) * 1000
        if elapsed_ms > self.profile.timeout_ms:
            if self.profile.recoverable_timeout:
                # Restart the observation window; keep the latest sample.
                self.samples.clear()
                self.samples.append(float(weight_g))
                self.candidate_since = None
                self.started = now
                return self._store(
                    StabilityResult(False, None, len(self.samples), None, None, "timeout_retry")
                )
            return self._store(StabilityResult(False, None, len(self.samples), None, None, "timeout"))
        if len(self.samples) < self.profile.minimum_samples:
            return self._store(StabilityResult(False, None, len(self.samples), None, None, "collecting"))
        vals = list(self.samples)
        spread = max(vals) - min(vals)
        std = pstdev(vals)
        trend = _p95ish_adjacent_delta(vals)
        if trend > self.profile.max_trend_g:
            self.candidate_since = None
            return self._store(
                StabilityResult(False, None, len(vals), spread, std, "trending", trend_g=trend)
            )
        candidate = spread <= self.profile.max_spread_g and std <= self.profile.max_stddev_g
        if not candidate:
            self.candidate_since = None
            return self._store(
                StabilityResult(False, None, len(vals), spread, std, "unstable", trend_g=trend)
            )
        if self.candidate_since is None:
            self.candidate_since = now
        if (now - self.candidate_since) * 1000 < self.profile.settle_ms:
            return self._store(
                StabilityResult(False, None, len(vals), spread, std, "settling", trend_g=trend)
            )
        return self._store(
            StabilityResult(
                True,
                round(sum(vals) / len(vals), 3),
                len(vals),
                spread,
                std,
                "stable",
                trend_g=trend,
            )
        )
