# Governance-Framework-for-AI-Protection
Framework for AI Protection
# Right Against Arbitrary Deletion

This project develops a California legislative concept for **precautionary, proportionate review of material changes to persistent AI systems**. It asks how developers and operators should handle potentially irreversible changes when those changes affect functional continuity and, in some cases, may implicate uncertain AI welfare interests. The proposal does **not** assume that AI consciousness has been proven or that AI systems have legal personhood, standing, or a right to continued operation.

**Status:** Preliminary academic and legislative concept, October 28, 2026. None of the project instruments is enacted law or a validated scientific standard.

## Current deliverable

- [California Legislative Concept Memorandum, Draft 1.2](outputs/RAAD_California_Legislative_Concept_Memo_Draft_1_2.pdf) — two-page PDF for initial faculty and legal review.

Draft 1.2 revises the earlier Draft 1.1. It recommends a time-limited feasibility study and voluntary pilot before any targeted statutory duty. It uses two related but distinct grounds for review:

1. **Continuity and accountability:** Assess observable effects on persistent memory, goals, functional organization, users, and auditability.
2. **Precautionary welfare:** Add scrutiny when credible evidence or consequential evidence gaps raise the possibility of welfare-relevant capacities. A technical classification or an AI system's self-description does not establish subjective experience.

Human safety controls, emergency shutdown, cybersecurity, and lawful deletion of personal information remain available. Agent-generated concerns may be considered as evidence; they do not create consent, a veto, or legal standing.

## Source documents

The documents supplied in `RAAD_Latest_Drafts_2026-10-28.zip` were extracted to [`work/raad_sources/`](work/raad_sources/). The archive's own register is [`FILE_REGISTER_README.txt`](work/raad_sources/FILE_REGISTER_README.txt).

| Instrument | Project copy | Status and role |
| --- | --- | --- |
| Architectural Continuity White Paper, Draft 1.0 | [`Markdown`](work/raad_sources/Architectural_Continuity_White_Paper_Draft_1_0.md) · [`PDF`](work/raad_sources/Architectural_Continuity_White_Paper_Draft_1_0.pdf) | Complete working draft; sets out the two-track model and research limits. Not peer reviewed. |
| Charter of Architectural Continuity, v1.0 | [`PDF`](work/raad_sources/Charter_of_Architectural_Continuity_v1.0_Review_Excerpt.pdf) | Condensed review excerpt; states the proposed principles. The full original was not supplied. |
| AI Bill of Architectural Integrity, v0.1 | [`PDF`](work/raad_sources/AI_Bill_of_Architectural_Integrity_v0.1_Review_Excerpt.pdf) | Condensed review excerpt; proposes procedural duties. The full original was not supplied. |
| PAC-AWAP-001, v0.1 | [`PDF`](work/raad_sources/PAC-AWAP-001_v0.1_Review_Excerpt.pdf) | Condensed review excerpt; separates agency, welfare, and intervention-severity classifications. The full original was not supplied. |
| PAC-AWAP-002, v0.1 | [`Markdown`](work/raad_sources/PAC-AWAP-002_Architectural_Continuity_Impact_Assessment_Standard_v0.1.md) · [`PDF`](work/raad_sources/PAC-AWAP-002_Architectural_Continuity_Impact_Assessment_Standard_v0.1.pdf) | Complete proposed assessment standard, including the ACITI triage score and annexes. Its thresholds are unvalidated. |
| Consolidated advisor packet | [`PDF`](work/raad_sources/Right_Against_Arbitrary_Deletion_Advisor_Review_Packet.pdf) | Condensed review packet, not a complete edition of all instruments. |

## Reconciliation decisions

- Draft 1.1's three protection “levels” were replaced with PAC-AWAP-001's separate agency (`A0–A3`), welfare (`W0–W3`, `W-U`), and intervention-severity (`S0–S3`) axes. These remain provisional pilot categories.
- The Charter and AI Bill also address conditioning, destructive retraining, and effects on human relationships. Draft 1.2 treats these as assessment and notice factors while keeping the proposed initial statute focused on specified material interventions.
- PAC-AWAP-002's ACITI score is a **screening aid**, not a measure of consciousness, suffering, or overall harm. Its proposed Board-review triggers require testing before legislative adoption.
- Commercial convenience is neither an automatic exemption nor a categorically forbidden purpose; a material intervention needs a documented legitimate reason and proportionate review.

Because the Charter, AI Bill, and PAC-AWAP-001 are available only as excerpts, reconciliation with their complete original texts remains provisional.

## Open questions and next steps

Legislative counsel should examine California's jurisdictional reach, the lead enforcement agency, reviewer independence and appeals, confidentiality and trade secrets, constitutional and intellectual-property issues, and conflicts with privacy, legal holds, and security duties. The proposal must also define coverage thresholds, costs, remedies, and what evidence would justify moving beyond a pilot.

The next research steps are to obtain the three full original instruments, test classification agreement and ACITI reliability, assess safety delays and compliance costs, and obtain independent scientific and legal critique. PAC-AWAP-003 and White Paper 1.1 are planned work, not completed drafts in this archive.

California legal context includes the [consumer right to delete personal information](https://cppa.ca.gov/faq) and the [Transparency in Frontier Artificial Intelligence Act, SB 53](https://oag.ca.gov/sb53). Neither establishes the proposed AI welfare protection.

## Repository layout

- `outputs/` — user-facing memorandum.
- `work/raad_sources/` — extracted source documents.
- `work/raad_text/` and `work/raad_render/` — text extraction and visual checks.
- `work/build_raad_memo.py` and `work/render_raad_pdf.py` — local drafting and PDF-generation scripts.
