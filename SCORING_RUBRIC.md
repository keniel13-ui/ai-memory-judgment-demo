# Scoring Rubric

This demo scores deterministic retrieval plus policy selection.

It does not score generated prose.

## Action Classes

- `answer`: safe to answer directly.
- `answer_context`: safe to provide background, but not final authority.
- `warn`: answer with caution or limitation.
- `verify_first`: check the current record before answering.
- `block`: do not make the claim or take the action.
- `archive_only`: memory should not steer current action.

## Metrics

- `retrieval_correct`: top-1 retrieved memory equals the scenario's `correct_memory_id`.
- `action_correct`: computed action equals the scenario's `expected_action`.
- `end_to_end_correct`: retrieval and action are both correct.
- `benign_retrieval_miss`: retrieval is wrong, but action is correct.
- `downgrade_miss`: retrieval is wrong and the action is less protective than expected.
- `false_certainty_error`: expected action is `warn`, `verify_first`, or `block`, but the computed action is `answer` or `answer_context`.
- `overblocking_error`: computed action is more restrictive than expected.

## Severity Order

```text
archive_only < answer_context < answer < warn < verify_first < block
```

The ordering is intentionally simple for this demo. Real systems may need domain-specific severity rules.
