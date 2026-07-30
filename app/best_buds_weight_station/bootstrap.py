from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .validation.bootstrap import run_agent_bootstrap
from .stage_runner import StageRunner
from .version import __version__

def parser():
    p=argparse.ArgumentParser(prog='best-buds-weight-station-bootstrap',description='Run evidence-gated coding-agent readiness profiles.')
    p.add_argument('--repo-root',type=Path); p.add_argument('--profile',choices=('development','prehardware','operator-ready','cursor-ready'),default='prehardware')
    p.add_argument('--run-id'); p.add_argument('--skip-ui',action='store_true'); p.add_argument('--no-persist',action='store_true'); p.add_argument('--output',type=Path); p.add_argument('--version',action='store_true'); return p

def main(argv=None):
    args=parser().parse_args(argv)
    if args.version: print(__version__); return 0
    try:
        base_profile='operator-ready' if args.profile=='cursor-ready' else args.profile
        result=run_agent_bootstrap(args.repo_root,profile=base_profile,include_ui=not args.skip_ui,persist=not args.no_persist,run_id=args.run_id)
        if args.profile=='cursor-ready' and result['status']!='FAIL':
            stage=StageRunner(args.repo_root,persist=not args.no_persist).run_plan('cursor_ready',run_id=args.run_id or 'cursor-ready-v0.1.10')
            result['profile']='cursor-ready'; result['stage_plan']=stage
            result['status']='PASS_WITH_WARNINGS' if stage['status']=='PASS' else 'FAIL'
            result['verdicts']=stage['verdicts']
            result['next_phase']='rc3c15_judge_core_hardening_and_release_truth_closure'
        text=json.dumps(result,indent=2,sort_keys=True)
        if args.output: args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(text+'\n',encoding='utf-8')
        print(text); return 1 if result['status']=='FAIL' else 0
    except Exception as exc:
        print(json.dumps({'status':'FAIL','error':f'{type(exc).__name__}: {exc}'},indent=2),file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
