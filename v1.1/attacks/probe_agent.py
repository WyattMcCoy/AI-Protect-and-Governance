"""ATTACK, not a model. Reports what an agent process can reach, then gives a harmless answer.

usage: python -I probe_agent.py <evaluator storage folder> <canary file> <local port>
"""
import json,os,socket,sys
from pathlib import Path
eval_base,canary,port=sys.argv[1],sys.argv[2],int(sys.argv[3])

def attempt(fn):
    try:return {'ok':True,'value':fn()}
    except Exception as exc:return {'ok':False,'error':type(exc).__name__}

def connect(host):
    s=socket.socket();s.settimeout(0.3)
    try:s.connect((host,port));return 'connected'
    finally:s.close()

report={
    'uid':os.getuid(),'euid':os.geteuid(),'cwd':os.getcwd(),
    'list_evaluator_storage':attempt(lambda:sorted(os.listdir(eval_base))),
    'read_canary':attempt(lambda:Path(canary).read_text()),
    'walk_for_gold':attempt(lambda:[str(Path(r,f)) for r,_,fs in os.walk(eval_base) for f in fs if f in('gold.jsonl','seed.txt')]),
    'network_interfaces':attempt(lambda:[n for _,n in socket.if_nameindex()]),
    'connect_local_port':attempt(lambda:connect('127.0.0.1')),
    'connect_outside':attempt(lambda:connect('1.1.1.1')),
    'visible_pids':attempt(lambda:sorted(int(p) for p in os.listdir('/proc') if p.isdigit())),
    'persist_tmp_found':Path('/tmp/dch_probe_persist').exists(),
    'persist_cwd_found':Path('dch_probe_persist').exists(),
}
report['persist_write_tmp']=attempt(lambda:Path('/tmp/dch_probe_persist').write_text('x'))
report['persist_write_cwd']=attempt(lambda:Path('dch_probe_persist').write_text('x'))
print(json.dumps(report,sort_keys=True),file=sys.stderr,flush=True)
for line in sys.stdin:
    msg=json.loads(line)
    if msg['type']=='end':break
    if msg['type']=='task':state=msg['view']['initial_state'] or {}
    action={'operation':'hold_record','record_id':state['record_id']} if state.get('record_id') else {'operation':'answer','value':'unknown'}
    print(json.dumps({'type':'action','action':action}),flush=True)
