#!/usr/bin/env python3
from __future__ import annotations
import json,tempfile
from pathlib import Path
from run_v016_operator_acceptance import automatic_flow,manual_and_calibration_flow
from best_buds_weight_station.version import __version__

def main()->int:
 with tempfile.TemporaryDirectory(prefix='bbws-v017-operator-') as td:
  root=Path(td); automatic=automatic_flow(root); manual=manual_and_calibration_flow(root)
  result={
   'version':__version__,'status':'PASS' if automatic['pass'] and manual['pass'] else 'FAIL',
   'automatic':{'pass':automatic['pass'],'state':automatic['snapshot']['state'],'truth_class':automatic['snapshot']['alice_truth_class'],'record_id':automatic['snapshot']['last_saved']['record_id'] if automatic['snapshot']['last_saved'] else None},
   'manual':{'pass':manual['pass'],'state':manual['snapshot']['state'],'truth_class':manual['snapshot']['alice_truth_class'],'record_id':manual['snapshot']['last_saved']['record_id'] if manual['snapshot']['last_saved'] else None,'calibration_truth_class':manual['accepted']['truth_class']},
   'physical_device':'NOT_RUN','windows_native_runtime':'NOT_RUN'
  }
  print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
