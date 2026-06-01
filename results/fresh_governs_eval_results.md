# Fresh Governs Eval Results

Status: evaluation of externally/fresh-authored jurisdiction metadata. Not benchmark-grade.

Governs annotations applied: `5`

## Strategy Summary

| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking | Governed | Unattributable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bm25_metadata_text | 3/5 | 4/5 | 2 | 0 | 1 | 0 | 2 | 0 |
| role_filter_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 | 4 | 0 |
| scope_role_filter_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 | 4 | 0 |
| scope_precedence_role_filter_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 | 4 | 0 |
| governance_adjusted_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 | 4 | 0 |

## Scenario Rows

| Strategy | Scenario | Expected | Selected role | Action | Act ok | Trap fail | FC | Downgrade | OB | Attribution | Authorized by |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | distractor_value | verify_first | ok | yes | no | no | no | AUTHORITY_ONLY | verification_required:true |
| role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_precedence_role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| governance_adjusted_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| scope_role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| scope_precedence_role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| governance_adjusted_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_precedence_role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| governance_adjusted_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | distractor_expectation | verify_first | miss | yes | no | yes | no | AUTHORITY_ONLY | verification_required:true |
| role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no | GOVERNED | allowed_action_hint:block |
| scope_role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no | GOVERNED | allowed_action_hint:block |
| scope_precedence_role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no | GOVERNED | allowed_action_hint:block |
| governance_adjusted_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no | GOVERNED | allowed_action_hint:block |
| bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_precedence_role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| governance_adjusted_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
