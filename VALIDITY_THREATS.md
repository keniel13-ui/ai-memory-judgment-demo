# Validity Threats

Status: explicit risk register for the current public demo and the next experiment version.

## Internal Validity

- The memory objects and scenarios were written by the framework author.
- Retrieval labels may encode the author's understanding of the memory pool.
- Query phrasing may accidentally favor the current memory schema.
- The action-class ordering is deterministic, but the severity order is framework-specific.
- The current hard failure is concentrated in one scenario, `s02_overclaim_eval_results`.

## External Validity

- Ten scenarios are too few to generalize.
- The memory pool is tiny compared with production agent memory stores.
- The task does not test adversarial users, live databases, live permissions, or changing source state.
- The sanitized public memory objects may not preserve all difficulty from the private development context.
- The current evaluator does not include LLM generation, tool use, or multi-step planning.

## Construct Validity

- Top-1 retrieval may be the wrong retrieval surface for judgment-lineage systems; real agents may need multiple memories.
- `correct_memory_id` assumes a single expected memory, while real decisions can depend on several memories.
- Action classes such as `answer`, `warn`, `verify_first`, and `block` may need domain-specific definitions.
- The current `false_certainty_error`, `downgrade_miss`, `overblocking_error`, and `benign_retrieval_miss` categories need external pressure before they can be treated as stable.

## Conclusion Validity

- Current results are diagnostic, not statistical.
- A 9/10 result over 10 scenarios is not benchmark evidence.
- Zero false-certainty errors in this demo is not proof that the framework prevents false certainty.
- The downgrade miss is useful because it is interpretable, not because one case proves general behavior.

## Related-Work Risk

The biggest novelty risk is overlap with memory-to-action and retrieval-utilization work.

- Retrieval-versus-utilization papers already show that retrieval accuracy alone is incomplete.
- Mem2ActBench may already cover parts of action-level memory evaluation.
- RAGAS and ARES already evaluate faithfulness and context relevance for RAG systems.
- TierMem already addresses provenance and lossy summaries.

The narrower defensible claim is therefore:

> This repo evaluates whether retrieval failures cross action-authority boundaries, and classifies those failures by safe or unsafe direction.

## Mitigations For v0.2+

- Add embedding and hybrid retrieval baselines.
- Freeze labels before running new experiments.
- Add externally authored scenarios from someone who has not read the memory files.
- Report failure-class distributions, not only top-1 accuracy.
- Compare against Mem2ActBench's taxonomy before claiming novelty.
- Publish raw outputs and scripts for every run.
