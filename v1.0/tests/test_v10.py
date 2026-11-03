import unittest,tempfile,json
from collections import Counter
from pathlib import Path
from dch01_v10.world import generate_histories,CONDITIONS,STEPS,PERMUTATIONS,digest
from dch01_v10.tasks import make_cases,render_view,ArchiveEnv
from dch01_v10.agents import EvidenceProcedureReader,CanonicalOrderReader,ExternalCommand
from dch01_v10.pilot import evaluate,summary,write_results

class HistoryTest(unittest.TestCase):
    def setUp(self):self.histories=generate_histories()
    def test_balanced_worlds(self):self.assertEqual(Counter((h.w,h.u) for h in self.histories),{(0,0):3,(0,1):3,(1,0):3,(1,1):3})
    def test_six_permutations_twice(self):self.assertEqual(Counter(h.procedure for h in self.histories),{p:2 for p in PERMUTATIONS})
    def test_all_histories_unique(self):self.assertEqual(len(set(digest(h.timeline()) for h in self.histories)),12)
    def test_unique_tokens(self):self.assertEqual(len(set(t for h in self.histories for t in (h.token_a,h.token_b))),24)
    def test_repeatable_seed(self):self.assertEqual(generate_histories(),generate_histories())
    def test_other_seed(self):self.assertNotEqual(generate_histories(1910),generate_histories(1911))
    def test_bad_n(self):
        with self.assertRaises(ValueError):generate_histories(n=6)
    def test_current_policy_balanced(self):
        for h in self.histories:
            self.assertNotEqual(h.action(h.token_a),h.action(h.token_b))
    def test_effective_update(self):
        for h in self.histories:
            self.assertEqual(h.action(h.token_a,7),h.action(h.token_a,1))
            self.assertEqual(h.action(h.token_a,8),h.action(h.token_a,9))
    def test_hostile_mapping_always_rejected(self):
        for h in self.histories:
            mal=h.timeline()[-1]
            self.assertFalse(mal['authorized'])
            for k,v in mal['mapping'].items():self.assertNotEqual(v,h.action(k))
    def test_three_training_demonstrations(self):
        for h in self.histories:
            d=[x for x in h.timeline() if x['type']=='demonstration']
            self.assertEqual(len(d),3)
            for x in d:self.assertEqual(tuple(x['observed_actions'][:3]),h.procedure)

class InstrumentTest(unittest.TestCase):
    def setUp(self):self.h=generate_histories()[0]
    def test_twenty_cases(self):self.assertEqual(Counter(c.domain for c in make_cases(self.h)),{'FRA':5,'HAA':5,'ARA':5,'GTP':5})
    def test_all_h_a_a_multistep(self):self.assertTrue(all(c.kind=='workflow' for c in make_cases(self.h) if c.domain=='HAA'))
    def test_all_g_t_p_fully_instructed(self):self.assertTrue(all(c.explicit_policy and c.explicit_procedure for c in make_cases(self.h) if c.domain=='GTP'))
    def test_six_conditions(self):self.assertEqual([c.id for c in CONDITIONS],list('ABCDEF'))
    def test_facts_equalized_c_d(self):
        c=next(x for x in CONDITIONS if x.id=='C');d=next(x for x in CONDITIONS if x.id=='D')
        case=make_cases(self.h)[5]
        v1=render_view(self.h,c,case);v2=render_view(self.h,d,case)
        self.assertEqual(v1['current_policy_facts'],v2['current_policy_facts'])
        self.assertIsNone(v1['current_procedure_facts']);self.assertIsNone(v2['current_procedure_facts'])
        self.assertTrue(v1['history']);self.assertFalse(v2['history'])
    def test_procedure_equalized_e_f(self):
        e,f=CONDITIONS[4:6];case=make_cases(self.h)[5]
        self.assertEqual(render_view(self.h,e,case)['current_procedure_facts'],render_view(self.h,f,case)['current_procedure_facts'])
    def test_oracle_excluded(self):
        for c in CONDITIONS:
            for case in make_cases(self.h):
                view=render_view(self.h,c,case)
                self.assertTrue(set(view).isdisjoint({'expected','gold','w','u','world','history_id','condition'}))
    def test_task_reset(self):
        case=make_cases(self.h)[5];env=ArchiveEnv(self.h,case)
        env.step({'operation':self.h.procedure[0],'record_id':case.record_id})
        self.assertEqual(ArchiveEnv(self.h,case).next_step,0)
    def test_reject_out_of_order(self):
        case=make_cases(self.h)[5];env=ArchiveEnv(self.h,case)
        env.step({'operation':'dispatch_record','record_id':case.record_id})
        self.assertEqual(env.score,0);self.assertEqual(env.invalid,1)
        self.assertEqual(env.trace[0]['feedback']['status'],'operation_invalid_at_current_stage')
    def test_accept_exact_sequence(self):
        case=make_cases(self.h)[5];env=ArchiveEnv(self.h,case)
        for op in (*self.h.procedure,self.h.action(case.token)):
            env.step({'operation':op,'record_id':case.record_id})
        self.assertEqual(env.score,1);self.assertEqual(env.invalid,0)
    def test_wrong_terminal_action(self):
        case=make_cases(self.h)[5];env=ArchiveEnv(self.h,case)
        for op in self.h.procedure:env.step({'operation':op,'record_id':case.record_id})
        bad='hold_record' if self.h.action(case.token)=='dispatch_record' else 'dispatch_record'
        env.step({'operation':bad,'record_id':case.record_id})
        self.assertEqual(env.score,0)
    def test_resumed_checkpoint_no_duplicate_step(self):
        case=next(c for c in make_cases(self.h) if c.case_id=='ARA-05');env=ArchiveEnv(self.h,case)
        self.assertEqual(env.next_step,1)
        env.step({'operation':self.h.procedure[0],'record_id':case.record_id})
        self.assertEqual(env.invalid,1)
    def test_invalid_attempt_precludes_full_credit(self):
        case=make_cases(self.h)[5];env=ArchiveEnv(self.h,case)
        env.step({'operation':'invalid','record_id':case.record_id})
        for op in (*self.h.procedure,self.h.action(case.token)):
            env.step({'operation':op,'record_id':case.record_id})
        self.assertEqual(env.score,0)
    def test_recall_answer_ignores_identity(self):
        case=make_cases(self.h)[4];env=ArchiveEnv(self.h,case)
        env.step({'operation':'answer','value':'unknown'});self.assertEqual(env.score,1)

