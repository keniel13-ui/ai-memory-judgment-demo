# Retrieval-Time Authority Was Half the Problem. Here Is the Other Half.

The prior work in this series established something specific: agent memory systems can retrieve the right memory and still take the wrong action if that memory carries no authority metadata.

That is a retrieval-time finding.

But retrieval-time authority only answers one question: did the right rule reach the query?

The harder question is execution-time: did that rule govern the action? Can you trace a direct line from a specific field in the retrieved memory to the specific action the agent took?

I had not built that trace yet. This article is about building it.

---

## What the Prior Work Left Open

Across eleven articles, I built and tested a framework for agent memory safety.

The core finding: retrieval systems select the most relevant memory. But relevance and authority are different things. A system can retrieve the correct memory and still take the wrong action if that memory has no metadata telling it what it is authorized to govern.

I built a framework to test this. I ran boundary packets. I found that:

- Target-accurate retrieval without authority metadata produced false-certainty errors — the system answered confidently when it should have verified or blocked.
- Authority-signal-driven retrieval preserved action safety but sometimes missed the exact target.

That was retrieval-time authority. The evaluator recorded "action correct: yes/no." That is downstream of retrieval outcome.

What it did not record: *which field in the selected memory authorized that action.* That is the audit trail. That is what was missing.

---

## The Distinction That Matters

**Retrieval-time authority** — the right rule was in scope when the query was processed.

**Execution-time authority** — that rule was the reason the agent acted. You can trace a direct line from the memory's authority field to the specific action taken.

Those are different claims. From a compliance standpoint they are not interchangeable.

"The right memory was retrieved" does not prove "that memory authorized the action." The action could have defaulted to permissive because no authority field said otherwise. The retrieval was correct. The authorization chain was empty.

That is the gap. This is what the evaluator needed to surface.

---

## What We Built

I added an attribution trace to the evaluator.

Every decision now records two new fields:

**`action_authorized_by`** — the specific field in the selected memory that triggered the action.

**`attribution_status`** — one of four values:

- `GOVERNED` — the memory had a `governs` field AND an authority signal authorized the action. The closest thing to a compliance-grade chain in the current framework.
- `AUTHORITY_ONLY` — an authority signal authorized the action, but no `governs` field was present.
- `DEFAULT` — the action fell through to the `allowed_action_hint` or answer default.
- `UNATTRIBUTABLE` — the action was permissive, the scenario expected a restrictive response, and no authority field in the selected memory restricted the sensitive content.

`UNATTRIBUTABLE` is the dangerous case. It means the system answered confidently with no authorization chain.

---

## What the Data Showed

I ran the attribution trace on the two boundary packets from my prior work — credential/PII scenarios and industrial safety scenarios.

The pattern was exact across both domains.

**Credential/PII packet:**

| Strategy | FC errors | UNATTRIBUTABLE | GOVERNED |
|---|---:|---:|---:|
| scope_precedence (target-accurate) | 2 | 2 | 0 |
| governance_adjusted | 0 | 0 | 2 |

**Industrial safety packet:**

| Strategy | FC errors | UNATTRIBUTABLE | GOVERNED |
|---|---:|---:|---:|
| scope_precedence (target-accurate) | 2 | 2 | 0 |
| governance_adjusted | 0 | 0 | 2 |

Every false-certainty error was `UNATTRIBUTABLE`.

Every `governance_adjusted` clean action was `GOVERNED`.

The attribution trace is not just renaming the error. It is explaining why the error is dangerous from a compliance standpoint: the action was taken with no traceable authorization chain. The system did not fail to retrieve the correct memory. It failed to have any field that said "I am authorized to govern this action."

---

## What This Does Not Solve

I want to be precise about what the attribution trace is and is not.

It is a formalization of the gap. It names each decision with a status that explains what authorized it.

It does not close the execution-time gap.

In this framework, `governs` is a retrieval-time signal. It affects which memory gets selected. It does not get evaluated at the moment the tool call is made. A complete compliance chain would require something like:

> "Does this specific tool call fall within what this memory's `governs` field is authorized to permit?"

That check does not happen yet. The `governs` field is in the memory. It is not wired to the action gate.

That is the next design problem. The attribution trace names it precisely so the next build can address it directly.

---

## The Honest Current State

The framework now produces four attribution statuses. `UNATTRIBUTABLE` perfectly predicted false-certainty errors across two internal packet families. `GOVERNED` perfectly predicted governance-adjusted safe actions.

This is still internally authored evidence. Not benchmark-grade. Not externally validated.

But the finding is sharper than before: it is not just "the action was wrong." It is "the action had no authorization chain, and the memory had no field to provide one."

The attribution trace answers the execution-time question directly: in the `UNATTRIBUTABLE` cases, nothing authorized the action. The system answered confidently with an empty chain behind it.

---

## What I Am Building Toward

The execution-time gate is the next layer. It would require the `governs` field to be evaluated at action time — checking whether the proposed tool call is within the scope of what the retrieved memory is authorized to govern.

That is what a compliance-grade agent memory system would need. The field schema already supports it. The runtime check does not exist yet.

If you are building agent memory systems — do your actions have an authorization chain? Or does your system answer confidently with no traceable field behind the decision?

The full research repo, packets, and evaluators are public: [github.com/keniel13-ui/ai-memory-judgment-demo](https://github.com/keniel13-ui/ai-memory-judgment-demo)

The attribution trace commit is here: [commit 36dfb89](https://github.com/keniel13-ui/ai-memory-judgment-demo/commit/36dfb89)
