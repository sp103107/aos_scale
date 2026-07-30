#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/"app"))
from best_buds_weight_station.validation.cli import main
raise SystemExit(main(sys.argv[1:]))