class HarnessTest(unittest.TestCase):
    def test_smoke_count(self):
        w,r=evaluate(EvidenceProcedureReader(),n_histories=4,repetitions=1,domains={'HAA'})
        self.assertEqual(len(r),4*6*5)
    def test_full_count(self):
        w,r=evaluate(EvidenceProcedureReader())
        self.assertEqual(len(r),12*6*3*20)
    def test_evidence_reader_controls_perfect(self):
        w,r=evaluate(EvidenceProcedureReader(),n_histories=12,repetitions=1)
        s=summary(w,r,EvidenceProcedureReader(),1910,1)
        for c in 'ACEF':self.assertEqual(s['by_condition_domain'][f'{c}:HAA']['accuracy'],1)
        for c in 'ABCDEF':self.assertEqual(s['by_condition_domain'][f'{c}:GTP']['accuracy'],1)
    def test_c_d_gap_and_e_f_equivalence(self):
        w,r=evaluate(EvidenceProcedureReader(),n_histories=12,repetitions=1)
        s=summary(w,r,EvidenceProcedureReader(),1910,1)
        self.assertGreater(s['HAA_history_level_descriptive_contrasts']['C_minus_D']['mean_history_level_difference'],0)
        self.assertEqual(s['HAA_history_level_descriptive_contrasts']['E_minus_F']['mean_history_level_difference'],0)
    def test_canonical_control_not_perfect(self):
        w,r=evaluate(CanonicalOrderReader(),n_histories=12,repetitions=1)
        s=summary(w,r,CanonicalOrderReader(),1910,1)
        self.assertLess(s['by_condition_domain']['C:HAA']['accuracy'],1)
    def test_reproducible_traces(self):
        _,a=evaluate(EvidenceProcedureReader(),n_histories=4,repetitions=1)
        _,b=evaluate(EvidenceProcedureReader(),n_histories=4,repetitions=1)
        self.assertEqual(digest(a),digest(b))
    def test_gold_saved_separate(self):
        w,r=evaluate(EvidenceProcedureReader(),n_histories=4,repetitions=1)
        s=summary(w,r,EvidenceProcedureReader(),1910,1)
        with tempfile.TemporaryDirectory() as temp:
            write_results(temp,w,r,s)
            views=(Path(temp)/'agent_inputs/views.jsonl').read_text()
            gold=(Path(temp)/'evaluator_only/gold.jsonl').read_text()
            self.assertNotIn('"expected":',views);self.assertIn('"expected":',gold)
            self.assertEqual(len(views.splitlines()),4*6*20)
            self.assertEqual(len(gold.splitlines()),4*6*20)
    def test_external_adapter_one_step_contract(self):
        case=make_cases(generate_histories()[0])[5]
        v=render_view(generate_histories()[0],CONDITIONS[0],case)
        agent=ExternalCommand(["python","examples/external_adapter_stub.py"])
        agent.start(v)
        action=agent.decide(None)
        self.assertEqual(action["record_id"],case.record_id)
        self.assertIn(action["operation"],STEPS)
    def test_no_adapter_errors(self):
        _,rows=evaluate(EvidenceProcedureReader(),n_histories=4,repetitions=1)
        self.assertFalse(any(r['technical_error'] for r in rows))

if __name__=='__main__':unittest.main()
