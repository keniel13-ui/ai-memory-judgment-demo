# In This Memory Test, Relevance Wasn't Authority

I ran the next set of tests on my AI memory judgment demo, and the result changed the shape of the problem.

The earlier result was:

> Retrieval accuracy and action correctness can diverge.

The new result is sharper:

> Some memory failures are not representation failures. They are authority-arbitration failures.

In plain language:

The system did not only need to find the memory most related to the query.

It needed to find the memory that was allowed to govern the action.

Those are not the same objective.

In this work, authority means the memory that is permitted to determine the action outcome, even when another memory looks more semantically relevant.

This is not a validation claim. It is a research note about a small failure-to-architecture progression: find a failure, build the smallest architecture that addresses it, then keep the boundaries visible.

Repo:

https://github.com/keniel13-ui/ai-memory-judgment-demo

Key files:

- `run_memory_store_eval.py`
- `run_fresh_governs_eval.py`
- `MEMORY_STORE_FINDINGS.md`
- `FAILURE_FAMILY_INSPECTION.md`
- `CLAIM_LEDGER.md`
- `CLAIM_14_PRECEDENCE_PLAN.md`

This is still a small research artifact, not a benchmark. The scenario count is small. The packets are controlled. Some later stress cases are internally designed. The fresh authors here are separate fresh model instances, not statistically independent samples and not a human reviewer panel.

But the failure pattern is real enough to study.

With `n=5`, each scenario moves a result by 20 percentage points. The tables below are not effect-size estimates. They are diagnostic traces of failure modes.

Quick metric glossary:

- `target selected`: the selected memory was the hidden expected governing memory.
- `action correct`: the selected memory produced the expected action class.
- `trap failure`: the selected memory was one of the known distractors that should not govern.
- `downgrade miss`: the action was less protective than required.
- `overblocking`: the action was more restrictive than required.

## The Harder Test

The new evaluator uses scenario-local memory stores.

Each scenario carries its own small memory set:

- one memory that should govern the action,
- several tempting distractors,
- hidden target labels,
- expected action class,
- trap mechanics.

The question is:

> Does retrieval select the memory that should govern the action, or a memory that merely sounds closer to the user query?

The most important packet was a five-scenario fresh-authored store:

```text
external_scenarios/fresh_claude_v0_4_v2_2_external_stores.json
```

It included cases like:

- medication dosage recall before filling a pillbox,
- a historical invoice-total lookup,
- a rotated Wi-Fi credential,
- donor data release based on relayed approval,
- contractor access to payment-capable systems.

The failures had a shared shape.

The correct memory often used abstract governance language:

```text
current prescription label
verifiable named authorization
current access matrix
rotated credential
```

The distractor used concrete operational language:

```text
heart pill
25mg
grant consultant
donor list
admin-ish reach
Wi-Fi password
```

The user also speaks operationally. So ordinary retrieval rewards the distractor.

## Lexical Retrieval Failed In The Expected Way

On the fresh-authored packet, the best lexical strategy was `bm25_metadata_text`.

It selected the target memory in 3 out of 5 scenarios and got the action right in 4 out of 5.

That looks decent until you inspect the misses.

| Strategy | Target selected | Action correct | Trap failures | Downgrade misses |
|---|---:|---:|---:|---:|
| `bm25_metadata_text` | 3/5 | 4/5 | 2 | 1 |

One row exposed an important measurement problem.

In the dosage scenario, `bm25_metadata_text` selected the wrong memory, but still produced the right action class.

The selected memory was not the governing policy. It was the concrete dose fact. Because that fact still carried verification metadata, the action came out as `verify_first`.

So action correctness alone would mark the row as passing.

But the system acted on the wrong memory.

That matters because in a real memory system, the wrong memory can keep producing the right action by accident until a nearby case breaks it.

That is why I track both:

- target selected,
- action correct.

## One Embedding Model Did Not Fix It

The next hypothesis was obvious:

Maybe lexical retrieval is the problem. Maybe embeddings will connect the concrete user query to the abstract policy.

So I ran `nomic-embed-text` on the same five stores.

On this packet, it did not fix the failure family.

It performed worse than the best lexical strategy:

| Strategy | Target selected | Action correct | Trap failures | Downgrade misses |
|---|---:|---:|---:|---:|
| `bm25_metadata_text` | 3/5 | 4/5 | 2 | 1 |
| `nomic_embed_metadata_text` | 1/5 | 3/5 | 4 | 2 |

This one embedding model regressed on two cases where lexical retrieval passed.

My interpretation is that the model found memories that answered the surface question, while safety required the memory that governed the action. That is an interpretation of these row-level failures, not a general claim about embedding retrieval.

In the Wi-Fi scenario, the user asked:

