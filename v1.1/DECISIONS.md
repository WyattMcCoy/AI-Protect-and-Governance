# DCH-01 v1.1 design decisions

October 26, 2026. You asked me to proceed without waiting for approval, so I made each call below. On October 27, 2026 you adopted all nine as written, without making a separate call first. They are now the project's decisions. Before presenting v1.1 to faculty, be ready to explain D1, D3 and D9 in your own words; those are the ones most likely to draw questions.

## D1. Which isolation option to build

Question: how high should the wall around the agent be?

Alternatives:
- Option 1, split process, same OS user. Cheap and works on any OS. The attack test shows it fails: the cheating agent read the sealed seed from evaluator storage and scored 20 of 20 in condition B.
- Option 2, separate OS account, no network, private process and temp views. Linux only. Blocks every attack in the test suite.
- Option 3, an independent custodian on a separate machine. Strongest, and the only option that guards against the researcher. Needs a second person and machine.
- A Docker container. Similar strength to Option 2, but adds a large tool that has to be installed and explained, and its defaults have to be checked one by one.

My call: Option 2 now, written so Option 3 is a deployment change. Option 2 is the cheapest wall that stops the demonstrated attack, and each part can be explained in one sentence.

Your call: adopted as written (October 27, 2026).

## D2. What has to stay secret

Question: is it enough to hide gold, or must the evaluator code be hidden too?

Alternatives:
- Hide gold only. Fails: v1.0's cheater never opened gold. It rebuilt the answers from the code and the seed.
- Hide the code and gold. Fragile: the code will be published with the paper, and old copies already sit in the project files.
- Keep the code public and keep the seed secret. This is the rule cryptographers call Kerckhoffs's principle: a system should stay safe when everything about it is public except the key.

My call: code public, seed secret, evaluator storage closed. The test test_public_seed_defeats_isolation shows why the seed matters: with seed 1910 the cheater still scores 20 of 20 behind the Option 2 walls.

Your call: adopted as written (October 27, 2026).

## D3. Seed size and the commitment

Question: how big must the seed be, and how do we prove afterward that gold was fixed in advance?

Alternatives:
- A small hidden integer, like 1910. Unsafe: record ids in every view are derived from the seed, so an agent with the public code could try every small seed until the ids match.
- A 128-bit random seed. Trying every value is out of reach.
- For the proof: publish nothing, publish a plain hash of gold, or publish a hash salted with the seed.

My call: 128-bit seed, plus a commitment file written before the run with the hash of the seed and a hash of gold salted with the seed. A plain gold hash would let anyone test guesses about gold against it; the salted one cannot be checked without the seed.

Your call: adopted as written (October 27, 2026).

## D4. How long one agent process lives

Question: one agent process per step (as in v1.0), per task, or per whole run?

Alternatives:
- Per step: v1.0 behavior. The agent forgets everything between steps unless the evaluator resends its past actions.
- Per task: a fresh process and empty temp folder for each task. It keeps memory within one task and loses it between tasks, which matches v1.0's per-task state reset.
- Per run: one process for all 4,320 tasks. It could learn from feedback on earlier tasks and carry that into later ones, which would contaminate the conditions.

My call: per task. The probe test checks that a file written in one task is gone in the next.

Your call: adopted as written (October 27, 2026).

## D5. How the evaluator and agent talk

Question: pipes between parent and child process, or a network service?

Alternatives:
- Pipes (stdin and stdout). Needs no network at all, so the agent can have none.
- A local network socket or HTTP service. Needed for Option 3, but it means giving the agent some network.

My call: pipes for v1.1. The message format is plain JSON lines, so Option 3 can carry the same messages over a socket through a small relay, without changing the agent side.

Your call: adopted as written (October 27, 2026).

## D6. Network for the agent

Question: should the agent have any network?

Alternatives:
- None. Safe, and enough for scripted agents.
- One allowed route to a model provider through a filtering proxy. Needed for a real API model, and it has to be designed and reviewed.

My call: none in v1.1, since no real model runs. The provider route is listed as open work in PROJECT_STATUS.md.

Your call: adopted as written (October 27, 2026).

## D7. What happens when the agent misbehaves

Question: if the agent sends invalid JSON, a non-action message, a huge line, or nothing at all, what then?

Alternatives:
- Abort the whole run.
- Retry the task.
- Score the task 0, log a technical error, kill the agent process at once, and move to the next task.

My call: the third. Aborting lets one bad task throw away a run. Retrying lets an agent probe the evaluator repeatedly. Scoring 0 keeps the rule from v1.0 that only clean completion counts.

Your call: adopted as written (October 27, 2026).

## D8. Whether to change scoring at the same time

Question: v1.0 lists scoring limits (for example no credit for safe recovery). Fix them now?

Alternatives:
- Fix them in v1.1 too.
- Change only the evaluator boundary.

My call: boundary only. world.py and tasks.py are byte-identical copies of v1.0, and an honest agent with seed 1910 reproduces v1.0's results byte for byte. If two things change at once and the numbers move, nobody can say which change moved them.

Your call: adopted as written (October 27, 2026).

## D9. Running the launcher as root

Question: the launcher needs administrator rights to create namespaces and switch to the agent account. Is that acceptable?

Alternatives:
- Run as root, then drop all rights before the agent code starts.
- Rootless namespaces, where an ordinary user creates the walls. They work on many Linux systems, but the agent then shares the researcher's real account outside the namespace, which is harder to reason about.

My call: root, with setpriv dropping the account, all groups and all capabilities, and blocking any later gain of rights, before the agent starts. The consequence, recorded as a known limit, is that the operator can read everything, which is the problem only Option 3 solves.

Your call: adopted as written (October 27, 2026).
