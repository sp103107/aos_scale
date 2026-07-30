from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from .harness import ValidationHarness
from .bootstrap import AgentBootstrap

PROFILES=("development","prehardware","operator-ready","integration","release")

def parser():
    p=argparse.ArgumentParser(prog="best-buds-weight-station-validation")
    p.add_argument("--repo-root",type=Path)
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("inspect")
    prep=sub.add_parser("prepare"); prep.add_argument("--profile",choices=PROFILES,default="development")
    run=sub.add_parser("run"); run.add_argument("--lane",required=True); run.add_argument("--profile",choices=PROFILES,default="integration"); run.add_argument("--port"); run.add_argument("--fqbn",default="arduino:avr:uno"); run.add_argument("--reference-weight-g",type=float); run.add_argument("--barcode"); run.add_argument("--samples",type=int,default=5); run.add_argument("--zero-tolerance-g",type=float,default=2.0)
    ev=sub.add_parser("evaluate"); ev.add_argument("--profile",choices=PROFILES,default="integration")
    boot=sub.add_parser("bootstrap"); boot.add_argument("--profile",choices=("development","prehardware","operator-ready"),default="prehardware"); boot.add_argument("--skip-ui",action="store_true"); boot.add_argument("--run-id"); boot.add_argument("--no-persist",action="store_true")
    sub.add_parser("graph")
    return p

def main(argv=None):
    a=parser().parse_args(argv); h=ValidationHarness(a.repo_root)
    try:
        if a.command=="inspect": out=h.inspect()
        elif a.command=="prepare": out=h.prepare(a.profile).to_dict()
        elif a.command=="run": out=h.run_lane(a.lane,a.profile,{"port":a.port,"fqbn":a.fqbn,"reference_weight_g":a.reference_weight_g,"barcode":a.barcode,"samples":a.samples,"zero_tolerance_g":a.zero_tolerance_g}).to_dict()
        elif a.command=="evaluate": out=h.evaluate(a.profile).to_dict()
        elif a.command=="bootstrap": out=AgentBootstrap(a.repo_root,persist=not a.no_persist).run(profile=a.profile,include_ui=not a.skip_ui,run_id=a.run_id).to_dict()
        else: out=h.graph.data
        print(json.dumps(out,indent=2,sort_keys=True))
        status=out.get("status") if isinstance(out,dict) else None
        return 1 if status=="FAIL" else 0
    except Exception as exc:
        print(json.dumps({"status":"FAIL","error":f"{type(exc).__name__}: {exc}"},indent=2),file=sys.stderr); return 2
