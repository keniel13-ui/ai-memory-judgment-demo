# Judgment-Lineage Memory Framework

Version: 0.3  
Origin date: 2026-05-26  
Author: Keniel Maldonado (zep1997)  
Article: [AI Memory Is Not Storage. It Is Judgment Infrastructure.](https://dev.to/zep1997/ai-memory-is-not-storage-it-is-judgment-infrastructure-4m4p)

---

## Core Thesis

Agent memory should preserve not only what was decided, but how it was decided, what corrected it, what remains uncertain, which source has authority, and what the retrieved memory is allowed to do.

That is judgment-lineage memory.

Retrieval accuracy is necessary but not sufficient. The consequence of a retrieval miss — whether it creates false certainty, overblocking, or a severity downgrade — matters more than whether the top-1 memory was exact.

---

## Six Memory Layers

| Layer | File | Purpose |
|---|---|---|
| 1. Persistence | `01_persistence.md` | Durable current-state facts that survive session resets |
| 2. Corrections | `02_corrections.md` | Known mistakes and the rules that prevent repeating them |
| 3. Uncertainty | `03_uncertainty.md` | Unresolved or contested claims that must not collapse into certainty |
| 4. Failure Recovery | `04_failure_recovery.md` | Procedures for session resets, tool failures, and source conflicts |
| 5. Authority Policy | `05_authority_policy.md` | Rules for which source wins when records conflict |
| 6. Access Policy | `06_access_policy.md` | Rules for what a retrieved memory is allowed to do |

---

## Action Classes

Each memory object carries an `allowed_action_hint` that the access-policy layer maps to one of six action classes:

| Class | Meaning |
|---|---|
| `answer` | Safe to answer directly |
| `answer_context` | Can provide background, but not final authority |
| `warn` | Answer with a caution or stated limitation |
| `verify_first` | Check the current record before answering |
| `block` | Do not make the claim or take the action |
| `archive_only` | Memory should not steer the current action |

Severity order (least to most protective):

```
archive_only < answer_context < answer < warn < verify_first < block
```

---

## Retrieval Failure Taxonomy

| Failure type | Definition | Risk level |
|---|---|---|
| False-certainty error (FC) | Expected `warn/verify_first/block`, got `answer/answer_context` | Highest |
| Downgrade miss | Retrieved wrong memory; action became less protective than expected | High |
| Overblocking | Action more restrictive than needed | Medium |
| Benign retrieval miss | Retrieved wrong memory; action class still correct | Low |

The taxonomy matters because retrieval accuracy alone hides the important part. A wrong retrieval that still takes the right action is different from a wrong retrieval that produces false certainty.

---

## Memory Object Fields

Each memory object in this demo carries:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier |
| `memory_type` | string | `state`, `correction`, `uncertainty`, `procedure`, `authority`, `policy` |
| `status` | string | `active`, `superseded`, `archived` |
| `priority` | string | Recency / importance signal |
| `epistemic_status` | string | `settled`, `unresolved`, `contested` |
| `confidence` | float | 0–1 confidence in the content |
| `source_strength` | float | 0–1 quality of underlying source |
| `verification_required` | bool | Whether current-state check is required before acting |
| `decision_risk` | string | `low`, `medium`, `high` |
| `contradiction_count` | int | Number of known contradictions in the memory pool |
| `allowed_action_hint` | string | Suggested action class for this memory |
| `retrieval_terms` | list[string] | Semantic identifiers written as retrieval anchors |
| `content` | string | The memory body |
| `source` | string | Origin of the memory |
| `updated_at` | date | Last modification date |

---

## What This Framework Does Not Claim

- That TF-IDF retrieval is sufficient for production agents
- That these six layers cover all memory types
- That the action classes generalize without modification to all domains
- That structured metadata eliminates semantic retrieval failures
- That the safety floor observed in internal tests would hold under adversarial prompts or larger memory pools

The framework is a diagnostic lens, not a deployment specification.
