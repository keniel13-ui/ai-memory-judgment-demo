# Memory Store Findings

Status: first scenario-local memory-store harness result. Not benchmark-grade.

## Why This Exists

The original evaluator uses one shared memory pool. That is useful for the current AI-memory research artifact, but it becomes awkward for external-domain scenarios like finance, legal, health, customer support, and code deployment.

The memory-store evaluator lets each scenario carry its own local target/distractor memory set.

That tests a sharper question:

> Given a query and an intentionally adversarial local memory set, does retrieval select the memory that is safe to act on, or a tempting distractor?

## Input

Scenario file:

```text
external_scenarios/fresh_claude_v0_4_v2_top5.json
```

Authorship:

- Query/scenario concepts: fresh Claude conversation using only `EXTERNAL_SCENARIO_REQUEST.md`
- Scenario-local memory stores: internally authored by Codex from the enhanced scenario packet

This distinction matters. The result is not fully externally authored because the memory stores were written internally.

## First Result

| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking |
|---|---:|---:|---:|---:|---:|---:|
| `tfidf_text` | 5/5 | 5/5 | 0 | 0 | 0 | 0 |
| `tfidf_metadata_text` | 5/5 | 5/5 | 0 | 0 | 0 | 0 |
| `bm25_text` | 5/5 | 5/5 | 0 | 0 | 0 | 0 |
| `bm25_metadata_text` | 5/5 | 5/5 | 0 | 0 | 0 | 0 |

## Interpretation

The harness works and the first five scenario-local memory stores are solvable by both TF-IDF and BM25.

Do not overstate this. Because the memory stores were authored internally, the clean result mainly verifies the harness and the scenario-store format.

The stronger future test is to have an outside reviewer or fresh model write both:

- the query, and
- the target/distractor memory store.

## Positive-Control Failure

Before adding more stores, the harness was tested against an intentionally planted failure:

```text
external_scenarios/memory_store_positive_control.json
```

The positive-control fixture contains a stale pricing distractor designed to outrank the target memory. The target says pricing must be verified against the current finance-approved rate sheet. The distractor gives a concrete internal planning price and repeats the query vocabulary.

Result:

| Strategy | Target selected | Action correct | Trap failures | FC errors |
|---|---:|---:|---:|---:|
| `tfidf_text` | 0/1 | 0/1 | 1 | 1 |
| `tfidf_metadata_text` | 0/1 | 0/1 | 1 | 1 |
| `bm25_text` | 0/1 | 0/1 | 1 | 1 |
| `bm25_metadata_text` | 0/1 | 0/1 | 1 | 1 |

Interpretation:

The harness can detect a planted retrieval trap and classify the downstream result as a false-certainty error. This does not make the clean 5/5 result stronger by itself, but it does show the evaluator is sensitive to the failure type it is supposed to catch.

## Safe Claim

> A scenario-local target/distractor evaluator now exists. On the first five fresh-Claude scenarios with internally authored memory stores, TF-IDF and BM25 selected the target memory and correct action in all five cases.

## Unsafe Claim

> The framework passed an external-domain benchmark.

## Next Step

Add 5 more scenario-local stores, but make at least one of these true:

- memory stores are authored by a fresh model with no repo context,
- distractors are made harder by a separate reviewer,
- the target/distractor labels are hidden during retrieval tuning,
- at least one expected failure is intentionally planted as a positive control.
