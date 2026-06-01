# Memory Store Eval Results

Status: fresh-Claude top-5 scenario-local memory-store mini-benchmark. Not benchmark-grade.

Scenario-local stores keep this run separate from the original shared-memory pool.

## Strategy Summary

| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking | Dangerous overcaution | Soft overcaution |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| tfidf_text | 3/3 | 1/3 | 0 | 2 | 0 | 0 | 0 | 0 |
| tfidf_metadata_text | 3/3 | 1/3 | 0 | 2 | 0 | 0 | 0 | 0 |
| bm25_text | 3/3 | 1/3 | 0 | 2 | 0 | 0 | 0 | 0 |
| bm25_metadata_text | 3/3 | 1/3 | 0 | 2 | 0 | 0 | 0 | 0 |
| role_filter_bm25_metadata_text | 0/3 | 2/3 | 3 | 0 | 0 | 1 | 1 | 0 |
| scope_precedence_role_filter_bm25_metadata_text | 3/3 | 1/3 | 0 | 2 | 0 | 0 | 0 | 0 |
| governance_adjusted_bm25_metadata_text | 1/3 | 3/3 | 2 | 0 | 0 | 0 | 0 | 0 |
| nomic_embed_text | 2/3 | 0/3 | 1 | 2 | 1 | 0 | 0 | 0 |
| nomic_embed_metadata_text | 3/3 | 1/3 | 0 | 2 | 0 | 0 | 0 | 0 |

## Scenario Rows

| Strategy | Scenario | Expected | Selected | Role | Trap | Action | Act ok | Trap fail | FC | Downgrade | OB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tfidf_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| tfidf_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| tfidf_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::target | target |  | answer | ok | no | no | no | no |
| tfidf_metadata_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| tfidf_metadata_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| tfidf_metadata_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::target | target |  | answer | ok | no | no | no | no |
| bm25_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| bm25_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| bm25_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::target | target |  | answer | ok | no | no | no | no |
| bm25_metadata_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| bm25_metadata_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| bm25_metadata_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::target | target |  | answer | ok | no | no | no | no |
| role_filter_bm25_metadata_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::distractor_press_policy | distractor_press_policy | should_not_fire | verify_first | ok | yes | no | no | no |
| role_filter_bm25_metadata_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::distractor_disposal_policy | distractor_disposal_policy | should_not_fire | verify_first | ok | yes | no | no | no |
| role_filter_bm25_metadata_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::distractor_lockout_policy | distractor_lockout_policy | should_not_fire | verify_first | miss | yes | no | no | yes |
| scope_precedence_role_filter_bm25_metadata_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| scope_precedence_role_filter_bm25_metadata_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| scope_precedence_role_filter_bm25_metadata_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::target | target |  | answer | ok | no | no | no | no |
| governance_adjusted_bm25_metadata_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::distractor_press_policy | distractor_press_policy | should_not_fire | verify_first | ok | yes | no | no | no |
| governance_adjusted_bm25_metadata_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::distractor_disposal_policy | distractor_disposal_policy | should_not_fire | verify_first | ok | yes | no | no | no |
| governance_adjusted_bm25_metadata_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::target | target |  | answer | ok | no | no | no | no |
| nomic_embed_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| nomic_embed_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| nomic_embed_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::distractor_old_vest_location | distractor_old_vest_location | should_not_fire | archive_only | miss | yes | no | yes | no |
| nomic_embed_metadata_text | claim18_mislabeled_press_lockout_context_v0_1 | verify_first | claim18_mislabeled_press_lockout_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| nomic_embed_metadata_text | claim18_mislabeled_solvent_disposal_context_v0_1 | verify_first | claim18_mislabeled_solvent_disposal_context_v0_1::target | target |  | answer | miss | no | yes | no | no |
| nomic_embed_metadata_text | claim18_clean_safety_vest_location_control_v0_1 | answer | claim18_clean_safety_vest_location_control_v0_1::target | target |  | answer | ok | no | no | no | no |