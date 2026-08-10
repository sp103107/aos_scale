#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).parents[1]
VERSION=(ROOT/'VERSION').read_text().strip()
OUT=ROOT/f'manifests/file_manifest.v{VERSION}.json'
# Volatile/generated paths (venv installs, logs, build outputs, egg metadata)
# are excluded so the manifest stays reproducible across validation runs.
# Must stay concordant with best_buds_weight_station.validation.drift.EXCLUDED_DIRS.
EXCLUDED_DIRS={'.git','.pytest_cache','__pycache__','build','.venv','logs','dist'}
def included(path:Path)->bool:
    rel=path.relative_to(ROOT)
    if path==OUT or any(part in EXCLUDED_DIRS or part.endswith('.egg-info') for part in rel.parts): return False
    if rel.parts[:2]==('data','runtime') or rel.parts[:3]==('validation','receipts','stages') or rel.parts[:2]==('validation','checkpoints') or (rel.parts[:2]==('validation','reports') and (rel.name.startswith('stage_plan.') or (rel.name.startswith('pytest') and rel.name!=f'pytest_full_suite.v{VERSION}.log'))) or path.suffix=='.pyc': return False
    return path.is_file()
files=[]
for path in sorted(ROOT.rglob('*')):
    if included(path):
        data=path.read_bytes(); files.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'size_bytes':len(data)})
manifest={'package_name':'best_buds_cultivator_weight_station','version':VERSION,'manifest_version':'1.0.0','generated_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),'file_count':len(files),'exclusions':[OUT.relative_to(ROOT).as_posix(),'.git/','.pytest_cache/','__pycache__/','build/','.venv/','logs/','dist/','*.egg-info/','data/runtime/','validation/receipts/stages/','validation/checkpoints/','validation/reports/stage_plan.*','validation/reports/pytest* except pytest_full_suite.vNEXT.log','*.pyc'],'files':files}
OUT.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':'pass','path':str(OUT),'file_count':len(files)},indent=2))
