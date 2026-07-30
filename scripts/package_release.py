#!/usr/bin/env python3
from __future__ import annotations
import argparse, zipfile
from pathlib import Path
FIXED_TIME=(2026,7,21,0,0,0)
EXCLUDED_PARTS={'.git','.pytest_cache','build','__pycache__'}

def included(root:Path):
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in rel.parts): continue
        if rel.parts[:2]==('data','runtime') or rel.parts[:3]==('validation','receipts','stages') or rel.parts[:2]==('validation','checkpoints') or (rel.parts[:2]==('validation','reports') and (rel.name.startswith('stage_plan.') or (rel.name.startswith('pytest') and rel.name!='pytest_full_suite.v0.1.8.log'))): continue
        if p.suffix=='.pyc': continue
        yield p, rel

def build(root:Path,out:Path):
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p,rel in included(root):
            arc=Path(root.name)/rel
            info=zipfile.ZipInfo(arc.as_posix(),FIXED_TIME)
            info.compress_type=zipfile.ZIP_DEFLATED
            mode=p.stat().st_mode & 0o777
            info.external_attr=(mode or 0o644)<<16
            z.writestr(info,p.read_bytes())
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).parents[1]); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); print(build(a.root.resolve(),a.output.resolve()))
if __name__=='__main__': main()
