from best_buds_weight_station.alice import AliceResponseAgent, TruthClass
from best_buds_weight_station.models import RunContext, StabilityProfile
from best_buds_weight_station.state_machine import CaptureMachine, State
from best_buds_weight_station.storage import SessionStore
from best_buds_weight_station.ui import process_terminal_result


def machine_for(tmp_path, mode='automatic'):
    context = RunContext('S', 'R', 'O', 'F', 'ST', 'C', 'raw', 'norm', 'BIN', 0)
    beeps = []
    machine = CaptureMachine(
        SessionStore(tmp_path, context),
        StabilityProfile(window_size=3, minimum_samples=3, settle_ms=0),
        beeps.append,
    )
    machine.connect()
    machine.start_session(mode)
    return machine, beeps


def test_automatic_terminal_result_reaches_alice_before_feedback(tmp_path):
    machine, beeps = machine_for(tmp_path, 'automatic')
    agent = AliceResponseAgent()
    machine.scan('AUTO-1')
    result = None
    for value in [100.0, 100.1, 100.0]:
        result = machine.reading(value)
    assert isinstance(result, tuple)
    assert machine.state == State.RECORD_SAVED and beeps == []
    response, record, advanced = process_terminal_result(machine, agent, result, session_id='S')
    assert advanced is True
    assert response.truth_class == TruthClass.RECEIPT_CONFIRMED
    assert record['barcode_normalized'] == 'AUTO-1'
    assert beeps == ['success'] and machine.state == State.WAITING_FOR_BARCODE


def test_manual_terminal_result_reaches_alice_before_feedback(tmp_path):
    machine, beeps = machine_for(tmp_path, 'manual')
    agent = AliceResponseAgent()
    machine.scan('MANUAL-1')
    for value in [100.0, 100.1, 100.0]:
        machine.reading(value)
    result = machine.confirm()
    assert machine.state == State.RECORD_SAVED and beeps == []
    response, record, advanced = process_terminal_result(machine, agent, result, session_id='S')
    assert advanced and response.truth_class == TruthClass.RECEIPT_CONFIRMED
    assert record['barcode_normalized'] == 'MANUAL-1'
    assert beeps == ['success'] and machine.state == State.WAITING_FOR_BARCODE


def test_verified_duplicate_uses_warning_feedback_and_advances(tmp_path):
    machine, beeps = machine_for(tmp_path, 'automatic')
    agent = AliceResponseAgent()
    machine.state = State.RECORD_SAVED
    duplicate = {
        'status': 'duplicate',
        'record_id': 'record-1',
        'original_receipt_id': 'receipt-1',
    }
    response, record, advanced = process_terminal_result(machine, agent, duplicate, session_id='S')
    assert record is None and advanced
    assert response.truth_class == TruthClass.RECEIPT_CONFIRMED
    assert beeps == ['warning'] and machine.state == State.WAITING_FOR_BARCODE


def test_unresolved_duplicate_blocks_feedback_and_progression(tmp_path):
    machine, beeps = machine_for(tmp_path, 'automatic')
    agent = AliceResponseAgent()
    machine.state = State.LOCAL_COMMIT_PENDING
    duplicate = {'status': 'duplicate', 'record_id': 'record-1'}
    response, _, advanced = process_terminal_result(machine, agent, duplicate, session_id='S')
    assert not advanced and response.truth_class == TruthClass.BLOCKED
    assert 'original commit receipt' in response.operator_message
    assert beeps == [] and machine.state == State.LOCAL_COMMIT_PENDING
