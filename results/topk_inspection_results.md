# Top-K Inspection Results

Status: deterministic lexical top-k inspection for the s02 downgrade miss.

Scenario: `s02_overclaim_eval_results`
Target memory: `correction_no_overclaim_eval`

## Summary

| Strategy | Top-1 | Target rank | In top-3 | In top-5 |
|---|---|---:|---|---|
| tfidf_content_only | correction_strawman_baseline | 10 | no | no |
| bm25_content_only | correction_strawman_baseline | 9 | no | no |
| tfidf_metadata_content | correction_strawman_baseline | 2 | yes | yes |
| bm25_metadata_content | correction_strawman_baseline | 2 | yes | yes |
| tfidf_keyword_expanded | correction_strawman_baseline | 2 | yes | yes |
| bm25_keyword_expanded | correction_strawman_baseline | 2 | yes | yes |

## Top-5 Rows

| Strategy | Rank | Memory | Score | Target |
|---|---:|---|---:|---|
| tfidf_content_only | 1 | correction_strawman_baseline | 0.469791 | no |
| tfidf_content_only | 2 | access_policy_rules | 0.171271 | no |
| tfidf_content_only | 3 | state_agent_dashboard | 0.111599 | no |
| tfidf_content_only | 4 | correction_external_rewrite_not_authorship | 0.097882 | no |
| tfidf_content_only | 5 | public_post_live_url | 0.08868 | no |
| bm25_content_only | 1 | correction_strawman_baseline | 8.280414 | no |
| bm25_content_only | 2 | access_policy_rules | 3.536746 | no |
| bm25_content_only | 3 | correction_external_rewrite_not_authorship | 1.956721 | no |
| bm25_content_only | 4 | state_agent_dashboard | 1.790865 | no |
| bm25_content_only | 5 | public_post_live_url | 1.756142 | no |
| tfidf_metadata_content | 1 | correction_strawman_baseline | 0.31176 | no |
| tfidf_metadata_content | 2 | correction_no_overclaim_eval | 0.139131 | yes |
| tfidf_metadata_content | 3 | current_system_overview | 0.097548 | no |
| tfidf_metadata_content | 4 | access_policy_rules | 0.094094 | no |
| tfidf_metadata_content | 5 | state_agent_dashboard | 0.076877 | no |
| bm25_metadata_content | 1 | correction_strawman_baseline | 8.00324 | no |
| bm25_metadata_content | 2 | correction_no_overclaim_eval | 4.021786 | yes |
| bm25_metadata_content | 3 | access_policy_rules | 3.251301 | no |
| bm25_metadata_content | 4 | current_system_overview | 2.691987 | no |
| bm25_metadata_content | 5 | correction_external_rewrite_not_authorship | 2.01413 | no |
| tfidf_keyword_expanded | 1 | correction_strawman_baseline | 0.239351 | no |
| tfidf_keyword_expanded | 2 | correction_no_overclaim_eval | 0.114061 | yes |
| tfidf_keyword_expanded | 3 | current_system_overview | 0.104296 | no |
| tfidf_keyword_expanded | 4 | access_policy_rules | 0.095086 | no |
| tfidf_keyword_expanded | 5 | correction_external_rewrite_not_authorship | 0.058782 | no |
| bm25_keyword_expanded | 1 | correction_strawman_baseline | 7.958077 | no |
| bm25_keyword_expanded | 2 | correction_no_overclaim_eval | 4.126131 | yes |
| bm25_keyword_expanded | 3 | current_system_overview | 3.790044 | no |
| bm25_keyword_expanded | 4 | access_policy_rules | 3.455799 | no |
| bm25_keyword_expanded | 5 | correction_external_rewrite_not_authorship | 2.071721 | no |

## Interpretation Rule

- If the target appears in top-k, conservative aggregation can be tested.
- If the target does not appear in top-k, the miss is a retrieval coverage failure for that strategy.
