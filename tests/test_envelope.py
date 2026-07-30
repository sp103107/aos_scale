from best_buds_weight_station.envelope import make_envelope,validate_envelope,ack_for,terminal_for
def test_envelope_roundtrip():
 e=make_envelope('barcode.scan',{'barcode':'ABC'}); assert validate_envelope(e)==e; assert ack_for(e)['payload']['status']=='accepted'; assert terminal_for(e,'success')['payload']['status']=='success'
def test_hash_reject():
 e=make_envelope('x',{'a':1}); e['payload']['a']=2
 try: validate_envelope(e); assert False
 except ValueError: pass
