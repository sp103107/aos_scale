import pytest
from best_buds_weight_station.hardware_buttons import ButtonEvent, LocalHardwareButtonAdapter
from best_buds_weight_station.remote_boundaries import RemoteTransportConfig, normalize_remote_action


@pytest.mark.parametrize('button,action',[('green','capture.confirm'),('yellow','scale.zero'),('red','capture.cancel'),('blue','ui.open_scale_setup')])
def test_default_hardware_button_mapping(button,action):
    request=LocalHardwareButtonAdapter().translate(ButtonEvent(button))
    assert request.action_type==action and request.source=='local_hardware_button'


def test_unknown_button_rejected():
    with pytest.raises(ValueError): LocalHardwareButtonAdapter().translate(ButtonEvent('purple'))


def test_transport_config_forbids_anonymous_commands():
    with pytest.raises(ValueError): RemoteTransportConfig('wifi',require_authentication=False).validate()


def test_transport_disabled_by_default():
    config=RemoteTransportConfig('bluetooth')
    with pytest.raises(PermissionError): normalize_remote_action({'transport':'bluetooth'},config)


def test_enabled_transport_requires_identity_auth_and_idempotency():
    config=RemoteTransportConfig('wifi',enabled=True)
    with pytest.raises(PermissionError): normalize_remote_action({'transport':'wifi','action_type':'device.status','payload':{}},config)


def test_remote_action_normalizes_to_canonical_boundary():
    config=RemoteTransportConfig('wifi',enabled=True)
    request=normalize_remote_action({'transport':'wifi','device_identity':'REMOTE-1','authenticated':True,'idempotency_key':'I-1','action_type':'device.status','payload':{}},config)
    assert request.action_type=='device.status' and request.source=='wifi' and request.idempotency_key=='I-1'


def test_remote_calibration_acceptance_forbidden():
    with pytest.raises(ValueError): RemoteTransportConfig('wifi',remote_calibration_acceptance=True).validate()
