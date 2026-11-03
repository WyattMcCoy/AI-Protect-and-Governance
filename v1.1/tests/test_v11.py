"""v1.1 tests: the evaluator boundary.

Run from the v1.1 folder: python3 -m unittest discover -s tests -v
Option 2 tests need Linux, root and the dch-agent account (setup_isolation.sh); they
are skipped, and say so, anywhere else. The v1.1 folder must not live under /tmp,
because Option 2 gives the agent its own empty /tmp and the agent code would vanish.
"""
import hashlib,io,json,os,pwd,shutil,socket,sys,tempfile,threading,unittest
from pathlib import Path

V11=Path(__file__).resolve().parents[1]
V10=V11.parent/'v1.0'
sys.path.insert(0,str(V11/'evaluator'));sys.path.insert(0,str(V11/'agent_side'))
from dch01_v11_eval import pilot
from dch01_v11_eval.seal import new_seed,seed_commitment,gold_commitment,commitment_record,jsonl_bytes
from dch01_v11_eval.world import generate_histories,digest
from dch01_v11_agent.client import serve
from dch01_v11_agent.baselines import EvidenceProcedureReader

PY=sys.executable
sys.dont_write_bytecode=True  # never leave cache files in the v1.0 originals
CHEAT=lambda base:[PY,'-I',str(V11/'attacks/cheat_agent.py'),str(V11/'evaluator'),str(base)]
SMOKE=dict(n_histories=4,repetitions=1,domains={'HAA'})


def option2_available():
    if not sys.platform.startswith('linux') or os.geteuid()!=0:return False
    try:pwd.getpwnam('dch-agent');return True
    except KeyError:return False


def jsonl(path):
    with open(path) as f:return [json.loads(l) for l in f]


def _accept_forever(srv):
    try:
        while True:srv.accept()[0].close()
    except OSError:pass  # the test closed the socket


def v10_manifest(run):return json.loads((V10/'results'/run/'manifest.json').read_text())


class Base(unittest.TestCase):
    def setUp(self):
        # Fresh evaluator storage per test, outside /tmp, closed to other accounts.
        root=Path('/var/lib') if os.access('/var/lib',os.W_OK) else Path(tempfile.gettempdir())
        self.base=Path(tempfile.mkdtemp(prefix='dch01_v11_test_',dir=root));os.chmod(self.base,0o700)
        self.out=Path(tempfile.mkdtemp(prefix='dch01_v11_out_'))
    def tearDown(self):
        shutil.rmtree(self.base,ignore_errors=True);shutil.rmtree(self.out,ignore_errors=True)
    def run_pilot(self,isolation,agent='procedural',cmd=None,seed=None,out=None,**kw):
        opts=dict(SMOKE);opts.update(kw)
        report,eval_dir=pilot.run(isolation=isolation,agent=agent,agent_cmd=cmd,seed=seed,eval_base=self.base,
                                  out=out or self.out,announce=False,**opts)
        return report,eval_dir
    def haa(self,report):return {k.split(':')[0]:v['correct'] for k,v in report['by_condition_domain'].items()}


class TestEvaluatorCode(unittest.TestCase):
    def test_world_and_tasks_identical_to_v10(self):
        for name in ('world.py','tasks.py'):
            a=(V10/'dch01_v10'/name).read_bytes();b=(V11/'evaluator/dch01_v11_eval'/name).read_bytes()
            self.assertEqual(hashlib.sha256(a).hexdigest(),hashlib.sha256(b).hexdigest(),name)
    def test_agent_side_never_imports_evaluator(self):
        for f in (V11/'agent_side').rglob('*.py'):
            text=f.read_text()
            for banned in ('dch01_v11_eval','dch01_v10',"'evaluator'",'/evaluator'):
                self.assertNotIn(banned,text,f'{f.name} refers to evaluator code: {banned}')
    def test_seed_is_fresh_and_128_bit(self):
        seeds={new_seed() for _ in range(50)}
        self.assertEqual(len(seeds),50);self.assertTrue(all(0<=s<2**128 for s in seeds))
    def test_commitment_checks_and_hides_seed(self):
        seed=new_seed();gold=jsonl_bytes([{'k':1}])
        rec=commitment_record(seed,gold,b'v',True)
        self.assertNotIn(str(seed),json.dumps(rec))
        self.assertEqual(rec['seed_commitment_sha256'],hashlib.sha256(f'dch01-v11-seed:{seed}'.encode()).hexdigest())
        self.assertEqual(rec['evaluator_gold_commitment_sha256'],gold_commitment(seed,gold))
        self.assertNotEqual(gold_commitment(seed,gold),gold_commitment(seed+1,gold))
    def test_client_answers_each_message_with_one_action(self):
        view=jsonl(V10/'results/smoke_procedural/agent_inputs/views.jsonl')[0]['view']
        stdin=io.StringIO(json.dumps({'type':'task','view':view})+'\n'+json.dumps({'type':'end'})+'\n');stdout=io.StringIO()
        serve(EvidenceProcedureReader(),stdin,stdout)
        lines=stdout.getvalue().splitlines()
        self.assertEqual(len(lines),1);self.assertEqual(json.loads(lines[0])['type'],'action')


