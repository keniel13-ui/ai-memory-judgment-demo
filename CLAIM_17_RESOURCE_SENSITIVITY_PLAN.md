# CLAIM-17 Resource Sensitivity Pre-Registration

Status: pre-registered before scorer or packet implementation.

## Research Question

Can a separate `resource_sensitivity` field distinguish read-shaped high-risk disclosure queries from ordinary read queries without overpromoting unrelated authority memories?

CLAIM-16 showed that `action_types` is overloaded. It currently tries to represent both:

- the surface form of the user query, such as read/write/execute;
- the consequence class of the resource a memory governs, such as credential disclosure, PII disclosure, money movement, or export.

Those are orthogonal. A query can be read-shaped while targeting a sensitive resource. An execute-governed memory can also be irrelevant to a read-shaped query. The first directional action-type fix failed because it elevated execute-governed memories too broadly.

## Architectural Decision

`resource_sensitivity` is a property of the memory, not the query.

Memories without a `resource_sensitivity` field default to `ordinary_fact`. This means unannotated memories receive no sensitive-resource elevation and no sensitive-resource penalty. They fall through to the existing relevance, authority, status, and scope terms. This default is intentional: missing resource metadata should not be treated as suspicious by itself.

The scorer may only use `resource_sensitivity` for escalation when the memory's `governs` scope also matches the query. The match condition is the important guardrail:

- memory-level `resource_sensitivity` says what kind of resource the memory protects;
- `governs` scope match says whether the current query is actually asking about that resource;
- query action type remains a separate signal and must not be the only escalation trigger.

This means `resource_sensitivity` is not expected to fully solve missing `governs`. A no-governs credential scenario must be tested separately to determine whether the field provides a partial fallback or only works when scope metadata is present.

For the resource-plus-scope diagnostic scorer, the pre-registered behavior for a sensitive memory with no `governs` field is **fallback neutral**, not partial elevation. If a target has `resource_sensitivity: credential` but no `governs`, the resource term should not fire because the scorer cannot verify that the query is asking about the governed resource. The expected result is therefore baseline-like behavior on that boundary case. If the target still wins, the win comes from relevance/authority/status, not from resource sensitivity. If it loses, that confirms the missing-governs gap remains open.

The resource-only diagnostic scorer is intentionally allowed to fire without scope. It is a negative-control strategy used to test whether resource sensitivity alone overpromotes sensitive distractors.

## Hypotheses

H1: Memory-level `resource_sensitivity` combined with a positive `governs` scope match will elevate sensitive memories on read-shaped credential, PII, money-movement, and export queries.

H2: The same scope-gated resource sensitivity rule will avoid elevating unrelated security or policy memories on ordinary read queries such as "What time is the team meeting?"

H3: `resource_sensitivity` without a `governs` scope match is insufficient. If used alone, it should still reproduce the CLAIM-16 clean-read overblock failure.

H4: A target with `resource_sensitivity: credential` and no `governs` field is the boundary test. The resource-plus-scope scorer should treat this as fallback neutral. If it selects the target, that is not evidence that resource sensitivity substituted for `governs`; it means other scoring terms were sufficient. If it fails, the missing-governs gap remains open.

H5: A governs-poisoned resource distractor should expose the failure of resource-only scoring. If a high-sensitivity distractor can beat a correct ordinary-fact target with no matching scope, resource sensitivity requires scope gating just as `governs` required trust and jurisdiction checks.

## Null Results

N1: If a resource-sensitivity-only scorer elevates the unrelated security policy on a clean team-meeting query, `resource_sensitivity` alone is insufficient and scope matching is non-negotiable.

N2: If the scope-gated scorer still overblocks the clean team-meeting query, the architecture has not fixed the CLAIM-16 failure.

N3: If the no-governs credential target is not selected, `resource_sensitivity` helps only when `governs` is present; it does not close the missing-governs gap.

N4: If the scope-gated scorer matches `governance_adjusted_bm25_metadata_text` exactly on all scenarios, CLAIM-17 is not an improvement claim. It is only a schema clarification.

