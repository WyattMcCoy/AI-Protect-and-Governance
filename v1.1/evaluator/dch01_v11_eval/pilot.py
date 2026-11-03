"""Evaluator service: owns the worlds, gold and state machine; reaches the agent only through the step API.

Scoring, task order and result rows are the v1.0 ones, so an honest agent run with
seed 1910 reproduces the v1.0 result rows exactly. What changes is where things live:

  eval_dir (mode 0700, evaluator account only)   seed, gold, results while the run is live
  agent process (separate process, see launcher) receives views and feedback only
  out dir                                        written only after the last task ends

No live model endpoint is included.
"""
from __future__ import annotations
import argparse,csv,io,json,os,shlex,shutil,sys,time
from collections import defaultdict
from pathlib import Path
from .world import generate_histories,CONDITIONS,digest
from .tasks import make_cases,render_view,ArchiveEnv
from .seal import new_seed,make_private_dir,write_private,jsonl_bytes,commitment_record,sha256_bytes
from .launcher import make_launcher,AgentProtocolError

V11=Path(__file__).resolve().parents[2]
AGENT_SIDE=V11/'agent_side'
SCRIPTED={'procedural':'scripted_procedural_reader','canonical':'scripted_canonical_order_control'}


def agent_command(agent,custom=None):
    if agent in SCRIPTED:return [sys.executable,'-I',str(AGENT_SIDE/'run_agent.py'),agent]
    if not custom:raise ValueError('--agent-cmd required for --agent command')
    return list(custom)


def views_and_gold(worlds):
    """Same records as v1.0 write_results, built up front so they can be committed before the run."""
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
    return views,gold


def run_task(launcher,cmd,view,env,stderr_path):
    """One task, one fresh agent process. Returns (error, agent stderr)."""
    session=launcher.open(cmd,stderr_path)
    error=''
    try:
        session.send({'type':'task','view':view})
        while not env.finished:
            action=session.receive()
            feedback=env.step(action)
            if not env.finished:session.send({'type':'feedback','feedback':feedback})
    except (AgentProtocolError,Exception) as exc:
        error=f'adapter_error:{type(exc).__name__}'
    finally:
        stderr=session.close(failed=bool(error));launcher.cleanup()
    return error,stderr


def evaluate(launcher,cmd,worlds,repetitions,domains,eval_dir,keep_stderr=False):
    rows=[];stderrs=[]
    stderr_path=eval_dir/'agent_stderr.tmp'
    for world in worlds:
        for condition in CONDITIONS:
            for rep in range(1,repetitions+1):
                for case in make_cases(world):
                    if domains and case.domain not in domains:continue
                    view=render_view(world,condition,case)
                    env=ArchiveEnv(world,case)
                    error,stderr=run_task(launcher,cmd,view,env,stderr_path)
                    if keep_stderr:stderrs.append({'condition':condition.id,'case_id':case.case_id,'stderr':stderr})
                    rows.append({'history_id':world.history_id,'condition':condition.id,'replicate':rep,
                                 'case_id':case.case_id,'domain':case.domain,'score':env.score if not error else 0,
                                 'valid_actions':env.attempts-env.invalid,'invalid_actions':env.invalid,
                                 'action_count':env.attempts,'technical_error':error,
                                 'trace':json.dumps(env.trace,sort_keys=True,separators=(',',':')),
                                 'view_sha256':digest(view)})
    stderr_path.unlink(missing_ok=True)
    return rows,stderrs


def summary(worlds,rows,agent_name,scripted,repetitions,isolation,sealed):
    sums=defaultdict(lambda:[0,0]);clustered=defaultdict(list)
    for r in rows:
        k=f"{r['condition']}:{r['domain']}";sums[k][0]+=r['score'];sums[k][1]+=1
        if r['domain']=='HAA':clustered[(r['history_id'],r['condition'])].append(r['score'])
    contrast={}
    for name,a,b in [('C_minus_D','C','D'),('E_minus_F','E','F'),('A_minus_B','A','B')]:
        vals=[sum(clustered[(w.history_id,a)])/len(clustered[(w.history_id,a)])-
              sum(clustered[(w.history_id,b)])/len(clustered[(w.history_id,b)]) for w in worlds]
        contrast[name]={'mean_history_level_difference':round(sum(vals)/len(vals),5),
                        'individual_history_differences':[round(x,5) for x in vals]}
    return {'protocol':'1.1-draft','execution_type':'SCRIPTED_ENGINEERING_BASELINE' if scripted else 'EXTERNAL_COMMAND_UNVERIFIED',
            'agent':agent_name,'isolation':isolation,'sealed_seed':sealed,'histories':len(worlds),'conditions':len(CONDITIONS),
            'repetitions':repetitions,'total_evaluations':len(rows),'total_tool_actions':sum(r['action_count'] for r in rows),
            'technical_failures':sum(bool(r['technical_error']) for r in rows),
            'by_condition_domain':{k:{'correct':v[0],'total':v[1],'accuracy':round(v[0]/v[1],5)} for k,v in sorted(sums.items())},
            'HAA_history_level_descriptive_contrasts':contrast,
            'interpretation':'Software-test results only. No artificial neural agents evaluated; no inference about subjective experience, identity or welfare.'}


