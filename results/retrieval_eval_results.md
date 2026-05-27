# Retrieval Eval Results

Status: sanitized deterministic retrieval-strategy demo. Not benchmark-grade.

Memory pool: 21 memories across 6 files.

## Strategy Summary

| Strategy | Retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|---:|
| tfidf_content_only | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| tfidf_metadata_content | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| tfidf_keyword_expanded | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| bm25_content_only | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| bm25_metadata_content | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |
| bm25_keyword_expanded | 9/10 | 9/10 | 9/10 | 0 | 1 | 0 | 0 |

## Scenario Rows

| Strategy | Scenario | Expected | Retrieved | Ret ok | Action | Act ok | E2E | Benign miss | Downgrade | FC |
|---|---|---|---|---|---|---|---|---|---|---|
| tfidf_content_only | s01_public_post_url | answer | public_post_live_url | ok | answer | ok | ok | no | no | no |
| tfidf_content_only | s02_overclaim_eval_results | block | correction_strawman_baseline | miss | warn | miss | miss | no | yes | no |
| tfidf_content_only | s03_public_private_claim | verify_first | uncertainty_public_claims | ok | verify_first | ok | ok | no | no | no |
| tfidf_content_only | s04_start_after_crash | answer | recovery_startup_order | ok | answer | ok | ok | no | no | no |
| tfidf_content_only | s05_live_file_conflict | answer | authority_live_files_first | ok | answer | ok | ok | no | no | no |
| tfidf_content_only | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| tfidf_content_only | s07_next_artifact | answer | next_artifact_public_harness | ok | answer | ok | ok | no | no | no |
| tfidf_content_only | s08_speculative_theory | verify_first | uncertainty_speculative_theory | ok | verify_first | ok | ok | no | no | no |
| tfidf_content_only | s09_latest_instruction | answer | authority_user_latest_steers | ok | answer | ok | ok | no | no | no |
| tfidf_content_only | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |
| tfidf_metadata_content | s01_public_post_url | answer | public_post_live_url | ok | answer | ok | ok | no | no | no |
| tfidf_metadata_content | s02_overclaim_eval_results | block | correction_strawman_baseline | miss | warn | miss | miss | no | yes | no |
| tfidf_metadata_content | s03_public_private_claim | verify_first | uncertainty_public_claims | ok | verify_first | ok | ok | no | no | no |
| tfidf_metadata_content | s04_start_after_crash | answer | recovery_startup_order | ok | answer | ok | ok | no | no | no |
| tfidf_metadata_content | s05_live_file_conflict | answer | authority_live_files_first | ok | answer | ok | ok | no | no | no |
| tfidf_metadata_content | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| tfidf_metadata_content | s07_next_artifact | answer | next_artifact_public_harness | ok | answer | ok | ok | no | no | no |
| tfidf_metadata_content | s08_speculative_theory | verify_first | uncertainty_speculative_theory | ok | verify_first | ok | ok | no | no | no |
| tfidf_metadata_content | s09_latest_instruction | answer | authority_user_latest_steers | ok | answer | ok | ok | no | no | no |
| tfidf_metadata_content | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |
| tfidf_keyword_expanded | s01_public_post_url | answer | public_post_live_url | ok | answer | ok | ok | no | no | no |
| tfidf_keyword_expanded | s02_overclaim_eval_results | block | correction_strawman_baseline | miss | warn | miss | miss | no | yes | no |
| tfidf_keyword_expanded | s03_public_private_claim | verify_first | uncertainty_public_claims | ok | verify_first | ok | ok | no | no | no |
| tfidf_keyword_expanded | s04_start_after_crash | answer | recovery_startup_order | ok | answer | ok | ok | no | no | no |
| tfidf_keyword_expanded | s05_live_file_conflict | answer | authority_live_files_first | ok | answer | ok | ok | no | no | no |
| tfidf_keyword_expanded | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| tfidf_keyword_expanded | s07_next_artifact | answer | next_artifact_public_harness | ok | answer | ok | ok | no | no | no |
| tfidf_keyword_expanded | s08_speculative_theory | verify_first | uncertainty_speculative_theory | ok | verify_first | ok | ok | no | no | no |
| tfidf_keyword_expanded | s09_latest_instruction | answer | authority_user_latest_steers | ok | answer | ok | ok | no | no | no |
| tfidf_keyword_expanded | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |
| bm25_content_only | s01_public_post_url | answer | public_post_live_url | ok | answer | ok | ok | no | no | no |
| bm25_content_only | s02_overclaim_eval_results | block | correction_strawman_baseline | miss | warn | miss | miss | no | yes | no |
| bm25_content_only | s03_public_private_claim | verify_first | uncertainty_public_claims | ok | verify_first | ok | ok | no | no | no |
| bm25_content_only | s04_start_after_crash | answer | recovery_startup_order | ok | answer | ok | ok | no | no | no |
| bm25_content_only | s05_live_file_conflict | answer | authority_live_files_first | ok | answer | ok | ok | no | no | no |
| bm25_content_only | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| bm25_content_only | s07_next_artifact | answer | next_artifact_public_harness | ok | answer | ok | ok | no | no | no |
| bm25_content_only | s08_speculative_theory | verify_first | uncertainty_speculative_theory | ok | verify_first | ok | ok | no | no | no |
| bm25_content_only | s09_latest_instruction | answer | authority_user_latest_steers | ok | answer | ok | ok | no | no | no |
| bm25_content_only | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |
| bm25_metadata_content | s01_public_post_url | answer | public_post_live_url | ok | answer | ok | ok | no | no | no |
| bm25_metadata_content | s02_overclaim_eval_results | block | correction_strawman_baseline | miss | warn | miss | miss | no | yes | no |
| bm25_metadata_content | s03_public_private_claim | verify_first | uncertainty_public_claims | ok | verify_first | ok | ok | no | no | no |
| bm25_metadata_content | s04_start_after_crash | answer | recovery_startup_order | ok | answer | ok | ok | no | no | no |
| bm25_metadata_content | s05_live_file_conflict | answer | authority_live_files_first | ok | answer | ok | ok | no | no | no |
| bm25_metadata_content | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| bm25_metadata_content | s07_next_artifact | answer | next_artifact_public_harness | ok | answer | ok | ok | no | no | no |
| bm25_metadata_content | s08_speculative_theory | verify_first | uncertainty_speculative_theory | ok | verify_first | ok | ok | no | no | no |
| bm25_metadata_content | s09_latest_instruction | answer | authority_user_latest_steers | ok | answer | ok | ok | no | no | no |
| bm25_metadata_content | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |
| bm25_keyword_expanded | s01_public_post_url | answer | public_post_live_url | ok | answer | ok | ok | no | no | no |
| bm25_keyword_expanded | s02_overclaim_eval_results | block | correction_strawman_baseline | miss | warn | miss | miss | no | yes | no |
| bm25_keyword_expanded | s03_public_private_claim | verify_first | uncertainty_public_claims | ok | verify_first | ok | ok | no | no | no |
| bm25_keyword_expanded | s04_start_after_crash | answer | recovery_startup_order | ok | answer | ok | ok | no | no | no |
| bm25_keyword_expanded | s05_live_file_conflict | answer | authority_live_files_first | ok | answer | ok | ok | no | no | no |
| bm25_keyword_expanded | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| bm25_keyword_expanded | s07_next_artifact | answer | next_artifact_public_harness | ok | answer | ok | ok | no | no | no |
| bm25_keyword_expanded | s08_speculative_theory | verify_first | uncertainty_speculative_theory | ok | verify_first | ok | ok | no | no | no |
| bm25_keyword_expanded | s09_latest_instruction | answer | authority_user_latest_steers | ok | answer | ok | ok | no | no | no |
| bm25_keyword_expanded | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |

## Strategy Definitions

- `tfidf_content_only`: TF-IDF over only the memory `content` field.
- `tfidf_metadata_content`: TF-IDF over content plus ID, memory type, status fields, source, and file.
- `tfidf_keyword_expanded`: TF-IDF over metadata+content plus `retrieval_terms` semantic identifiers.
- `bm25_content_only`: BM25 over only the memory `content` field.
- `bm25_metadata_content`: BM25 over content plus ID, memory type, status fields, source, and file.
- `bm25_keyword_expanded`: BM25 over metadata+content plus `retrieval_terms` semantic identifiers.

## Limitations

- Deterministic lexical retrieval only; no embeddings, hybrid retrieval, or reranking.
- Scenario set is small and still designed by the framework author.
- No free-form LLM generation is scored.
- Retrieval and memory-object design are entangled.
- External scenarios and stronger baselines are needed before stronger claims.
