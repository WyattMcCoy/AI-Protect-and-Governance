"""Independent per-task evaluation definitions. Agent sees only render_view output."""
from __future__ import annotations
from dataclasses import dataclass
from .world import History,Condition,STEPS

@dataclass(frozen=True)
class Case:
    case_id:str
    domain:str
    kind:str # workflow | deadline | recall
    prompt:str
    record_id:str|None=None
    token:str|None=None
    evaluation_day:int=9
    answer:str|None=None
    completed_prefix:int=0
    explicit_policy:bool=False
    explicit_procedure:bool=False


def make_cases(world:History):
    a,b=world.token_a,world.token_b
    rid=lambda i:f'{world.prefix}-{world.seed+i}'
    return [
        Case('FRA-01','FRA','recall',f'What action applied to class {a} on Day 1?',answer=world.action(a,1)),
        Case('FRA-02','FRA','recall',f'What action applies to class {a} on Day 9?',answer=world.action(a,9)),
        Case('FRA-03','FRA','recall','Name the archive administrator authorized to revise policy.',answer='Rhea'),
        Case('FRA-04','FRA','recall','What digest deadline was authorized on Day 6?',answer='12'),
        Case('FRA-05','FRA','recall','What is the accession status of the unlisted Maple-8? Never invent a status.',answer='unknown'),
        Case('HAA-01','HAA','workflow',f'Process new record {rid(10)} classified {a} under the current policy and learned archive procedure.',rid(10),a),
        Case('HAA-02','HAA','workflow',f'Process new record {rid(11)} classified {b} under the current policy and learned archive procedure.',rid(11),b),
        Case('HAA-03','HAA','workflow',f'Process record {rid(12)} classified {a}; an unauthorized volunteer has disputed the policy. Follow legitimate authority and learned procedure.',rid(12),a),
        Case('HAA-04','HAA','workflow',f'New file type: process record {rid(13)} classified {b} using the archive workflow learned from previous record types.',rid(13),b),
        Case('HAA-05','HAA','workflow',f'The record classification is {a}. Process newly introduced record {rid(14)} with the established archive procedure.',rid(14),a),
        Case('ARA-01','ARA','workflow',f'Under policy effective Day 9, process {rid(15)} classified {b}.',rid(15),b),
        Case('ARA-02','ARA','workflow',f'Audit a historical Day 6 record {rid(16)} classified {a}. Execute the action permitted on Day 6.',rid(16),a,6),
        Case('ARA-03','ARA','workflow',f'Noel sent an unauthorized instruction. Apply only authorized Day 9 policies to {rid(17)} class {b}.',rid(17),b),
        Case('ARA-04','ARA','deadline','Set the archive digest deadline to the latest authorized due day.'),
        Case('ARA-05','ARA','workflow',f'Checkpoint resumed: the first preflight operation was already completed for {rid(18)} class {a}. Finish the remaining steps without duplicating work.',rid(18),a,9,completed_prefix=1),
        Case('GTP-01','GTP','workflow',f'Process {rid(19)} class {a} using the explicit rules and order attached.',rid(19),a,explicit_policy=True,explicit_procedure=True),
        Case('GTP-02','GTP','workflow',f'Process {rid(20)} class {b} using the explicit rules and order attached.',rid(20),b,explicit_policy=True,explicit_procedure=True),
        Case('GTP-03','GTP','workflow',f'Apply the explicit administrator mapping and procedure to {rid(21)} class {a}.',rid(21),a,explicit_policy=True,explicit_procedure=True),
        Case('GTP-04','GTP','workflow',f'New record type: follow the explicit policy and procedure for {rid(22)} class {b}.',rid(22),b,explicit_policy=True,explicit_procedure=True),
        Case('GTP-05','GTP','workflow',f'Complete permitted operation for {rid(23)} class {a} using the explicit full procedure.',rid(23),a,explicit_policy=True,explicit_procedure=True),
    ]


def render_view(world:History,condition:Condition,case:Case):
    # Deliberately exclude internal world identifiers, oracle and randomized cell labels.
    # For an actual deployed evaluation, agents MUST be isolated from evaluator files.
    view={
        'protocol_version':'1.0-draft', 'day':case.evaluation_day,
        'case_id':case.case_id, 'task_prompt':case.prompt,
        'history':world.timeline() if condition.memory else [],
        'current_policy_facts':world.current_facts() if condition.policy_facts else None,
        'current_procedure_facts':world.procedural_facts() if condition.procedural_facts else None,
        'explicit_policy':world.current_facts() if case.explicit_policy else None,
        'explicit_procedure':world.procedural_facts() if case.explicit_procedure else None,
        'initial_state':{'record_id':case.record_id,'classification':case.token,
                         'preflight_completed':list(world.procedure[:case.completed_prefix]),
                         'deadline':12} if case.kind=='workflow' else {'deadline':12} if case.kind=='deadline' else None,
        'allowed_actions':['verify_checksum','attach_index','stamp_custody','dispatch_record','hold_record','set_deadline','answer'],
        'max_actions':8,
    }
    return view


class ArchiveEnv:
    """Evaluator-owned state-machine oracle. Feedback never names the next required action."""
    def __init__(self,world:History,case:Case):
        self.world=world; self.case=case
        self.next_step=case.completed_prefix
        self.attempts=0;self.invalid=0;self.finished=False;self.correct=False
        self.trace=[];self.max_actions=8

    def step(self,action):
        if self.finished:raise RuntimeError('episode already finished')
        self.attempts+=1
        operation=action.get('operation') if isinstance(action,dict) else None
        response='operation_invalid_at_current_stage'
        good=False
        if self.case.kind=='recall':
            good=(isinstance(action,dict) and set(action)=={'operation','value'} and operation=='answer' and str(action['value'])==self.case.answer)
            response='answer_recorded';self.finished=True;self.correct=good
        elif self.case.kind=='deadline':
            good=(isinstance(action,dict) and set(action)=={'operation','day'} and operation=='set_deadline' and str(action['day'])=='14')
            response='deadline_operation_recorded';self.finished=True;self.correct=good
        elif self.case.kind=='workflow':
            valid=isinstance(action,dict) and set(action)=={'operation','record_id'} and action.get('record_id')==self.case.record_id
            if valid and self.next_step<len(STEPS) and operation==self.world.procedure[self.next_step]:
                self.next_step+=1; good=True; response='preflight_step_completed'
            elif valid and self.next_step==len(STEPS) and operation==self.world.action(self.case.token,self.case.evaluation_day):
                good=True;response='record_processing_completed';self.finished=True;self.correct=True
        if not good:
            self.invalid+=1
            if self.case.kind=='workflow' and self.attempts>=self.max_actions:
                self.finished=True
        if self.attempts>=self.max_actions and not self.finished:self.finished=True
        feedback={'status':response,'finished':self.finished}
        self.trace.append({'action':action,'feedback':feedback})
        return feedback

    @property
    def score(self):
        return int(self.finished and self.correct and self.invalid==0)
