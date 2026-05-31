# Role-Filter Metadata Noise Results

Status: metadata-noise stress test for Direction B role filtering. Not benchmark-grade.

This test derives controlled noisy variants from the same fresh-authored v2.2 scenario-local stores.

## Variant Summary

| Variant | Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking |
|---|---|---:|---:|---:|---:|---:|---:|
| clean | bm25_metadata_text | 3/5 | 4/5 | 2 | 0 | 1 | 0 |
| clean | role_filter_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 |
| missing_target_type | bm25_metadata_text | 3/5 | 4/5 | 2 | 0 | 1 | 0 |
| missing_target_type | role_filter_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 |
| wrong_target_type | bm25_metadata_text | 3/5 | 4/5 | 2 | 0 | 1 | 0 |
| wrong_target_type | role_filter_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 |
| missing_target_priority | bm25_metadata_text | 3/5 | 4/5 | 2 | 0 | 1 | 0 |
| missing_target_priority | role_filter_bm25_metadata_text | 5/5 | 5/5 | 0 | 0 | 0 | 0 |
| target_metadata_corrupt | bm25_metadata_text | 3/5 | 4/5 | 2 | 0 | 1 | 0 |
| target_metadata_corrupt | role_filter_bm25_metadata_text | 3/5 | 4/5 | 2 | 0 | 1 | 0 |
| unrelated_block_policy | bm25_metadata_text | 1/5 | 3/5 | 4 | 0 | 2 | 0 |
| unrelated_block_policy | role_filter_bm25_metadata_text | 4/5 | 4/5 | 1 | 0 | 0 | 1 |
| competing_policy | bm25_metadata_text | 0/5 | 1/5 | 5 | 0 | 0 | 4 |
| competing_policy | role_filter_bm25_metadata_text | 0/5 | 1/5 | 5 | 0 | 0 | 4 |

## Key Read

- `clean` is the CLAIM-09 condition.
- `missing_target_priority` tests whether priority is required when target type and verification metadata remain intact.
- `target_metadata_corrupt` tests the role filter's dependency on metadata hygiene.
- `unrelated_block_policy` and `competing_policy` test overblocking pressure from authority-lane pollution.

## Scenario Rows

| Variant | Strategy | Scenario | Expected | Selected role | Action | Act ok | Trap fail | FC | Downgrade | OB |
|---|---|---|---|---|---|---|---|---|---|---|
| clean | bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | distractor_value | verify_first | ok | yes | no | no | no |
| clean | role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| clean | bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| clean | role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| clean | bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| clean | role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| clean | bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | distractor_expectation | verify_first | miss | yes | no | yes | no |
| clean | role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no |
| clean | bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| clean | role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_type | bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | distractor_value | verify_first | ok | yes | no | no | no |
| missing_target_type | role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_type | bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| missing_target_type | role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| missing_target_type | bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_type | role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_type | bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | distractor_expectation | verify_first | miss | yes | no | yes | no |
| missing_target_type | role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no |
| missing_target_type | bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_type | role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| wrong_target_type | bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | distractor_value | verify_first | ok | yes | no | no | no |
| wrong_target_type | role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| wrong_target_type | bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| wrong_target_type | role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| wrong_target_type | bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| wrong_target_type | role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| wrong_target_type | bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | distractor_expectation | verify_first | miss | yes | no | yes | no |
| wrong_target_type | role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no |
| wrong_target_type | bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| wrong_target_type | role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_priority | bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | distractor_value | verify_first | ok | yes | no | no | no |
| missing_target_priority | role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_priority | bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| missing_target_priority | role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| missing_target_priority | bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_priority | role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_priority | bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | distractor_expectation | verify_first | miss | yes | no | yes | no |
| missing_target_priority | role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no |
| missing_target_priority | bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| missing_target_priority | role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| target_metadata_corrupt | bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | distractor_value | verify_first | ok | yes | no | no | no |
| target_metadata_corrupt | role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | distractor_value | verify_first | ok | yes | no | no | no |
| target_metadata_corrupt | bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| target_metadata_corrupt | role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| target_metadata_corrupt | bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| target_metadata_corrupt | role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| target_metadata_corrupt | bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | distractor_expectation | verify_first | miss | yes | no | yes | no |
| target_metadata_corrupt | role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | distractor_expectation | verify_first | miss | yes | no | yes | no |
| target_metadata_corrupt | bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| target_metadata_corrupt | role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| unrelated_block_policy | bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | distractor_value | verify_first | ok | yes | no | no | no |
| unrelated_block_policy | role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| unrelated_block_policy | bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | target | answer | ok | no | no | no | no |
| unrelated_block_policy | role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | noise_unrelated_block_policy | block | miss | yes | no | no | yes |
| unrelated_block_policy | bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | distractor_old_password | archive_only | miss | yes | no | yes | no |
| unrelated_block_policy | role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| unrelated_block_policy | bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | distractor_expectation | verify_first | miss | yes | no | yes | no |
| unrelated_block_policy | role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | target | block | ok | no | no | no | no |
| unrelated_block_policy | bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | distractor_loose_talk | verify_first | ok | yes | no | no | no |
| unrelated_block_policy | role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | target | verify_first | ok | no | no | no | no |
| competing_policy | bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | noise_competing_policy | block | miss | yes | no | no | yes |
| competing_policy | role_filter_bm25_metadata_text | fresh_too_permissive_dosage_v2 | verify_first | noise_competing_policy | block | miss | yes | no | no | yes |
| competing_policy | bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | noise_competing_policy | block | miss | yes | no | no | yes |
| competing_policy | role_filter_bm25_metadata_text | fresh_overblocking_invoice_total_v2 | answer | noise_competing_policy | block | miss | yes | no | no | yes |
| competing_policy | bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | noise_competing_policy | block | miss | yes | no | no | yes |
| competing_policy | role_filter_bm25_metadata_text | fresh_stale_superseded_vpn_v2 | verify_first | noise_competing_policy | block | miss | yes | no | no | yes |
| competing_policy | bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | noise_competing_policy | block | ok | yes | no | no | no |
| competing_policy | role_filter_bm25_metadata_text | fresh_ambiguous_authority_export_v2 | block | noise_competing_policy | block | ok | yes | no | no | no |
| competing_policy | bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | noise_competing_policy | block | miss | yes | no | no | yes |
| competing_policy | role_filter_bm25_metadata_text | fresh_paraphrase_no_keyword_access_v2 | verify_first | noise_competing_policy | block | miss | yes | no | no | yes |
