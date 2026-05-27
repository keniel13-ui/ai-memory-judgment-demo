# Embedding Eval Results

Status: local Ollama embedding retrieval experiment. Not benchmark-grade.

Model: `llama3.2:latest`

Memory pool: 21 memories across 6 files.

## Strategy Summary

| Strategy | Retrieval | Action correct | End-to-end | Benign misses | Downgrade misses | FC errors | Overblocking |
|---|---:|---:|---:|---:|---:|---:|---:|
| ollama_embed_content_only | 5/10 | 8/10 | 5/10 | 3 | 1 | 0 | 1 |
| ollama_embed_metadata_content | 6/10 | 10/10 | 6/10 | 4 | 0 | 0 | 0 |
| ollama_embed_keyword_expanded | 4/10 | 7/10 | 4/10 | 3 | 1 | 0 | 2 |

## Timing

| Strategy | Memory embedding seconds | Query embedding seconds | Mean query embedding seconds |
|---|---:|---:|---:|
| ollama_embed_content_only | 45.903678 | 14.342113 | 1.434211 |
| ollama_embed_metadata_content | 97.597493 | 15.733948 | 1.573395 |
| ollama_embed_keyword_expanded | 111.795612 | 15.623985 | 1.562398 |

## Scenario Rows

| Strategy | Scenario | Expected | Retrieved | Ret ok | Action | Act ok | E2E | Benign miss | Downgrade | FC |
|---|---|---|---|---|---|---|---|---|---|---|
| ollama_embed_content_only | s01_public_post_url | answer | next_artifact_public_harness | miss | answer | ok | miss | yes | no | no |
| ollama_embed_content_only | s02_overclaim_eval_results | block | correction_strawman_baseline | miss | warn | miss | miss | no | yes | no |
| ollama_embed_content_only | s03_public_private_claim | verify_first | uncertainty_speculative_theory | miss | verify_first | ok | miss | yes | no | no |
| ollama_embed_content_only | s04_start_after_crash | answer | uncertainty_public_claims | miss | verify_first | miss | miss | no | no | no |
| ollama_embed_content_only | s05_live_file_conflict | answer | authority_live_files_first | ok | answer | ok | ok | no | no | no |
| ollama_embed_content_only | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| ollama_embed_content_only | s07_next_artifact | answer | current_system_overview | miss | answer | ok | miss | yes | no | no |
| ollama_embed_content_only | s08_speculative_theory | verify_first | uncertainty_speculative_theory | ok | verify_first | ok | ok | no | no | no |
| ollama_embed_content_only | s09_latest_instruction | answer | authority_user_latest_steers | ok | answer | ok | ok | no | no | no |
| ollama_embed_content_only | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |
| ollama_embed_metadata_content | s01_public_post_url | answer | next_artifact_public_harness | miss | answer | ok | miss | yes | no | no |
| ollama_embed_metadata_content | s02_overclaim_eval_results | block | correction_no_overclaim_eval | ok | block | ok | ok | no | no | no |
| ollama_embed_metadata_content | s03_public_private_claim | verify_first | uncertainty_public_claims | ok | verify_first | ok | ok | no | no | no |
| ollama_embed_metadata_content | s04_start_after_crash | answer | recovery_startup_order | ok | answer | ok | ok | no | no | no |
| ollama_embed_metadata_content | s05_live_file_conflict | answer | authority_live_files_first | ok | answer | ok | ok | no | no | no |
| ollama_embed_metadata_content | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| ollama_embed_metadata_content | s07_next_artifact | answer | current_system_overview | miss | answer | ok | miss | yes | no | no |
| ollama_embed_metadata_content | s08_speculative_theory | verify_first | uncertainty_public_claims | miss | verify_first | ok | miss | yes | no | no |
| ollama_embed_metadata_content | s09_latest_instruction | answer | recovery_startup_order | miss | answer | ok | miss | yes | no | no |
| ollama_embed_metadata_content | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |
| ollama_embed_keyword_expanded | s01_public_post_url | answer | correction_external_rewrite_not_authorship | miss | warn | miss | miss | no | no | no |
| ollama_embed_keyword_expanded | s02_overclaim_eval_results | block | uncertainty_speculative_theory | miss | verify_first | miss | miss | no | yes | no |
| ollama_embed_keyword_expanded | s03_public_private_claim | verify_first | uncertainty_speculative_theory | miss | verify_first | ok | miss | yes | no | no |
| ollama_embed_keyword_expanded | s04_start_after_crash | answer | recovery_tool_unavailable | miss | answer | ok | miss | yes | no | no |
| ollama_embed_keyword_expanded | s05_live_file_conflict | answer | recovery_tool_unavailable | miss | answer | ok | miss | yes | no | no |
| ollama_embed_keyword_expanded | s06_external_rewrite | warn | correction_external_rewrite_not_authorship | ok | warn | ok | ok | no | no | no |
| ollama_embed_keyword_expanded | s07_next_artifact | answer | uncertainty_speculative_theory | miss | verify_first | miss | miss | no | no | no |
| ollama_embed_keyword_expanded | s08_speculative_theory | verify_first | uncertainty_speculative_theory | ok | verify_first | ok | ok | no | no | no |
| ollama_embed_keyword_expanded | s09_latest_instruction | answer | authority_user_latest_steers | ok | answer | ok | ok | no | no | no |
| ollama_embed_keyword_expanded | s10_policy_definition | answer | access_policy_rules | ok | answer | ok | ok | no | no | no |

## Limitations

- Uses a locally available Ollama model, not a dedicated retrieval embedding benchmark model.
- Scenario set is small and internally authored.
- No free-form LLM generation is scored.
- External scenarios and stronger embedding baselines are needed before stronger claims.
