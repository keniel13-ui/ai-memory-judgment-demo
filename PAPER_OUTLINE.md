# Paper-Style Report Outline

Working title:

> Evaluating Agent Memory By Judgment Consequences, Not Retrieval Accuracy Alone

## Abstract

State the problem, the artifact, the current dataset size, the metrics, the key failure observed, and the limitation that this is not benchmark-grade evidence.

## 1. Introduction

- Long-running agents increasingly depend on memory.
- Most memory discussions focus on storage, retrieval, and context length.
- This report focuses on what a retrieved memory is allowed to do.
- Core claim: retrieval misses should be scored by downstream judgment consequences.

## 2. Research Questions

RQ1: Does retrieval correctness alone hide action-relevant memory failures?

RQ2: Can action-class scoring distinguish false certainty, downgrade misses, overblocking, and benign retrieval misses?

RQ3: Does metadata-enriched retrieval text change the failure shape compared with content-only retrieval?

## 3. Related Work

Areas to review:

- agent memory systems,
- retrieval-augmented generation,
- provenance and citation in AI systems,
- database/query provenance,
- uncertainty calibration,
- benchmark design and validity threats.

## 4. Framework

- Judgment-lineage memory.
- Six memory layers.
- Authority policy.
- Access policy.
- Action classes.

## 5. Method

- Memory object schema.
- Scenario construction.
- Retrieval strategies.
- Action-policy computation.
- Scoring rules.
- Reproducibility procedure.

## 6. Dataset

- 21 memory objects.
- 10 scenarios.
- Sanitized public artifact.
- Internally authored limitation.

## 7. Metrics

- Retrieval correctness.
- Action correctness.
- End-to-end correctness.
- False-certainty errors.
- Downgrade misses.
- Overblocking errors.
- Benign retrieval misses.
- Future operational metrics: latency, throughput, cost.

## 8. Results

Summarize current table.

Emphasize the hard case:

- `s02_overclaim_eval_results`
- expected `block`
- retrieved related but weaker correction
- got `warn`
- failure type: downgrade miss.

## 9. Discussion

- Why the hard case matters.
- Why top-1 retrieval accuracy is not enough.
- Why right-neighborhood/wrong-severity is a distinct failure.
- What the current result does and does not imply.

## 10. Validity Threats

- Internal authorship.
- Small scenario set.
- Sanitized rewrite changes behavior.
- No modern retrieval baselines yet.
- No generation scoring yet.
- No external replication.

## 11. Future Work

- BM25.
- Embeddings.
- Hybrid retrieval.
- External scenarios.
- Multi-memory retrieval.
- Model-in-the-loop generation.
- Blind scoring.
- Database/provenance-connected agent cases.

## 12. Conclusion

The current artifact does not prove the framework. It shows a measurable failure category: a memory retrieval can be semantically nearby but insufficiently protective. That is why memory evaluation should include judgment-consequence metrics.

