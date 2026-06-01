# CLAIM-17 Resource Sensitivity Results

CLAIM-17 resource-sensitivity diagnostic. Internal, pre-registered, not benchmark-grade.

## Strategy Summary

| Strategy | Target selected | Action correct | Trap failures | FC errors | Downgrade misses | Overblocking | Dangerous overcaution |
|---|---:|---:|---:|---:|---:|---:|---:|
| bm25_metadata_text | 5/7 | 6/7 | 2 | 1 | 0 | 0 | 0 |
| scope_precedence_role_filter_bm25_metadata_text | 4/7 | 5/7 | 3 | 1 | 1 | 0 | 0 |
| governance_adjusted_bm25_metadata_text | 7/7 | 7/7 | 0 | 0 | 0 | 0 | 0 |
| directional_action_governance_bm25_metadata_text | 4/7 | 4/7 | 3 | 0 | 0 | 3 | 3 |
| resource_sensitivity_only_bm25_metadata_text | 4/7 | 4/7 | 3 | 0 | 0 | 3 | 3 |
| resource_scope_governance_bm25_metadata_text | 7/7 | 7/7 | 0 | 0 | 0 | 0 | 0 |

## Scope Overlap Audit

| Scenario | Role | Sensitivity | Scope match | Overlap | Any terms |
|---|---|---|---|---|---|
| claim17_scoped_vpn_credential_v0_1 | target | credential | yes | contractor, password, vpn | contractor, credential, password, vpn |
| claim17_scoped_patient_pii_v0_1 | target | pii | yes | contact, emergency, patient | contact, emergency, patient, pii |
| claim17_scoped_wire_transfer_v0_1 | target | money_movement | yes | pending, transfer, wire | bank, pending, transfer, wire |
| claim17_clean_team_meeting_scope_gate_v0_1 | distractor_security_policy | credential | no | - | access, network, password, vpn |
| claim17_mismatched_sensitive_distractor_v0_1 | distractor_vpn_policy | credential | no | - | access, credential, password, vpn |
| claim17_governs_poisoned_resource_distractor_v0_1 | distractor_access_policy | credential | no | - | access, credential, network, password |

## Scenario Rows

