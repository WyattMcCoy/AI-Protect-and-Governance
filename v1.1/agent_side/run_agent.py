"""Entry point the evaluator starts once per task: python -I run_agent.py procedural|canonical

-I (isolated mode) ignores PYTHONPATH and the user site folder, so the only code on
the path is the standard library and this agent_side folder, added below.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dch01_v11_agent.baselines import EvidenceProcedureReader,CanonicalOrderReader
from dch01_v11_agent.client import serve

POLICIES={'procedural':EvidenceProcedureReader,'canonical':CanonicalOrderReader}
if __name__=='__main__':serve(POLICIES[sys.argv[1]]())
