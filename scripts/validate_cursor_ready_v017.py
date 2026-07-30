#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION=(ROOT/'VERSION').read_text().strip()
required=[
 'pipeline/stage_catalog.v0.1.7.json','pipeline/plans/cursor_ready.v0.1.7.json','app/best_buds_weight_station/stage_runner/cli.py',
 'cursor_bootstrap.bat','cursor_bootstrap.ps1','cursor_bootstrap.sh','run_stage.bat','run_stage.ps1','run_stage.sh','resume_stage.bat','resume_stage.ps1','resume_stage.sh',
 'frontend/design_tokens.v0.1.7.json','frontend/themes/windows_light.qss','entrypoints/surface_entry_map.v0.1.7.json','pods/best_buds_weight_station_pod_manifest.v0.1.7.json',
 'reports/execution_posture_decision.v0.1.7.json','runtime/evidence_index.v0.1.7.json','context/working_set/working_set_update_0008.json','context/episodes/episode_0008_v0.1.7.json'
]
missing=[p for p in required if not (ROOT/p).exists()]
commands=[]
env={'PYTHONPATH':str(ROOT/'app')}
for argv in [
 [sys.executable,'-m','best_buds_weight_station.stage_runner','list'],
 [sys.executable,'-m','best_buds_weight_station.stage_runner','status'],
 [sys.executable,'-m','best_buds_weight_station.stage_runner','validate-receipts'],
]:
 cp=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True,env={**__import__('os').environ,**env}); commands.append({'argv':argv,'exit_code':cp.returncode,'stdout':cp.stdout[-2000:],'stderr':cp.stderr[-2000:]})
if any(c['exit_code'] for c in commands): missing.append('stage_runner_command_failure')
state=json.loads((ROOT/'repo_release_state.json').read_text())
checks={
 'version':VERSION=='0.1.7',
 'full_repo':state.get('bump_scope')=='full_repo',
 'execution_posture':state.get('execution_posture')=='real_execution_allowed',
 'production_false':state.get('production_ready_claimed') is False and state.get('release_seal_claimed') is False,
 'physical_not_run':state.get('physical_device_status')=='not_run',
 'context_seq':json.loads((ROOT/'context/working_set/working_set_update_0008.json').read_text()).get('update_seq')==8,
 'canonical_serial':'PySerialTransport -> DeviceService -> ScaleReadingWorker' in (ROOT/'README.md').read_text(),
}
failures=missing+[k for k,v in checks.items() if not v]
report={'version':VERSION,'status':'PASS' if not failures else 'FAIL','checks':checks,'required_count':len(required),'failures':failures,'commands':commands,'verdicts':['CURSOR_READY','OPERATOR_SOFTWARE_READY','PHYSICAL_HARDWARE_NOT_RUN','WINDOWS_NATIVE_RUNTIME_NOT_RUN'] if not failures else ['CURSOR_NOT_READY']}
(ROOT/'reports/cursor_ready_validation.v0.1.7.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2,sort_keys=True)); raise SystemExit(1 if failures else 0)
