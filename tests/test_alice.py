from best_buds_weight_station.alice import validate_start_manifest
def test_alice_blocks_missing(): assert not validate_start_manifest({})['accepted']
def test_alice_accepts_complete():
 m={k:'x' for k in ['operator_id','facility_id','station_id','run_id','measurement_stage','weight_purpose','capture_mode','stability_profile_id']}; m.update({'maximum_capacity_g':50000,'cultivars':[{'x':1}],'data_root_writable':True}); assert validate_start_manifest(m)['accepted']
