#!/usr/bin/env python3
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parents[1]/"app"))
from best_buds_weight_station.validation.harness import ValidationHarness
profile=sys.argv[1] if len(sys.argv)>1 else "development"
print(json.dumps(ValidationHarness(Path(__file__).parents[1]).prepare(profile).to_dict(),indent=2,sort_keys=True))
