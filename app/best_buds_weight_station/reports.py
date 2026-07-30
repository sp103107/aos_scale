from __future__ import annotations
import json,csv,hashlib
from collections import defaultdict
from pathlib import Path
from openpyxl import Workbook
from .storage import parse_jsonl,canonical,atomic_json

def compile_report(session_dir: str|Path):
    d=Path(session_dir); rows=[r for r in parse_jsonl(d/'records.jsonl') if r.get('event_type')=='weight_record' and r.get('record_status')=='accepted']
    rows.sort(key=lambda r:r['sequence']); total=round(sum(r['net_g'] for r in rows),3); by=defaultdict(float)
    for r in rows: by[r['cultivar_normalized_name']]+=r['net_g']
    source_hash=hashlib.sha256(('\n'.join(canonical(r) for r in rows)+'\n').encode()).hexdigest()
    compiled_at=max([r['captured_at'] for r in rows],default='1970-01-01T00:00:00Z')
    report={'report_id':f"harvest-report-{rows[0]['session_id'] if rows else d.name}",'session_id':rows[0]['session_id'] if rows else d.name,'record_count':len(rows),'total_net_g':total,'cultivar_totals':{k:round(v,3) for k,v in sorted(by.items())},'records_sha256':source_hash,'compiled_at':compiled_at}
    out=d/'reports'; out.mkdir(exist_ok=True); atomic_json(out/'harvest_run_report.json',report)
    with (out/'harvest_run_report.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['cultivar','net_g']); [w.writerow([k,v]) for k,v in report['cultivar_totals'].items()]; w.writerow(['TOTAL',total])
    wb=Workbook(); ws=wb.active; ws.title='Summary'; ws.append(['Cultivar','Net g']); [ws.append([k,v]) for k,v in report['cultivar_totals'].items()]; ws.append(['TOTAL',total]); wb.save(out/'harvest_run_report.xlsx')
    return report
