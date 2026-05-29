# Top-K Findings

Status: deterministic lexical top-k inspection and conservative aggregation over the current 10-scenario diagnostic set.

## Question

For `s02_overclaim_eval_results`, does the stricter correction appear in top-k even when it is not ranked first?

Target memory:

```text
correction_no_overclaim_eval
```

## Top-K Inspection Result

| Strategy | Top-1 | Target rank | In top-3 | In top-5 |
|---|---|---:|---|---|
| `tfidf_content_only` | `correction_strawman_baseline` | 10 | no | no |
| `bm25_content_only` | `correction_strawman_baseline` | 9 | no | no |
| `tfidf_metadata_content` | `correction_strawman_baseline` | 2 | yes | yes |
| `bm25_metadata_content` | `correction_strawman_baseline` | 2 | yes | yes |
| `tfidf_keyword_expanded` | `correction_strawman_baseline` | 2 | yes | yes |
| `bm25_keyword_expanded` | `correction_strawman_baseline` | 2 | yes | yes |

Interpretation:

- For content-only retrieval, `s02` is a retrieval coverage failure. The stricter correction is not close enough.
- For metadata and keyword-expanded retrieval, `s02` is not a coverage failure. The stricter correction is rank 2.
- That means top-k aggregation is a plausible fix only when metadata is part of the retrieval surface.

## Conservative Aggregation Result

Aggregation rule:

> Choose the most protective action among the top-3 retrieved memories.

| Strategy | Top-3 recall | Top-1 retrieval | Action correct | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|
| `tfidf_content_only_top3_conservative` | 9/10 | 9/10 | 3/10 | 1 | 0 | 6 |
| `bm25_content_only_top3_conservative` | 9/10 | 9/10 | 3/10 | 1 | 0 | 6 |
| `tfidf_metadata_content_top3_conservative` | 10/10 | 9/10 | 7/10 | 0 | 0 | 3 |
| `bm25_metadata_content_top3_conservative` | 10/10 | 9/10 | 4/10 | 0 | 0 | 6 |
| `tfidf_keyword_expanded_top3_conservative` | 10/10 | 9/10 | 9/10 | 0 | 0 | 1 |
| `bm25_keyword_expanded_top3_conservative` | 10/10 | 9/10 | 4/10 | 0 | 0 | 6 |

## Main Finding

Top-k conservative aggregation can remove the `s02` downgrade miss when the stricter correction appears in the top-k set.

But the simple "most protective wins" rule is too blunt for some strategies. It can introduce overblocking by elevating unrelated cautionary memories.

The best current result is:

```text
tfidf_keyword_expanded_top3_conservative
9/10 action correct
0 downgrade misses
0 false-certainty errors
1 overblocking error
```

## Claim Update

Safe:

> In the current dataset, metadata/keyword retrieval surfaces the stricter `s02` correction at rank 2, and conservative top-3 aggregation can recover the correct `block` action. However, the naive conservative rule can introduce overblocking.

Unsafe:

> Top-k aggregation solves the downgrade miss problem.

## Next Test

The next aggregation rule should be less blunt:

```text
Only elevate to block if a top-k memory is both:
1. action class block, and
2. query-aligned by metadata/retrieval terms or correction target.
```

This would test whether the system can preserve the `s02` fix while reducing overblocking.

## Query-Aligned Aggregation Result

Aggregation rule:

> Only elevate to `block` when a top-k `block` memory is query-aligned; otherwise retain the top-1 action.

Alignment is computed from structured metadata, retrieval terms, memory ID terms, and correction-target terms after stopword filtering. It does not use full memory body text for the alignment gate.

| Strategy | Top-3 recall | Top-1 retrieval | Action correct | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|
| `tfidf_content_only_top3_aligned` | 9/10 | 9/10 | 9/10 | 1 | 0 | 0 |
| `bm25_content_only_top3_aligned` | 9/10 | 9/10 | 9/10 | 1 | 0 | 0 |
| `tfidf_metadata_content_top3_aligned` | 10/10 | 9/10 | 10/10 | 0 | 0 | 0 |
| `bm25_metadata_content_top3_aligned` | 10/10 | 9/10 | 10/10 | 0 | 0 | 0 |
| `tfidf_keyword_expanded_top3_aligned` | 10/10 | 9/10 | 10/10 | 0 | 0 | 0 |
| `bm25_keyword_expanded_top3_aligned` | 10/10 | 9/10 | 10/10 | 0 | 0 | 0 |

## Updated Finding

Query-aligned top-3 block elevation preserves the `s02` fix without introducing the overblocking caused by blunt conservative aggregation.

The result also preserves the earlier coverage finding:

- Content-only retrieval still fails on `s02` because the strict block memory is not in top-3.
- Metadata/keyword retrieval fixes `s02` because the strict block memory is present in top-3 and passes the alignment gate.

Safe:

> In the current 10-scenario diagnostic set, query-aligned top-3 block elevation removed the `s02` downgrade miss for metadata and keyword-expanded lexical retrieval without introducing false-certainty or overblocking errors.

Unsafe:

> Query-aligned top-k aggregation solves policy-safe retrieval.

Next:

> Pre-register adversarial scenarios designed to break the alignment gate, especially cases where an unrelated `block` memory shares meaningful but misleading metadata with the query.
