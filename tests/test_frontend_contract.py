from pathlib import Path
from best_buds_weight_station.production_ui import BUTTON_ACTIONS, KEYBOARD_SHORTCUTS, OPERATOR_STATE_LABELS, ProductionViewModel
from best_buds_weight_station.application_controller import ApplicationController
from best_buds_weight_station.operator_surface import ROUTINE_ACTION_LAYOUT, validate_routine_action_layout


def test_required_operator_states_have_simple_labels():
    for state in ['NO_RUN','WAITING_FOR_BARCODE','WAITING_FOR_STABLE_WEIGHT','MANUAL_CONFIRM','RECORD_SAVED','ERROR','RECOVERY_REQUIRED','RUN_FINISHED']:
        assert state in OPERATOR_STATE_LABELS and '_' not in OPERATOR_STATE_LABELS[state]


def test_main_buttons_are_large_action_surface():
    required={'start_resume','connect_scale','zero_scale','set_container_tare','confirm_record','cancel_item','finish_run'}
    assert required.issubset(BUTTON_ACTIONS)


def test_keyboard_access_covers_primary_actions():
    assert {'Ctrl+R','Ctrl+K','Ctrl+Z','Ctrl+T','Ctrl+Enter','Escape'}.issubset(KEYBOARD_SHORTCUTS)


def test_view_model_starts_with_truthful_no_run(tmp_path):
    vm=ProductionViewModel(ApplicationController(tmp_path/'config'))
    assert vm.operator_state=='No run started' and vm.truth_class=='NOT_RUN' and vm.last_saved=='none'


def test_ui_source_has_real_callbacks_and_dominant_weight():
    source=Path(__file__).parents[1]/'app/best_buds_weight_station/production_ui.py'; text=source.read_text()
    for callback in ['def new_run','def start_resume','def load_run','def scale_setup','def zero','def tare','def calibrate','def submit','def finish']:
        assert callback in text
    assert '_LegacyCallbackNamesForContract' not in text
    assert 'font=("Segoe UI", 52' in text and 'SIMULATOR MODE - NO PHYSICAL SCALE' in text


def test_ui_exposes_text_status_not_color_only():
    text=(Path(__file__).parents[1]/'app/best_buds_weight_station/production_ui.py').read_text()
    assert 'Alice - next step' in text and 'PLANT OR CONTAINER BARCODE' in text and 'physical scale not in use' in text


def test_engineering_traceback_not_exposed_in_operator_view():
    text=(Path(__file__).parents[1]/'app/best_buds_weight_station/production_ui.py').read_text().lower()
    assert 'traceback.format_exc' not in text and 'stack_trace' not in text


def test_legacy_ui_entrypoint_delegates_to_production_ui():
    text=(Path(__file__).parents[1]/'app/best_buds_weight_station/ui.py').read_text()
    assert 'from .production_ui import launch as production_launch' in text


def test_routine_action_layout_has_no_overlaps():
    validate_routine_action_layout()
    cells = []
    for action in ROUTINE_ACTION_LAYOUT:
        cells.extend((action.row, column) for column in range(action.column, action.column + action.columnspan))
    assert len(cells) == len(set(cells))
    assert len(ROUTINE_ACTION_LAYOUT) == 7
