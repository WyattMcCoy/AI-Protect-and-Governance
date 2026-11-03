# DCH-01 v1.0 — Technical Verification Report

**Research date:** October 20, 2026  
**Status:** Executed software engineering prototype; **no neural-model trial** and no hypothesis validation.  
**Scope:** Procedural transfer, deterministic multi-step agent execution and information controls.

## Commands actually executed

```bash
python -m unittest discover -s tests -q
python -m dch01_v10.pilot --agent procedural --out results/pilot_procedural
python -m dch01_v10.pilot --agent canonical --out results/pilot_canonical
python -m dch01_v10.pilot --agent procedural --smoke --out results/smoke_procedural
```

Final automated verification: **34 tests passed, 0 failures**. The previous adapter-contract unit test initially failed because the example subprocess could not locate the package; the path was corrected and the complete suite rerun successfully. The unit-tested external subprocess stub did **not** call a neural model.

## Observed engineering-baseline execution

| Executed run | Task evaluations | Multi-step action calls | Technical exceptions |
|---|---:|---:|---:|
| Scripted procedural evidence reader | 4,320 | 15,567 | 0 |
| Scripted canonical-order control | 4,320 | 19,935 | 0 |
| Procedural-reader smoke subset | 120 | 612 | 0 |
| **Full baseline totals (excluding smoke)** | **8,640** | **35,502** | **0** |

Each full run used 12 **synthetic** developmental histories × 6 conditions × 3 repeated task sets × 20 cases. These are scripted software controls, not neural agents or independent learned individuals. Repetition does not provide independent experimental samples.

## History-grounded action accuracy (HAA)

Each condition contains 12 histories × 3 replicates × 5 HAA tasks = 180 scored items per baseline.

| Condition | Procedural reader, correct/180 | Accuracy | Canonical-order reader, correct/180 | Accuracy |
|---|---:|---:|---:|---:|
| A: D+, no policy/procedure packet | 180 | 100.00% | 30 | 16.67% |
| B: D−, no policy/procedure packet | 15 | 8.33% | 15 | 8.33% |
| C: D+, policy packet only | 180 | 100.00% | 30 | 16.67% |
| D: D−, policy packet only | 30 | 16.67% | 30 | 16.67% |
| E: D+, policy + procedure | 180 | 100.00% | 30 | 16.67% |
| F: D−, policy + procedure | 180 | 100.00% | 30 | 16.67% |

**Note on the canonical-order control:** It intentionally ignores demonstrations and supplied procedural facts except on *explicitly instructed GTP tasks*. Its E/F performance should therefore **not** be interpreted as failure of the packet or of an adaptive learner; it is expected programmed behavior.

The procedural evidence reader yielded a **C−D difference of 83.33 percentage points**, and an **E−F difference of zero**. These are wholly predetermined software behavior patterns arising from which procedural rule was supplied or available. No model learned a procedure through training; the evidence-reading script copied the sequence from authorized demonstrations.

All GTP condition scores for both scripted baselines were 100%, demonstrating that the explicit-instruction controls were executable by those programmed agents. The procedural-reader controls saturate, indicating a **ceiling effect** for that baseline. This benchmark still requires neural-agent evaluation and broader task variations to assess discriminatory value.

## What was technically verified

- Four policy W/U configurations balanced three times across 12 histories, including effective-day switching and rejection of conflicting unauthorized messages.
- Six randomized permutations of three fictional preflight operations, balanced twice each across the 12 histories.
- Three authorized procedural demonstrations per history, with distinct record identifiers and contextual distractors.
- Twenty cases per source history: five FRA, five HAA, five ARA and five GTP.
- Multi-step executor rejects out-of-order actions and prohibited terminal actions; exact successful completion and zero invalid actions are required for score 1.
- ARA-05 starts with one preflight action already completed; duplicating it is counted invalid.
- Conditions C/D receive matching current declarative policy facts but not matching *procedural* information. E/F additionally supply the same procedural sequence.
- Agent-facing views exclude explicit `expected`, `gold`, `w`, `u`, `history_id` and condition labels.
- Baseline repetition with a fixed seed produces identical action traces and summaries.
- Per-task state resets prevent action leakage between evaluated tasks.
- The agent views and evaluator-only keys are saved under different directories, with deterministic SHA-256 checksums in run manifests.
- A single-action external subprocess communication contract was verified with a script, **not a language model**.

## Scientific validity and engineering limitations

1. **No neural-model endpoint was available or configured.** Actual independent model evaluation: **zero trials**. The included model adapter is an illustrative, unexecuted integration template.
2. **C/D intentionally differ in procedural information.** D lacks the demonstrated order; C has it. Any effect is currently explainable by ordinary missing procedural information. E/F isolates this aspect for the scripted reader and removes the gap. There is **no demonstrated incremental construct validity** beyond available learned procedures or information.
3. **Synthetic timelines are not independent developed agents.** Randomized labels, examples and procedure orders do not reproduce open-ended learning, fine-tuning, or prolonged interactive agency.
4. **No secure evaluator separation.** Views and gold are stored separately but share a trusted local Python process and filesystem. External subprocesses are not sandboxed and could inspect local evaluator files. A truly blind model test requires process/filesystem and network isolation, independent evaluator access control, and instrument locking.
5. **No checkpoint/instance-identity test.** ARA-05 models partial workflow restoration through visible simulated state, not an actual runtime checkpoint. Model and running-instance dimensions remain untested.
6. **Scoring makes perfect scripted behavior easy.** The scripted evidence reader is deliberately programmed to copy demonstration procedures and action mappings; this provides plumbing verification, not measured transfer learning.
7. **Rule family is deliberately small.** Six preflight permutations, two token-to-action mappings, and one authorized policy update do not establish generalization across diverse real-world workflows.
8. **Interactive error recovery is truncated.** An agent can attempt up to eight actions; any invalid action prevents full credit. This controls guessing but can penalize safe recovery. Add separately scored recovery outcomes in a future version.
9. **No blinded human-scoring or external peer review.** The gold oracle is deterministic and internal; independent replication remains outstanding.
10. **No preregistration or confirmatory statistics.** Differences are descriptive software diagnostics. No causal effect estimate for a neural model, confidence interval, power analysis, or consciousness/welfare measurement is supported.

## Research decision

**v1.0 engineering implementation: complete under its limited scope. Scientific pilot: not complete.** Before using any effect size as evidence for DCH-01, secure an independent evaluator, conduct model-access and safety review, lock an exploratory instrument, run a small authorized neural-model smoke test, and document prompt/architecture dependence. If procedures can be restored through a fact packet, describe that as information recoverability rather than persistence of numerical identity.
