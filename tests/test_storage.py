import json
from best_buds_weight_station.models import RunContext,CaptureCommand
from best_buds_weight_station.storage import SessionStore,parse_jsonl

def ctx(s='S'): return RunContext(s,'R','O','F','ST','C','raw','norm','BIN',10)
def test_commit_outputs_and_hash_chain(tmp_path):
 st=SessionStore(tmp_path,ctx()); rec,receipt=st.commit(CaptureCommand('abc',110,8,{'spread_g':.1},'automatic',idempotency_key='1'))
 assert rec['net_g']==100 and receipt.status=='committed'; assert st.records_path.exists() and st.snapshot_path.exists(); assert list(st.records_dir.glob('*.json')); assert (st.session_dir/'records.csv').exists(); assert (st.session_dir/'records.xlsx').exists(); assert st.verify_chain()==(True,'ok')
def test_duplicate_and_idempotency(tmp_path):
 st=SessionStore(tmp_path,ctx()); st.commit(CaptureCommand('abc',110,8,{},'automatic',idempotency_key='1')); rec,_=st.commit(CaptureCommand('abc',111,8,{},'automatic',idempotency_key='2')); assert rec['duplicate_status']=='warning'
 try: st.commit(CaptureCommand('x',12,8,{},'automatic',idempotency_key='2')); assert False
 except ValueError: pass
def test_write_failure_no_jsonl(tmp_path):
 st=SessionStore(tmp_path,ctx('F'),fail_step='jsonl')
 try: st.commit(CaptureCommand('a',20,8,{},'automatic')); assert False
 except OSError: pass
 assert not st.records_path.exists()


def test_crash_recovery_reopens_sequence(tmp_path):
 st=SessionStore(tmp_path,ctx()); r1,_=st.commit(CaptureCommand('a',20,8,{},'automatic',idempotency_key='a'))
 reopened=SessionStore(tmp_path,ctx()); assert reopened.sequence==1 and reopened.previous_hash==r1['record_hash']; r2,_=reopened.commit(CaptureCommand('b',21,8,{},'automatic',idempotency_key='b')); assert r2['sequence']==2 and reopened.verify_chain()==(True,'ok')

def test_derivative_failure_preserves_local_commit(tmp_path):
 from openpyxl import Workbook
 st=SessionStore(tmp_path,ctx()); wb=Workbook(); wb.active.append(['wrong']); wb.save(st.session_dir/'records.xlsx')
 rec,receipt=st.commit(CaptureCommand('a',20,8,{},'automatic',idempotency_key='a'))
 assert rec['sequence']==1 and receipt.derivative_status['xlsx']=='pending_sync'; assert st.records_path.exists(); assert list(st.pending_dir.glob('*.xlsx.json'))
