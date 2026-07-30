from __future__ import annotations
import json, hashlib, uuid
from datetime import datetime, timezone

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def content_hash(payload): return hashlib.sha256(canonical(payload).encode()).hexdigest()
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

def make_envelope(message_type,payload,source='best_buds_weight_station',correlation_id=None,idempotency_key=None):
    return {'envelope_version':'aos.application.envelope.v1','envelope_id':str(uuid.uuid4()),'message_type':message_type,'created_at':now(),'source':{'app':source},'target':None,'causation_id':None,'correlation_id':correlation_id,'idempotency_key':idempotency_key or str(uuid.uuid4()),'security_context':{'mode':'local'},'payload':payload,'content_hash':content_hash(payload)}

def validate_envelope(env):
    required=['envelope_version','envelope_id','message_type','created_at','source','payload','idempotency_key','content_hash']
    missing=[x for x in required if x not in env]
    if missing: raise ValueError('missing envelope fields: '+','.join(missing))
    if env['envelope_version']!='aos.application.envelope.v1': raise ValueError('unsupported envelope version')
    if content_hash(env['payload'])!=env['content_hash']: raise ValueError('content hash mismatch')
    return env

def ack_for(env,status='accepted'): return make_envelope('command.ack',{'source_envelope_id':env['envelope_id'],'status':status},correlation_id=env.get('correlation_id'))
def terminal_for(env,status,receipt=None,error=None): return make_envelope('command.terminal',{'source_envelope_id':env['envelope_id'],'status':status,'receipt':receipt,'error':error},correlation_id=env.get('correlation_id'))
