import pytest
from best_buds_weight_station.alice import AliceCommandBuilder
from best_buds_weight_station.alice.errors import IncompleteContext
from best_buds_weight_station.envelope import validate_envelope


def complete_context():
    return {'session_id':'S','run_id':'R','barcode_raw':'B','cultivar_id':'C','container_id':'BIN','tare_g':84.6,'gross_g':1284.6,'net_g':1200.0,'capture_mode':'manual'}


def test_weight_command_uses_existing_aos_envelope_family():
    proposal = AliceCommandBuilder().weight_record(complete_context(), idempotency_key='idem-1', manual=True)
    env = validate_envelope(proposal.envelope)
    assert env['envelope_version'] == 'aos.application.envelope.v1'
    assert env['message_type'] == 'weight.record.request'
    assert proposal.requires_operator_confirmation is True
    assert proposal.retry_policy == 'never_automatic_after_ambiguous_failure'


def test_missing_identifier_is_not_invented():
    context = complete_context(); context['cultivar_id'] = ''
    with pytest.raises(IncompleteContext):
        AliceCommandBuilder().weight_record(context)