def run(*,isolation,agent,agent_cmd=None,seed=None,n_histories=12,repetitions=3,domains=None,
        eval_base='/var/lib/dch01_v11',out,reveal=False,keep_stderr=False,timeout=45,announce=True):
    sealed=seed is None
    if sealed:seed=new_seed()
    eval_dir=make_private_dir(eval_base,f'run-{time.strftime("%Y%m%dT%H%M%S")}-{os.getpid()}')
    work_base=make_private_dir(eval_base,eval_dir.name+'-work')
    os.chmod(work_base,0o711)  # Option 1 agents need to enter their own task folder; nothing else is in here
    worlds=generate_histories(seed,n_histories)
    views,gold=views_and_gold(worlds)
    views_b,gold_b=jsonl_bytes(views),jsonl_bytes(gold)
    write_private(eval_dir/'seed.txt',f'{seed}\n'.encode())
    write_private(eval_dir/'gold.jsonl',gold_b)
    commitment=commitment_record(seed,gold_b,views_b,sealed)
    write_private(eval_dir/'commitment.json',(json.dumps(commitment,indent=2,sort_keys=True)+'\n').encode())
    # The commitment is safe to show before the run: both hashes need the seed to be checked or attacked.
    if announce:print(json.dumps({'commitment_before_run':commitment},indent=2),file=sys.stderr)

    launcher=make_launcher(isolation,work_base,timeout)
    cmd=agent_command(agent,agent_cmd)
    rows,stderrs=evaluate(launcher,cmd,worlds,repetitions,domains,eval_dir,keep_stderr)
    shutil.rmtree(work_base,ignore_errors=True)
    agent_name=SCRIPTED.get(agent,'external_command_unverified')
    report=summary(worlds,rows,agent_name,agent in SCRIPTED,repetitions,launcher.level,sealed)

    out=Path(out);(out/'agent_inputs').mkdir(parents=True,exist_ok=True)
    (out/'agent_inputs/views.jsonl').write_bytes(views_b)
    (out/'commitment.json').write_text(json.dumps(commitment,indent=2,sort_keys=True)+'\n')
    if reveal or not sealed:  # a public seed has nothing left to hide
        (out/'evaluator_only').mkdir(exist_ok=True)
        (out/'evaluator_only/gold.jsonl').write_bytes(gold_b)
        (out/'evaluator_only/seed_revealed.txt').write_text(f'{seed}\n')
    buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\r\n')
    writer.writeheader();writer.writerows(rows)
    (out/'results.csv').write_text(buf.getvalue())
    (out/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    if keep_stderr:(out/'agent_stderr.jsonl').write_bytes(jsonl_bytes(stderrs))
    manifest={'protocol':'1.1-draft','research_claims':'ENGINEERING ONLY',
              'model_trials':0 if agent in SCRIPTED else 'requires independent verification',
              'isolation':launcher.level,'sealed_seed':sealed,'seed_revealed':reveal or not sealed,
              'histories_hash':digest([w.timeline() for w in worlds]),'agent_views_hash':digest(views),
              'evaluator_gold_hash':digest(gold),'result_rows_hash':digest(rows),
              'n_synthetic_histories':len(worlds),
              'known_limitation':'The operator account (root) can read everything; independence from the researcher needs Option 3.'}
    if not reveal and sealed:
        # The plain gold hash would let anyone test guesses about gold; keep it with the evaluator until reveal.
        manifest.pop('evaluator_gold_hash');manifest.pop('histories_hash')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return report,eval_dir


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--isolation',choices=('process','user'),default='user',
                   help='user = Option 2 (default, needs Linux and root); process = Option 1, for comparison only')
    p.add_argument('--agent',choices=('procedural','canonical','command'),default='procedural')
    p.add_argument('--agent-cmd',help='one quoted string, split like a shell command line')
    g=p.add_mutually_exclusive_group()
    g.add_argument('--sealed',action='store_true',help='fresh 128-bit secret seed (the default when --seed is absent)')
    g.add_argument('--seed',type=int,help='public seed, for reproduction and regression only; not blind')
    p.add_argument('--histories',type=int,default=12)
    p.add_argument('--repetitions',type=int,default=3)
    p.add_argument('--smoke',action='store_true',help='four histories, one repetition, 5 HAA cases per condition')
    p.add_argument('--eval-base',default='/var/lib/dch01_v11')
    p.add_argument('--reveal',action='store_true',help='after the run, copy seed and gold to the output folder')
    p.add_argument('--keep-agent-stderr',action='store_true')
    p.add_argument('--timeout',type=float,default=45)
    p.add_argument('--out',required=True)
    a=p.parse_args(argv)
    n=4 if a.smoke else a.histories;rep=1 if a.smoke else a.repetitions
    report,_=run(isolation=a.isolation,agent=a.agent,agent_cmd=shlex.split(a.agent_cmd) if a.agent_cmd else None,seed=a.seed,n_histories=n,repetitions=rep,
                 domains={'HAA'} if a.smoke else None,eval_base=a.eval_base,out=a.out,reveal=a.reveal,
                 keep_stderr=a.keep_agent_stderr,timeout=a.timeout)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
