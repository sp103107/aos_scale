#!/usr/bin/env python3
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'app'))
from best_buds_weight_station.reports import compile_report
print(json.dumps(compile_report(sys.argv[1]),indent=2,sort_keys=True))
