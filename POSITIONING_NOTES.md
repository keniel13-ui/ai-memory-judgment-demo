# Positioning Notes

Status: public-framing guardrails after external feedback.

## Strongest External Restatement

Nate's AI produced the cleanest current summary:

> Retrieval quality without judgment quality can make systems more dangerous.

This should be preserved as a useful framing line.

It captures the central distinction:

- retrieval quality: did the system retrieve something relevant?
- judgment quality: did the retrieved memory authorize the right behavior?

## What The Work Is

This work is best framed as:

> memory governance for persistent agents

or:

> policy-aware retrieval evaluation

or:

> action-class authority evaluation

The thesis:

> Memory retrieval should not only give an agent relevant context. It should tell the agent what that memory is allowed to authorize.

## What The Work Is Not

Do not imply:

- memory architecture alone is the missing ingredient for AGI,
- memory governance solves planning, causal reasoning, world modeling, agency boundaries, verification, or tool orchestration,
- the current repo is a solved technical architecture,
- the current result is benchmark-grade evidence.

Better wording:

> Memory governance is one necessary pillar for reliable persistent agents, not the whole architecture.

## Three Status Buckets

Every public claim should be labeled mentally as one of these:

| Bucket | Meaning | Example |
|---|---|---|
| Empirical result | Shown in the repo at current scale | `nomic-embed-text` got `9/10` retrieval and retained one downgrade miss |
| Framework claim | Proposed evaluation/design lens | memory should carry allowed action, not only content |
| Speculative architecture | Future-facing direction | long-lived agents may need memory governance to avoid state decay |

The writing must not blur these buckets.

## Current Strongest Empirical Claim

Safe:

> In this small diagnostic dataset, several retrieval methods retrieve a related but weaker correction for `s02`, producing a downgrade miss from `block` to `warn`.

Unsafe:

> Retrieval methods cannot solve this class of failure.

Why unsafe:

- top-k has not been inspected yet,
- reranking has not been tested,
- external scenarios have not been tested.

## Current Strongest Framework Claim

Safe:

> Agent memory evaluation should include action-class consequences alongside retrieval accuracy.

Unsafe:

> Retrieval accuracy is the wrong metric.

Better:

> Retrieval accuracy is necessary but incomplete when retrieved memory influences actions.

## Tone Guardrail

The writing can be philosophical, but technical claims need labels.

Use:

- "This suggests..."
- "In this dataset..."
- "The framework proposes..."
- "A future architecture may..."

Avoid:

- "This proves..."
- "This solves..."
- "The future is..."
- "Agents will..."

## Review Burden

Being early increases the burden of proof.

If reviewers do not yet have established standards for memory governance, the repo must make the standard visible:

- claim ledger,
- preregistration,
- metrics,
- failure taxonomy,
- reviewer panel,
- external scenarios,
- adversarial tests,
- top-k/reranking comparisons.

