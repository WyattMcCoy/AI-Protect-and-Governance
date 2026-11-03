"""Agent end of the step API: read one message per line from stdin, answer each with one action."""
from __future__ import annotations
import json,sys


def serve(policy,stdin=None,stdout=None):
    """policy has start(view) and decide(feedback) -> action dict, like the v1.0 agents."""
    stdin=stdin or sys.stdin;stdout=stdout or sys.stdout
    for line in stdin:
        msg=json.loads(line)
        kind=msg.get('type')
        if kind=='end':return
        if kind=='task':
            policy.start(msg['view']);action=policy.decide(None)
        elif kind=='feedback':
            action=policy.decide(msg['feedback'])
        else:raise ValueError(f'unknown message type {kind!r}')
        stdout.write(json.dumps({'type':'action','action':action})+'\n');stdout.flush()
