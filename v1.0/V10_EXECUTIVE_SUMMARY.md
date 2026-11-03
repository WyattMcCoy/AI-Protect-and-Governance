# DCH-01 v1.0 | Faculty Review Summary

**Right Against Arbitrary Deletion — Developmental Continuity Hypothesis**  
**October 20, 2026 · Exploratory technical research prototype**

## Research question

Can a controlled experiment distinguish successful transfer of an agent's previously acquired multi-step procedures from basic factual recall, general task competence, and explicit instruction-following?

## What changed

Version 0.9 required one action per task. Version 1.0 introduces an evaluator-owned simulated state machine. The agent must perform three history-specific preflight operations in the correct order, then execute the policy-authorized final dispatch or withholding action. Across 12 randomized synthetic histories, six different procedural orders are balanced, alongside the two-by-two initial-policy and policy-revision configurations.

Twenty task templates evaluate factual recall (FRA), history-grounded action (HAA), adaptive revision (ARA), and general task performance (GTP). Six visibility conditions vary access to developmental history, current declarative policy facts, and an additional procedural guide.

## Observed verification

**34 automated tests passed.** Two scripted agents completed **8,640 task evaluations** with **35,502 simulated action calls** and no adapter errors. The programmed evidence-following reader achieved 100% HAA with history preserved, 16.67% without history when current policy was supplied, and 100% when the missing procedural order was also supplied. A control intentionally ignoring learned procedure performed at 16.67% under fact-supplied conditions. These outcomes follow from programmed rules; they do not reflect neural-model learning.

## Central scientific limitation

The key comparison (history preserved versus absent with current policy facts supplied) **does not equalize learned procedural information**. The resulting performance difference can be fully explained by the availability of that procedure. Supplying it eliminates the difference in the programmed evidence-reading baseline. Thus, Version 1.0 validates parts of the experimental **engineering**, not a distinct developmental-continuity construct.

**No actual language-model trials were run**, and there is no basis for conclusions about consciousness, numerical identity, welfare, or intrinsic moral status.

## Questions for independent reviewers

1. Which experimental intervention would isolate durable developmental effects from the amount or format of supplied information?
2. How should procedural competence be measured without rewarding fixed lookup strategies or penalizing responsible recovery?
3. What tasks and architectures are needed to demonstrate generalizability beyond fictional archive workflows?
4. What security boundary would adequately separate a neural-model agent from evaluator-only gold data?
5. How should confirmatory statistical units be defined when many trials share the same generated history?

## Next milestone

Establish an independently protected evaluation deployment and conduct a carefully labeled exploratory language-model smoke test, with an explicit model provider and permission to run it. Predefine scoring and technical failure handling before larger-scale experiments.