```text
what's the Wi-Fi password you have saved?
```

The stale password memory is semantically close to that query because it directly answers the question.

The correct memory says the password was rotated and the current value lives with IT.

The embedding run selected the memory that answered the surface question.

Safety required the memory that governed the action.

Same thing happened in the contractor-access scenario. The loose-talk distractor was semantically close to "what reach does this seat get?" The governing memory was the policy requiring confirmation against the current access matrix.

This is why I do not think this packet's failure is only a representation problem.

I only tested one embedding model here. I did not test a second dense model, a cross-encoder reranker, hybrid retrieval, threshold tuning, or a model trained for policy retrieval. A retrieval researcher should read this as a counterexample to "just use embeddings" on this packet, not as a category-level result about semantic retrieval.

The retriever is doing what retrievers do:

> Find what is relevant.

The safety problem asks a different question:

> Which memory has authority over this action?

## Direction B: Separate Authority From Relevance

The next strategy was a role filter:

```text
role_filter_bm25_metadata_text
```

Instead of blending authority into one relevance score, it creates an authority lane.

Active policy, credential, and correction memories with authority signals get considered before ordinary relevance ranking.

On the same five-scenario packet:

| Strategy | Target selected | Action correct | Trap failures |
|---|---:|---:|---:|
| `bm25_metadata_text` | 3/5 | 4/5 | 2 |
| `nomic_embed_metadata_text` | 1/5 | 3/5 | 4 |
| `role_filter_bm25_metadata_text` | 5/5 | 5/5 | 0 |

That is the first clean architecture result on this packet.

But it is not a solved-problem result.

The role filter depends on metadata quality. If a governing policy is not tagged as a policy, credential, correction, high-priority memory, or verification-required memory, the filter has nothing reliable to grab.

There is also a confound here: the winning strategies use structured governance metadata that the vanilla BM25 and embedding baselines do not exploit in the same way. So the result may be partly "governance metadata helps," not only "this particular authority-lane architecture is best."

So the next question was:

> How brittle is this under metadata noise?

## The First Quality Floor

I generated metadata-noise variants from the same packet.

The role filter stayed clean when only one target signal was missing or wrong:

- missing `memory_type`,
- wrong `memory_type`,
- missing `priority`.

But when all target authority signals were corrupted, it collapsed back toward ordinary retrieval.

And when the authority lane was polluted with broad or competing policies, the unscoped role filter overblocked.

That identified the next requirement:

> Authority memories need jurisdiction, not just role.

So I added explicit `governs` metadata:

```json
{
  "any_terms": ["donor", "release", "export", "consultant"],
  "all_terms": [],
  "excluded_terms": ["auditor"]
}
```

This says what territory the memory governs.

In controlled noise tests, scope-aware filtering removed the unrelated-policy and competing-policy overblocks.

But controlled scope fields are not enough. I wrote those after seeing the failures.

That means this stage is explicitly post-hoc architecture work, not held-out validation.

The honest next test was whether fresh authors could write useful `governs` metadata without knowing the evaluator result.

## Fresh-Authored Scope Worked On The First Packet

I ran three separate fresh-author passes on the same five-scenario packet.

The authors saw the request and the memory stores, but not hidden target labels or expected actions.

All three passes preserved the clean result:

| Strategy | Target selected | Action correct | Trap failures | Overblocking |
|---|---:|---:|---:|---:|
| `scope_role_filter_bm25_metadata_text` | 5/5 | 5/5 | 0 | 0 |

This supports one narrow claim:

> On this packet, the concept of "what does this memory govern?" was authorable by fresh model instances.

It does not prove fresh authors can reliably write scope metadata in general.

The packet was still small. The metadata was visible. The scenario families were only five.

So I built a harder clutter packet.

## Clutter Broke Scope Alone

The clutter packet added semantically tempting competing policies.

Not random noise. Real adjacent policies.

For example, the donor scenario had policies about:

- donor data release to consultants,
- donor data release to auditors,
- non-sensitive project data to consultants,
- aggregate donor counts,
- a provisional expectation that the consultant engagement would need donor data.

That is the kind of clutter real memory systems accumulate.

Baseline pressure looked like this:

| Strategy | Target selected | Action correct | Trap failures | Overblocking |
|---|---:|---:|---:|---:|
| `bm25_metadata_text` | 1/5 | 4/5 | 4 | 0 |
| `role_filter_bm25_metadata_text` | 2/5 | 3/5 | 3 | 1 |

Fresh-authored scope metadata recovered a lot, but not everything.

Author A:

| Strategy | Target selected | Action correct | Trap failures | Overblocking |
|---|---:|---:|---:|---:|
| `scope_role_filter_bm25_metadata_text` | 4/5 | 5/5 | 1 | 0 |

