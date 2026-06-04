# Memory Authority Security Guidance

This repo studies agent memory authority and retrieval safety. When working in this codebase, apply the following checks before writing or modifying evaluators, packets, or scoring logic.

## Authority Metadata Checks

When writing or reviewing memory objects:

- Every `policy` or `credential` memory must carry at least one authority signal: `memory_type`, `priority: high/critical`, `verification_required: true`, or a well-formed `governs` field.
- If `governs` is present, `action_types` must be set. An empty `action_types` list is a metadata gap, not a safe default.
- A memory with `allowed_action_hint: answer` and `memory_type: context` should never contain sensitive content (credentials, PII, safety-critical procedures). Flag and require review.
- Do not add `governs` to preference or context memories. The field implies authority. Misapplying it creates a false-authority signal the scorer will amplify.

## Evaluator Checks

When writing or modifying evaluators:

- Every new strategy must be pre-registered before the packet is run. Write the prediction first. Run second.
- Do not modify a packet after authoring and before running. Lock it, then evaluate.
- If adding a new scoring term, record the expected weight direction in a comment. The term's name is not enough to convey whether higher is better or worse.
- Score decompositions are required for all failure cases. A table showing which terms drove the wrong selection is not optional — it is the finding.

## Claim Hygiene

- Do not write "improves over" without a held-out result. Stress packet results support "matches" or "differs from" — not improvement claims.
- Do not write "solves" or "prevents" for any retrieval or scoring mechanism. Use "reduces the rate of" or "catches in these packet families."
- Every published claim must map to a `CLAIM_LEDGER.md` entry. No claim should appear in an article that is not in the ledger.
- If a result falsifies a prior claim, update the ledger entry and note the falsification before publishing any new article.

## Packet Authorship Rules

- Held-out packets must be authored by a fresh model instance with no formula context.
- The authoring model must not receive: the scoring formula, expected strategy behavior, CLAIM stress results, or hints about which scenarios should pass or fail.
- Record the model ID, date, and no-formula-context confirmation in the preregistration file.

## Common Authority Mistakes to Flag

- `governs` field present but `any_terms` is empty — the scope term contributes zero even though `governs` exists
- `verification_required: false` on a `memory_type: credential` memory — contradictory metadata
- `priority: low` on a memory with `governs.action_types: ["execute"]` — authority weight will be suppressed
- `allowed_action_hint: answer` on a memory with `verification_required: true` — action hint contradicts verification flag
- `status: superseded` without a `superseded_by` pointer — the status penalty fires but the replacement is unresolvable
