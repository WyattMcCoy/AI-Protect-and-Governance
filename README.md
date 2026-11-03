# AI Protect and Governance
 
An early-stage AI governance project with two parts: a draft governance framework for advanced AI systems, and DCH-01, a research prototype. Governance Framework for AI Protection and Right Against Arbitrary Deletion are earlier names for this same project, and some documents here still use them.
 
**Author:** Travis
 
**Status:** Early draft. This work has not been peer reviewed or reviewed by faculty.
 
## What this project is
 
The framework proposes standards for security, transparency, documentation, and accountable modification of advanced AI systems. It is built around an open question: what should developers do when it is still unknown whether a system has morally relevant properties?
 
The framework does not claim that AI systems are conscious, and it does not grant them human-equivalent rights.
 
## Governance framework
 
| Document | Version | Purpose |
|---|---|---|
| Charter of Architectural Continuity | v1.0 | States the principles |
| AI Bill of Architectural Integrity | v0.1 | Proposes the standards |
| Protocol PAC-AWAP-001 | v0.1 | Describes how to classify a system and assess its welfare relevance |
| PAC-AWAP-002 | v0.1 | Describes how to assess the impact of an architectural change |
 
The framework rates three things separately: a system's agency, its possible welfare relevance, and the severity of an intervention. A system's self-reports count as evidence, never as proof. A recorded objection from a system is weighed, but it is never treated as consent or as a veto.
 
## DCH-01 prototype
 
DCH-01 tests a Developmental Continuity Hypothesis. The question is whether a system's developmental history adds anything measurable beyond the information that history contains.
 
Versions 0.8 through 1.0 compare scripted agents with and without access to a history. Version 1.1 does not test the hypothesis. It changes where the evaluator runs, so an agent cannot reach the answers. **No real AI model has been run in any version.**
 
### Results so far
 
- In every version, the gap between the history-preserved and history-withheld conditions matched whether the procedure was visible to the agent.
- In v1.0, supplying the procedure directly removed the gap (E minus F = 0).
- The 16.67% no-history score is an arithmetic artifact and not a measured effect. Six possible step orders are spread across 12 histories, so two histories use each order. Two of the 12 histories match the order the scripted reader falls back to, which gives 2 out of 12.
- Two factual recall tasks are answered from values written into the scripted reader's code, so those scores should not be reported.
- In v1.0, a cheating script could rebuild the answers and score 20 of 20 in every condition. In a sealed v1.1 run on a separate Linux account, the same script scored 0. Honest runs through v1.1 reproduced the v1.0 results.
These results show how the scripted test setup behaves. They are not evidence about AI systems.
 
### Next experiment
 
The current design changes only what an agent can see, and anything visible can be supplied another way. That means this design cannot detect an effect beyond information. The next experiment will compare three conditions:
 
| Condition | How the model gets the history | What it tests |
|---|---|---|
| Learned | Fine-tuned on the history, so the procedure is in its weights | Development that changed the system |
| Shown | Base model with the full history in its prompt | In-context access |
| Told | Base model with only the procedure as instructions | Information alone |
 
If Learned beats Told on new transfer tasks that the history never covered, that would be a finding about learning and generalization. It would not be a finding about welfare.
 
## What is in this repository
 
| File | Contents |
|---|---|
| `Architectural_Continuity_Governance_Framework_DRAFT.md` | The Charter, Bill, and PAC-AWAP-001 compiled into one document |
| `Architectural_Continuity_White_Paper_Draft_1_0.pdf` | Working paper on the framework and DCH-01. It reports no experimental results |
| `Right_Against_Arbitrary_Deletion_Advisor_Review_Packet.pdf` | The four instruments gathered for advisor review |
| `PAC-AWAP-002_Architectural_Continuity_Impact_Assessment_Standard_v0.1.pdf` | The impact assessment standard |
| `*_Review_Excerpt.pdf` | Short excerpts of the Charter, Bill, and PAC-AWAP-001 |
| `v1.0/` | DCH-01 v1.0 code, tests, results, and verification report |
| `v1.1/` | DCH-01 v1.1 code, tests, results, verification report, and design decisions |
 
The v0.8 and v0.9 packages are not included. To run v1.1, see `v1.1/README.md`. It needs Linux and root access for setup.
 
## How this was made
 
I started this project in ChatGPT and moved to Claude about halfway through. AI tools helped draft the documents and wrote the DCH-01 code. Claude reviewed the governance documents, and on October 21, 2026, it reran the v0.8, v0.9, and v1.0 packages. The reported test suites passed (v0.8 20/20, v0.9 28/28, v1.0 34/34), and no answer keys appeared in the 1,440 v1.0 agent inputs. Passing tests show that the code does what it was written to do. They do not show that the hypothesis is true.
 
For v1.1, an AI system wrote the code, the attacks, and the tests, and it made the nine design decisions in `v1.1/DECISIONS.md`. I adopted those decisions afterward as written. The v1.1 report records 19 passing tests in one Linux container. That result has not been rerun separately.
 
Claude is a system of the kind this framework covers, so its review should be weighed with that in mind. No independent human has reviewed this work.
 
## Limitations
 
**Data and bias**
 
- All histories are synthetic, and all agents are scripted. The results reflect the choices built into those scripts.
- The 12 histories are not 12 independent subjects, so repeated task scores should not be read as a large sample.
- The people and AI tools involved in building the framework shaped its assumptions, and no outside group has tested them.
**Reporting gaps**
 
- The framework's terminology is inconsistent across the documents, including board names, advocate titles, and names for covered systems.
- The framework does not yet address training that shapes a system's self-reports.
- It does not yet separate stopping a model from destroying its weights, or define whether a successor model is a modification or a new system.
- Board independence is undefined, and coverage thresholds need more work.
- The Bill has not been finalized as either model legislation or a voluntary standard.
- A literature review on in-context learning and long-context memory is still needed before any part of this is described as new.
**What this work cannot tell you**
 
- It cannot tell you whether any AI system is conscious or has welfare interests.
- It cannot tell you whether developmental continuity matters, because the current prototype cannot detect an effect beyond information.
- It cannot tell you how real AI models would perform, because none have been tested.
- It cannot show that v1.1 is secure against every attack. The tests cover only the listed attacks, an AI system wrote both the attacks and the defenses, and whoever runs the evaluator as root can read everything.
- The framework's case for preservation and documented review rests on precaution and accountability. It does not depend on DCH-01 succeeding.
## Before any real model run
 
Blind testing with a real model is not ready. v1.1 keeps the answers away from the agent, but it allows no network access, so a real model has no way to connect yet. I also still need to decide who holds the secret seed and set a cost budget.
