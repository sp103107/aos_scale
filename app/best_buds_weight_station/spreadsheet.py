from __future__ import annotations
import csv, os, shutil
from pathlib import Path
from openpyxl import Workbook, load_workbook

HEADERS=['sequence','record_id','captured_at','barcode_raw','barcode_normalized','cultivar_raw_name','cultivar_normalized_name','run_id','container_id','tare_g','gross_g','net_g','operator_id','station_id','device_id','calibration_id','capture_mode','duplicate_status','record_hash']

def safe_cell(value):
    if isinstance(value,str) and value[:1] in ('=','+','-','@'): return "'"+value
    return value

def row_for(record): return [safe_cell(record.get(h,'')) for h in HEADERS]

def append_csv(path: Path, record: dict):
    path.parent.mkdir(parents=True,exist_ok=True); new=not path.exists()
    with path.open('a',newline='',encoding='utf-8') as f:
        out=csv.writer(f)
        if new: out.writerow(HEADERS)
        out.writerow(row_for(record)); f.flush(); os.fsync(f.fileno())

def append_xlsx(path: Path, record: dict):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        wb=load_workbook(path); ws=wb.active
        existing=[c.value for c in ws[1]]
        if existing[:len(HEADERS)] != HEADERS:
            backup=path.with_suffix(path.suffix+'.incompatible.backup')
            if not backup.exists(): shutil.copy2(path,backup)
            raise ValueError('incompatible spreadsheet header')
    else:
        wb=Workbook(); ws=wb.active; ws.title='Weights'; ws.append(HEADERS); ws.freeze_panes='A2'; ws.auto_filter.ref=f'A1:S1'
    ws.append(row_for(record))
    tmp=path.with_suffix('.tmp.xlsx'); wb.save(tmp); os.replace(tmp,path)
