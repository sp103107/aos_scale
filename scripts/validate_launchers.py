from __future__ import annotations
import json,os,stat,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=['launch_best_buds','launch_simulator','bootstrap_agent','run_validation','cursor_bootstrap','run_stage','resume_stage']
REQUIRED=[f'{name}.{ext}' for name in BASE for ext in ('bat','ps1','sh')]

def main()->int:
 results={'required':{},'shell_syntax':{},'dry_run':{},'status':'PASS'}; failures=[]
 for rel in REQUIRED:
  path=ROOT/rel; exists=path.is_file(); results['required'][rel]=exists
  if not exists: failures.append(f'missing:{rel}'); continue
  text=path.read_text(encoding='utf-8')
  if rel.endswith('.bat'): markers=['%~dp0','scripts\\launcher.py','exit /b']
  elif rel.endswith('.ps1'): markers=['$PSScriptRoot','scripts/launcher.py','$LASTEXITCODE']
  else:
   markers=['dirname','scripts/launcher.py','exec']
   if not (path.stat().st_mode & stat.S_IXUSR): failures.append(f'not_executable:{rel}')
  for marker in markers:
   if marker not in text: failures.append(f'missing_marker:{rel}:{marker}')
 for rel in [x for x in REQUIRED if x.endswith('.sh')]:
  cp=subprocess.run(['sh','-n',str(ROOT/rel)],text=True,capture_output=True); results['shell_syntax'][rel]=cp.returncode
  if cp.returncode: failures.append(f'shell_syntax:{rel}:{cp.stderr.strip()}')
 for mode,args in [('launch',[]),('simulator',[]),('bootstrap',[]),('validation',[]),('stage',['list'])]:
  cp=subprocess.run([sys.executable,'scripts/launcher.py',mode,'--direct','--dry-run',*args],cwd=ROOT,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  results['dry_run'][mode]={'exit_code':cp.returncode,'stdout':cp.stdout.strip()}
  if cp.returncode or 'best_buds_weight_station' not in cp.stdout: failures.append(f'dry_run:{mode}')
 if failures: results['status']='FAIL'; results['failures']=failures
 print(json.dumps(results,indent=2,sort_keys=True)); return 1 if failures else 0
if __name__=='__main__': raise SystemExit(main())
