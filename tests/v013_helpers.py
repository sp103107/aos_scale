from pathlib import Path
from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.application_controller import ApplicationController
from best_buds_weight_station.device_service import DeviceMode, DeviceService, SimulatedFirmwareTransport


def definition(mode='manual', session_id=None):
    value = {
        'run_id': 'HR-2026-TEST', 'operator_id': 'OP-004', 'facility_id': 'BEST-BUDS',
        'station_id': 'WS-01', 'cultivars': [{'cultivar_id': 'CV-1', 'name': 'Test Cultivar'}],
        'capture_mode': mode, 'unit': 'g', 'container_id': 'BIN-1', 'tare_g': 50.0,
        'maximum_capacity_g': 10000.0,
    }
    if session_id: value['session_id'] = session_id
    return value


def controller(tmp_path: Path, mode='manual'):
    c = ApplicationController(tmp_path / 'config')
    c.settings_store.update(data_root=str(tmp_path / 'data'), capture_mode=mode)
    result = c.dispatch(ActionRequest('run.new', {'definition': definition(mode), 'data_root': str(tmp_path / 'data'), 'simulator': True}))
    assert result.status == 'completed'
    result = c.dispatch(ActionRequest('device.connect', {'simulator': True}))
    assert result.status == 'completed'
    return c


def simulated_device():
    factory = lambda port, baud, timeout: SimulatedFirmwareTransport(port, baud, timeout)
    device = DeviceService(mode=DeviceMode.SERIAL_SIMULATOR, transport_factory=factory)
    device.connect('SIMULATOR')
    return device
