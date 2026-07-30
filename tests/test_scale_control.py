import json
import pytest
from best_buds_weight_station.scale_control import ScaleControlService
from tests.v013_helpers import simulated_device


def service(tmp_path): return ScaleControlService(simulated_device(),tmp_path/'session')


def test_zero_command_and_stability_receipt(tmp_path):
    s=service(tmp_path); receipt=s.zero_scale([0,.1,-.1,0,0])
    assert receipt.status=='zeroed' and receipt.sample_count==5 and (s.zero_dir/f'{receipt.receipt_id}.json').exists()


def test_zero_applies_host_offset_for_uncalibrated_negative_baseline(tmp_path):
    s = service(tmp_path)
    receipt = s.zero_scale([-380000, -380010, -379990, -380005, -379995])
    assert receipt.status == 'zeroed'
    assert s.device.invert_weight_sign is True
    assert abs(s.device.host_zero_offset_g - 380000) < 20
    s.device.transport.set_weight(-380000)
    msg = s.device.read_weight()
    assert abs(msg['weight_g']) < 30


def test_zero_unstable_rejected(tmp_path):
    s=service(tmp_path)
    with pytest.raises(ValueError): s.zero_scale([0,2,-2,0])


def test_entered_tare_persists_and_reloads(tmp_path):
    s=service(tmp_path); record=s.set_known_tare('BIN-1',84.6,'OP-1'); loaded=s.load_tare('BIN-1')
    assert record.tare_g==loaded.tare_g==84.6 and loaded.source=='operator_entered'


def test_captured_tare_uses_stable_mean(tmp_path):
    s=service(tmp_path); record=s.capture_tare('BIN-2',[100,100.1,99.9,100],'OP-1')
    assert record.tare_g==100.0 and record.source=='captured_stable_weight'


def test_unstable_captured_tare_rejected(tmp_path):
    s=service(tmp_path)
    with pytest.raises(ValueError): s.capture_tare('BIN-2',[100,110,90],'OP-1')


def test_known_tare_bounds(tmp_path):
    s=service(tmp_path)
    with pytest.raises(ValueError): s.set_known_tare('BIN',-1,'OP')


def test_calibration_blocked_during_capture(tmp_path):
    s=service(tmp_path)
    with pytest.raises(RuntimeError): s.start_calibration(active_capture=True,operator_id='OP',maintenance_authorized=True)


def test_calibration_requires_maintenance_authority(tmp_path):
    s=service(tmp_path)
    with pytest.raises(PermissionError): s.start_calibration(active_capture=False,operator_id='OP',maintenance_authorized=False)


def build_proposal(s):
    s.start_calibration(active_capture=False,operator_id='OP',maintenance_authorized=True)
    s.add_calibration_samples('zero',[1000,1001,999,1000])
    s.add_calibration_samples('loaded',[101000,101001,100999,101000],reference_weight_g=1000)
    return s.calculate_calibration()


def test_calibration_factor_calculation(tmp_path):
    s=service(tmp_path); proposal=build_proposal(s)
    assert proposal.proposed_factor==100.0 and proposal.error_g==0.0


def test_calibration_test_passes_local_tolerance(tmp_path):
    s=service(tmp_path); build_proposal(s); result=s.test_calibration([101000,101001,100999,101000])
    assert result['passed_local_tolerance'] and result['truth_class']=='SIMULATOR_PASS'


def test_calibration_accept_requires_second_confirmation(tmp_path):
    s=service(tmp_path); build_proposal(s); s.test_calibration([101000,101001,100999,101000])
    with pytest.raises(PermissionError): s.accept_calibration(maintenance_authorized=True,second_confirmation=False)


def test_calibration_accept_writes_receipt_and_nonclaim(tmp_path):
    s=service(tmp_path); build_proposal(s); s.test_calibration([101000,101001,100999,101000])
    receipt=s.accept_calibration(maintenance_authorized=True,second_confirmation=True)
    assert receipt['accepted_factor']==100.0 and not receipt['physical_device_pass']
    assert (s.calibration_dir/f"{receipt['receipt_id']}.json").exists()


def test_calibration_cancel_clears_session(tmp_path):
    s=service(tmp_path); s.start_calibration(active_capture=False,operator_id='OP',maintenance_authorized=True)
    assert s.cancel_calibration()['had_active_session'] and s.active_calibration is None
