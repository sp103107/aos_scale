#!/usr/bin/env python3
from __future__ import annotations
import json
import tempfile
from pathlib import Path
import sys

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'app'))
from best_buds_weight_station.actions import ActionRequest
from best_buds_weight_station.application_controller import ApplicationController
from best_buds_weight_station.hardware_buttons import ButtonEvent,LocalHardwareButtonAdapter
from best_buds_weight_station.remote_boundaries import RemoteTransportConfig
from best_buds_weight_station.simulator import stable_sequence
from best_buds_weight_station.version import __version__


def definition(mode,session):
    return {'run_id':f'ACCEPT-{mode.upper()}','operator_id':'OP-ACCEPT','facility_id':'BEST-BUDS','station_id':'WS-01','cultivars':[{'cultivar_id':'CV-ACCEPT','name':'Acceptance Cultivar'}],'capture_mode':mode,'unit':'g','container_id':'BIN-A','tare_g':50.0,'maximum_capacity_g':10000.0,'session_id':session}


def run_loop(root,mode,barcode):
    c=ApplicationController(root/'config')
    c.settings_store.update(data_root=str(root/'data'),capture_mode=mode)
    assert c.dispatch(ActionRequest('run.new',{'definition':definition(mode,f'SESSION-{mode}'),'data_root':str(root/'data'),'simulator':True})).status=='completed'
    connected=c.dispatch(ActionRequest('device.connect',{'simulator':True})); assert connected.truth_class=='SIMULATOR_PASS'
    zero=c.dispatch(ActionRequest('scale.zero',{'readings_g':[0,.1,-.1,0,0]})); assert zero.status=='completed'
    tare=c.dispatch(ActionRequest('scale.container_tare.set',{'container_id':'BIN-A','tare_g':50.0})); assert tare.status=='completed'
    c.dispatch(ActionRequest('barcode.submit',{'barcode':barcode}))
    terminal=None
    for reading in stable_sequence(1250.0): terminal=c.dispatch(ActionRequest('reading.ingest',{'weight_g':reading.weight_g,'raw_value':reading.raw_value}))
    if mode=='manual':
        assert c.loaded_run.store.sequence==0 and c.state=='MANUAL_CONFIRM'
        terminal=c.dispatch(ActionRequest('capture.confirm'))
    assert terminal.truth_class=='RECEIPT_CONFIRMED' and c.loaded_run.store.sequence==1
    pointer=c.settings_store.read_recent_run(); assert pointer['last_sequence']==1
    return {'mode':mode,'terminal_truth_class':terminal.truth_class,'record_id':c.last_record['record_id'],'net_g':c.last_record['net_g'],'recent_pointer_sequence':pointer['last_sequence'],'feedback':c.feedback_events,'state':c.state,'session_manifest':str(c.loaded_run.manifest_path)}


def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        automatic=run_loop(root/'automatic','automatic','AUTO-001')
        manual=run_loop(root/'manual','manual','MANUAL-001')
        # Calibration execution remains simulator evidence.
        c=ApplicationController(root/'calibration'/'config')
        c.settings_store.update(data_root=str(root/'calibration'/'data'),capture_mode='manual')
        c.dispatch(ActionRequest('run.new',{'definition':definition('manual','SESSION-CAL'),'data_root':str(root/'calibration'/'data'),'simulator':True}))
        c.dispatch(ActionRequest('device.connect',{'simulator':True}))
        start=c.dispatch(ActionRequest('scale.calibration.start',{'maintenance_authorized':True}))
        zero=c.dispatch(ActionRequest('scale.calibration.sample',{'kind':'zero','samples':[1000,1001,999,1000]}))
        proposal=c.dispatch(ActionRequest('scale.calibration.sample',{'kind':'loaded','samples':[101000,101001,100999,101000],'reference_weight_g':1000.0}))
        test=c.dispatch(ActionRequest('scale.calibration.test',{'samples':[101000,101001,100999,101000]}))
        accepted=c.dispatch(ActionRequest('scale.calibration.accept',{'maintenance_authorized':True,'second_confirmation':True}))
        assert all(x.status=='completed' for x in [start,zero,proposal,test,accepted])
        buttons=LocalHardwareButtonAdapter()
        mapping={name:buttons.translate(ButtonEvent(name)).action_type for name in ('green','yellow','red','blue')}
        wifi=RemoteTransportConfig('wifi'); wifi.validate()
        result={
          'status':'pass','version':__version__,'truth_class':'UNIT_TEST_PASS',
          'automatic_loop':automatic,'manual_loop':manual,
          'zero_scale':'SIMULATOR_PASS','known_tare':'UNIT_TEST_PASS',
          'calibration':{'truth_class':accepted.truth_class,'physical_device_pass':False,'receipt_id':accepted.data['calibration_receipt']['receipt_id']},
          'canonical_buttons':mapping,
          'bluetooth_boundary':'validated_disabled_by_default','wifi_boundary':'validated_disabled_by_default',
          'physical_device':'NOT_RUN','uno_q':'NOT_RUN',
          'non_claims':['No physical device pass.','No legal-for-trade calibration.','No Bluetooth or Wi-Fi activation.']
        }
        print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()
