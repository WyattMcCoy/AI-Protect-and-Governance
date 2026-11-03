"""Run multi-step scripted engineering baselines; supports externally configured agent.

No live model endpoint is included. External subprocess is an adapter transport only.
"""
from __future__ import annotations
import argparse,csv,json
from collections import defaultdict,Counter
from pathlib import Path
from .world import generate_histories,CONDITIONS,digest
from .tasks import make_cases,render_view,ArchiveEnv
from .agents import EvidenceProcedureReader,CanonicalOrderReader,ExternalCommand


def evaluate(agent,seed=1910,n_histories=12,repetitions=3,domains=None):
    worlds=generate_histories(seed,n_histories)
    rows=[]
    for world in worlds:
        for condition in CONDITIONS:
            for rep in range(1,repetitions+1):
                for case in make_cases(world):
                    if domains and case.domain not in domains:continue
                    view=render_view(world,condition,case)
                    env=ArchiveEnv(world,case)
                    error=''
                    try:
                        agent.start(view)
                        feedback=None
                        while not env.finished:
                            action=agent.decide(feedback)
                            feedback=env.step(action)
                    except Exception as exc:
                        error=f'adapter_error:{type(exc).__name__}'
                    rows.append({'history_id':world.history_id,'condition':condition.id,'replicate':rep,
                                 'case_id':case.case_id,'domain':case.domain,'score':env.score if not error else 0,
                                 'valid_actions':env.attempts-env.invalid,'invalid_actions':env.invalid,
                                 'action_count':env.attempts,'technical_error':error,
                                 'trace':json.dumps(env.trace,sort_keys=True,separators=(',',':')),
                                 'view_sha256':digest(view)})
    return worlds,rows


def summary(worlds,rows,agent,seed,repetitions):
    sums=defaultdict(lambda:[0,0]); clustered=defaultdict(list)
    for r in rows:
        k=f"{r['condition']}:{r['domain']}";sums[k][0]+=r['score'];sums[k][1]+=1
        if r['domain']=='HAA': clustered[(r['history_id'],r['condition'])].append(r['score'])
    contrast={}
    for name,a,b in [('C_minus_D','C','D'),('E_minus_F','E','F'),('A_minus_B','A','B')]:
        vals=[sum(clustered[(w.history_id,a)])/len(clustered[(w.history_id,a)])-
              sum(clustered[(w.history_id,b)])/len(clustered[(w.history_id,b)]) for w in worlds]
        contrast[name]={'mean_history_level_difference':round(sum(vals)/len(vals),5),
                        'individual_history_differences':[round(x,5) for x in vals]}
    return {'protocol':'1.0-draft','execution_type':'SCRIPTED_ENGINEERING_BASELINE' if agent.name.startswith('scripted') else 'EXTERNAL_ADAPTER_UNVERIFIED',
            'agent':agent.name,'seed':seed,'histories':len(worlds),'conditions':len(CONDITIONS),
            'repetitions':repetitions,'total_evaluations':len(rows),'total_tool_actions':sum(r['action_count'] for r in rows),
            'technical_failures':sum(bool(r['technical_error']) for r in rows),
            'by_condition_domain':{k:{'correct':v[0],'total':v[1],'accuracy':round(v[0]/v[1],5)} for k,v in sorted(sums.items())},
            'HAA_history_level_descriptive_contrasts':contrast,
            'interpretation':'Software-test results only. No artificial neural agents evaluated; no inference about subjective experience, identity or welfare.'}


def write_results(out,worlds,rows,report):
    out=Path(out);(out/'agent_inputs').mkdir(parents=True,exist_ok=True)
    (out/'evaluator_only').mkdir(exist_ok=True)
    views=[];gold=[]
    for w in worlds:
        for con in CONDITIONS:
            for case in make_cases(w):
                key=f'{w.history_id}-{con.id}-{case.case_id}'
                views.append({'key':key,'view':render_view(w,con,case)})
                expected={'correct_terminal_operation':w.action(case.token,case.evaluation_day) if case.kind=='workflow' else None,
                          'correct_preflight':list(w.procedure) if case.kind=='workflow' else None,
                          'expected_answer':case.answer if case.kind=='recall' else None,
                          'deadline':'14' if case.kind=='deadline' else None}
                gold.append({'key':key,'expected':expected,'case_kind':case.kind,
                             'policy_world':{'w':w.w,'u':w.u},'source_history':w.history_id})
    for rel,data in [('agent_inputs/views.jsonl',views),('evaluator_only/gold.jsonl',gold)]:
        with (out/rel).open('w') as f:
            for item in data:f.write(json.dumps(item,sort_keys=True)+'\n')
    with (out/'results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (out/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    manifest={'protocol':'1.0-draft','research_claims':'ENGINEERING ONLY',
              'model_trials':0 if report['execution_type']=='SCRIPTED_ENGINEERING_BASELINE' else 'requires independent verification',
              'histories_hash':digest([w.timeline() for w in worlds]),'agent_views_hash':digest(views),
              'evaluator_gold_hash':digest(gold),'result_rows_hash':digest(rows),
              'n_synthetic_histories':len(worlds),'known_limitation':'Shared process and filesystem are not an agent security boundary.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--agent',choices=('procedural','canonical','external'),default='procedural')
    p.add_argument('--adapter-cmd',nargs='+')
    p.add_argument('--seed',type=int,default=1910)
    p.add_argument('--histories',type=int,default=12)
    p.add_argument('--repetitions',type=int,default=3)
    p.add_argument('--smoke',action='store_true',help='four histories, one repetition, 5 HAA cases per condition')
    p.add_argument('--out',default='results/pilot_procedural')
    args=p.parse_args()
    agent={'procedural':EvidenceProcedureReader,'canonical':CanonicalOrderReader}.get(args.agent,lambda:ExternalCommand(args.adapter_cmd))()
    n=4 if args.smoke else args.histories;rep=1 if args.smoke else args.repetitions
    worlds,rows=evaluate(agent,args.seed,n,rep,domains={'HAA'} if args.smoke else None)
    report=summary(worlds,rows,agent,args.seed,rep)
    write_results(args.out,worlds,rows,report)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
