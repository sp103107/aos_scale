from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory

from .alice import AliceResponseAgent, TruthClass
from .envelope import ack_for, make_envelope, terminal_for, validate_envelope
from .models import RunContext, StabilityProfile
from .reports import compile_report
from .simulator import stable_sequence
from .state_machine import CaptureMachine, State
from .storage import SessionStore


def _alice_complete(machine: CaptureMachine, agent: AliceResponseAgent, result, beeps: list[str], feedback_kind='success'):
    before = list(beeps)
    if isinstance(result, dict):
        response = agent.respond('LOCAL_COMMIT_PENDING', backend_result=result, session_id=machine.store.context.session_id)
    else:
        _, receipt = result
        response = agent.respond('LOCAL_COMMIT_PENDING', backend_result=receipt.to_dict(), session_id=machine.store.context.session_id)
    assert response.truth_class == TruthClass.RECEIPT_CONFIRMED
    assert beeps == before, 'terminal feedback occurred before Alice validation'
    machine.complete_terminal_result(feedback_kind)
    return response


def run_self_test(data_root=None):
    holder = TemporaryDirectory() if data_root is None else None
    root = Path(data_root or holder.name)
    beeps: list[str] = []
    agent = AliceResponseAgent()
    ctx = RunContext(
        'SELFTEST-SESSION', 'HARVEST-2026-001', 'operator-test', 'facility-test',
        'station-test', 'cultivar-1', 'Test Strain', 'Test Cultivar', 'BUCKET-01', 10.0,
    )
    store = SessionStore(root, ctx)
    machine = CaptureMachine(store, StabilityProfile(settle_ms=0), beep=beeps.append)
    machine.connect()
    machine.start_session('automatic')
    machine.scan('BB-0001')
    saved = None
    for reading in stable_sequence(125.0):
        out = machine.reading(reading.weight_g, reading.raw_value, reading.ready)
        if isinstance(out, tuple):
            saved = out
    assert saved and beeps == [] and machine.state == State.RECORD_SAVED
    _alice_complete(machine, agent, saved, beeps)
    assert beeps == ['success'] and machine.state == State.WAITING_FOR_BARCODE
    assert saved[0]['gross_g'] == 125.0 and saved[0]['tare_g'] == 10.0 and saved[0]['net_g'] == 115.0

    machine.mode = 'manual'
    machine.scan('BB-0002')
    for reading in stable_sequence(200.0):
        machine.reading(reading.weight_g, reading.raw_value, reading.ready)
    assert machine.state == State.MANUAL_CONFIRM
    saved2 = machine.confirm()
    assert beeps == ['success'] and machine.state == State.RECORD_SAVED
    _alice_complete(machine, agent, saved2, beeps)
    assert saved2[0]['net_g'] == 190.0 and beeps == ['success', 'success']

    ok, reason = store.verify_chain()
    assert ok, reason
    report = compile_report(store.session_dir)
    assert report['record_count'] == 2 and report['total_net_g'] == 305.0

    env = make_envelope('weight.capture', {'barcode': 'BB-0003'})
    validate_envelope(env)
    ack = ack_for(env)
    term = terminal_for(env, 'success', saved2[1].to_dict())
    assert ack['payload']['status'] == 'accepted' and term['payload']['status'] == 'success'

    failure_beeps: list[str] = []
    failstore = SessionStore(
        root / 'failure',
        RunContext('FAIL-SESSION', 'RUN-F', 'op', 'fac', 'st', 'c', 'r', 'n', 'b', 0),
        fail_step='jsonl',
    )
    failing = CaptureMachine(failstore, StabilityProfile(settle_ms=0), beep=failure_beeps.append)
    failing.connect()
    failing.start_session()
    failing.scan('FAIL-1')
    failed = False
    try:
        for reading in stable_sequence(50):
            failing.reading(reading.weight_g, reading.raw_value, reading.ready)
    except OSError:
        failed = True
    assert failed and failure_beeps == ['error'] and not (
        failstore.records_path.exists() and failstore.records_path.stat().st_size
    )

    result = {
        'status': 'pass',
        'truth_class': 'SIMULATOR_PASS',
        'records': 2,
        'total_net_g': 305.0,
        'hash_chain': 'pass',
        'automatic_capture': 'pass',
        'manual_capture': 'pass',
        'alice_terminal_receipt_gate': 'pass',
        'no_success_before_alice_receipt_validation': 'pass',
        'local_write_failure_prevents_success_beep': 'pass',
        'data_root': str(root),
    }
    if holder:
        holder.cleanup()
    return result
