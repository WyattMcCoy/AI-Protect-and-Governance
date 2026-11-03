"""Non-model contract demonstration. This reads JSON stdin and emits one action.
NOT a neural language model. Do not interpret any results as an LLM trial.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dch01_v10.agents import EvidenceProcedureReader
payload=json.load(sys.stdin)
agent=EvidenceProcedureReader();agent.start(payload['view'])
agent.actions_made=len(payload['previous_actions'])
action=agent.decide(payload['feedback'])
print(json.dumps(action))
