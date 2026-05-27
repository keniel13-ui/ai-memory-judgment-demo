# Experiment Plan

This plan converts the current public demo into a sequence of increasingly comparable experiments.

## v0.1 Current Public Demo

Status: complete.

Scope:

- deterministic lexical retrieval,
- 10 internally authored scenarios,
- 21 memory objects,
- TF-IDF and BM25 across 3 text-construction strategies,
- consequence-oriented action metrics.

Claim:

- useful diagnostic artifact,
- not benchmark-grade,
- not externally validated.

## v0.2 Semantic Baseline Upgrade

Goal:

Compare current lexical strategies against semantic retrieval.

Candidate additions:

- embedding retrieval,
- hybrid lexical + embedding retrieval,
- top-k retrieval,
- timing measurements.

Success criteria:

- same scenario labels,
- same memory pool,
- same action policy,
- raw outputs committed,
- latency reported.

## v0.3 Semantic Retrieval Upgrade

Goal:

Test whether policy aggregation across multiple retrieved memories fixes the s02 downgrade miss without creating false certainty.

Candidate additions:

- top-k aggregation.

Success criteria:

- report whether `s02_overclaim_eval_results` retrieves the stricter overclaiming correction,
- report any new false-certainty or overblocking failures,
- report cost/latency if an external embedding API is used.

## v0.4 External Scenario Set

Goal:

Reduce author bias.

Procedure:

- accept 20-50 scenarios from someone who did not author the memory objects,
- freeze labels before running,
- record scenario author role and instructions,
- preserve rejected/ambiguous scenarios in a separate notes file.

Success criteria:

- external scenario packet committed,
- scoring rubric unchanged before run,
- results reported separately from internal scenario set.

## v0.5 Model-In-The-Loop Generation

Goal:

Test whether retrieval/action policy changes generated answers, not only deterministic action labels.

Procedure:

- run baseline memory and structured memory conditions,
- keep prompt constant,
- score outputs blind where possible,
- separate task success, epistemic handling, citation/provenance behavior, and false certainty.

Success criteria:

- raw outputs saved,
- scoring sheet saved,
- scorer identity or blinding method disclosed,
- limitations stated.

## v1.0 Paper-Style Report

Goal:

Produce a paper-style technical report, not a claim of journal acceptance.

Suggested structure:

1. Abstract
2. Introduction
3. Research questions
4. Related work
5. Method
6. Dataset
7. Metrics
8. Results
9. Discussion
10. Validity threats
11. Conclusion
12. Reproducibility appendix
