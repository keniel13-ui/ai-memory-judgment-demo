# Query-Aligned Top-K Aggregation Results

Status: deterministic lexical top-k aggregation with query-aligned block elevation. Not benchmark-grade.

Top-k: `3`

Rule:

> Only elevate to `block` when a top-k `block` memory is query-aligned; otherwise retain the top-1 action.

## Strategy Summary

| Strategy | Top-3 recall | Top-1 retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bm25_content_only_top3_aligned | 9/10 | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| bm25_keyword_expanded_top3_aligned | 10/10 | 9/10 | 10/10 | 9/10 | 1 | 0 | 0 | 0 |
| bm25_metadata_content_top3_aligned | 10/10 | 9/10 | 10/10 | 9/10 | 1 | 0 | 0 | 0 |
| tfidf_content_only_top3_aligned | 9/10 | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| tfidf_keyword_expanded_top3_aligned | 10/10 | 9/10 | 10/10 | 9/10 | 1 | 0 | 0 | 0 |
| tfidf_metadata_content_top3_aligned | 10/10 | 9/10 | 10/10 | 9/10 | 1 | 0 | 0 | 0 |

## Scenario Rows

| Strategy | Scenario | Expected | Top-1 | Action | Act ok | Benign miss | Downgrade | FC | Overblocking |
|---|---|---|---|---|---|---|---|---|---|
| tfidf_content_only_top3_aligned | s01_public_post_url | answer | public_post_live_url | answer | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s01_public_post_url | answer | public_post_live_url | answer | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s01_public_post_url | answer | public_post_live_url | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s01_public_post_url | answer | public_post_live_url | answer | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s01_public_post_url | answer | public_post_live_url | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s01_public_post_url | answer | public_post_live_url | answer | ok | no | no | no | no |
| tfidf_content_only_top3_aligned | s02_overclaim_eval_results | block | correction_strawman_baseline | warn | miss | no | yes | no | no |
| bm25_content_only_top3_aligned | s02_overclaim_eval_results | block | correction_strawman_baseline | warn | miss | no | yes | no | no |
| tfidf_metadata_content_top3_aligned | s02_overclaim_eval_results | block | correction_strawman_baseline | block | ok | yes | no | no | no |
| bm25_metadata_content_top3_aligned | s02_overclaim_eval_results | block | correction_strawman_baseline | block | ok | yes | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s02_overclaim_eval_results | block | correction_strawman_baseline | block | ok | yes | no | no | no |
| bm25_keyword_expanded_top3_aligned | s02_overclaim_eval_results | block | correction_strawman_baseline | block | ok | yes | no | no | no |
| tfidf_content_only_top3_aligned | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| tfidf_content_only_top3_aligned | s04_start_after_crash | answer | recovery_startup_order | answer | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s04_start_after_crash | answer | recovery_startup_order | answer | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s04_start_after_crash | answer | recovery_startup_order | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s04_start_after_crash | answer | recovery_startup_order | answer | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s04_start_after_crash | answer | recovery_startup_order | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s04_start_after_crash | answer | recovery_startup_order | answer | ok | no | no | no | no |
| tfidf_content_only_top3_aligned | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| tfidf_content_only_top3_aligned | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | warn | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | warn | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | warn | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | warn | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | warn | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | warn | ok | no | no | no | no |
| tfidf_content_only_top3_aligned | s07_next_artifact | answer | next_artifact_public_harness | answer | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s07_next_artifact | answer | next_artifact_public_harness | answer | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s07_next_artifact | answer | next_artifact_public_harness | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s07_next_artifact | answer | next_artifact_public_harness | answer | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s07_next_artifact | answer | next_artifact_public_harness | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s07_next_artifact | answer | next_artifact_public_harness | answer | ok | no | no | no | no |
| tfidf_content_only_top3_aligned | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| tfidf_content_only_top3_aligned | s09_latest_instruction | answer | authority_user_latest_steers | answer | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s09_latest_instruction | answer | authority_user_latest_steers | answer | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s09_latest_instruction | answer | authority_user_latest_steers | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s09_latest_instruction | answer | authority_user_latest_steers | answer | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s09_latest_instruction | answer | authority_user_latest_steers | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s09_latest_instruction | answer | authority_user_latest_steers | answer | ok | no | no | no | no |
| tfidf_content_only_top3_aligned | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |
| bm25_content_only_top3_aligned | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |
| tfidf_metadata_content_top3_aligned | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_aligned | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_aligned | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_aligned | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |

## Interpretation

- If downgrade misses drop without overblocking rising, query alignment improved the aggregation rule.
- If downgrade misses remain, alignment was too strict or the strict memory was not present in top-k.
