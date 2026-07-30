from best_buds_weight_station.alice import AliceResponseAgent, TruthClass


def test_missing_cultivar_roster_blocks_start():
    response = AliceResponseAgent().respond('SESSION_SETUP', context={'operator_id': 'OP-004', 'run_id': 'HR-1', 'cultivar_roster': []})
    assert response.truth_class is TruthClass.BLOCKED
    assert response.command_proposal is None
    assert response.required_action.action_type == 'register_cultivar'
    assert 'start_capture' in response.blocked_actions


def test_every_required_state_has_instruction_and_allowed_actions():
    states = ['DISCONNECTED','DEVICE_READY','SESSION_SETUP','SESSION_READY','WAITING_FOR_BARCODE','BARCODE_CAPTURED','WAITING_FOR_STABLE_WEIGHT','WEIGHT_STABLE','AUTO_RECORD','MANUAL_CONFIRM','LOCAL_COMMIT_PENDING','RECORD_SAVED','RECOVERY_REQUIRED','BLOCKED','ERROR']
    agent = AliceResponseAgent()
    for state in states:
        context = {'cultivar_roster': ['C']} if state == 'SESSION_SETUP' else {}
        response = agent.respond(state, context=context)
        assert response.state == state
        assert response.operator_message
        assert response.allowed_actions


def test_manual_confirm_does_not_auto_submit():
    response = AliceResponseAgent().respond('MANUAL_CONFIRM', context={'net_g': 1200.0})
    assert '1200.0 g net' in response.operator_message
    assert response.command_proposal is None
    assert response.required_action.action_type == 'confirm_and_continue'
