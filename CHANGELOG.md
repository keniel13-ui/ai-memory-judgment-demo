# Changelog

## Public demo — V0.3 (2026-05-26)

First public release. Sanitized from a private diagnostic harness.

**What changed from the private V0.3:**
- All 21 memory objects rewritten as generic long-running-agent examples
- Scenario labels updated to match the sanitized memory pool
- Private project context removed; no project names, handles, or identifiers remain
- Evaluator code is identical in logic to the private version

**Known consequence of sanitization:**
The public memory objects are simpler than the private ones. Sanitization changed retrieval behavior. The private V0.3 results were:

| Strategy | Retrieval | Action correct |
|---|---:|---:|
| content_only | 4/10 | 6/10 |
| metadata_content | 6/10 | 9/10 |
| keyword_expanded | 7/10 | 9/10 |

The public results are 9/10 across all three strategies. The three-way tie is a consequence of sanitization, not a correction to the private results. The private table is the one referenced in the article.

**What is preserved:**
- The six-file memory structure
- The three retrieval strategies (content_only, metadata_content, keyword_expanded)
- The action-class scoring method
- The retrieval failure taxonomy (FC error, downgrade miss, benign miss, overblocking)
- The semantic hard case: s02 still produces a block→warn downgrade across all three strategies

---

## Private V0.3 (2026-05-26)

Added three-strategy comparison (content_only, metadata_content, keyword_expanded) over the full private memory pool. Added `retrieval_terms` field to all memory objects. Introduced `downgrade_miss` and `benign_retrieval_miss` as distinct scoring dimensions. Main finding: zero false-certainty errors across all strategies; one persistent downgrade miss (s02) demonstrating "right neighborhood, wrong severity."

## Private V0.2 (2026-05-26)

Added deterministic TF-IDF retrieval layer. Removed preselected memory IDs from scenarios; evaluator now selects top-1 memory. Introduced `correct_memory_id` as retrieval ground truth in scenario files.

## Private V0.1 (2026-05-26)

Initial six-file memory framework demo with preselected memory IDs and deterministic policy evaluation. No retrieval layer.
