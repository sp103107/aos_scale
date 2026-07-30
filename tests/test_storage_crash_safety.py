import json
import pytest
from best_buds_weight_station.models import CaptureCommand, RunContext
from best_buds_weight_station.storage import CommitStepError, SessionStore, parse_jsonl


def context(): return RunContext('CRASH-S','CRASH-R','OP','FAC','ST','CV','raw','norm','BIN',0)
def command(): return CaptureCommand('BC-1',100.0,8,{'spread_g':0.1,'stddev_g':0.02},'automatic',idempotency_key='CRASH-S:1:BC-1')


@pytest.mark.parametrize('step', ['before_jsonl','jsonl'])
def test_crash_before_authoritative_append_loses_no_commit(tmp_path,step):
    store=SessionStore(tmp_path,context(),step)
    with pytest.raises(CommitStepError): store.commit(command())
    assert parse_jsonl(store.records_path)==[]


def test_crash_during_jsonl_quarantines_incomplete_tail(tmp_path):
    store=SessionStore(tmp_path,context(),'during_jsonl')
    with pytest.raises(CommitStepError): store.commit(command())
    reopened=SessionStore(tmp_path,context())
    assert reopened.recovery_required
    receipt=reopened.recover_from_ledger()
    assert receipt['records_seen']==0 and receipt['jsonl_tail_repair']['repaired']


@pytest.mark.parametrize('step', ['after_jsonl','before_individual','individual_json','during_individual','after_individual','before_checkpoint','checkpoint','during_checkpoint','after_checkpoint','recent_pointer','before_receipt'])
def test_post_append_interruptions_recover_single_commit(tmp_path,step):
    pointer=tmp_path/'config'/'recent.json'
    store=SessionStore(tmp_path,context(),step,recent_pointer_path=pointer)
    with pytest.raises(CommitStepError): store.commit(command())
    reopened=SessionStore(tmp_path,context(),recent_pointer_path=pointer)
    assert reopened.recovery_required
    receipt=reopened.recover_from_ledger()
    rows=[r for r in parse_jsonl(reopened.records_path) if r.get('event_type')=='weight_record']
    assert len(rows)==1 and reopened.verify_chain()==(True,'ok')
    assert json.load(reopened.snapshot_path.open())['last_sequence']==1
    assert receipt['uncommitted_weight_restored'] is False
    assert reopened.idempotency_map['CRASH-S:1:BC-1']['receipt_id']


def test_restart_after_receipt_does_not_duplicate(tmp_path):
    store=SessionStore(tmp_path,context()); record,receipt=store.commit(command())
    reopened=SessionStore(tmp_path,context())
    with pytest.raises(Exception) as exc: reopened.commit(command())
    assert getattr(exc.value,'record_id',None)==record['record_id']


def test_temporary_files_are_quarantined(tmp_path):
    store=SessionStore(tmp_path,context()); tmp=store.session_dir/'orphan.tmp'; tmp.write_text('partial')
    reopened=SessionStore(tmp_path,context()); assert reopened.recovery_required
    receipt=reopened.recover_from_ledger(); assert receipt['temporary_files_quarantined'] and not tmp.exists()


def test_hash_chain_corruption_is_not_repaired(tmp_path):
    store=SessionStore(tmp_path,context()); store.commit(command())
    row=json.loads(store.records_path.read_text().splitlines()[0]); row['gross_g']=999
    store.records_path.write_text(json.dumps(row)+'\n')
    reopened=SessionStore(tmp_path,context())
    with pytest.raises(ValueError): reopened.recover_from_ledger()
