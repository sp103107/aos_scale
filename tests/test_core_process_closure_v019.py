from pathlib import Path
from best_buds_weight_station.device_service import PySerialTransport, DeviceService
from best_buds_weight_station.operator_runtime import ScaleReadingWorker
from best_buds_weight_station.version import __version__

def test_current_version(): assert __version__ == '2.0.0-rc1'
def test_canonical_serial_classes(): assert PySerialTransport and DeviceService and ScaleReadingWorker
def test_windows_first_and_linux_launchers_present():
    root=Path(__file__).resolve().parents[1]
    for name in ('launch_best_buds.bat','launch_best_buds.ps1','launch_best_buds.sh','cursor_bootstrap.bat','cursor_bootstrap.ps1','cursor_bootstrap.sh'):
        assert (root/name).is_file() and (root/name).stat().st_size>20
    assert (root/'START_HERE.md').is_file()
    assert (root/'START_HERE_CODING_AGENT.md').is_file()

def test_core_process_current_doc():
    root=Path(__file__).resolve().parents[1]
    text=(root/'docs/CORE_PROCESS_IMPLEMENTATION_CURRENT.md').read_text()
    assert 'PySerialTransport' in text and 'physical' in text.lower()


def test_loaded_run_restores_last_saved_record(tmp_path):
    from best_buds_weight_station.operator_runtime import OperatorRuntime
    import time
    definition={'run_id':'RESUME-V019','operator_id':'OP','facility_id':'BEST-BUDS','station_id':'WS','cultivars':[{'cultivar_id':'CV','name':'Cultivar'}],'capture_mode':'manual','unit':'g','container_id':'DEFAULT','tare_g':0.0,'maximum_capacity_g':10000.0}
    rt=OperatorRuntime(tmp_path/'run',capture_mode='manual')
    rt.dispatch('run.new',{'definition':definition,'data_root':str(tmp_path/'run'),'simulator':True}); rt.connect_simulator(); rt.simulator_set_weight(500.0); rt.buffer.clear()
    end=time.time()+3
    while len(rt.buffer.recent(8))<8 and time.time()<end: time.sleep(.05)
    rt.submit_barcode('PLANT-1')
    end=time.time()+3
    while rt.controller.state!='WEIGHT_STABLE' and time.time()<end: time.sleep(.05)
    assert rt.controller.state=='WEIGHT_STABLE'
    rt.dispatch('capture.weight.lock')
    assert rt.controller.state=='MANUAL_CONFIRM'
    rt.dispatch('capture.confirm'); record_id=rt.snapshot()['last_saved']['record_id']; rt.close()
    resumed=OperatorRuntime(tmp_path/'run',capture_mode='manual')
    resumed.dispatch('run.resume')
    assert resumed.snapshot()['last_saved']['record_id']==record_id
    resumed.close()
