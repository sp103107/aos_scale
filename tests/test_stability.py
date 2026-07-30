from best_buds_weight_station.models import StabilityProfile
from best_buds_weight_station.stability import StabilityDetector
class Clock:
 def __init__(self): self.v=0
 def __call__(self): return self.v
 def step(self,x=.2): self.v+=x

def test_stability_requires_settle():
 c=Clock(); d=StabilityDetector(StabilityProfile(window_size=4,minimum_samples=4,max_spread_g=.5,max_stddev_g=.3,settle_ms=300),clock=c)
 for v in [100,100.1,99.9,100.05]: c.step(); r=d.add(v)
 assert not r.stable and r.reason=='settling'; c.step(.4); r=d.add(100); assert r.stable and abs(r.weight_g-100)<.1

def test_capacity_gate():
 d=StabilityDetector(StabilityProfile(maximum_weight_g=10,settle_ms=0)); assert d.add(11).reason=='above_capacity'
