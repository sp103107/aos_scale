import pytest
from best_buds_weight_station.alice import allowed_actions_for, redact_operator_payload
from best_buds_weight_station.alice.authority import require_allowed
from best_buds_weight_station.alice.errors import AuthorityViolation


def test_only_state_valid_actions_are_offered():
    assert 'scan_barcode' in allowed_actions_for('WAITING_FOR_BARCODE')
    assert 'confirm_and_continue' not in allowed_actions_for('WAITING_FOR_BARCODE')
    assert 'confirm_and_continue' in allowed_actions_for('MANUAL_CONFIRM')


def test_direct_persistence_action_is_forbidden():
    with pytest.raises(AuthorityViolation):
        require_allowed('WAITING_FOR_BARCODE', 'append_weight_record_directly')


def test_operator_payload_redacts_secrets_and_limits_long_text():
    result = redact_operator_payload({'token': 'abc', 'note': 'x' * 700})
    assert result['token'] == '[REDACTED]'
    assert result['note'].endswith('...') and len(result['note']) == 500
