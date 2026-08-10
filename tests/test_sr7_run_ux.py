"""BBWS SR7 S02 — run lifecycle + capture display UX contract tests.

Covers the three operator-reported fixes:
1. Finish Run works from RECORD_SAVED (post-save idle) and renders a closed state.
2. Main weight display freezes at the locked value while MANUAL_CONFIRM.
3. Resume Run picker lists in-progress sessions via RunManager.list_sessions.

Capture law (scan → settle → lock → confirm → reset) is unchanged.
"""
import json
from pathlib import Path

from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.operator_surface import frozen_display_weight
from best_buds_weight_station.state_machine import State
from best_buds_weight_station.ui_tokens import capture_pill_label

from tests.v013_helpers import controller, definition


def test_finish_run_allowed_from_record_saved(tmp_path):
    c = controller(tmp_path)
    assert c.machine is not None
    c.machine.state = State.RECORD_SAVED
    result = c.dispatch(ActionRequest('run.finish'))
    assert result.status == 'completed'
    assert c.state == 'RUN_FINISHED'
    manifest = json.load(Path(c.loaded_run.manifest_path).open(encoding='utf-8'))
    assert manifest.get('status') == 'finished'


def test_finish_run_blocked_mid_capture(tmp_path):
    c = controller(tmp_path)
    assert c.machine is not None
    c.machine.state = State.MANUAL_CONFIRM
    result = c.dispatch(ActionRequest('run.finish'))
    assert result.status == 'failed'
    assert 'cancel or complete' in result.message.lower()
    assert c.state == 'MANUAL_CONFIRM'


def test_finish_run_refreshes_alice_message(tmp_path):
    c = controller(tmp_path)
    c.machine.state = State.WAITING_FOR_BARCODE
    result = c.dispatch(ActionRequest('run.finish'))
    assert result.status == 'completed'
    alice = c.last_alice_response or {}
    assert 'finished' in str(alice.get('operator_message', '')).lower()


def test_run_finished_pill_label():
    assert capture_pill_label('RUN_FINISHED') == 'Finished'


def test_frozen_display_weight_freezes_while_locked():
    # Live reading keeps moving, but the display value must hold the lock.
    assert frozen_display_weight(1234.5, 1000.0) == 1000.0
    assert frozen_display_weight(999.9, 1000.0) == 1000.0


def test_frozen_display_weight_live_when_unlocked():
    assert frozen_display_weight(1234.5, None) == 1234.5


def test_pyside_refresh_uses_frozen_display_weight():
    source = Path(__file__).parents[1] / 'app/best_buds_weight_station/pyside_frontend.py'
    text = source.read_text(encoding='utf-8')
    assert 'frozen_display_weight' in text
    assert 'Weight locked — Confirm & Record to save, or Cancel to release.' in text


def test_list_sessions_excludes_finished(tmp_path):
    c = controller(tmp_path)
    first_manifest = str(c.loaded_run.manifest_path)
    # Finish the first run, then create a second one under the same root.
    c.machine.state = State.WAITING_FOR_BARCODE
    assert c.dispatch(ActionRequest('run.finish')).status == 'completed'
    c.loaded_run = None
    c.machine = None
    second = definition(session_id='HR-2026-TEST-second')
    second['run_id'] = 'HR-2026-SECOND'
    result = c.dispatch(ActionRequest('run.new', {'definition': second, 'data_root': str(tmp_path / 'data'), 'simulator': True}))
    assert result.status == 'completed'

    active_only = c.run_manager.list_sessions(data_root=tmp_path / 'data')
    assert [entry['run_id'] for entry in active_only] == ['HR-2026-SECOND']
    everything = c.run_manager.list_sessions(data_root=tmp_path / 'data', include_finished=True)
    assert {entry['run_id'] for entry in everything} == {'HR-2026-TEST', 'HR-2026-SECOND'}
    picked = active_only[0]
    assert Path(picked['manifest_path']).name == 'session_manifest.json'
    assert picked['status'] == 'active'
    assert picked['manifest_path'] != first_manifest


def test_list_sessions_entries_loadable(tmp_path):
    c = controller(tmp_path)
    sessions = c.run_manager.list_sessions(data_root=tmp_path / 'data')
    assert sessions, 'active run should be listed'
    loaded = c.run_manager.load(sessions[0]['manifest_path'])
    assert loaded.store.context.run_id == 'HR-2026-TEST'


def test_resume_picker_wired_in_both_frontends():
    root = Path(__file__).parents[1] / 'app/best_buds_weight_station'
    pyside = (root / 'pyside_frontend.py').read_text(encoding='utf-8')
    tk_ui = (root / 'production_ui.py').read_text(encoding='utf-8')
    assert 'class ResumeRunDialog' in pyside
    assert 'Resume Run (Choose)...' in pyside
    assert 'def choose_run' in tk_ui
    assert 'Resume Run (Choose)...' in tk_ui
