import pytest
from best_buds_weight_station.alice import AliceResponseAgent, TruthClass
from best_buds_weight_station.models import CaptureCommand, RunContext
from best_buds_weight_station.storage import CommitStepError, SessionStore


def ctx(session='S'):
    return RunContext(session,'R','O','F','ST','C','raw','norm','BIN',0)


@pytest.mark.parametrize(('fail_step','failure_code'), [('jsonl','AUTHORITATIVE_APPEND_FAILED'),('individual_json','INDIVIDUAL_RECORD_WRITE_FAILED'),('checkpoint','CHECKPOINT_WRITE_FAILED')])
def test_failure_injection_never_produces_success_receipt(tmp_path, fail_step, failure_code):
    store=SessionStore(tmp_path,ctx(f'S-{fail_step}'),fail_step=fail_step)
    with pytest.raises(CommitStepError) as caught:
        store.commit(CaptureCommand('B',100,8,{},'automatic',idempotency_key='idem'))
    assert caught.value.failure_code == failure_code
    response=AliceResponseAgent().respond('LOCAL_COMMIT_PENDING',backend_result=caught.value.to_result())
    assert response.truth_class is TruthClass.FAIL
    assert 'success_beep' in response.blocked_actions
    assert 'saved locally' not in response.operator_message


def test_success_sequence_returns_all_authoritative_evidence(tmp_path):
    store=SessionStore(tmp_path,ctx())
    record,receipt=store.commit(CaptureCommand('B',100,8,{},'automatic',idempotency_key='idem'))
    body=receipt.to_dict()
    assert body['local_commit'] is True
    assert store.records_path.exists()
    assert body['individual_record_path']
    assert store.snapshot_path.exists()
    assert body['checkpoint_version'] == record['sequence']