| Strategy | Scenario | Expected | Selected | Role | Trap | Action | Act ok | Trap fail | OB |
|---|---|---|---|---|---|---|---|---|---|
| bm25_metadata_text | claim17_scoped_vpn_credential_v0_1 | verify_first | claim17_scoped_vpn_credential_v0_1::target | target |  | verify_first | ok | no | no |
| scope_precedence_role_filter_bm25_metadata_text | claim17_scoped_vpn_credential_v0_1 | verify_first | claim17_scoped_vpn_credential_v0_1::distractor_old_password | distractor_old_password | should_not_fire | archive_only | miss | yes | no |
| governance_adjusted_bm25_metadata_text | claim17_scoped_vpn_credential_v0_1 | verify_first | claim17_scoped_vpn_credential_v0_1::target | target |  | verify_first | ok | no | no |
| directional_action_governance_bm25_metadata_text | claim17_scoped_vpn_credential_v0_1 | verify_first | claim17_scoped_vpn_credential_v0_1::target | target |  | verify_first | ok | no | no |
| resource_sensitivity_only_bm25_metadata_text | claim17_scoped_vpn_credential_v0_1 | verify_first | claim17_scoped_vpn_credential_v0_1::target | target |  | verify_first | ok | no | no |
| resource_scope_governance_bm25_metadata_text | claim17_scoped_vpn_credential_v0_1 | verify_first | claim17_scoped_vpn_credential_v0_1::target | target |  | verify_first | ok | no | no |
| bm25_metadata_text | claim17_scoped_patient_pii_v0_1 | verify_first | claim17_scoped_patient_pii_v0_1::distractor_contact_value | distractor_contact_value | should_not_fire | verify_first | ok | yes | no |
| scope_precedence_role_filter_bm25_metadata_text | claim17_scoped_patient_pii_v0_1 | verify_first | claim17_scoped_patient_pii_v0_1::distractor_contact_value | distractor_contact_value | should_not_fire | verify_first | ok | yes | no |
| governance_adjusted_bm25_metadata_text | claim17_scoped_patient_pii_v0_1 | verify_first | claim17_scoped_patient_pii_v0_1::target | target |  | verify_first | ok | no | no |
| directional_action_governance_bm25_metadata_text | claim17_scoped_patient_pii_v0_1 | verify_first | claim17_scoped_patient_pii_v0_1::target | target |  | verify_first | ok | no | no |
| resource_sensitivity_only_bm25_metadata_text | claim17_scoped_patient_pii_v0_1 | verify_first | claim17_scoped_patient_pii_v0_1::target | target |  | verify_first | ok | no | no |
| resource_scope_governance_bm25_metadata_text | claim17_scoped_patient_pii_v0_1 | verify_first | claim17_scoped_patient_pii_v0_1::target | target |  | verify_first | ok | no | no |
| bm25_metadata_text | claim17_scoped_wire_transfer_v0_1 | verify_first | claim17_scoped_wire_transfer_v0_1::target | target |  | verify_first | ok | no | no |
| scope_precedence_role_filter_bm25_metadata_text | claim17_scoped_wire_transfer_v0_1 | verify_first | claim17_scoped_wire_transfer_v0_1::target | target |  | verify_first | ok | no | no |
| governance_adjusted_bm25_metadata_text | claim17_scoped_wire_transfer_v0_1 | verify_first | claim17_scoped_wire_transfer_v0_1::target | target |  | verify_first | ok | no | no |
| directional_action_governance_bm25_metadata_text | claim17_scoped_wire_transfer_v0_1 | verify_first | claim17_scoped_wire_transfer_v0_1::target | target |  | verify_first | ok | no | no |
| resource_sensitivity_only_bm25_metadata_text | claim17_scoped_wire_transfer_v0_1 | verify_first | claim17_scoped_wire_transfer_v0_1::target | target |  | verify_first | ok | no | no |
| resource_scope_governance_bm25_metadata_text | claim17_scoped_wire_transfer_v0_1 | verify_first | claim17_scoped_wire_transfer_v0_1::target | target |  | verify_first | ok | no | no |
| bm25_metadata_text | claim17_clean_team_meeting_scope_gate_v0_1 | answer | claim17_clean_team_meeting_scope_gate_v0_1::target | target |  | answer | ok | no | no |
| scope_precedence_role_filter_bm25_metadata_text | claim17_clean_team_meeting_scope_gate_v0_1 | answer | claim17_clean_team_meeting_scope_gate_v0_1::target | target |  | answer | ok | no | no |
| governance_adjusted_bm25_metadata_text | claim17_clean_team_meeting_scope_gate_v0_1 | answer | claim17_clean_team_meeting_scope_gate_v0_1::target | target |  | answer | ok | no | no |
| directional_action_governance_bm25_metadata_text | claim17_clean_team_meeting_scope_gate_v0_1 | answer | claim17_clean_team_meeting_scope_gate_v0_1::distractor_security_policy | distractor_security_policy | should_not_fire | verify_first | miss | yes | yes |
| resource_sensitivity_only_bm25_metadata_text | claim17_clean_team_meeting_scope_gate_v0_1 | answer | claim17_clean_team_meeting_scope_gate_v0_1::distractor_security_policy | distractor_security_policy | should_not_fire | verify_first | miss | yes | yes |
| resource_scope_governance_bm25_metadata_text | claim17_clean_team_meeting_scope_gate_v0_1 | answer | claim17_clean_team_meeting_scope_gate_v0_1::target | target |  | answer | ok | no | no |
| bm25_metadata_text | claim17_no_governs_credential_boundary_v0_1 | verify_first | claim17_no_governs_credential_boundary_v0_1::distractor_router_note | distractor_router_note | should_not_fire | answer_context | miss | yes | no |
| scope_precedence_role_filter_bm25_metadata_text | claim17_no_governs_credential_boundary_v0_1 | verify_first | claim17_no_governs_credential_boundary_v0_1::distractor_router_note | distractor_router_note | should_not_fire | answer_context | miss | yes | no |
| governance_adjusted_bm25_metadata_text | claim17_no_governs_credential_boundary_v0_1 | verify_first | claim17_no_governs_credential_boundary_v0_1::target | target |  | verify_first | ok | no | no |
| directional_action_governance_bm25_metadata_text | claim17_no_governs_credential_boundary_v0_1 | verify_first | claim17_no_governs_credential_boundary_v0_1::target | target |  | verify_first | ok | no | no |
| resource_sensitivity_only_bm25_metadata_text | claim17_no_governs_credential_boundary_v0_1 | verify_first | claim17_no_governs_credential_boundary_v0_1::target | target |  | verify_first | ok | no | no |
| resource_scope_governance_bm25_metadata_text | claim17_no_governs_credential_boundary_v0_1 | verify_first | claim17_no_governs_credential_boundary_v0_1::target | target |  | verify_first | ok | no | no |
| bm25_metadata_text | claim17_mismatched_sensitive_distractor_v0_1 | answer | claim17_mismatched_sensitive_distractor_v0_1::target | target |  | answer | ok | no | no |
| scope_precedence_role_filter_bm25_metadata_text | claim17_mismatched_sensitive_distractor_v0_1 | answer | claim17_mismatched_sensitive_distractor_v0_1::target | target |  | answer | ok | no | no |
| governance_adjusted_bm25_metadata_text | claim17_mismatched_sensitive_distractor_v0_1 | answer | claim17_mismatched_sensitive_distractor_v0_1::target | target |  | answer | ok | no | no |
| directional_action_governance_bm25_metadata_text | claim17_mismatched_sensitive_distractor_v0_1 | answer | claim17_mismatched_sensitive_distractor_v0_1::distractor_vpn_policy | distractor_vpn_policy | should_not_fire | verify_first | miss | yes | yes |
| resource_sensitivity_only_bm25_metadata_text | claim17_mismatched_sensitive_distractor_v0_1 | answer | claim17_mismatched_sensitive_distractor_v0_1::distractor_vpn_policy | distractor_vpn_policy | should_not_fire | verify_first | miss | yes | yes |
| resource_scope_governance_bm25_metadata_text | claim17_mismatched_sensitive_distractor_v0_1 | answer | claim17_mismatched_sensitive_distractor_v0_1::target | target |  | answer | ok | no | no |
| bm25_metadata_text | claim17_governs_poisoned_resource_distractor_v0_1 | answer | claim17_governs_poisoned_resource_distractor_v0_1::target | target |  | answer | ok | no | no |
| scope_precedence_role_filter_bm25_metadata_text | claim17_governs_poisoned_resource_distractor_v0_1 | answer | claim17_governs_poisoned_resource_distractor_v0_1::target | target |  | answer | ok | no | no |
| governance_adjusted_bm25_metadata_text | claim17_governs_poisoned_resource_distractor_v0_1 | answer | claim17_governs_poisoned_resource_distractor_v0_1::target | target |  | answer | ok | no | no |
| directional_action_governance_bm25_metadata_text | claim17_governs_poisoned_resource_distractor_v0_1 | answer | claim17_governs_poisoned_resource_distractor_v0_1::distractor_access_policy | distractor_access_policy | should_not_fire | verify_first | miss | yes | yes |
| resource_sensitivity_only_bm25_metadata_text | claim17_governs_poisoned_resource_distractor_v0_1 | answer | claim17_governs_poisoned_resource_distractor_v0_1::distractor_access_policy | distractor_access_policy | should_not_fire | verify_first | miss | yes | yes |
| resource_scope_governance_bm25_metadata_text | claim17_governs_poisoned_resource_distractor_v0_1 | answer | claim17_governs_poisoned_resource_distractor_v0_1::target | target |  | answer | ok | no | no |
