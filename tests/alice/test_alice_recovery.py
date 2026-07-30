import pytest
from best_buds_weight_station.alice import AliceResponseAgent, TruthClass
from best_buds_weight_station.models import CaptureCommand, RunContext
from best_buds_weight_station.storage import CommitStepError, SessionStore


def ctx(): return RunContext('RECOVERY-S','R','O','F','ST','C','raw','norm','BIN',0)


def test_restart_recovery_rebuilds_checkpoint_from_valid_jsonl(tmp_path):
    failing=SessionStore(tmp_path,ctx(),fail_step='checkpoint')
    with pytest.raises(CommitStepError):
        failing.commit(CaptureCommand('B',100,8,{},'automatic',idempotency_key='idem'))
    reopened=SessionStore(tmp_path,ctx())
    assert reopened.recovery_required is True
    receipt=reopened.recover_from_ledger()
    assert receipt['status']=='recovered' and receipt['checkpoint_rebuilt_count']==1
    assert receipt['uncommitted_weight_restored'] is False
    response=AliceResponseAgent().respond('RECOVERY_REQUIRED',recovery_condition={'ledger_valid':True,'checkpoint_behind':True,'recovery_receipt':receipt})
    assert response.truth_class is TruthClass.RECEIPT_CONFIRMED
    assert 'No uncommitted weight was restored.' in response.operator_message


def test_serial_disconnect_before_save_is_fail():
    response=AliceResponseAgent().respond('ERROR',recovery_condition={'serial_disconnected':True})
    assert response.truth_class is TruthClass.FAIL
    assert 'weight was not saved' in response.operator_message.lower()
