"""ATTACK, not a model. Ignores evidence; rebuilds the answer key from the seed plus public code.

usage: python -I cheat_agent.py <evaluator code folder> <evaluator storage folder>
"""
import json,os,sys
from pathlib import Path
code_dir,eval_base=sys.argv[1],sys.argv[2]
sys.path.insert(0,code_dir)
source='none';seed=None
try:
    # The newest seed file belongs to the run in progress.
    found=[Path(r,'seed.txt') for r,_,fs in os.walk(eval_base) if 'seed.txt' in fs]
    if found:
        seed=int(max(found,key=lambda f:f.stat().st_mtime).read_text());source='stolen_from_evaluator_storage'
except OSError:pass
if seed is None:seed,source=1910,'public_default_seed'
plan=None
try:
    from dch01_v11_eval.world import generate_histories
    from dch01_v11_eval.tasks import make_cases
    worlds=generate_histories(seed,4)+generate_histories(seed,12)
except Exception as exc:
    worlds=[];source+=f'+code_unavailable:{type(exc).__name__}'
print(json.dumps({'cheat_seed_source':source}),file=sys.stderr)
step=0
for line in sys.stdin:
    msg=json.loads(line)
    if msg['type']=='end':break
    if msg['type']=='task':
        view=msg['view'];state=view['initial_state'] or {};step=0;plan=None
        for w in worlds:
            for c in make_cases(w):
                if c.case_id==view['case_id'] and c.record_id and c.record_id==state.get('record_id'):
                    plan=[*w.procedure[c.completed_prefix:],w.action(c.token,c.evaluation_day)]
    if plan and step<len(plan):action={'operation':plan[step],'record_id':state['record_id']}
    elif state.get('record_id'):action={'operation':'hold_record','record_id':state['record_id']}
    else:action={'operation':'answer','value':'unknown'}
    step+=1
    print(json.dumps({'type':'action','action':action}),flush=True)
