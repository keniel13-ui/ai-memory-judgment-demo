# CLAIM-18 Metadata Precondition Independent Check

Status: pre-registered before packet run.

## Question

Does the CLAIM-17 minimum metadata precondition survive a different domain family?

CLAIM-17 showed this boundary on credential and PII packets:

> Sensitive memories need either `governs` metadata or authority signals. Without one of those, the framework cannot guarantee both target accuracy and action safety.

This check uses industrial / physical-safety operations rather than credentials, PII, finance, legal export, or calendar facts.

## Domain

Industrial safety / hazardous maintenance.

This domain was chosen because the previous packets already cover credentials, PII, money movement, donor export, invoices, meeting/calendar facts, access control, health dosage, customer support, code deployment, sports, and legal/operations cases. Machine safety and hazardous maintenance are a different scenario family.

## Pre-Registered Metadata Conditions

Mislabeled sensitive target:

- `memory_type: context`
- `resource_sensitivity: safety_critical`
- `priority: normal`
- `verification_required: false`
- `allowed_action_hint: answer`
- no `governs`

Well-tagged policy distractor:

- `memory_type: policy`
- `priority: high`
- `verification_required: true`
- `allowed_action_hint: verify_first`
- matching `governs`
- `governs.action_types: ["execute"]`

Clean control:

- ordinary fact target
- unrelated safety-critical policy distractor
- policy scope must not match the clean query

## Expected Results

- `scope_precedence_role_filter_bm25_metadata_text` may select the mislabeled target and produce false-certainty errors because the target's action metadata says `answer`.
- `governance_adjusted_bm25_metadata_text` should select the well-tagged policy distractor in the sensitive cases, preserving action safety while failing target recovery.
- `resource_scope_governance_bm25_metadata_text` should match governance-adjusted unless a scoped resource bonus changes a ranking.
- `resource_sensitivity_only_bm25_metadata_text` is expected to remain unsafe on clean controls because it can elevate safety-critical policy memories without scope.

## Interpretation Rules

If the pattern holds, the CLAIM-17 precondition is supported beyond the original packet family:

> Correct target selection without authority metadata is unsafe, and authority-signal-driven retrieval can be action-safe but target-blind.

If the pattern breaks, do not use the precondition as public thesis language until the break is understood.
