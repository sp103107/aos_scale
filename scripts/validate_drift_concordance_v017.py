#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION=(ROOT/'VERSION').read_text().strip()
CURRENT=[
 'README.md','docs/SYSTEM_STATE_CURRENT.md','docs/WINDOWS_FIRST_OPERATOR_APPLICATION_V0.1.7.md','docs/WINDOWS_BUILD.md','docs/DEBIAN_INSTALL.md',
 'repo_release_state.json','guide_pack.json','backend/backend_manifest.v0.1.7.json','frontend/frontend_manifest.v0.1.7.json',
 'release_candidate/rc_phase_matrix.v0.1.7.json','cursor/CURSOR_UNO_R3_PHYSICAL_INTEGRATION_HANDOFF_V0_1_7.md',
 'context/working_set/working_set_update_0008.json','context/episodes/episode_0008_v0.1.7.json','context/resume_pack/resume_pack_manifest.v0.1.7.json',
 'pipeline/stage_catalog.v0.1.7.json','pipeline/plans/cursor_ready.v0.1.7.json'
]
issues=[]
for rel in CURRENT:
 p=ROOT/rel
 if not p.exists(): issues.append({'code':'CURRENT_MISSING','path':rel}); continue
 text=p.read_text(encoding='utf-8',errors='ignore')
 if VERSION not in text: issues.append({'code':'CURRENT_VERSION_MISSING','path':rel})
# Current docs must not present an older version as current.
for rel in CURRENT[:5]:
 text=(ROOT/rel).read_text(encoding='utf-8')
 for old in ('0.1.3','0.1.4','0.1.5','0.1.6'):
  if re.search(rf'(?i)(current|version|package)\D{{0,25}}{re.escape(old)}',text): issues.append({'code':'STALE_CURRENT_REFERENCE','path':rel,'value':old})
# Historical immutable records may retain old versions.
historical=list((ROOT/'context/episodes').glob('episode_*_v0.1.[0-6].json'))+list((ROOT/'manifests').glob('file_manifest.v0.1.[0-6].json'))
report={'version':VERSION,'status':'PASS' if not issues else 'FAIL','current_surface_count':len(CURRENT),'historical_immutable_count':len(historical),'compatibility_policy':'allowed_only_when_explicitly_labeled','issues':issues}
out=ROOT/'reports/drift_concordance_report.v0.1.7.json'; out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,indent=2,sort_keys=True)); raise SystemExit(1 if issues else 0)
