#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "app"))
from best_buds_weight_station.validation.dry_run import run_software_dry_run

print(json.dumps(run_software_dry_run(), indent=2, sort_keys=True))
