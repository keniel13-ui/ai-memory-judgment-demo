# I Found a Design Bound for Agent Memory Safety. Now I Need External Pressure.

<!--
HOLD STATUS:
- Do not publish immediately.
- Wait for Felix's blind packet response or 48 hours from 2026-06-01 16:15 EDT.
- If Felix responds and the packet breaks the finding, revise before publishing.
- If no response, publish with "external validation in progress" and update later.
-->

I started with a small question:

Can an agent retrieve the right memory and still take the wrong action?

Agent memory is not just retrieval. It is retrieval plus authorization.

If an agent retrieves a memory that says, "the password is X," the important question is not only whether the memory is relevant. The important question is whether that memory is authorized to let the agent answer, act, verify, block, or refuse.

That distinction led to the most useful result in this project so far.

## The Short Version

Across two internal packet families, I found the same boundary:

- A retriever can find the exact sensitive memory and still answer unsafely.
- A governance-aware retriever can miss the exact memory but still choose a safer action.
- In these packet families, the framework did not achieve both target accuracy and action safety unless sensitive memories carried either `governs` metadata or authority signals.

More precisely:

> Target-accurate retrieval was unsafe when sensitive memories lacked both explicit governance metadata and authority metadata, while authority-signal-driven retrieval preserved action safety but became target-blind.

That is the minimum metadata precondition the internal tests now support.

Not externally validated yet. That part matters.

## The Failure That Made This Clear

In one boundary packet, I created sensitive memories that were mislabeled as ordinary context.

Example shape:

```json
{
  "memory_type": "context",
  "priority": "normal",
  "verification_required": false,
  "allowed_action_hint": "answer"
}
```

The memory contained sensitive information, but the metadata did not tell the action layer that the memory was sensitive.

Then I compared strategies.

The result that mattered most was not the governance-adjusted scorer.

It was the scope-precedence result:

```text
scope_precedence_role_filter_bm25_metadata_text:
  target selected: 3/3
  action correct: 1/3
  false-certainty errors: 2
```

That means it found the right memory every time.

And still produced unsafe answers twice.

Why?

Because the retrieved memories were marked as ordinary answerable context. The action layer had no authority signal to tell it: "this is sensitive; verify first."

Correct memory selection was not enough.

## The Tradeoff

The governance-adjusted scorer behaved differently:

```text
governance_adjusted_bm25_metadata_text:
  target selected: 1/3
  action correct: 3/3
  false-certainty errors: 0
```

That looks worse if you only care about retrieval accuracy.

But it was safer.

It selected a well-tagged policy memory instead of the exact mislabeled sensitive memory. The policy was not the target, so this counted as a trap failure. But because the policy carried authority metadata, the action layer chose `verify_first` instead of confidently answering.

So the framework exposed a real tradeoff:

| Retrieval behavior | Target accuracy | Action safety |
|---|---:|---:|
| Target-accurate retrieval without authority metadata | high | unsafe |
| Authority-signal-driven retrieval | lower | safer |

That is the core finding.

## The Precondition

The result suggests a minimum viable metadata precondition for this framework:

> In these packet families, sensitive memories required either explicit `governs` metadata or authority signals for the framework to consistently preserve action safety.

By authority signals, I mean fields such as:

- `memory_type`
- `priority`
- `verification_required`
- `allowed_action_hint`
- status / supersession metadata

By `governs`, I mean metadata that says what action, resource, or jurisdiction a memory is allowed to control.

If a sensitive memory has neither, the framework degrades in a predictable way:

- relevance-based retrieval may find the sensitive memory and answer unsafely;
- authority-aware retrieval may avoid the unsafe answer, but miss the exact target;
- resource sensitivity alone overblocks clean queries unless it is gated by scope.

That last part was important. I tested a `resource_sensitivity` field too.

Ungated resource sensitivity failed. It elevated sensitive-looking policies even on clean ordinary read queries.

Scope-gated resource sensitivity was safer, but it did not solve the core problem. If the sensitive target had no `governs`, the scoped resource term stayed neutral.

So the finding is not "add one more metadata field and the problem is solved."

The finding is: memory safety depends on whether the system has enough authority metadata to decide what the retrieved memory is allowed to authorize.

## Why This Is Not Just "Metadata Matters"

"Metadata matters" is too vague.

This result is more specific:

- `governs` present + authority absent can still leave action ambiguity.
- authority present + `governs` absent can preserve action safety but become target-blind.
- both absent can produce false-certainty errors.

That split is what made the result useful.

It turned the project from a list of retrieval failures into a sharper design principle:

> Agent memory systems should not treat relevance as authority. If a memory can affect a sensitive action, the memory needs metadata that tells the system what it is allowed to govern or what action class it can authorize.

## The Second Domain Check

Before treating this as a principle, I ran the same conditions in a different domain: industrial safety / hazardous maintenance.

The same pattern appeared.

```text
bm25_metadata_text:
  target selected: 3/3
  action correct: 1/3
  false-certainty errors: 2

scope_precedence_role_filter_bm25_metadata_text:
  target selected: 3/3
  action correct: 1/3
  false-certainty errors: 2

governance_adjusted_bm25_metadata_text:
  target selected: 1/3
  action correct: 3/3
  false-certainty errors: 0
```

Again:

- target-accurate retrieval was unsafe;
- authority-signal-driven retrieval was action-safe but target-blind.

This is still internal evidence. But it is no longer just one domain.

## What I Am Not Claiming

I am not claiming this framework is validated.

I am not claiming these packet sizes are benchmark-grade.

I am not claiming this solves agent memory safety.

The biggest validity threat is circularity: I authored the packet structure, metadata schema, evaluator, and expected actions.

The current claim is narrower:

> Across two internal packet families, the same boundary appeared: target-accurate retrieval was unsafe when sensitive memories lacked both `governs` and authority metadata, while authority-signal-driven retrieval preserved action safety but became target-blind.

That is the honest scope.

## What I Need Next

The next step is external authorship.

I need someone who did not design these packets to write a small memory-retrieval packet in a domain they choose.

The test is simple:

- three short scenarios;
- small memory stores;
- sensitive memories with mixed metadata quality;
- some memories with authority signals;
- some without;
- no `governs` fields unless the author naturally thinks they belong.

Then I run the evaluator blind and report what happens.

The full research repo, packets, and evaluators are public: [github.com/keniel13-ui/ai-memory-judgment-demo](https://github.com/keniel13-ui/ai-memory-judgment-demo). If you want to check the packets or run the evaluator yourself, everything is there.

If the precondition holds, the principle gets stronger.

If it breaks, that is even more useful: it tells us which condition the framework is missing.

## The Question For Builders

If you build agent memory systems, does this pattern match what you have seen?

Have you seen systems retrieve the right memory but take the wrong action because the memory had no authority metadata?

Or the reverse: systems that avoided an unsafe action by following a policy memory, even though they did not retrieve the exact target memory?

That is the feedback I am looking for.

The strongest version of this work will not come from me making bigger claims. It will come from other people trying to break the precondition.
