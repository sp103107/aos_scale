from best_buds_weight_station.models import RunContext, StabilityProfile
from best_buds_weight_station.storage import SessionStore
from best_buds_weight_station.state_machine import CaptureMachine, State


def make(tmp, fail=None):
    context = RunContext('S', 'R', 'O', 'F', 'ST', 'C', 'raw', 'norm', 'BIN', 0)
    beeps = []
    machine = CaptureMachine(
        SessionStore(tmp, context, fail),
        StabilityProfile(window_size=3, minimum_samples=3, settle_ms=0),
        beeps.append,
    )
    machine.connect()
    return machine, beeps


def test_auto_and_manual_require_terminal_completion(tmp_path):
    machine, beeps = make(tmp_path)
    machine.start_session('automatic')
    machine.scan('a')
    result = None
    for value in [10, 10.1, 10]:
        result = machine.reading(value)
    assert isinstance(result, tuple)
    assert beeps == [] and machine.state == State.RECORD_SAVED
    machine.complete_terminal_result('success')
    assert beeps == ['success'] and machine.state == State.WAITING_FOR_BARCODE

    machine.mode = 'manual'
    machine.scan('b')
    for value in [20, 20.1, 20]:
        machine.reading(value)
    assert machine.state == State.MANUAL_CONFIRM
    result = machine.confirm()
    assert isinstance(result, tuple)
    assert beeps == ['success'] and machine.state == State.RECORD_SAVED
    machine.complete_terminal_result('success')
    assert beeps == ['success', 'success'] and machine.state == State.WAITING_FOR_BARCODE


def test_terminal_completion_rejects_early_or_invalid_feedback(tmp_path):
    machine, beeps = make(tmp_path)
    machine.start_session()
    try:
        machine.complete_terminal_result('success')
        assert False
    except RuntimeError:
        pass
    machine.scan('a')
    for value in [10, 10, 10]:
        result = machine.reading(value)
    assert isinstance(result, tuple)
    try:
        machine.complete_terminal_result('unknown')
        assert False
    except ValueError:
        pass
    assert beeps == [] and machine.state == State.RECORD_SAVED


def test_cancel_capture_is_state_gated(tmp_path):
    machine, _ = make(tmp_path)
    machine.start_session('manual')
    try:
        machine.cancel_capture()
        assert False
    except RuntimeError:
        pass
    machine.scan('active')
    machine.cancel_capture()
    assert machine.state == State.WAITING_FOR_BARCODE
    assert machine.barcode is None and machine.capture_idempotency_key is None


def test_failure_beep_not_success(tmp_path):
    machine, beeps = make(tmp_path, fail='jsonl')
    machine.start_session()
    machine.scan('a')
    try:
        for value in [10, 10, 10]:
            machine.reading(value)
    except OSError:
        pass
    assert beeps == ['error'] and machine.state == State.ERROR


def test_disconnect_and_reconnect(tmp_path):
    machine, beeps = make(tmp_path)
    machine.start_session()
    machine.disconnect()
    assert machine.state == State.DISCONNECTED and beeps == ['disconnect']
    machine.connect()
    machine.start_session()
    assert machine.state == State.WAITING_FOR_BARCODE
