import pytest
from best_buds_weight_station.alice import AliceResponseAgent, TruthClass
from best_buds_weight_station.models import CaptureCommand, RunContext
from best_buds_weight_station.storage import DuplicateCommitError, SessionStore


def test_duplicate_idempotency_returns_original_receipt_and_no_second_record(tmp_path):
    ctx=RunContext('S','R','O','F','ST','C','raw','norm','BIN',0)
    store=SessionStore(tmp_path,ctx)
    record,receipt=store.commit(CaptureCommand('B',100,8,{},'automatic',idempotency_key='same'))
    with pytest.raises(DuplicateCommitError) as caught:
        store.commit(CaptureCommand('B',100,8,{},'automatic',idempotency_key='same'))
    result=caught.value.to_result()
    assert result['record_id']==record['record_id'] and result['original_receipt_id']==receipt.receipt_id
    response=AliceResponseAgent().respond('LOCAL_COMMIT_PENDING',backend_result=result)
    assert response.truth_class is TruthClass.RECEIPT_CONFIRMED
    assert 'No second record was created.' in response.operator_message
    assert store.sequence==1
