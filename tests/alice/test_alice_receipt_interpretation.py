from best_buds_weight_station.alice import AliceResponseAgent, TruthClass, valid_commit_receipt


def receipt(**updates):
    value={'status':'committed','local_commit':True,'receipt_id':'commit-42','record_id':'BB-HR-42','jsonl_event_id':'event-42','individual_record_path':'records/42.json','checkpoint_version':42,'record_hash':'a'*64,'net_g':1200.0,'derivative_status':{'xlsx':'updated'}}
    value.update(updates); return value


def test_valid_commit_receipt_allows_saved_language_and_evidence():
    response=AliceResponseAgent().respond('LOCAL_COMMIT_PENDING',backend_result=receipt())
    assert response.truth_class is TruthClass.RECEIPT_CONFIRMED
    assert 'saved locally' in response.operator_message
    assert {r['evidence_type'] for r in response.evidence_refs} == {'jsonl_event','individual_record','checkpoint','hash_chain','commit_receipt'}


def test_invalid_receipt_never_allows_success():
    bad=receipt(); bad.pop('checkpoint_version')
    assert not valid_commit_receipt(bad)
    response=AliceResponseAgent().respond('LOCAL_COMMIT_PENDING',backend_result=bad)
    assert response.truth_class is TruthClass.FAIL
    assert 'saved locally' not in response.operator_message
    assert 'success_beep' in response.blocked_actions


def test_spreadsheet_pending_does_not_block_loop_after_local_commit():
    response=AliceResponseAgent().respond('LOCAL_COMMIT_PENDING',backend_result=receipt(derivative_status={'xlsx':'pending_sync'}))
    assert response.truth_class is TruthClass.RECEIPT_CONFIRMED
    assert 'spreadsheet update is pending' in response.operator_message.lower()
    assert 'Spreadsheet continuation is not authoritative.' in response.non_claims


def test_duplicate_requires_resolvable_original_receipt():
    response = AliceResponseAgent().respond(
        'LOCAL_COMMIT_PENDING',
        backend_result={'status': 'duplicate', 'record_id': 'record-1'},
    )
    assert response.truth_class == TruthClass.BLOCKED
    assert 'scan_barcode' in response.blocked_actions
    assert 'success_beep' in response.blocked_actions
