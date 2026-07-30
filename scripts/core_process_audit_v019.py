#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, time
from pathlib import Path
from best_buds_weight_station.operator_runtime import OperatorRuntime
from best_buds_weight_station.version import __version__


def wait(runtime, state, timeout=4.0):
    end=time.time()+timeout
    while time.time()<end:
        if runtime.controller.state==state: return
        time.sleep(.05)
    raise TimeoutError(f'{state} not reached; got {runtime.controller.state}')

def samples(runtime, n=8, timeout=4.0):
    end=time.time()+timeout
    while time.time()<end:
        if len(runtime.buffer.recent(n))>=n: return
        time.sleep(.05)
    raise TimeoutError('samples unavailable')

def definition(run_id, mode):
    return {'run_id':run_id,'operator_id':'CORE-AUDIT','facility_id':'BEST-BUDS','station_id':'WS-01','cultivars':[{'cultivar_id':'CV-001','name':'Audit Cultivar'}],'capture_mode':mode,'unit':'g','container_id':'DEFAULT','tare_g':0.0,'maximum_capacity_g':10000.0}

def flow(root: Path, mode: str):
    rt=OperatorRuntime(root/mode,capture_mode=mode)
    try:
        rt.dispatch('run.new',{'definition':definition(f'V019-{mode.upper()}',mode),'data_root':str(root/mode),'simulator':True})
        rt.connect_simulator(); rt.zero_scale()
        rt.simulator_set_weight(100.0); rt.buffer.clear(); samples(rt)
        rt.capture_container_tare('HOOK-SLING')
        rt.simulator_set_weight(1350.0); rt.buffer.clear(); samples(rt)
        rt.submit_barcode(f'{mode.upper()}-PLANT-001')
        if mode=='manual':
            wait(rt,'MANUAL_CONFIRM'); rt.dispatch('capture.confirm')
        wait(rt,'WAITING_FOR_BARCODE')
        snap=rt.snapshot(); record=snap['last_saved']
        manifest=rt.controller.loaded_run.manifest_path
        rt.close()
        resumed=OperatorRuntime(root/mode,capture_mode=mode)
        try:
            result=resumed.dispatch('run.resume')
            rsnap=resumed.snapshot()
            resumed_ok=result['status']=='completed' and rsnap['last_saved'] is not None and rsnap['last_saved']['record_id']==record['record_id']
        finally: resumed.close()
        return {'pass':bool(record and abs(record['net_g']-1250.0)<1e-6 and resumed_ok),'record_id':record['record_id'],'net_g':record['net_g'],'manifest':str(manifest),'resumed':resumed_ok,'truth_class':snap['alice_truth_class']}
    finally:
        try: rt.close()
        except Exception: pass

def main():
    root=Path(__file__).resolve().parents[1]
    required=['launch_best_buds.bat','launch_best_buds.ps1','launch_best_buds.sh','cursor_bootstrap.bat','cursor_bootstrap.ps1','cursor_bootstrap.sh']
    launchers={p:(root/p).is_file() and (root/p).stat().st_size>20 for p in required}
    source=(root/'app/best_buds_weight_station/device_service.py').read_text()
    worker=(root/'app/best_buds_weight_station/operator_runtime.py').read_text()
    with tempfile.TemporaryDirectory(prefix='bbws-core-v019-') as td:
        base=Path(td)
        automatic=flow(base,'automatic'); manual=flow(base,'manual')
    checks={
      'version':__version__=='0.1.9',
      'launchers':all(launchers.values()),
      'pyserial_transport':'class PySerialTransport' in source and 'serial.Serial' in source,
      'canonical_worker':'class ScaleReadingWorker' in worker and 'reading.ingest' in worker,
      'automatic_flow':automatic['pass'],
      'manual_flow':manual['pass'],
      'alice_receipt_gate':automatic['truth_class']=='RECEIPT_CONFIRMED' and manual['truth_class']=='RECEIPT_CONFIRMED',
    }
    result={'version':__version__,'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'launchers':launchers,'automatic':automatic,'manual':manual,'physical_hardware':'NOT_RUN','windows_native_runtime':'NOT_RUN','firmware_compile':'BLOCKED_OR_NOT_RUN'}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
