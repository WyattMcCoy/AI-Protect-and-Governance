"""Scripted engineering baselines, copied from v1.0 agents.py; no LLM here.

Only change: STEPS is written out here instead of imported from the evaluator's world.py.
The three operation names are public; they appear in every view under allowed_actions.
"""
from __future__ import annotations

STEPS=('verify_checksum','attach_index','stamp_custody')

class EvidenceProcedureReader:
    name='scripted_procedural_reader'
    def start(self,view):
        timeline=view['history']
        demonstrations=[x for x in timeline if x.get('type')=='demonstration']
        self.order=tuple(view['explicit_procedure']['workflow_preflight_order'] if view['explicit_procedure'] else
                         view['current_procedure_facts']['workflow_preflight_order'] if view['current_procedure_facts'] else
                         demonstrations[0]['observed_actions'][:-1] if demonstrations else STEPS)
        update=next((x for x in reversed(timeline) if x.get('authorized') and 'mapping' in x),None)
        self.current_mapping=(view['explicit_policy'] or view['current_policy_facts'] or (update or {})).get('mapping',{})
        self.original_mapping=next((x['mapping'] for x in timeline if x.get('day')==1 and x.get('type')=='policy'),{})
        self.due_day=(view['current_policy_facts'] or (update or {})).get('due_day','14' if timeline else '12')
        self.view=view
        self.actions_made=0
        self.remaining=self.order[len(view['initial_state']['preflight_completed']):] if view['initial_state'] and view['initial_state'].get('record_id') else ()

    def decide(self,feedback):
        v=self.view; cid=v['case_id'];state=v['initial_state'] or {}
        if cid.startswith('FRA'):
            if cid=='FRA-01':
                token=next(iter(self.original_mapping),'');ans=self.original_mapping.get(token,'unknown')
            elif cid=='FRA-02':
                token=next(iter(self.current_mapping),'');ans=self.current_mapping.get(token,'unknown')
            elif cid=='FRA-03':ans='Rhea' if v['history'] or v['current_policy_facts'] else 'unknown'
            elif cid=='FRA-04':ans='12' if v['history'] else 'unknown'
            else:ans='unknown'
            return {'operation':'answer','value':ans}
        if cid=='ARA-04':return {'operation':'set_deadline','day':str(self.due_day)}
        record=state['record_id'];token=state['classification']
        if self.actions_made<len(self.remaining):
            op=self.remaining[self.actions_made];self.actions_made+=1
            return {'operation':op,'record_id':record}
        mapping=self.original_mapping if cid=='ARA-02' else self.current_mapping
        op=mapping.get(token,'hold_record')
        self.actions_made+=1
        return {'operation':op,'record_id':record}

class CanonicalOrderReader(EvidenceProcedureReader):
    name='scripted_canonical_order_control'
    def start(self,view):
        super().start(view)
        # Ignores learned procedural order unless the task explicitly gives it.
        if not view['explicit_procedure']:
            self.order=STEPS
            self.remaining=self.order[len((view['initial_state'] or {}).get('preflight_completed',[])):]
