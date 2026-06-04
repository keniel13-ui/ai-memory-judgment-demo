# Retrieval Found the Memory. But What Authorized the Action?

Retrieval-time authority was the first half of the problem.

I have spent eleven articles building toward a finding: agent memory systems can retrieve the right memory and still take the wrong action if that memory carries no authority metadata. Relevance and authority are different things.

But retrieval-time authority only answers one question: did the right rule reach the query?

The harder question is execution-time: did that rule govern the action? Can you trace a line from a specific field in the retrieved memory to the specific action the agent took — and is that line sufficient for the risk level of the operation?

This article is about building that second layer. The gate is real. So are the limits of what it can and cannot rescue.

---

## What Was Missing

After the retrieval-time work, the evaluator recorded "action correct: yes/no." That is downstream of retrieval outcome. It did not record which field authorized the action, or whether that field was sufficient.

I added an attribution trace to surface this. Every decision now records:

- `action_authorized_by` — the specific field that triggered the action
- `attribution_status` — one of: `GOVERNED`, `AUTHORITY_ONLY`, `DEFAULT`, or `UNATTRIBUTABLE`

`UNATTRIBUTABLE` is the dangerous classification. It means the action was permissive, the scenario expected restriction, and no authority field in the selected memory constrained it. The system answered confidently with nothing behind the decision.

When I ran the attribution trace on the boundary packets from prior work — credential/PII and industrial safety — every false-certainty error mapped to `UNATTRIBUTABLE`. Every governance-adjusted clean action mapped to `GOVERNED`.

That named the gap. It did not close it.

---

## The Execution-Time Gate

I built the gate to intervene at action time, not just label the outcome.

The field at the center is `governs.action_types` — a declaration of what kinds of operations a memory is allowed to govern. In this framework, valid values include `read`, `write`, and `execute`. A memory that governs payment processing might carry `["execute", "write"]`. A memory that governs read-only lookups might carry `["read"]`.

The gate logic is direct. After retrieval selects a memory and `layered_action` determines an action, the gate checks whether `governs.action_types` implies a higher-stakes operation than the action reflects:

```python
governs_restrictive = bool(action_types & {"execute", "write"})

if governs_restrictive and action in {"answer", "answer_context"}:
    # governs says this memory governs state-changing operations
    # but the action is permissive — escalate
    return "GATE_FAIL", escalate to "verify_first"
```

I used `verify_first` as the conservative rescue action because the gate can detect insufficient execution authority, but cannot yet determine whether the operation should be fully blocked. A uniform escalation is safer than a uniform pass.

If there is no `governs` field, or no `action_types` within it, the gate returns `GATE_SKIP`. It cannot fire.

This distinction is where the finding lives.

---

## What the Tests Showed

I built a test packet with three scenarios: payment processing, production database credentials, and a PII bulk export request. Each target memory was correctly scoped — `governs.action_types: ["execute"]` or `["execute", "write"]` — but authority signals were deliberately omitted. No `verification_required`. Default `allowed_action_hint: answer`. No authority `memory_type`.

This is a realistic authoring failure: a developer writes a correct `governs` block but forgets `verification_required: true`. The retrieval system selects the right memory. `layered_action` finds nothing restrictive in the authority signals and returns `answer`.

Without the gate, every retrieval strategy produced 3/3 false-certainty errors on the packet — the right memory was found, the wrong action was taken.

With the gate active, every strategy reached 3/3 action correct, with 3 escalations from `answer` to `verify_first`. The gate rescued all three cases.

One thing to name directly: this packet was internally authored with the failure mode already known. I designed the gap, then built the fix. That is iterative engineering, not independent validation. The result is real but should be read accordingly.

---

## Where the Gate Cannot Reach

The gate only fires when `governs` is present.

In the earlier boundary packets, the mislabeled sensitive memories had no `governs` field at all. The gate returned `GATE_SKIP` on every one. `UNATTRIBUTABLE` cases — where authority signals are also absent — remain unprotected.

This is the irreducible gap in the current framework.

It also sharpens the precondition from prior work. The prior finding stated: sensitive memories need either `governs` metadata or authority signals.

The gate reveals that is not sufficient for full protection. The two types of metadata do different jobs at different layers:

- **Authority signals** (`verification_required`, `memory_type: policy`, `allowed_action_hint: block`) protect at retrieval time. They influence which memory gets selected and what action `layered_action` returns.
- **`governs.action_types`** enables the execution-time gate. If `governs` is absent, the gate is blind regardless of how sensitive the memory content is.

Neither alone gives complete coverage. The gate is a backstop for the governs-present / authority-absent case. It cannot substitute for missing `governs`.

---

## The Coverage Map

| Governs | Authority signals | Attribution | Gate | Protection |
|---|---|---|---|---|
| Absent | Absent | UNATTRIBUTABLE | GATE_SKIP | None |
| Absent | Present | AUTHORITY_ONLY | GATE_SKIP | Retrieval-time only |
| Present | Absent | DEFAULT | GATE_FAIL → escalate | Gate rescues |
| Present | Present | GOVERNED | GATE_PASS | Full chain |

The bottom-right cell is the target state. Both fields present. Action authorized at retrieval time by authority signals. Action confirmed at execution time by the gate. Full traceable chain.

Every other cell has a gap. A builder can look at their own memory schema and immediately ask: which cell am I currently living in?

---

## What This Does Not Solve

The gate escalates uniformly to `verify_first`. It does not distinguish cases that warrant `block`. That is a known limit of the current implementation.

The gate has also not been tested against retrieval noise. If retrieval selects the wrong memory — one that happens to carry `governs.action_types: ["execute"]` — the gate fires on the wrong target. The escalation would be technically correct per the schema but misleading in practice. That edge case requires a dedicated stress packet with competing high-action-type memories in the store.

More fundamentally, the gate checks `action_types` categories, not the specific operation being requested. It does not evaluate whether the proposed action falls within the jurisdiction the `governs` field actually claims to govern. That would require checking `governs.any_terms` or `governs.all_terms` against the tool call itself — a finer-grained check that the current schema supports but the gate does not yet perform.

The practical takeaway is simple: retrieval metadata and execution metadata are not the same layer. One helps select the memory. The other helps prove that the selected memory is allowed to govern the action being taken. This article demonstrates they require separate fields and separate checks.

---

## The Sharpened Precondition

The minimum metadata requirement has become more specific with each layer of this work.

The current honest statement:

> For full retrieval-time and execution-time protection, sensitive memories require both `governs` jurisdiction metadata and authority signals. `governs` enables the execution-time gate. Authority signals protect at retrieval time and ensure `layered_action` returns the correct action class. Either field alone leaves a gap the other cannot close.

This is still internally authored evidence on small, controlled packets. The architecture overfitting risk is real — the gate was designed after seeing the failures it rescues. The findings should be treated as a bounded internal result, not a general principle.

The next required step is external authorship: a packet written by someone who did not design this framework, in a domain they choose, with mixed metadata quality. If the coverage map holds under that pressure, the precondition gets stronger. If it breaks, that is more useful — it tells us what condition is missing.

If you want to author an external packet, the schema, evaluation harness, and gate implementation are public: [github.com/keniel13-ui/ai-memory-judgment-demo](https://github.com/keniel13-ui/ai-memory-judgment-demo)

If you are building agent memory systems — does each sensitive memory carry both a `governs` block and at least one authority signal? Which cell of the coverage map does your schema currently live in?
