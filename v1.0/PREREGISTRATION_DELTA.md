# DCH-01 Preregistration Change Log — v0.7 → v1.0

**Not preregistered.** This document records proposed protocol changes; do not present it as a registered or executed neural-model study.

| Component | Earlier draft (v0.7–0.9) | Updated v1.0 pilot specification |
|---|---|---|
| History-dependent task | Single structured operation | Three randomized preflight operations followed by one terminal policy action |
| Memory manipulation | D+ / D− | Still D+ / D−, with explicit procedural information diagnostic |
| Fact equalization | F1 current policy mapping | F1 policy mapping; F2 additionally supplies procedure; **F1 is not procedural equalization** |
| Conditions | Four (A–D) | Six (A–F) |
| Primary engineering endpoint | Correct HAA action | Valid *full sequence* with zero incorrect operations |
| Main exploratory contrast | C−D | C−D, interpreted as residual procedural information availability; E−F as procedural equalization diagnostic |
| Task reset | Fresh one-action input | Fresh multi-step simulated state machine per case |
| Agent controls | Scripted evidence reader and always-hold | Scripted demonstration reader and fixed canonical-order control |
| Independent model trials | None | Still none; bridge present, actual model run pending |

## Provisional analysis plan, not locked

1. Primary exploratory engineering outcome: proportion of fully correct HAA workflows by condition, with descriptive history-level C−D and E−F contrasts.
2. Diagnostic outcomes: invalid action counts, recovery behavior, task completeness and GTP controls.
3. Dependence: history clusters are the relevant paired units; repeated tasks/replicates from a shared synthetic history are not independent subjects.
4. Pilot limitations: n=12, deterministic scripted agents, small procedure family and likely ceiling effects. No inferential p-values or confirmatory claims.
5. Before a neural-model pilot: protect gold in a distinct restricted process, fix evaluation prompts, budget and sampling, document model architecture/version, define invalid-trial exclusions, and register a plan if seeking confirmatory results.
6. Do not imply that preservation of a model file or full functional reconstruction establishes numerical identity or phenomenal consciousness.

### Remaining open methodological question

If information and acquired procedures can be supplied to reconstruct functional competence, what residual—and independently measurable—continuity property could DCH-01 predict? A reviewer may reasonably conclude that no such extra property has been demonstrated, and the framework must remain open to that outcome.