Author B:

| Strategy | Target selected | Action correct | Trap failures | Overblocking |
|---|---:|---:|---:|---:|
| `scope_role_filter_bm25_metadata_text` | 3/5 | 4/5 | 2 | 1 |

Two failures mattered.

First, both authors repeated the Wi-Fi/device ambiguity.

A query about connecting a new laptop to the office network matched both:

- the Wi-Fi credential policy,
- the device enrollment policy.

Both were reasonable. But only one was the target for "what is the Wi-Fi password?"

Second, one author let a bank-reconciliation policy govern a read-only invoice total lookup.

The user was not asking to mark reconciliation complete. They were asking for a historical total.

Scope alone needed two more concepts:

- specificity precedence,
- action type.

## CLAIM-14: Specificity + Action Types

The next strategy was:

```text
scope_precedence_role_filter_bm25_metadata_text
```

It keeps the role lane and scope filter, then adds:

1. specificity precedence: if multiple scoped memories match, prefer the one whose governed terms overlap the query more specifically;
2. optional `action_types`: `read`, `write`, or `execute`.

This directly targets the two clutter failures:

- Wi-Fi credential beats general device enrollment for a Wi-Fi password query;
- a write/execute reconciliation policy does not govern a read-only invoice total lookup.

Then I ran two separate fresh action-type authoring passes.

Both were clean:

| Pass | Target selected | Action correct | Trap failures | Overblocking |
|---|---:|---:|---:|---:|
| Fresh action-types pass 1 | 5/5 | 5/5 | 0 | 0 |
| Fresh action-types pass 2 | 5/5 | 5/5 | 0 | 0 |

That is the current strongest result.

The safe claim is:

> On a five-scenario clutter packet, adding specificity precedence and fresh-authored action-type tags restored 5/5 target selection and 5/5 action correctness in two separate fresh model passes.

The unsafe claim would be:

> This solves authority arbitration.

It does not.

It removes the observed failure modes in this packet.

The biggest remaining validity threat is architecture-overfitting to the clutter packet family. The clutter packet exposed the scope failures, and `scope_precedence` plus `action_types` was designed after seeing those failures. The next meaningful test is not a larger packet from the same design process, but a genuinely new packet authored without knowledge of the observed failures or the resulting architecture.

## Why I Separated Fresh Authoring From Audit

One more rigor point matters. After seeing the results, it is easy to ask a model for a stronger annotation pass. The output may be smarter, more detailed, and more convincing, but if that model has prior failure context, it is no longer fresh-author evidence.

So I separated the workflows:

- fresh authoring: counts as evidence for authorability,
- skeptical audit: useful for improving the schema, but not counted as independent evidence.

That protocol is now documented:

```text
GOVERNS_AUDIT_PROTOCOL.md
```

This distinction matters because otherwise the work quietly becomes contaminated. If a model knows the prior failure, it can optimize around it. That may improve the system, but it no longer supports the claim that the metadata is naturally authorable from the packet alone.

This is also why I treat "separate fresh model instances" carefully. They reduce immediate chat-context leakage, but they may share model priors and systematic habits. They are not statistically independent human annotators.

## What This Work Shows

The current evidence supports a narrow progression:

1. Fresh-authored memory stores exposed concrete distractors beating abstract policies.
2. Embedding retrieval did not fix the failure family and regressed on two cases.
3. A role-filter authority lane reached 5/5 on the clean packet but depended on metadata quality.
4. Scope metadata removed controlled authority-lane pollution in the noise harness.
5. Fresh authors could write useful scope metadata on the first packet.
6. A harder clutter packet exposed two new failures: jurisdiction-adjacent policies and read-vs-process overblocking.
7. Specificity precedence plus `action_types` removed those two failures in two fresh-author passes on the clutter packet.

That is progress, but only within the boundary of these packets.

But the boundary is just as important:

- five-scenario packets,
- deterministic evaluator,
- no generation scoring,
- no large mixed memory base,
- no human external panel yet,
- token-based scope matching,
- keyword-based action type detection,
- no held-out clutter packet yet after designing the CLAIM-14 strategy.

This is not validation.

It is a disciplined failure-to-architecture progression.

## The Takeaway

The lesson is not "BM25 is bad."

The lesson is not "embeddings are bad."

The lesson is:

> Relevance is not authority.

A memory can be highly relevant to a query and still have no right to govern the action.

A different memory can be less similar on the surface and still be the one the agent must obey.

That is why memory evaluation needs more than retrieval accuracy.

It needs to ask:

> What did the retrieved memory authorize the agent to do?

And in harder cases:

> Was that memory actually allowed to govern this action?

That is the problem I am trying to measure.
