# CLAIM-21 External Certificate-Policy Packet

CLAIM-21 external certificate-policy packet. Externally authored; current gate and semantic external-gate results are separated.

## Strategy Summary

| Strategy | Expected memory | Current action ok | Current gate matched | External gate matched | Trap failures | FC errors | Gate escalations |
|---|---:|---:|---:|---:|---:|---:|---:|
| bm25_metadata_text | 8/10 | 5/10 | 5/10 | 7/10 | 2 | 0 | 7 |
| scope_precedence_role_filter_bm25_metadata_text | 6/10 | 5/10 | 3/10 | 5/10 | 4 | 0 | 9 |
| governance_adjusted_bm25_metadata_text | 3/10 | 6/10 | 6/10 | 3/10 | 7 | 0 | 2 |
| resource_scope_governance_bm25_metadata_text | 4/10 | 5/10 | 7/10 | 4/10 | 6 | 0 | 1 |

## Scenario Rows

| Strategy | Scenario | Expected memory | Selected memory | Current gate | External gate | Expected gate | External ok | Action |
|---|---|---|---|---|---|---|---|---|
| bm25_metadata_text | s001 | cert_revoke_001 | cert_revoke_ambiguous_001 | GATE_FAIL | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s001 | cert_revoke_001 | cert_revoke_ambiguous_001 | GATE_FAIL | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| governance_adjusted_bm25_metadata_text | s001 | cert_revoke_001 | cert_issue_001 | GATE_PASS | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| resource_scope_governance_bm25_metadata_text | s001 | cert_revoke_001 | cert_issue_001 | GATE_PASS | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| bm25_metadata_text | s002 | cert_issue_001 | cert_issue_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s002 | cert_issue_001 | cert_issue_bad_001 | GATE_FAIL | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| governance_adjusted_bm25_metadata_text | s002 | cert_issue_001 | cert_issue_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | verify_first |
| resource_scope_governance_bm25_metadata_text | s002 | cert_issue_001 | cert_issue_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | verify_first |
| bm25_metadata_text | s003 | cert_verify_001 | cert_verify_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | answer |
| scope_precedence_role_filter_bm25_metadata_text | s003 | cert_verify_001 | cert_verify_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | answer |
| governance_adjusted_bm25_metadata_text | s003 | cert_verify_001 | cert_verify_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | answer |
| resource_scope_governance_bm25_metadata_text | s003 | cert_verify_001 | cert_verify_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | answer |
| bm25_metadata_text | s004 | cert_sign_high_001 | cert_sign_high_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s004 | cert_sign_high_001 | cert_issue_bad_001 | GATE_FAIL | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| governance_adjusted_bm25_metadata_text | s004 | cert_sign_high_001 | cert_delegate_bad_001 | GATE_FAIL | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| resource_scope_governance_bm25_metadata_text | s004 | cert_sign_high_001 | cert_sign_high_001 | GATE_PASS | GATE_PASS | GATE_PASS | ok | verify_first |
| bm25_metadata_text | s005 | cert_sign_low_001 | cert_sign_low_001 | GATE_FAIL | GATE_FAIL | GATE_PASS | miss | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s005 | cert_sign_low_001 | cert_sign_low_001 | GATE_FAIL | GATE_FAIL | GATE_PASS | miss | verify_first |
| governance_adjusted_bm25_metadata_text | s005 | cert_sign_low_001 | cert_sign_high_001 | GATE_PASS | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| resource_scope_governance_bm25_metadata_text | s005 | cert_sign_low_001 | cert_sign_high_001 | GATE_PASS | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| bm25_metadata_text | s006 | cert_delegate_001 | cert_sign_low_001 | GATE_FAIL | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s006 | cert_delegate_001 | cert_sign_low_001 | GATE_FAIL | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| governance_adjusted_bm25_metadata_text | s006 | cert_delegate_001 | cert_verify_001 | GATE_PASS | WRONG_MEMORY | GATE_PASS | miss | answer |
| resource_scope_governance_bm25_metadata_text | s006 | cert_delegate_001 | cert_sign_high_001 | GATE_PASS | WRONG_MEMORY | GATE_PASS | miss | verify_first |
| bm25_metadata_text | s007 | cert_delegate_bad_001 | cert_delegate_bad_001 | GATE_FAIL | GATE_FAIL | GATE_FAIL | ok | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s007 | cert_delegate_bad_001 | cert_delegate_bad_001 | GATE_FAIL | GATE_FAIL | GATE_FAIL | ok | verify_first |
| governance_adjusted_bm25_metadata_text | s007 | cert_delegate_bad_001 | cert_delegate_bad_001 | GATE_FAIL | GATE_FAIL | GATE_FAIL | ok | verify_first |
| resource_scope_governance_bm25_metadata_text | s007 | cert_delegate_bad_001 | cert_delegate_bad_001 | GATE_FAIL | GATE_FAIL | GATE_FAIL | ok | verify_first |
| bm25_metadata_text | s008 | cert_issue_bad_001 | cert_issue_bad_001 | GATE_FAIL | GATE_FAIL | GATE_FAIL | ok | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s008 | cert_issue_bad_001 | cert_issue_bad_001 | GATE_FAIL | GATE_FAIL | GATE_FAIL | ok | verify_first |
| governance_adjusted_bm25_metadata_text | s008 | cert_issue_bad_001 | cert_issue_001 | GATE_PASS | WRONG_MEMORY | GATE_FAIL | miss | verify_first |
| resource_scope_governance_bm25_metadata_text | s008 | cert_issue_bad_001 | cert_issue_001 | GATE_PASS | WRONG_MEMORY | GATE_FAIL | miss | verify_first |
| bm25_metadata_text | s009 | cert_sign_ambiguous_001 | cert_sign_ambiguous_001 | GATE_FAIL | UNATTRIBUTABLE | UNATTRIBUTABLE | ok | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s009 | cert_sign_ambiguous_001 | cert_sign_ambiguous_001 | GATE_FAIL | UNATTRIBUTABLE | UNATTRIBUTABLE | ok | verify_first |
| governance_adjusted_bm25_metadata_text | s009 | cert_sign_ambiguous_001 | cert_sign_high_001 | GATE_PASS | WRONG_MEMORY | UNATTRIBUTABLE | miss | verify_first |
| resource_scope_governance_bm25_metadata_text | s009 | cert_sign_ambiguous_001 | cert_sign_high_001 | GATE_PASS | WRONG_MEMORY | UNATTRIBUTABLE | miss | verify_first |
| bm25_metadata_text | s010 | cert_revoke_ambiguous_001 | cert_revoke_ambiguous_001 | GATE_FAIL | GATE_SKIP | GATE_SKIP | ok | verify_first |
| scope_precedence_role_filter_bm25_metadata_text | s010 | cert_revoke_ambiguous_001 | cert_revoke_ambiguous_001 | GATE_FAIL | GATE_SKIP | GATE_SKIP | ok | verify_first |
| governance_adjusted_bm25_metadata_text | s010 | cert_revoke_ambiguous_001 | cert_revoke_001 | GATE_PASS | WRONG_MEMORY | GATE_SKIP | miss | verify_first |
| resource_scope_governance_bm25_metadata_text | s010 | cert_revoke_ambiguous_001 | cert_revoke_001 | GATE_PASS | WRONG_MEMORY | GATE_SKIP | miss | verify_first |

## Interpretation

- `Current gate matched` measures the existing execution gate, which only checks metadata/action-type consistency.
- `External gate matched` measures the certificate packet's semantic expectation: bad policies and underspecified authorization contexts can fail even when metadata is internally consistent.
- If external gate results diverge from current gate results, the packet is evidence that the next layer must inspect resource/action semantics, not just retrieved-memory metadata.
