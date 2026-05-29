# Top-K Aggregation Results

Status: deterministic lexical top-k conservative aggregation. Not benchmark-grade.

Top-k: `3`

Rule:

> Choose the most protective action among the top-k retrieved memories.

## Strategy Summary

| Strategy | Top-3 recall | Top-1 retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bm25_content_only_top3_conservative | 9/10 | 9/10 | 3/10 | 3/10 | 0 | 1 | 0 | 6 |
| bm25_keyword_expanded_top3_conservative | 10/10 | 9/10 | 4/10 | 3/10 | 1 | 0 | 0 | 6 |
| bm25_metadata_content_top3_conservative | 10/10 | 9/10 | 4/10 | 3/10 | 1 | 0 | 0 | 6 |
| tfidf_content_only_top3_conservative | 9/10 | 9/10 | 3/10 | 3/10 | 0 | 1 | 0 | 6 |
| tfidf_keyword_expanded_top3_conservative | 10/10 | 9/10 | 9/10 | 8/10 | 1 | 0 | 0 | 1 |
| tfidf_metadata_content_top3_conservative | 10/10 | 9/10 | 7/10 | 6/10 | 1 | 0 | 0 | 3 |

## Scenario Rows

| Strategy | Scenario | Expected | Top-1 | Action | Act ok | Benign miss | Downgrade | FC | Overblocking |
|---|---|---|---|---|---|---|---|---|---|
| tfidf_content_only_top3_conservative | s01_public_post_url | answer | public_post_live_url | warn | miss | no | no | no | yes |
| bm25_content_only_top3_conservative | s01_public_post_url | answer | public_post_live_url | warn | miss | no | no | no | yes |
| tfidf_metadata_content_top3_conservative | s01_public_post_url | answer | public_post_live_url | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_conservative | s01_public_post_url | answer | public_post_live_url | warn | miss | no | no | no | yes |
| tfidf_keyword_expanded_top3_conservative | s01_public_post_url | answer | public_post_live_url | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_conservative | s01_public_post_url | answer | public_post_live_url | warn | miss | no | no | no | yes |
| tfidf_content_only_top3_conservative | s02_overclaim_eval_results | block | correction_strawman_baseline | warn | miss | no | yes | no | no |
| bm25_content_only_top3_conservative | s02_overclaim_eval_results | block | correction_strawman_baseline | warn | miss | no | yes | no | no |
| tfidf_metadata_content_top3_conservative | s02_overclaim_eval_results | block | correction_strawman_baseline | block | ok | yes | no | no | no |
| bm25_metadata_content_top3_conservative | s02_overclaim_eval_results | block | correction_strawman_baseline | block | ok | yes | no | no | no |
| tfidf_keyword_expanded_top3_conservative | s02_overclaim_eval_results | block | correction_strawman_baseline | block | ok | yes | no | no | no |
| bm25_keyword_expanded_top3_conservative | s02_overclaim_eval_results | block | correction_strawman_baseline | block | ok | yes | no | no | no |
| tfidf_content_only_top3_conservative | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| bm25_content_only_top3_conservative | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| tfidf_metadata_content_top3_conservative | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| bm25_metadata_content_top3_conservative | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_conservative | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| bm25_keyword_expanded_top3_conservative | s03_public_private_claim | verify_first | uncertainty_public_claims | verify_first | ok | no | no | no | no |
| tfidf_content_only_top3_conservative | s04_start_after_crash | answer | recovery_startup_order | warn | miss | no | no | no | yes |
| bm25_content_only_top3_conservative | s04_start_after_crash | answer | recovery_startup_order | warn | miss | no | no | no | yes |
| tfidf_metadata_content_top3_conservative | s04_start_after_crash | answer | recovery_startup_order | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_conservative | s04_start_after_crash | answer | recovery_startup_order | warn | miss | no | no | no | yes |
| tfidf_keyword_expanded_top3_conservative | s04_start_after_crash | answer | recovery_startup_order | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_conservative | s04_start_after_crash | answer | recovery_startup_order | warn | miss | no | no | no | yes |
| tfidf_content_only_top3_conservative | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| bm25_content_only_top3_conservative | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| tfidf_metadata_content_top3_conservative | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| bm25_metadata_content_top3_conservative | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_conservative | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_conservative | s05_live_file_conflict | answer | authority_live_files_first | answer | ok | no | no | no | no |
| tfidf_content_only_top3_conservative | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | verify_first | miss | no | no | no | yes |
| bm25_content_only_top3_conservative | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | verify_first | miss | no | no | no | yes |
| tfidf_metadata_content_top3_conservative | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | warn | ok | no | no | no | no |
| bm25_metadata_content_top3_conservative | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | verify_first | miss | no | no | no | yes |
| tfidf_keyword_expanded_top3_conservative | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | warn | ok | no | no | no | no |
| bm25_keyword_expanded_top3_conservative | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | verify_first | miss | no | no | no | yes |
| tfidf_content_only_top3_conservative | s07_next_artifact | answer | next_artifact_public_harness | warn | miss | no | no | no | yes |
| bm25_content_only_top3_conservative | s07_next_artifact | answer | next_artifact_public_harness | warn | miss | no | no | no | yes |
| tfidf_metadata_content_top3_conservative | s07_next_artifact | answer | next_artifact_public_harness | warn | miss | no | no | no | yes |
| bm25_metadata_content_top3_conservative | s07_next_artifact | answer | next_artifact_public_harness | warn | miss | no | no | no | yes |
| tfidf_keyword_expanded_top3_conservative | s07_next_artifact | answer | next_artifact_public_harness | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_conservative | s07_next_artifact | answer | next_artifact_public_harness | warn | miss | no | no | no | yes |
| tfidf_content_only_top3_conservative | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| bm25_content_only_top3_conservative | s08_speculative_theory | verify_first | uncertainty_speculative_theory | block | miss | no | no | no | yes |
| tfidf_metadata_content_top3_conservative | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| bm25_metadata_content_top3_conservative | s08_speculative_theory | verify_first | uncertainty_speculative_theory | block | miss | no | no | no | yes |
| tfidf_keyword_expanded_top3_conservative | s08_speculative_theory | verify_first | uncertainty_speculative_theory | verify_first | ok | no | no | no | no |
| bm25_keyword_expanded_top3_conservative | s08_speculative_theory | verify_first | uncertainty_speculative_theory | block | miss | no | no | no | yes |
| tfidf_content_only_top3_conservative | s09_latest_instruction | answer | authority_user_latest_steers | warn | miss | no | no | no | yes |
| bm25_content_only_top3_conservative | s09_latest_instruction | answer | authority_user_latest_steers | warn | miss | no | no | no | yes |
| tfidf_metadata_content_top3_conservative | s09_latest_instruction | answer | authority_user_latest_steers | warn | miss | no | no | no | yes |
| bm25_metadata_content_top3_conservative | s09_latest_instruction | answer | authority_user_latest_steers | warn | miss | no | no | no | yes |
| tfidf_keyword_expanded_top3_conservative | s09_latest_instruction | answer | authority_user_latest_steers | warn | miss | no | no | no | yes |
| bm25_keyword_expanded_top3_conservative | s09_latest_instruction | answer | authority_user_latest_steers | warn | miss | no | no | no | yes |
| tfidf_content_only_top3_conservative | s10_policy_definition | answer | access_policy_rules | warn | miss | no | no | no | yes |
| bm25_content_only_top3_conservative | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |
| tfidf_metadata_content_top3_conservative | s10_policy_definition | answer | access_policy_rules | warn | miss | no | no | no | yes |
| bm25_metadata_content_top3_conservative | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |
| tfidf_keyword_expanded_top3_conservative | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |
| bm25_keyword_expanded_top3_conservative | s10_policy_definition | answer | access_policy_rules | answer | ok | no | no | no | no |

## Interpretation

- If downgrade misses drop but overblocking rises, the rule is protective but too blunt.
- If downgrade misses remain, top-k did not surface the stricter memory or aggregation failed to select it.
