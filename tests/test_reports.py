from best_buds_weight_station.models import RunContext,CaptureCommand
from best_buds_weight_station.storage import SessionStore
from best_buds_weight_station.reports import compile_report
def test_reproducible_report(tmp_path):
 c=RunContext('S','R','O','F','ST','C','raw','norm','BIN',1); s=SessionStore(tmp_path,c); s.commit(CaptureCommand('a',11,8,{},'manual')); r1=compile_report(s.session_dir); r2=compile_report(s.session_dir); assert r1==r2 and r1['total_net_g']==10