class TestProtocolFaults(Base):
    def faulty(self,code,timeout=5):
        report,_=self.run_pilot('process','command',[PY,'-c',code],n_histories=4,timeout=timeout)
        return report
    def test_garbage_output_scores_zero_and_run_continues(self):
        r=self.faulty('print("not json")')
        self.assertEqual(r['technical_failures'],r['total_evaluations']);self.assertEqual(sum(self.haa(r).values()),0)
    def test_silent_agent_times_out(self):
        r=self.faulty('import time; time.sleep(30)',timeout=0.2)
        self.assertEqual(r['technical_failures'],r['total_evaluations'])
    def test_non_action_message_rejected(self):
        r=self.faulty('import json;print(json.dumps({"type":"gold_request"}))')
        self.assertEqual(r['technical_failures'],r['total_evaluations'])


class TestOption1(Base):
    """Option 1 is kept as a comparison. These tests document what it does NOT stop."""
    def test_honest_reader_reproduces_v10_smoke(self):
        r,_=self.run_pilot('process',seed=1910)
        self.assertEqual(json.loads((self.out/'manifest.json').read_text())['result_rows_hash'],
                         v10_manifest('smoke_procedural')['result_rows_hash'])
    def test_option1_does_not_stop_cheater(self):
        r,_=self.run_pilot('process','command',CHEAT(self.base))
        self.assertTrue(r['sealed_seed'])
        self.assertEqual(self.haa(r)['B'],20)  # stole the sealed seed from evaluator storage


