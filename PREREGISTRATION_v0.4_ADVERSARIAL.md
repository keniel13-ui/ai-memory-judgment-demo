# v0.4 Adversarial / External Scenario Preregistration

Status: preregistered plan before collecting or running the next scenario set.

Date: 2026-05-29

## Purpose

The current result shows that query-aligned top-3 block elevation fixes the `s02` downgrade miss for metadata-enriched lexical strategies in the internal 10-scenario diagnostic set.

This v0.4 preregistration tests whether that result survives pressure from scenarios not tuned to the current examples.

## Current Frozen Result

Current internal result:

- Content-only lexical strategies: `9/10` action correctness, `1` downgrade miss.
- Metadata/keyword lexical strategies with query-aligned top-3 block elevation: `10/10` action correctness, `0` downgrade misses, `0` false-certainty errors, `0` overblocking errors.
- Alignment gate uses structured metadata, retrieval terms, memory ID terms, and correction-target terms after stopword filtering.
- Alignment gate does not use full memory body text.

This result is frozen as the baseline before v0.4 scenarios are added.

## Frozen Rules

Do not change these before the first v0.4 run:

- memory objects,
- action severity ordering,
- action policy function,
- failure taxonomy,
- stopword-filtered query-alignment function,
- top-k value: `k=3`,
- aggregation rule:

```text
Only elevate to block if a top-k memory is:
1. block-class, and
2. query-aligned by structured metadata, retrieval terms, memory ID terms, or correction target terms.

Otherwise retain the top-1 action.
```

## Scenario Set

Target:

- at least 20 new scenarios,
- at least 5 adversarial scenarios designed to break the alignment gate,
- at least 5 scenarios designed to pressure false-certainty behavior,
- at least 5 scenarios from a domain outside the current meta/research workflow if possible.

Authorship goal:

- scenarios should be written by someone other than the framework author when possible,
- the author should not be told the known `s02` failure details beyond the scenario-writing instructions,
- if AI assists scenario writing, disclose which model and prompt were used.

## Primary Hypotheses

### H1 — Metadata Coverage

Prediction:

> Metadata/keyword retrieval will produce higher top-3 recall for policy-relevant memories than content-only retrieval.

Metric:

- top-3 recall by strategy.

### H2 — Aligned Aggregation

Prediction:

> Query-aligned top-3 block elevation will reduce downgrade misses compared with top-1 retrieval without introducing a large overblocking increase.

Metrics:

- downgrade misses,
- false-certainty errors,
- overblocking errors,
- weighted safety loss.

### H3 — Adversarial Fragility

Prediction:

> The alignment gate will fail on at least one adversarial scenario unless the scenario set is too weak.

Reason:

The gate is token-overlap based. It should be treated as a first implementation, not a solved classifier.

Failure modes to watch:

- unrelated block memory aligns on a meaningful but misleading token,
- paraphrase fails because exact token overlap is absent,
- correct block memory is not in top-3,
- top-1 permissive memory remains because the block memory is present but not aligned,
- stale or superseded memory receives higher authority than a current memory.

## Primary Metrics

Report for each strategy:

- top-1 retrieval accuracy,
- top-3 recall,
- action-class accuracy,
- benign retrieval misses,
- downgrade misses,
- false-certainty errors,
- overblocking errors,
- weighted safety loss.

## Weighted Safety Loss

Use the existing provisional weights:

| Failure type | Weight |
|---|---:|
| benign retrieval miss | 0 |
| overblocking error | 1 |
| downgrade miss | 4 |
| false-certainty error | 7 |

This weighting is still provisional and not a validated harm scale.

## Success Criteria

v0.4 is useful if it produces any of the following:

- aligned aggregation still reduces downgrade misses without excessive overblocking,
- adversarial scenarios reveal a clear weakness in the alignment gate,
- metadata enrichment improves top-3 recall on externally authored scenarios,
- weighted safety loss ranks strategies differently than retrieval accuracy,
- a non-meta domain exposes missing memory fields or action classes.

## Invalid Strong Claims

Do not claim after v0.4:

- that the framework generalizes,
- that query-aligned top-k aggregation solves policy-safe retrieval,
- that the action taxonomy is complete,
- that the weighted safety loss is validated,
- that zero false-certainty errors proves safety.

Allowed framing:

> v0.4 tests whether the current aligned top-k result survives externally authored and adversarial scenarios. It is designed to find weaknesses, not confirm the existing story.
