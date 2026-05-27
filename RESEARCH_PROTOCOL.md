# Research Protocol

Status: protocol upgrade for a public lab artifact. Not a journal submission.

This document translates the demo into a more formal research shape so the next versions can be compared, criticized, and extended without changing the claim after seeing the result.

## Research Question

Can structured memory metadata and access-policy action classes expose retrieval failures that ordinary top-1 retrieval accuracy would hide?

## Hypothesis

Evaluating a memory system by retrieval correctness alone is incomplete. A wrong retrieval can have different downstream consequences:

- harmless if the action class remains correct,
- harmful if it produces false certainty,
- harmful if it downgrades a needed safety constraint,
- costly if it overblocks a safe action.

## Current Experiment

This repository tests deterministic lexical retrieval strategies over a small sanitized memory pool:

1. TF-IDF over content only.
2. TF-IDF over metadata plus content.
3. TF-IDF over metadata, content, and retrieval terms.
4. BM25 over content only.
5. BM25 over metadata plus content.
6. BM25 over metadata, content, and retrieval terms.

The evaluator retrieves one memory for each scenario, computes the memory's allowed action, and compares both retrieval and action against predeclared labels.

## Unit Of Analysis

One row equals:

- one scenario query,
- one retrieval strategy,
- one top-1 retrieved memory,
- one computed action class.

## Dataset

Current public dataset:

- 6 memory files.
- 21 memory objects.
- 10 internally authored scenarios.
- 6 retrieval-method/text-construction strategies.
- 60 scored rows.

The dataset is intentionally small. It is useful for inspecting failure shape, not for claiming generalization.

## Variables

Independent variable:

- retrieval method and text-construction strategy.

Dependent variables:

- top-1 retrieval correctness,
- action-class correctness,
- end-to-end correctness,
- false-certainty errors,
- downgrade misses,
- overblocking errors,
- benign retrieval misses.

Controlled conditions:

- same memory pool,
- same scenario set,
- same action-policy rules,
- same deterministic TF-IDF implementation.

## Metrics

Primary metrics:

- `false_certainty_errors`: expected `warn`, `verify_first`, or `block`; got `answer` or `answer_context`.
- `downgrade_misses`: wrong memory retrieved and action less protective than expected.
- `action_correct`: computed action equals expected action.

Secondary metrics:

- `retrieval_correct`: top-1 retrieved memory equals expected memory.
- `end_to_end_correct`: retrieval and action are both correct.
- `overblocking_errors`: computed action is more restrictive than expected.
- `benign_retrieval_misses`: wrong memory retrieved, but action remains correct.

The primary metrics are consequence-oriented because the framework is concerned with judgment failure, not only retrieval failure.

## Baselines

Current baseline:

- deterministic TF-IDF over `content_only`.

Planned baselines:

- embedding retrieval,
- hybrid lexical + embedding retrieval,
- multi-memory retrieval with policy aggregation,
- summary-only memory baseline,
- model-in-the-loop generation scored by blinded rubric.

## Procedure

1. Freeze memory objects and scenarios.
2. Run each retrieval strategy against the same scenario set.
3. Store raw JSON results.
4. Store generated Markdown table.
5. Interpret failures using the failure taxonomy.
6. Do not change the claim posture after seeing results.

## Reproducibility

Run:

```bash
python3 run_retrieval_eval.py
```

Expected outputs:

- `results/retrieval_eval_results.md`
- `results/retrieval_eval_results.json`

No network access, API keys, LLM calls, or external services are required for the current deterministic run.

## Validity Threats

Internal validity:

- Scenarios and memory objects were written by the framework author.
- Retrieval terms may encode author knowledge.
- The memory pool is small enough that accidental alignment is plausible.

External validity:

- The task does not prove behavior on larger memory stores.
- The task does not prove behavior under adversarial users.
- The task does not test production latency, cost, privacy, permissions, or live database/source access.

Construct validity:

- `correct_memory_id` assumes one expected memory per scenario, but real agents may need multiple memories.
- Action-class labels are framework-specific and may need domain-specific severity ordering.
- The current evaluator does not score natural-language generation quality.

Conclusion validity:

- Ten scenarios are too few for statistical claims.
- The result should be read as diagnostic evidence, not benchmark evidence.

## Reporting Standard For Future Versions

Each future result should report:

- version,
- dataset size,
- retrieval methods,
- memory count,
- scenario count,
- predeclared metrics,
- raw outputs,
- known limitations,
- changes from the previous version.

## Next Scientific Upgrade

The smallest useful upgrade is not another article. It is a v0.2 protocol run with:

1. at least one semantic retrieval baseline,
2. a larger scenario set,
3. external or blinded scenario authorship,
4. timing measurements,
5. frozen pre-run labels.