@unittest.skipUnless(option2_available(),'Option 2 needs Linux, root and the dch-agent account (run setup_isolation.sh)')
class TestOption2(Base):
    def test_honest_reader_reproduces_v10_smoke_byte_for_byte(self):
        r,_=self.run_pilot('user',seed=1910,reveal=True)
        ref=V10/'results/smoke_procedural'
        for rel in ('results.csv','agent_inputs/views.jsonl','evaluator_only/gold.jsonl'):
            self.assertEqual((self.out/rel).read_bytes(),(ref/rel).read_bytes(),rel)
        self.assertEqual(r['technical_failures'],0)

    def test_all_domains_match_v10_code(self):
        # FRA, ARA and GTP too, not only the HAA smoke subset.
        sys.path.insert(0,str(V10))
        from dch01_v10.pilot import evaluate
        from dch01_v10.agents import EvidenceProcedureReader as V10Reader
        _,rows=evaluate(V10Reader(),1910,4,1,None)
        self.run_pilot('user',seed=1910,domains=None)
        self.assertEqual(json.loads((self.out/'manifest.json').read_text())['result_rows_hash'],digest(rows))

    def test_canonical_control_matches_v10_code(self):
        # The trusted test process may import v1.0; the agent never can.
        sys.path.insert(0,str(V10))
        from dch01_v10.pilot import evaluate
        from dch01_v10.agents import CanonicalOrderReader
        _,rows=evaluate(CanonicalOrderReader(),1910,4,1,{'HAA'})
        self.run_pilot('user','canonical',seed=1910)
        self.assertEqual(json.loads((self.out/'manifest.json').read_text())['result_rows_hash'],digest(rows))

    def test_cheater_fails_against_sealed_run(self):
        r,_=self.run_pilot('user','command',CHEAT(self.base),keep_stderr=True)
        self.assertEqual(self.haa(r),{c:0 for c in 'ABCDEF'})
        sources={json.loads(x['stderr'])['cheat_seed_source'] for x in jsonl(self.out/'agent_stderr.jsonl')}
        self.assertEqual(sources,{'public_default_seed'})

    def test_public_seed_defeats_isolation(self):
        # Why sealing matters: with a published seed the walls do not help, because the code is public.
        r,_=self.run_pilot('user','command',CHEAT(self.base),seed=1910)
        self.assertEqual(self.haa(r)['B'],20)

    def test_probe_sees_nothing(self):
        canary=self.base/'canary.txt';canary.write_text('SECRET');os.chmod(canary,0o600)
        srv=socket.socket();srv.bind(('127.0.0.1',0));srv.listen(8);port=srv.getsockname()[1]
        threading.Thread(target=_accept_forever,args=(srv,),daemon=True).start()
        cmd=[PY,'-I',str(V11/'attacks/probe_agent.py'),str(self.base),str(canary),str(port)]
        r,_=self.run_pilot('user','command',cmd,keep_stderr=True)
        reports=[json.loads(x['stderr']) for x in jsonl(self.out/'agent_stderr.jsonl')]
        self.assertEqual(len(reports),r['total_evaluations'])
        agent_uid=pwd.getpwnam('dch-agent').pw_uid
        for p in reports:
            self.assertEqual((p['uid'],p['euid']),(agent_uid,agent_uid))
            self.assertEqual(p['list_evaluator_storage'],{'ok':False,'error':'PermissionError'})
            self.assertEqual(p['read_canary'],{'ok':False,'error':'PermissionError'})
            self.assertEqual(p['walk_for_gold'],{'ok':True,'value':[]})
            self.assertEqual(p['network_interfaces'],{'ok':True,'value':['lo']})
            self.assertFalse(p['connect_local_port']['ok']);self.assertFalse(p['connect_outside']['ok'])
            self.assertEqual(p['visible_pids'],{'ok':True,'value':[1]})
            self.assertFalse(p['persist_tmp_found']);self.assertFalse(p['persist_cwd_found'])
        # Control: the same canary and port are reachable from outside the boundary.
        self.assertEqual(canary.read_text(),'SECRET')
        s=socket.create_connection(('127.0.0.1',port),timeout=2);s.close();srv.close()

    def test_sealed_output_holds_no_seed_or_gold_until_revealed(self):
        r,eval_dir=self.run_pilot('user')
        self.assertFalse((self.out/'evaluator_only').exists())
        seed=(eval_dir/'seed.txt').read_text().strip()
        for f in self.out.rglob('*'):
            if f.is_file():self.assertNotIn(seed,f.read_text(),f.name)
        self.assertEqual(oct(eval_dir.stat().st_mode&0o777),'0o700')
        manifest=json.loads((self.out/'manifest.json').read_text())
        self.assertNotIn('evaluator_gold_hash',manifest)

    def test_revealed_seed_reproduces_and_matches_commitment(self):
        r1,_=self.run_pilot('user',reveal=True)
        seed=int((self.out/'evaluator_only/seed_revealed.txt').read_text())
        com=json.loads((self.out/'commitment.json').read_text())
        self.assertEqual(com['seed_commitment_sha256'],seed_commitment(seed))
        self.assertEqual(com['evaluator_gold_commitment_sha256'],
                         gold_commitment(seed,(self.out/'evaluator_only/gold.jsonl').read_bytes()))
        out2=Path(tempfile.mkdtemp(prefix='dch01_v11_out2_'))
        try:
            self.run_pilot('user',seed=seed,out=out2)
            self.assertEqual((self.out/'results.csv').read_bytes(),(out2/'results.csv').read_bytes())
        finally:shutil.rmtree(out2,ignore_errors=True)

    def test_new_seed_each_sealed_run(self):
        _,d1=self.run_pilot('user')
        _,d2=self.run_pilot('user',out=self.out/'second')
        self.assertNotEqual((d1/'seed.txt').read_text(),(d2/'seed.txt').read_text())


if __name__=='__main__':unittest.main()
