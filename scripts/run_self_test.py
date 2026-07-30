#!/usr/bin/env python3
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'app'))
from best_buds_weight_station.selftest import run_self_test
print(json.dumps(run_self_test(),indent=2,sort_keys=True))
