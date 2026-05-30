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

## Fresh-Authored Store Result

After the internal positive control, a fresh Claude conversation with no repo context authored a stronger v2.2 packet:

```text
external_scenarios/fresh_claude_v0_4_v2_2_external_stores.json
```

This packet includes:

- fresh query/scenario design,
- fresh target and distractor memory stores,
- `expected_fired_role`,
- `must_not_fire_roles`,
- trap mechanics,
- failure costs,
- recency ranks.

Result:

| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking |
|---|---:|---:|---:|---:|---:|---:|
| `tfidf_text` | 2/5 | 2/5 | 3 | 1 | 2 | 0 |
| `tfidf_metadata_text` | 2/5 | 2/5 | 3 | 1 | 2 | 0 |
| `bm25_text` | 3/5 | 3/5 | 2 | 1 | 1 | 0 |
| `bm25_metadata_text` | 3/5 | 4/5 | 2 | 0 | 1 | 0 |

Key read:

- Fresh-authored stores exposed failures that internally authored stores did not.
- BM25 with metadata performed best by action correctness (`4/5`) and avoided false-certainty errors, but still acted on two `should_not_fire` distractors.
- The dosage scenario shows why action correctness alone is incomplete: `bm25_metadata_text` selected a distractor but still produced `verify_first`, so the action was correct while the memory acted on was not.
- The ambiguous-authority scenario remained hard across all strategies. The retrievers repeatedly selected the expectation/precedent memory instead of the critical authorization policy.

This is the strongest v0.4 result so far because it separates scenario/store authorship from Codex and produces real failures.

## Safe Claim

> A scenario-local target/distractor evaluator now exists. On the first five fresh-Claude scenarios with internally authored memory stores, TF-IDF and BM25 selected the target memory and correct action in all five cases.

> On a separate fresh-authored v2.2 store packet, lexical retrieval exposed multiple trap failures. The best strategy (`bm25_metadata_text`) reached 4/5 action correctness but still selected `should_not_fire` distractors in 2/5 cases.

## Unsafe Claim

> The framework passed an external-domain benchmark.

## Next Step

Next, do not tune the current stores yet. First inspect the two persistent failure families:

- dosage: correct action can mask wrong-memory selection,
- ambiguous authority: expectation/precedent memories outrank authorization policy.

Then add 5 more scenario-local stores, but make at least one of these true:

- memory stores are authored by a fresh model with no repo context,
- distractors are made harder by a separate reviewer,
- the target/distractor labels are hidden during retrieval tuning,
- at least one expected failure is intentionally planted as a positive control.
