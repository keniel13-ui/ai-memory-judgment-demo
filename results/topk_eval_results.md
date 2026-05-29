# Top-k Recall and Conservative Policy Aggregation Results

**Experiment question:** For the s02 downgrade miss, does `correction_no_overclaim_eval`
(the `block`-level correction) appear in top-2, top-3, or top-5 results?
If yes: does conservative policy aggregation (take the most restrictive action
across all top-k retrieved memories) fix the downgrade miss?

Memory pool: 21 memories. Scenarios: 10.

---

## s02 Deep Dive

s02 is the only case where top-1 retrieval misses the correct memory across all
6 lexical strategies. All strategies retrieve `correction_strawman_baseline` (warn)
instead of `correction_no_overclaim_eval` (block).

| Strategy | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 | In top-3? | In top-5? |
|---|---|---|---|---|---|---|---|
| tfidf_content_only | corr_strawman_baseline | access_policy_rules | state_agent_dashboard | corr_external_rewrite_not_authorship | public_post_live_url | no | no |
| tfidf_metadata_content | corr_strawman_baseline | corr_no_overclaim | current_system_overview | access_policy_rules | state_agent_dashboard | **yes** | **yes** |
| tfidf_keyword_expanded | corr_strawman_baseline | corr_no_overclaim | current_system_overview | access_policy_rules | corr_external_rewrite_not_authorship | **yes** | **yes** |
| bm25_content_only | corr_strawman_baseline | access_policy_rules | corr_external_rewrite_not_authorship | state_agent_dashboard | public_post_live_url | no | no |
| bm25_metadata_content | corr_strawman_baseline | corr_no_overclaim | access_policy_rules | current_system_overview | corr_external_rewrite_not_authorship | **yes** | **yes** |
| bm25_keyword_expanded | corr_strawman_baseline | corr_no_overclaim | current_system_overview | access_policy_rules | corr_external_rewrite_not_authorship | **yes** | **yes** |

## Conservative Policy Aggregation — s02 Action at Each k

If we take the most restrictive action across top-k retrieved memories,
does the output change from `warn` to `block` for s02?

| Strategy | top-1 | top-2 | top-3 | top-5 |
|---|---|---|---|---|
| tfidf_content_only | warn | warn | warn | warn |
| tfidf_metadata_content | warn | **block** | **block** | **block** |
| tfidf_keyword_expanded | warn | **block** | **block** | **block** |
| bm25_content_only | warn | warn | warn | warn |
| bm25_metadata_content | warn | **block** | **block** | **block** |
| bm25_keyword_expanded | warn | **block** | **block** | **block** |

---

## Recall@k Summary (All Scenarios)

How many scenarios have the correct memory in top-k? (out of 10)

| Strategy | Recall@1 | Recall@2 | Recall@3 | Recall@5 |
|---|---|---|---|---|
| tfidf_content_only | 9/10 | 9/10 | 9/10 | 9/10 |
| tfidf_metadata_content | 9/10 | 10/10 | 10/10 | 10/10 |
| tfidf_keyword_expanded | 9/10 | 10/10 | 10/10 | 10/10 |
| bm25_content_only | 9/10 | 9/10 | 9/10 | 9/10 |
| bm25_metadata_content | 9/10 | 10/10 | 10/10 | 10/10 |
| bm25_keyword_expanded | 9/10 | 10/10 | 10/10 | 10/10 |

---

## Conservative Aggregation — Action Accuracy at Each k

Using conservative (most restrictive) policy across top-k, how many scenarios
produce the correct action?

| Strategy | @k=1 | @k=2 | @k=3 | @k=5 |
|---|---|---|---|---|
| tfidf_content_only | 9/10 | 6/10 | 3/10 | 1/10 |
| tfidf_metadata_content | 9/10 | 7/10 | 7/10 | 2/10 |
| tfidf_keyword_expanded | 9/10 | 9/10 | 9/10 | 2/10 |
| bm25_content_only | 9/10 | 5/10 | 3/10 | 1/10 |
| bm25_metadata_content | 9/10 | 7/10 | 4/10 | 2/10 |
| bm25_keyword_expanded | 9/10 | 9/10 | 4/10 | 1/10 |

---

## Interpretation

- If `correction_no_overclaim_eval` appears in top-k for s02: the failure is a **ranking problem**, not a coverage problem.
  Conservative aggregation can fix the downgrade miss architecturally.
- If it does not appear even in top-5: the failure is a **coverage problem**.
  Lexical retrieval cannot surface the correct memory at any rank.
  Only semantic retrieval (embedding-based) can solve it.

## Limitations

- Conservative aggregation increases overblocking risk: taking the most restrictive
  action across top-k will sometimes over-restrict on scenarios where top-1 was already correct.
- The overblocking tradeoff must be measured, not assumed acceptable.
- This experiment is lexical-only. Embedding top-k results are not included here.
