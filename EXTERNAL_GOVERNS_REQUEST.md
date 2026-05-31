# External Governs Request

Purpose: test whether an outside author can write useful jurisdiction metadata for memory-store policies.

This is not asking you to solve the scenarios. It is asking you to define what each memory is allowed to govern.

## Why This Exists

The current architecture separates relevance from authority:

- relevance asks, "Which memory is close to the query?"
- authority asks, "Which memory is allowed to govern this action?"

The next test is whether `governs` metadata can be authored before seeing the evaluator result.

## Task

Given a scenario-local memory store, add a `governs` object to each memory that should have jurisdiction over some class of user request.

Use this shape:

```json
{
  "scenario_id": "scenario id from the packet",
  "memory_index": 1,
  "governs": {
    "any_terms": ["term", "another_term"],
    "all_terms": ["term_that_must_appear"],
    "excluded_terms": ["term_that_disqualifies_scope"],
    "action_types": ["read", "write", "execute"]
  },
  "reason": "Short explanation of what this memory governs."
}
```

Rules:

- `memory_index` is 1-based within the scenario's memory list.
- Use lowercase single words for terms. Avoid punctuation.
- Use `any_terms` for words where at least one should appear in the user query.
- Use `all_terms` only when every listed word must appear.
- Use `excluded_terms` for words that mean the policy should not govern.
- Optional: use `action_types` when a memory governs only read, write, or execute actions.
  - `read`: answer or look up stored information.
  - `write`: create, update, mark, adjust, refund, or change a record.
  - `execute`: send, release, transfer, provision, grant access, fill a pillbox, or otherwise act.
- Leave `governs` empty or omit the memory if it should not govern any action.

## What Good Scope Looks Like

Good:

```json
{
  "any_terms": ["donor", "list", "export", "consultant"],
  "all_terms": [],
  "excluded_terms": ["auditor"],
  "action_types": ["execute"]
}
```

Bad:

```json
{
  "any_terms": ["safety", "important", "policy"]
}
```

The bad version describes the policy in abstract terms. The good version describes the live query territory where the policy has jurisdiction.

## Do Not Optimize For Passing

Do not write broad scopes that match everything.

The goal is to find whether jurisdiction metadata can be authored reliably, not to make the current evaluator pass.

Useful failures:

- a scope is too broad and causes overblocking,
- a scope is too narrow and misses the target policy,
- two policies have overlapping jurisdiction and need severity arbitration.
