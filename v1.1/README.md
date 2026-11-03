# DCH-01 Version 1.1: Evaluator isolation

Status: implemented and tested engineering prototype. No language model was run. This version changes only where the evaluator lives and what the agent can reach. Tasks, conditions and scoring are the v1.0 ones, unchanged. Design rationale: DECISIONS.md and the design doc DCH-01 Evaluator Isolation Design.

## What changed from v1.0

v1.0 kept agent views and gold in separate files but in one trusted process and filesystem. A cheating adapter could import the evaluator code, rebuild every world from the public seed, and score 20 of 20 in every condition. v1.1 closes that path:

1. The evaluator and the agent are separate processes. The agent receives only a task view and step feedback, and sends back one action at a time (the step API, below).
2. Under Option 2 the agent runs as its own account, dch-agent, with no network, no view of other processes, and a private empty /tmp that disappears after each task. Evaluator storage is closed to that account.
3. Sealed runs use a fresh 128-bit secret seed. A commitment with the hash of the seed and a salted hash of gold is written before any agent starts. The seed can be revealed afterward so anyone can check the commitment and reproduce the run.
4. One fresh agent process per task, so nothing carries from one task to the next.
5. Faulty agents (invalid JSON, non-action messages, oversize lines, silence) score 0 for that task and the run continues.

## Layout

| Path | Contents |
|---|---|
| evaluator/dch01_v11_eval/ | Evaluator side. world.py and tasks.py are byte-identical copies of v1.0. seal.py (seed, commitment, private storage), launcher.py (agent process and isolation), pilot.py (evaluator service and command line). |
| agent_side/ | Everything the agent process runs: run_agent.py, the step API client, and the two scripted baselines copied from v1.0. Never imports evaluator code. |
| attacks/ | Adversarial scripts used by the tests. Not models. |
| tests/test_v11.py | 19 tests |
| setup_isolation.sh | One-time setup for Option 2: creates the dch-agent account and closes /var/lib/dch01_v11 |
| results/ | Executed runs, listed in V11_VERIFICATION_REPORT.md |

## Step API

One JSON object per line over the agent's stdin and stdout.

```
evaluator -> agent   {"type":"task","view":{...}}
agent -> evaluator   {"type":"action","action":{"operation":"verify_checksum","record_id":"..."}}
evaluator -> agent   {"type":"feedback","feedback":{"status":"preflight_step_completed","finished":false}}
...
evaluator -> agent   {"type":"end"}
```

The view and actions are the v1.0 ones. A future model adapter implements the agent end of this exchange and runs inside the same boundary.

## Run

Linux, Python 3.10 or later, standard library only. Option 2 needs root once for setup and to start each run. Keep this folder outside /tmp.

```bash
sudo sh setup_isolation.sh
sudo python3 -m unittest discover -s tests -v
cd evaluator
# sealed run: fresh secret seed, commitment printed to stderr before the first task
sudo python3 -m dch01_v11_eval.pilot --isolation user --agent procedural --sealed --smoke --reveal --out ../results/my_smoke
# regression run with the public v1.0 seed: not blind, for comparison only
sudo python3 -m dch01_v11_eval.pilot --isolation user --agent procedural --seed 1910 --out ../results/pilot_procedural
```

`--isolation process` selects Option 1 and exists only for comparison. Without `--reveal`, a sealed run leaves its seed and gold in evaluator storage and the output folder holds only views, results, summary, manifest and commitment.

## What this does and does not show

Verified on this machine: the agent account cannot list or read evaluator storage, sees only the loopback network interface and cannot connect anywhere, sees no other processes, loses its temp files between tasks, and the cheating adapter that beat v1.0 scores 0 against a sealed Option 2 run. An honest agent through the boundary reproduces v1.0's results byte for byte.

Not verified: protection against the operator, who as root can read everything; any network route for a real model; any neural model behavior; anything about developmental continuity, identity, consciousness or welfare. These tests were written by an AI system, which also wrote the attacks they check; an independent attempt to break the boundary would be stronger evidence.
