from __future__ import annotations
import hashlib, json, os, signal, subprocess, sys, tempfile, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .catalog import StageCatalog

def now() -> str: return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(tmp,path)

class StageRunner:
    def __init__(self, repo_root: Path|None=None, *, persist: bool=True):
        self.repo_root=(repo_root or Path(__file__).resolve().parents[3]).resolve()
        self.catalog=StageCatalog(self.repo_root); self.version=self.catalog.version; self.persist=persist
    def _argv(self, argv: list[str]) -> list[str]:
        if argv and argv[0]=='python': return [sys.executable,*argv[1:]]
        return argv
    def _run_command(self, command: dict) -> dict[str,Any]:
        argv=self._argv(command['argv']); started=now(); start=time.time()
        env={**os.environ,'PYTHONPATH':str(self.repo_root/'app')+(os.pathsep+os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else ''),'PYTHONDONTWRITEBYTECODE':'1','DD_TRACE_ENABLED':'false','DD_TRACE_STARTUP_LOGS':'false'}
        timeout=int(command.get('timeout_seconds',900))
        with tempfile.TemporaryDirectory(prefix='bbws-command-') as td:
            out_path=Path(td)/'stdout.log'; err_path=Path(td)/'stderr.log'
            with out_path.open('w+',encoding='utf-8') as out, err_path.open('w+',encoding='utf-8') as err:
                process=subprocess.Popen(
                    argv, cwd=self.repo_root, env=env, text=True,
                    stdout=out, stderr=err,
                    start_new_session=(os.name != 'nt'),
                    creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0),
                )
                timed_out=False
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out=True
                    if os.name == 'nt':
                        process.kill()
                    else:
                        try: os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError: pass
                    try: process.wait(timeout=10)
                    except subprocess.TimeoutExpired: pass
                out.flush(); err.flush()
            stdout=out_path.read_text(encoding='utf-8',errors='replace')
            stderr=err_path.read_text(encoding='utf-8',errors='replace')
        exit_code=124 if timed_out else process.returncode
        if timed_out: stderr=(stderr+'\ntimeout').strip()
        return {'argv':argv,'started_at':started,'finished_at':now(),'duration_s':round(time.time()-start,3),'exit_code':exit_code,'stdout':stdout[-12000:],'stderr':stderr[-12000:],'evidence_class':command.get('evidence_class','runtime_execution_pass')}
    def _run_stage_isolated(self, stage_id: str, run_id: str) -> dict[str,Any]:
        stage=self.catalog.stage(stage_id)
        timeout=max(300,sum(int(c.get('timeout_seconds',900)) for c in stage['commands'])+60)
        argv=[sys.executable,'-m','best_buds_weight_station.stage_runner','--repo-root',str(self.repo_root),'run','--stage',stage_id,'--run-id',run_id]
        env={**os.environ,'PYTHONPATH':str(self.repo_root/'app')+(os.pathsep+os.environ['PYTHONPATH'] if os.environ.get('PYTHONPATH') else ''),'PYTHONDONTWRITEBYTECODE':'1','DD_TRACE_ENABLED':'false','DD_TRACE_STARTUP_LOGS':'false'}
        started=now()
        with tempfile.TemporaryDirectory(prefix='bbws-stage-child-') as td:
            out_path=Path(td)/'stdout.json'; err_path=Path(td)/'stderr.log'
            with out_path.open('w+',encoding='utf-8') as out, err_path.open('w+',encoding='utf-8') as err:
                process=subprocess.Popen(argv,cwd=self.repo_root,env=env,text=True,stdout=out,stderr=err,start_new_session=(os.name!='nt'),creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name=='nt' else 0))
                timed_out=False
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out=True
                    if os.name=='nt': process.kill()
                    else:
                        try: os.killpg(process.pid,signal.SIGKILL)
                        except ProcessLookupError: pass
                    try: process.wait(timeout=10)
                    except subprocess.TimeoutExpired: pass
                out.flush(); err.flush()
            stdout=out_path.read_text(encoding='utf-8',errors='replace')
            stderr=err_path.read_text(encoding='utf-8',errors='replace')
        try:
            receipt=json.loads(stdout)
        except Exception:
            receipt={
                'receipt_id':f'{run_id}-{stage_id}','run_id':run_id,'stage_id':stage_id,
                'version':self.version,'status':'FAIL','started_at':started,'finished_at':now(),
                'commands':[{'argv':argv,'started_at':started,'finished_at':now(),'duration_s':None,'exit_code':124 if timed_out else process.returncode,'stdout':stdout[-12000:],'stderr':stderr[-12000:] or ('timeout' if timed_out else 'invalid isolated stage output'),'evidence_class':'runtime_execution_pass'}],
                'evidence_class':'runtime_execution_pass','artifacts':[],
                'warnings':['isolated stage output was not valid JSON'],
                'non_claims':['Physical UNO R3, HX711, load-cell, and native Windows execution are not proven by this stage.'],
                'next_stage':stage.get('next_stage'),
            }
        return receipt

    def run_stage(self, stage_id: str, *, run_id: str|None=None) -> dict[str,Any]:
        stage=self.catalog.stage(stage_id); run_id=run_id or f'stage-{uuid.uuid4().hex[:12]}'; started=now(); results=[]
        if self.persist:
            atomic_json(self.repo_root/'validation/checkpoints'/f'{run_id}.json', {'run_id':run_id,'stage_id':stage_id,'version':self.version,'status':'RUNNING','updated_at':now(),'next_stage':stage.get('next_stage')})
        for command in stage['commands']:
            result=self._run_command(command); results.append(result)
            if command.get('required',True) and result['exit_code']!=0: break
        failed=[r for r in results if r['exit_code']!=0]
        status='FAIL' if failed else 'PASS'
        receipt={'receipt_id':f'{run_id}-{stage_id}','run_id':run_id,'stage_id':stage_id,'version':self.version,'status':status,'started_at':started,'finished_at':now(),'commands':results,'evidence_class':'runtime_execution_pass' if results else 'static_validation_pass','artifacts':[p for p in stage.get('expected_artifacts',[]) if (self.repo_root/p).exists()],'warnings':[],'non_claims':['Physical UNO R3, HX711, load-cell, and native Windows execution are not proven by this stage.'],'next_stage':stage.get('next_stage')}
        if self.persist:
            path=self.repo_root/'validation/receipts/stages'/f'{stage_id}.latest.json'; atomic_json(path,receipt)
            checkpoint={'run_id':run_id,'stage_id':stage_id,'version':self.version,'status':status,'updated_at':now(),'receipt_path':path.relative_to(self.repo_root).as_posix(),'next_stage':stage.get('next_stage')}
            atomic_json(self.repo_root/'validation/checkpoints'/f'{run_id}.json',checkpoint)
        return receipt
    def run_plan(self, plan_id: str, *, run_id: str|None=None, start_stage: str|None=None) -> dict[str,Any]:
        plan=self.catalog.plan(plan_id); run_id=run_id or f'{plan_id}-{uuid.uuid4().hex[:12]}'; started=now(); receipts=[]; started_flag=start_stage is None
        for stage_id in plan['stages']:
            if not started_flag:
                started_flag=stage_id==start_stage
                if not started_flag: continue
            # Stage commands use isolated subprocess groups with file-backed output.
            # This prevents GUI/test descendants from holding orchestration pipes open
            # while preserving one resumable plan process and atomic per-stage receipts.
            receipt=self.run_stage(stage_id,run_id=run_id)
            receipts.append(receipt)
            if receipt['status']=='FAIL': break
        status='PASS' if receipts and all(r['status']=='PASS' for r in receipts) and len(receipts)==len(plan['stages'])-(plan['stages'].index(start_stage) if start_stage else 0) else 'FAIL'
        verdicts=plan['final_verdicts'] if status=='PASS' else ['CURSOR_NOT_READY']
        report={'run_id':run_id,'plan_id':plan_id,'version':self.version,'status':status,'started_at':started,'finished_at':now(),'completed_stages':[r['stage_id'] for r in receipts if r['status']=='PASS'],'failed_stage':next((r['stage_id'] for r in receipts if r['status']=='FAIL'),None),'receipts':receipts,'verdicts':verdicts,'non_claims':plan.get('allowed_nonclaims',[])}
        if self.persist:
            atomic_json(self.repo_root/'validation/reports'/f'stage_plan.{run_id}.json',report)
            atomic_json(self.repo_root/'validation/reports'/f'stage_plan.{plan_id}.latest.json',report)
        return report
    def status(self) -> dict[str,Any]:
        rows=[]
        for stage in self.catalog.list():
            p=self.repo_root/'validation/receipts/stages'/f"{stage['stage_id']}.latest.json"
            rows.append({'stage_id':stage['stage_id'],'status':json.loads(p.read_text())['status'] if p.exists() else 'NOT_RUN','receipt':p.relative_to(self.repo_root).as_posix() if p.exists() else None})
        return {'version':self.version,'stages':rows}
    def validate_receipts(self) -> dict[str,Any]:
        errors=[]; count=0
        for p in sorted((self.repo_root/'validation/receipts/stages').glob('*.json')):
            data=json.loads(p.read_text()); count+=1
            for key in ('receipt_id','run_id','stage_id','version','status','started_at','finished_at','commands','evidence_class','non_claims'):
                if key not in data: errors.append(f'{p.name}:missing:{key}')
        return {'status':'PASS' if not errors else 'FAIL','receipt_count':count,'errors':errors}
