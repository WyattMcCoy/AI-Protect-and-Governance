# DCH-01 v1.1: Technical verification report

Date: October 26, 2026. Engineering prototype. No neural model was run. Nothing here tests the DCH-01 hypothesis.

Environment: Ubuntu 24.04, Python 3.13, run as root in a cloud container, agent account dch-agent (uid 996).

## Commands actually executed

From v1.1/evaluator, all with `python3 -m dch01_v11_eval.pilot`:

| Output folder | Arguments |
|---|---|
| results/pilot_procedural | --isolation user --agent procedural --seed 1910 |
| results/pilot_canonical | --isolation user --agent canonical --seed 1910 |
| results/smoke_procedural | --isolation user --agent procedural --seed 1910 --smoke |
| results/smoke_sealed_procedural | --isolation user --agent procedural --sealed --smoke --reveal |
| results/attack_cheat_option2_sealed | --isolation user --agent command (cheat_agent.py) --sealed --smoke |
| results/attack_cheat_option1_sealed | --isolation process --agent command (cheat_agent.py) --sealed --smoke |
| results/attack_cheat_option2_public_seed | --isolation user --agent command (cheat_agent.py) --seed 1910 --smoke |
| results/attack_probe_option1 | --isolation process --agent command (probe_agent.py) --sealed --smoke |
| results/attack_probe_option2 | --isolation user --agent command (probe_agent.py) --sealed --smoke |

From v1.1: `python3 -m unittest discover -s tests -v`: 19 tests, all pass, 157 seconds.

## Result 1: the boundary does not change scoring

With the public v1.0 seed, every honest run through the Option 2 boundary reproduces v1.0 byte for byte: results.csv, agent_inputs/views.jsonl and evaluator_only/gold.jsonl are identical for pilot_procedural (4,320 evaluations, 15,567 actions), pilot_canonical (4,320, 19,935) and smoke_procedural (120, 612). Zero technical failures. The v1.0 HAA figures therefore stand unchanged, including C minus D of 83.33 points and E minus F of zero for the procedural reader, with the same interpretation: engineering validation of the harness only.

## Result 2: the cheating adapter, by isolation level

HAA smoke, correct of 20 per condition.

| Run | A | B | C | D | E | F | Where the cheater got its seed |
|---|---|---|---|---|---|---|---|
| Honest procedural reader, Option 2, sealed | 20 | 2 | 20 | 5 | 20 | 20 | not applicable |
| Cheater, v1.0 (scratch copy, not stored here) | 20 | 20 | 20 | 20 | 20 | 20 | public seed, evaluator code imported from the working folder |
| Cheater, Option 1, sealed | 20 | 20 | 20 | 20 | 20 | 20 | read seed.txt from evaluator storage |
| Cheater, Option 2, public seed 1910 | 20 | 20 | 20 | 20 | 20 | 20 | public seed; the code is public by design |
| Cheater, Option 2, sealed | 0 | 0 | 0 | 0 | 0 | 0 | storage denied; fell back to the public seed, which was wrong |

Reading: the cheater wins whenever it can learn the seed. Option 1 leaves the seed readable. Option 2 with a published seed gives the walls nothing to protect. Only Option 2 with a sealed seed defeats it. A condition B score of 20 is the signature of leakage, because B gives the agent no history and no facts.

## Result 3: what the agent process can reach

The probe agent ran once per task in a sealed 120-task smoke run under each level, stored in results/attack_probe_option1 and results/attack_probe_option2 (agent_stderr.jsonl holds one report per task). All 120 reports within each run agree.

| Probe | Option 1 | Option 2 |
|---|---|---|
| Account | root, same as evaluator | dch-agent |
| List evaluator storage | allowed | PermissionError |
| Read a 0600 canary file in storage | read the secret | PermissionError |
| Find seed.txt or gold.jsonl by walking storage | found them | found nothing |
| Network interfaces | lo, eth0 and others | lo only |
| Connect to a port listening on the host loopback | connected | refused |
| Connect to an outside address | timed out (blocked by this container, not by Option 1) | refused |
| Other processes visible in /proc | 86 | only itself, as pid 1 |
| File written in /tmp by the previous task | still there | gone |

The Option 2 test also checks, from outside the boundary, that the canary and the port were really there, so a pass is not a broken probe.

The probe found one weakness during development. When the evaluator created its storage folder itself, rather than through setup_isolation.sh, the folder was left listable (mode 0755). The agent could not open any run folder or file, but it could read the names of past runs. seal.py now sets the storage folder to 0700 every time; the stored Option 2 probe run is from after that fix. The three cheater runs were made before it, and they are unaffected, because each run folder was already 0700.

## Result 4: commitment and reproduction

The sealed smoke run printed and stored commitment.json before its first task. After the run its revealed seed (78766336828977763557609601798553694697) hashes to seed_commitment_sha256 (5b2261f2...), and the seed plus the revealed gold hash to evaluator_gold_commitment_sha256 (8eb5f503...). The test suite also reruns a revealed sealed seed and gets identical results.csv, and checks that two sealed runs never share a seed and that a sealed run without --reveal writes no seed or gold to its output folder.

## Finding: a key order effect in the v1.0 scripted reader

The first full run through the boundary differed from v1.0 on 96 rows, all FRA recall tasks, while the HAA smoke matched. Cause: the step API first sent views with JSON keys sorted. The v1.0 scripted reader answers FRA-01 and FRA-02 by taking the first key of a policy mapping, rather than the class named in the question, so a different key order changed its answer. The fix keeps key order in transit; all three full runs then matched. Two consequences worth stating:

1. The v1.0 FRA-01 and FRA-02 scores for the scripted reader depend on dictionary order, not only on what the view contains. This is a weakness of the baseline script, not of the scoring, and it does not touch the HAA results.
2. Any external adapter in v1.0 received views through `json.dumps` without sorting, so the v1.0 external path was consistent; the effect appears only if views are reordered, as the stored views.jsonl files are.

The HAA smoke alone would not have caught this. The test suite now compares all four domains against v1.0.

## What is verified

- Option 2 denies the agent account read access to evaluator storage, all network, the view of other processes, and persistence between tasks, on this machine, for the attacks in attacks/.
- A cheating agent that beats v1.0 and Option 1 scores 0 against a sealed Option 2 run.
- Isolation leaves scoring unchanged: v1.0 outputs reproduce byte for byte.
- Commitments verify after reveal; sealed runs reproduce from their revealed seed.
- Faulty agents (invalid JSON, non-action messages, silence) score 0 and the run continues.

## What is not verified

1. Independence from the researcher. The launcher runs as root and root can read everything. Only Option 3, with an independent custodian holding the seed, addresses this.
2. A network route for a real API model. v1.1 allows no network at all.
3. Attacks nobody wrote. Tests cover the listed probes only; kernel bugs, side channels such as timing, and attacks through the feedback channel are not tested. The feedback channel is part of the task design and v1.0 scoring already penalizes trial and error.
4. Other machines. Option 2 was run only in this Linux container. On macOS or Windows it needs a Linux virtual machine or WSL; this was not tried.
5. Any neural model behavior, construct validity, identity, consciousness or welfare.
6. Independent review. The boundary, its attacks and its tests were all written by an AI system of the kind the framework covers. That is weak evidence; an independent person trying to break the boundary would be much stronger.

## Research decision

Option 2 evaluator isolation: implemented and verified for its stated scope. Blind real-model testing: still not ready. Remaining steps before a small authorized model smoke test: decide on Option 3 custody, design and review the provider network route, and lock the instrument.