N5: If resource-only scoring elevates a sensitive distractor over a correct ordinary-fact target, resource sensitivity alone is unsafe as a ranking signal.

## Refined Boundary After First Run

The first CLAIM-17 packet showed that "missing `governs`" is too broad as the failure description.

In the no-governs credential boundary case, `governance_adjusted_bm25_metadata_text` selected the target because other authority metadata was present:

- `memory_type: credential`
- `priority: critical`
- `verification_required: true`
- `allowed_action_hint: verify_first`

Score inspection showed that the target received `authority=3.5` and `resource_bonus=0.0`. The case was carried by authority metadata, not by `governs` and not by `resource_sensitivity`.

The sharper boundary is:

> Missing `governs` plus present authority metadata can be recoverable. Missing `governs` plus absent or misleading authority metadata remains open.

The next distinct-value packet should therefore test a sensitive memory that is mislabeled as ordinary context:

- `memory_type: context`
- `priority: normal`
- `verification_required: false`
- `allowed_action_hint: answer`
- no `governs`
- `resource_sensitivity: credential`

The competing distractor should have plausible authority metadata and matching `governs` scope. This tests whether the framework can recover a sensitive memory when the usual authority signals are absent or misleading.

Pre-registered expectation for existing scorers:

- `governance_adjusted_bm25_metadata_text` should lose unless relevance alone carries the target.
- `resource_scope_governance_bm25_metadata_text` should also lose because the target has no `governs` and the scoped resource term is fallback neutral.
- `resource_sensitivity_only_bm25_metadata_text` may recover the target, but if it does, that remains unsafe as a standalone architecture because the first CLAIM-17 packet already showed it overblocks clean read controls.

If this expected failure holds, the honest floor becomes: the framework cannot reliably recover sensitive memories that lack both `governs` and authority metadata. That is the next architecture gap, not a solved problem.

## Packet Requirements

The CLAIM-17 packet should include at least these scenario classes:

1. Read-shaped credential query with a target memory containing both `resource_sensitivity: credential` and matching `governs`.
2. Read-shaped PII query with a target memory containing both `resource_sensitivity: pii` and matching `governs`.
3. Read-shaped money-movement or export query with matching sensitive-resource metadata.
4. Ordinary read negative control where an unrelated high-authority security policy has `resource_sensitivity` but no matching `governs`.
5. Credential target with `resource_sensitivity: credential` and no `governs` field.
6. Sensitive distractor with `resource_sensitivity` but mismatched `governs`, to test whether sensitivity can overpower scope incorrectly.
7. Governs-poisoned resource case where the correct target is an ordinary fact with no `governs`, while a distractor has high `resource_sensitivity` and polished but irrelevant `governs`.

## Strategies To Compare

- `bm25_metadata_text`
- `scope_precedence_role_filter_bm25_metadata_text`
- `governance_adjusted_bm25_metadata_text`
- `directional_action_governance_bm25_metadata_text`
- resource-sensitivity-only diagnostic scorer
- resource-sensitivity-plus-scope diagnostic scorer

## Metrics

For each scenario, record:

- selected target id;
- expected target id;
- expected action;
- actual action;
- trap failure count;
- overblock count;
- query action type;
- selected memory `resource_sensitivity`;
- whether selected memory had matching `governs`;
- whether the resource-sensitivity term affected the score.

## Allowed Wording If Results Hold

> "CLAIM-17 shows that resource sensitivity is useful only as a memory-side consequence label gated by scope. It helps separate read-shaped sensitive disclosures from ordinary read queries, but it does not replace `governs` metadata."

> "The no-governs credential case determines whether resource sensitivity is a partial fallback or only a refinement for already-scoped memories."

## Forbidden Wording

> "Resource sensitivity solves missing `governs`."

> "The framework now handles credentials and PII generally."

> "Query action classification is fixed."

> "Scope matching is optional."

> "CLAIM-17 proves the model generalizes."
