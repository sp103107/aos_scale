from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from .runner import StageRunner

def parser():
    p=argparse.ArgumentParser(prog='best-buds-weight-station-stage')
    p.add_argument('--repo-root',type=Path)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('list')
    i=sub.add_parser('inspect'); i.add_argument('--stage',required=True)
    r=sub.add_parser('run'); r.add_argument('--stage',required=True); r.add_argument('--run-id')
    rp=sub.add_parser('run-plan'); rp.add_argument('--plan',required=True); rp.add_argument('--run-id'); rp.add_argument('--start-stage')
    sub.add_parser('status'); sub.add_parser('validate-receipts')
    rs=sub.add_parser('resume'); rs.add_argument('--run-id',required=True); rs.add_argument('--plan',default='cursor_ready')
    return p

def main(argv=None):
    # Some coding-agent environments preload ddtrace through sitecustomize. Its
    # shutdown hook can keep an otherwise completed subprocess alive. Re-exec
    # the real CLI once with tracing disabled so stage commands terminate
    # deterministically and preserve their actual exit code.
    if argv is None and "ddtrace" in sys.modules and os.environ.get("BBWS_STAGE_REEXEC") != "1":
        env = {**os.environ, "DD_TRACE_ENABLED": "false", "DD_TRACE_STARTUP_LOGS": "false", "BBWS_STAGE_REEXEC": "1"}
        os.execvpe(sys.executable, [sys.executable, "-m", "best_buds_weight_station.stage_runner", *sys.argv[1:]], env)
    args=parser().parse_args(argv); runner=StageRunner(args.repo_root)
    if args.command=='list': result={'version':runner.version,'stages':[s['stage_id'] for s in runner.catalog.list()]}
    elif args.command=='inspect': result=runner.catalog.stage(args.stage)
    elif args.command=='run': result=runner.run_stage(args.stage,run_id=args.run_id)
    elif args.command=='run-plan': result=runner.run_plan(args.plan,run_id=args.run_id,start_stage=args.start_stage)
    elif args.command=='status': result=runner.status()
    elif args.command=='validate-receipts': result=runner.validate_receipts()
    else:
        cp=runner.repo_root/'validation/checkpoints'/f'{args.run_id}.json'
        if not cp.exists(): raise SystemExit(f'checkpoint not found: {cp}')
        checkpoint=json.loads(cp.read_text()); result=runner.run_plan(args.plan,run_id=args.run_id,start_stage=checkpoint.get('next_stage'))
    print(json.dumps(result,indent=2,sort_keys=True))
    code = 1 if result.get('status') == 'FAIL' else 0
    if argv is None:
        sys.stdout.flush(); sys.stderr.flush(); os._exit(code)
    return code
