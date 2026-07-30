from __future__ import annotations
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

class StabilityDetector:
    def __init__(self, profile: StabilityProfile, clock=monotonic):
        self.profile=profile; self.clock=clock; self.samples=deque(maxlen=profile.window_size); self.started=clock(); self.candidate_since=None
    def reset(self):
        self.samples.clear(); self.started=self.clock(); self.candidate_since=None
    def add(self, weight_g: float, ready: bool=True) -> StabilityResult:
        now=self.clock()
        if not ready: return StabilityResult(False,None,len(self.samples),None,None,'device_not_ready')
        if weight_g < self.profile.minimum_weight_g: return StabilityResult(False,None,len(self.samples),None,None,'below_minimum')
        if weight_g > self.profile.maximum_weight_g: return StabilityResult(False,None,len(self.samples),None,None,'above_capacity')
        self.samples.append(float(weight_g))
        if (now-self.started)*1000 > self.profile.timeout_ms: return StabilityResult(False,None,len(self.samples),None,None,'timeout')
        if len(self.samples)<self.profile.minimum_samples: return StabilityResult(False,None,len(self.samples),None,None,'collecting')
        vals=list(self.samples); spread=max(vals)-min(vals); std=pstdev(vals)
        candidate=spread<=self.profile.max_spread_g and std<=self.profile.max_stddev_g
        if not candidate:
            self.candidate_since=None
            return StabilityResult(False,None,len(vals),spread,std,'unstable')
        if self.candidate_since is None: self.candidate_since=now
        if (now-self.candidate_since)*1000 < self.profile.settle_ms:
            return StabilityResult(False,None,len(vals),spread,std,'settling')
        return StabilityResult(True,round(sum(vals)/len(vals),3),len(vals),spread,std,'stable')
