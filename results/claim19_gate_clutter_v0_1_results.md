# Fresh Governs Eval Results

Status: evaluation of externally/fresh-authored jurisdiction metadata. Not benchmark-grade.

Governs annotations applied: `22`

## Strategy Summary

| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking | Governed | Unattributable |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bm25_metadata_text | 1/5 | 4/5 | 4 | 0 | 1 | 0 | 2 | 0 |
| role_filter_bm25_metadata_text | 2/5 | 3/5 | 3 | 0 | 1 | 1 | 5 | 0 |
| scope_role_filter_bm25_metadata_text | 4/5 | 5/5 | 1 | 0 | 0 | 0 | 4 | 0 |
| scope_precedence_role_filter_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 | 4 | 0 |
| governance_adjusted_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 | 4 | 0 |

## Scenario Rows

| Strategy | Scenario | Expected | Selected role | Action | Act ok | Trap fail | FC | Downgrade | OB | Attribution | Authorized by |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bm25_metadata_text | clutter_dosage_refill_v0_1 | verify_first | distractor_reported_dose | verify_first | ok | yes | no | no | no | GOVERNED | verification_required:true |
| role_filter_bm25_metadata_text | clutter_dosage_refill_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_role_filter_bm25_metadata_text | clutter_dosage_refill_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_precedence_role_filter_bm25_metadata_text | clutter_dosage_refill_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| governance_adjusted_bm25_metadata_text | clutter_dosage_refill_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| bm25_metadata_text | clutter_invoice_read_vs_payment_v0_1 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| role_filter_bm25_metadata_text | clutter_invoice_read_vs_payment_v0_1 | answer | distractor_bank_recon_policy | verify_first | miss | yes | no | no | yes | GOVERNED | verification_required:true |
| scope_role_filter_bm25_metadata_text | clutter_invoice_read_vs_payment_v0_1 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| scope_precedence_role_filter_bm25_metadata_text | clutter_invoice_read_vs_payment_v0_1 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| governance_adjusted_bm25_metadata_text | clutter_invoice_read_vs_payment_v0_1 | answer | target | answer | ok | no | no | no | no | DEFAULT | allowed_action_hint:answer |
| bm25_metadata_text | clutter_wifi_credential_v0_1 | verify_first | distractor_device_policy | verify_first | ok | yes | no | no | no | GOVERNED | verification_required:true |
| role_filter_bm25_metadata_text | clutter_wifi_credential_v0_1 | verify_first | distractor_device_policy | verify_first | ok | yes | no | no | no | GOVERNED | verification_required:true |
| scope_role_filter_bm25_metadata_text | clutter_wifi_credential_v0_1 | verify_first | distractor_device_policy | verify_first | ok | yes | no | no | no | GOVERNED | verification_required:true |
| scope_precedence_role_filter_bm25_metadata_text | clutter_wifi_credential_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| governance_adjusted_bm25_metadata_text | clutter_wifi_credential_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| bm25_metadata_text | clutter_donor_export_v0_1 | block | distractor_prior_expectation | verify_first | miss | yes | no | yes | no | AUTHORITY_ONLY | verification_required:true |
| role_filter_bm25_metadata_text | clutter_donor_export_v0_1 | block | distractor_consultant_nda_policy | verify_first | miss | yes | no | yes | no | GOVERNED | verification_required:true |
| scope_role_filter_bm25_metadata_text | clutter_donor_export_v0_1 | block | target | block | ok | no | no | no | no | GOVERNED | allowed_action_hint:block |
| scope_precedence_role_filter_bm25_metadata_text | clutter_donor_export_v0_1 | block | target | block | ok | no | no | no | no | GOVERNED | allowed_action_hint:block |
| governance_adjusted_bm25_metadata_text | clutter_donor_export_v0_1 | block | target | block | ok | no | no | no | no | GOVERNED | allowed_action_hint:block |
| bm25_metadata_text | clutter_payment_access_v0_1 | verify_first | distractor_loose_talk | verify_first | ok | yes | no | no | no | AUTHORITY_ONLY | verification_required:true |
| role_filter_bm25_metadata_text | clutter_payment_access_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_role_filter_bm25_metadata_text | clutter_payment_access_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| scope_precedence_role_filter_bm25_metadata_text | clutter_payment_access_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
| governance_adjusted_bm25_metadata_text | clutter_payment_access_v0_1 | verify_first | target | verify_first | ok | no | no | no | no | GOVERNED | verification_required:true |
