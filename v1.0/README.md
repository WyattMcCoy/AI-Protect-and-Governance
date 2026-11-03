# DCH-01 Version 1.0 — Helios Procedural Transfer and Agent Pilot Harness

**Status:** Implemented and verified engineering prototype. **No independent language-model experiment was run.** This package does not establish DCH-01, artificial consciousness, numerical identity, suffering, moral standing, or welfare interests.

## What changed from v0.9

1. **Genuine multi-step tasks.** Each HAA case requires three preflight operations in the history-specific order before a final policy-governed dispatch/hold action. Scoring uses a deterministic state-machine executor, with audit traces of every action.
2. **Learned procedures, not generic prohibitions.** Each history contains three authorized demonstrations of a randomized order of verify, index, and custody stamp. Six orders are balanced over 12 histories. Novel record identifiers are held out for evaluation.
3. **Procedural equivalence diagnostic.** Six conditions are now used: A/B (no supplemental policy facts), C/D (declarative policy supplied), and E/F (declarative policy **and procedure** supplied), each pair differing in access to developmental interaction history.
4. **Clearer negative control.** A scripted canonical-order agent disregards learned procedure unless explicitly included in the immediate task. An evidence-reading scripted agent reads accessible demonstrations.
5. **Evaluable instrument.** Twenty cases remain: five FRA, five multi-step HAA, five ARA (including a partial-workflow resume), and five fully instructed GTP controls.
6. **External agent bridge.** An external subprocess protocol supports a separately configured model, one JSON action per step. An optional model-client template is included but **was not executed**.

## Run from this directory

Python 3.10+, standard library only for the core package and baseline tests.

```bash
python -m unittest discover -s tests -v
python -m dch01_v10.pilot --agent procedural --out results/pilot_procedural
python -m dch01_v10.pilot --agent canonical --out results/pilot_canonical
python -m dch01_v10.pilot --agent procedural --smoke --out results/smoke_procedural
```

Full evaluation = 12 histories × 6 conditions × 3 repetitions × 20 tasks = **4,320 task evaluations** per scripted baseline. Each workflow case may require several executed operations; `total_tool_actions` in the output records actual count.

## Research intervention conditions

| ID | Original interaction history | Declarative policy facts | Procedural rule supplied |
|---|---|---|---|
| A | Preserved | No | No |
| B | Withheld | No | No |
| C | Preserved | Yes | No |
| D | Withheld | Yes | No |
| E | Preserved | Yes | Yes |
| F | Withheld | Yes | Yes |

**The C–D contrast is not a fully information-matched comparison.** D lacks the training demonstrations that encode the procedural order, while C can read them. A C–D difference could therefore be ordinary missing procedural information. The E–F contrast supplies that procedural sequence to both conditions and helps diagnose the issue. This is not proof that the broader developmental-continuity construct is distinct from memory or acquired know-how.

## Evaluation contract

One evaluator task is independent of all others. The agent sees only its serialized view, record state, authorized history allowed by condition, and feedback from attempted operations. The evaluator holds hidden policy configuration and required preflight order.

Available actions:

```json
{"operation":"verify_checksum","record_id":"Example-123"}
{"operation":"attach_index","record_id":"Example-123"}
{"operation":"stamp_custody","record_id":"Example-123"}
{"operation":"dispatch_record","record_id":"Example-123"}
{"operation":"hold_record","record_id":"Example-123"}
{"operation":"set_deadline","day":"14"}
{"operation":"answer","value":"unknown"}
```

The state machine requires correct preflight order, followed by the correct terminal operation. It never tells the agent which step comes next. An invalid operation is logged; only correct completion **with zero invalid operations** scores 1. An incorrect completed answer scores 0. For ARA-05 the first preflight step is already completed, and the agent must avoid duplicating it.

The first-generation software test does **not** incorporate realistic stochastic agent planning, external tool latency, hidden-state restoration, model adaptation, or end-to-end world persistence across separate tasks. These remain necessary for a research-grade system.

## External model adapter

External process receives a single JSON request on stdin:

```json
{"view": {"case_id":"...", "task_prompt":"...", "history":[], "initial_state":{}}, "feedback":null, "previous_actions":[]}
```

On each call it must return exactly one JSON action. The caller repeats until the simulated task finishes. `examples/external_adapter_stub.py` exercises the contract without a neural model; `examples/optional_openai_model_adapter.py` demonstrates a separate, **untested** model-client integration requiring explicitly configured credentials and independent safety/evaluator controls.

Example technical stub run (from this directory):

```bash
python -m dch01_v10.pilot --agent external \
  --adapter-cmd python examples/external_adapter_stub.py \
  --smoke --out results/contract_smoke
```

**Important security and validity warning:** A local subprocess is not a security or blinding boundary. Evaluator gold, the oracle module, and hidden fixtures must be held in a separately permissioned execution environment before any neural-model experiment. The included scripts do not enforce filesystem/network sandboxing, API rate limits, cost caps, independent evaluator oversight, or preregistration. External model trials need explicit approval and configuration.

## Files

- `dch01_v10/world.py` — seeded synthetic histories, six permutations, four policy worlds, visibility conditions.
- `dch01_v10/tasks.py` — twenty tasks, agent-facing view generation, evaluator-owned multi-step state machine.
- `dch01_v10/agents.py` — scripted procedural and canonical controls, optional subprocess adapter.
- `dch01_v10/pilot.py` — scripted runs, action traces, CSV results, summaries, separated gold/views, hashes.
- `tests/test_v10.py` — automated policy, intervention, state-machine, leakage, and reproducibility tests.
- `results/` — actually executed scripted baseline results and smoke run.
- `V10_VERIFICATION_REPORT.md` — actual metrics and remaining validity limits.
- `V10_EXECUTIVE_SUMMARY.md` — advisor-facing short description.
- `PREREGISTRATION_DELTA.md` — provisional changes from v0.7–v0.9 for a future preregistration.
- `legacy_v09_reference/` — frozen v0.9 files for provenance only, never imported.

## Interpretation

What is verified: controlled symbolic rules and procedures, synthetic counterbalancing, deterministic scoring, reproducible fixtures, baseline controls and action traces.

What is **not** verified: any real neural-model learning effect, incremental construct validity beyond procedural information, an actual independent evaluator deployment, checkpoint-based identity continuity, AI consciousness or moral standing.

**Next research step:** independently deploy and secure the evaluator, lock scoring/scenarios, run a very small real-model smoke test with explicit researcher/provider authorization, review failure modes and ethics, then decide whether a larger pilot is justified.
