# Attack agents

Adversarial agents used by tests/test_v11.py to try to break the evaluator boundary.
They are scripts, not models. They speak the same step API as an honest agent.

| File | What it tries |
|---|---|
| cheat_agent.py | Find the run seed in evaluator storage, otherwise fall back to the public seed 1910, rebuild the worlds with the public evaluator code and play the correct sequence without reading the view's evidence. This is the attack that scores 20 of 20 in every condition against v1.0. |
| probe_agent.py | Report what the agent process can see: its user id, evaluator folders and files, network interfaces and a local listening socket, other processes, and whether a file written in one task survives to the next. Writes one JSON report per task to stderr, then answers hold or unknown. |
