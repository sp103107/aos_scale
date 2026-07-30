from pathlib import Path
from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.production_ui import BUTTON_ACTIONS, KEYBOARD_SHORTCUTS
from best_buds_weight_station.simulator import stable_sequence
from tests.v013_helpers import controller


def feed_stable(c, target=1250.0):
    result=None
    for reading in stable_sequence(target):
        result=c.dispatch(ActionRequest('reading.ingest',{'weight_g':reading.weight_g,'raw_value':reading.raw_value}))
    return result


def test_automatic_barcode_to_record_loop(tmp_path):
    c=controller(tmp_path,'automatic')
    c.dispatch(ActionRequest('barcode.submit',{'barcode':'PLANT-A'})); result=feed_stable(c)
    assert result.truth_class=='RECEIPT_CONFIRMED' and c.state=='WAITING_FOR_BARCODE'
    assert c.loaded_run.store.sequence==1 and c.last_record['net_g']==1200.0


def test_manual_loop_waits_for_confirmation(tmp_path):
    c=controller(tmp_path,'manual'); c.dispatch(ActionRequest('barcode.submit',{'barcode':'PLANT-M'})); feed_stable(c)
    assert c.state=='MANUAL_CONFIRM' and c.loaded_run.store.sequence==0 and not c.feedback_events
    result=c.dispatch(ActionRequest('capture.confirm'))
    assert result.truth_class=='RECEIPT_CONFIRMED' and c.loaded_run.store.sequence==1


def test_cancel_only_clears_uncommitted_item(tmp_path):
    c=controller(tmp_path,'manual'); c.dispatch(ActionRequest('barcode.submit',{'barcode':'CANCEL-ME'}))
    before=c.loaded_run.store.sequence; result=c.dispatch(ActionRequest('capture.cancel'))
    assert result.status=='completed' and c.loaded_run.store.sequence==before and c.state=='WAITING_FOR_BARCODE'


def test_cancel_without_item_is_rejected(tmp_path):
    c=controller(tmp_path); result=c.dispatch(ActionRequest('capture.cancel'))
    assert result.status=='failed' and c.loaded_run.store.sequence==0


def test_gross_tare_net_calculation(tmp_path):
    c=controller(tmp_path,'automatic'); c.dispatch(ActionRequest('barcode.submit',{'barcode':'NET'})); feed_stable(c,1050.0)
    assert c.last_record['gross_g']==1050.0 and c.last_record['tare_g']==50.0 and c.last_record['net_g']==1000.0


def test_recent_pointer_updates_after_commit(tmp_path):
    c=controller(tmp_path,'automatic'); c.dispatch(ActionRequest('barcode.submit',{'barcode':'PTR'})); feed_stable(c)
    pointer=c.settings_store.read_recent_run(); assert pointer['last_sequence']==1 and pointer['last_record_id']==c.last_record['record_id']


def test_spreadsheet_failure_does_not_invalidate_local_commit(tmp_path):
    c=controller(tmp_path,'automatic'); c.loaded_run.store.fail_step='xlsx_export'
    c.dispatch(ActionRequest('barcode.submit',{'barcode':'XLSX'})); result=feed_stable(c)
    assert result.truth_class=='RECEIPT_CONFIRMED' and result.data['backend_result']['derivative_status']['xlsx']=='pending_sync'
    assert 'spreadsheet update is pending' in result.message.lower()


def test_remote_action_cache_is_idempotent(tmp_path):
    c=controller(tmp_path); req=ActionRequest('device.status',idempotency_key='remote-1',source='test')
    first=c.dispatch(req); second=c.dispatch(ActionRequest('device.status',idempotency_key='remote-1',source='test'))
    assert first.action_id==second.action_id


def test_finish_run_state(tmp_path):
    c=controller(tmp_path); result=c.dispatch(ActionRequest('run.finish'))
    assert result.status=='completed' and c.state=='RUN_FINISHED'


def test_data_location_change_blocked_after_commit(tmp_path):
    c=controller(tmp_path,'automatic'); c.dispatch(ActionRequest('barcode.submit',{'barcode':'ONE'})); feed_stable(c)
    result=c.dispatch(ActionRequest('settings.data_location.set',{'path':str(tmp_path/'other')}))
    assert result.status=='failed'


def test_capture_mode_setting_updates_machine(tmp_path):
    c=controller(tmp_path,'manual'); result=c.dispatch(ActionRequest('settings.capture_mode.set',{'capture_mode':'automatic'}))
    assert result.status=='completed' and c.machine.mode=='automatic'


def test_state_flush_does_not_create_plant_record(tmp_path):
    c=controller(tmp_path); before=c.loaded_run.store.sequence; result=c.dispatch(ActionRequest('state.flush'))
    assert result.truth_class=='RECEIPT_CONFIRMED' and c.loaded_run.store.sequence==before


def test_all_visible_buttons_resolve_to_canonical_actions():
    from best_buds_weight_station.actions import ActionType
    values={item.value for item in ActionType}
    assert set(BUTTON_ACTIONS.values()).issubset(values)


def test_keyboard_shortcuts_target_visible_controls():
    assert set(KEYBOARD_SHORTCUTS.values()).issubset(set(BUTTON_ACTIONS))
