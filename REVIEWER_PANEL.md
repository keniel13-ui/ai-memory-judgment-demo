# Reviewer Panel

Six reviewer personas. Each attacks the work from a different angle. Their objections are not hypothetical — they are the objections a real reviewer in that role would raise.

Use this before publishing any new claim. Ask: would each reviewer accept this? If not, what would make them accept it?

---

## Reviewer 1 — ML / RAG Systems Researcher

**Profile:** Has published on retrieval-augmented generation evaluation. Familiar with RAGAS, ARES, BEIR, and the LoCoMo/LongMemEval benchmarks. Cares about methodology, baselines, and reproducibility.

**First question they ask:**
> "What is your baseline? If you don't have a retrieval-accuracy-only baseline, you can't claim your metric adds information."

**Primary objections:**

1. The current baselines (TF-IDF, BM25, local Ollama embeddings) are weak. A proper comparison needs dense retrieval with a retrieval-optimized model (e.g., nomic-embed-text, text-embedding-3-small, or a fine-tuned bi-encoder).

2. You compare retrieval accuracy to action accuracy across methods. That is not a controlled comparison. To claim the failure taxonomy adds information, you need to show: given the same retrieval accuracy, the failure taxonomy produces different risk assessments.

3. The top-1 retrieval assumption is limiting. Real RAG systems retrieve top-k and re-rank. Showing results only for top-1 is an artifact of the experimental setup, not a property of the underlying problem.

**What would satisfy this reviewer:**
- At least one dedicated retrieval embedding model (nomic-embed-text is free and local)
- A table showing two strategies with equal retrieval accuracy but different failure-class distributions
- Top-k experiment to show whether policy aggregation changes the safety outcome

**Their likely verdict on current artifact:**
> "Interesting framework. Too early to evaluate. The baselines are not strong enough to make the divergence claim convincing. Come back with nomic-embed and top-3 results."

---

## Reviewer 2 — Systems / Production Reliability Engineer

**Profile:** Has built or evaluated production agent pipelines. Cares about latency, cost, failure modes at scale, and whether the framework is actually deployable.

**First question they ask:**
> "How does this perform at 10,000 memories, not 21? And what does it cost to run?"

**Primary objections:**

1. The embedding experiment takes 97 seconds to embed 21 memories. That is not production-viable. At 10,000 memories, this would take hours unless you use pre-computed embeddings with incremental updates.

2. The action-class computation is deterministic given a memory object. But who maintains the metadata? In a real system, memory objects are written by agents, not human-curated authors. The action-class taxonomy assumes high-quality metadata that may not exist in the wild.

3. There is no mechanism for handling memory conflicts beyond retrieving the top-1. What happens when two memories with conflicting action classes are both retrieved?

**What would satisfy this reviewer:**
- Pre-computed embedding timing (embed once, query fast — what is query-only latency?)
- A discussion of how memory metadata is generated and maintained in production
- Top-k policy aggregation: how does the framework handle two retrieved memories where one says `warn` and the other says `block`?

**Their likely verdict on current artifact:**
> "Useful framing problem. Not production-ready. Timing numbers suggest the embedding path needs a dedicated vector store, not llama3 running locally. The metadata dependency is an unresolved assumption."

---

## Reviewer 3 — AI Safety / Alignment Researcher

**Profile:** Cares about failure modes, harm severity, and whether the safety claims hold under adversarial conditions. Skeptical of systems that claim safety properties without adversarial testing.

**First question they ask:**
> "What is the failure mode of your gating rules? You have 0 false-certainty errors, but you built the gating rules. Have you tried to break them?"

**Primary objections:**

1. The 0 false-certainty finding is based on a non-adversarial dataset. Scenarios were designed to test the normal operation of the framework, not to find its failure boundary. Safety properties must be tested adversarially.

2. The action class taxonomy (answer, warn, verify_first, block, archive_only) has no external validation. It represents one design choice. A different taxonomy could produce different "safe" and "unsafe" classifications.

3. The framework tests policy computation, not policy enforcement. If an LLM ignores the action class in generation, the safety property disappears entirely.

**What would satisfy this reviewer:**
- At least 5 adversarial scenarios designed to bypass gating rules
- External review of the action class severity ordering
- A generation experiment showing a model either respects or violates action class constraints

**Their likely verdict on current artifact:**
> "The taxonomy is interesting and the gating-rules-as-safety-floor observation is worth investigating. But 0 false-certainty errors on a non-adversarial dataset is not evidence of safety. You need to build tests that try to produce false certainty, not just tests that confirm normal operation."

---

## Reviewer 4 — Statistician / Methodology Reviewer

**Profile:** Cares about sample size, statistical validity, pre-registration, and whether conclusions are licensed by the data.

**First question they ask:**
> "What is the statistical power of a 10-row comparison?"

**Primary objections:**

1. 10 scenarios is not enough to compute meaningful differences between strategies. A 9/10 vs 10/10 difference has no statistical significance at this scale — it is exactly one data point.

2. The scenarios were not pre-registered. You observed the results and then described the patterns. Post-hoc observation of patterns in a 10-row table is not hypothesis testing.

3. The "benign-miss locality" observation (CLAIM-03) is 4 data points. No conclusion should be drawn from 4 data points.

**What would satisfy this reviewer:**
- Pre-register a hypothesis before running the next experiment: "We predict that metadata-enriched embedding will produce fewer cross-class benign misses than content-only embedding."
- At least 50 scenarios to compute meaningful rates
- Confidence intervals or bootstrap estimates on the key metrics

**Their likely verdict on current artifact:**
> "The framework description is useful. The empirical component is exploratory. Nothing in the results tables should be stated as a finding — they should be stated as observations that motivated the following hypothesis. If you want to make claims, you need 50+ scenarios and pre-registration."

---

## Reviewer 5 — Epistemology / Provenance Researcher

**Profile:** Comes from database systems or knowledge representation. Familiar with provenance literature (Why, How, Where provenance). Cares about whether the "judgment lineage" framing is coherent and whether it adds to existing provenance frameworks.

**First question they ask:**
> "How is 'judgment lineage' different from 'data provenance'? Provenance already tracks where data came from and what transformations produced it."

**Primary objections:**

1. The term "judgment lineage" is evocative but needs precise definition. What exactly is a judgment? What makes a lineage of judgments different from a sequence of retrieval operations?

2. The action class taxonomy is not a provenance artifact — it is a policy artifact. Provenance tells you where something came from. Policy tells you what you are allowed to do with it. These are different dimensions. The work conflates them.

3. If the framework is provenance-aware, where is the lineage tracking? The current artifact stores metadata about memory source and authority, but it does not trace how a current judgment was influenced by past corrections.

**What would satisfy this reviewer:**
- A precise definition of "judgment lineage" distinct from data provenance
- A formal separation of provenance claims (where did this memory come from) and policy claims (what is this memory allowed to authorize)
- An example of lineage tracing: showing that a specific current judgment is the result of a chain of corrections, and that the chain is traceable

**Their likely verdict on current artifact:**
> "The framing is interesting but imprecise. 'Judgment lineage' conflates provenance with policy. The framework as implemented is a memory access policy with metadata enrichment — calling it lineage-based overstates the architectural commitment. Either implement actual lineage tracing or narrow the framing to 'authority-tagged memory access policy.'"

---

## Reviewer 6 — Domain Application Reviewer

**Profile:** A practitioner who builds real agent systems — customer support, legal research, clinical decision support, code generation. Cares about whether the framework applies to their use case.

**First question they ask:**
> "Your scenarios are about your own AI memory research project. Does this work for any other domain?"

**Primary objections:**

1. The memory objects describe a meta-domain (AI memory research) where the agent is reasoning about its own architecture. This is the easiest domain for an authority policy to work — the memories are structured, the authority relationships are explicit, and the queries are well-formed.

2. Real domains have noisy memory objects. A customer support agent's memory is full of partial updates, contradictory tickets, and ambiguous policies. The clean structured memories in this dataset do not resemble real production memory stores.

3. The action classes (answer, warn, verify_first, block, archive_only) are generic. Different domains need different action taxonomies. A medical agent needs `refer_to_specialist` or `do_not_act_without_confirmation`. A legal agent needs `cite_with_caveat` or `defer_to_jurisdiction`. The framework's value depends on whether the taxonomy is configurable.

**What would satisfy this reviewer:**
- Apply the framework to one non-meta domain (customer support, code review, or Q&A over a public knowledge base)
- Show that the action class taxonomy can be adapted to domain-specific severity orderings
- Include at least one scenario with noisy or conflicting memory objects

**Their likely verdict on current artifact:**
> "Useful for the demonstrated domain. Unknown whether it generalizes. The cleanness of the memory objects makes the framework look better than it would in a real deployment. Show me this working on a messy real-world memory store and I'll be interested."

---

## Running the panel

Before publishing any new claim, ask:

1. Does the ML reviewer accept the baseline comparison?
2. Does the systems reviewer accept the scalability and metadata assumptions?
3. Does the safety reviewer accept the adversarial coverage?
4. Does the statistician accept the sample size and pre-registration?
5. Does the provenance reviewer accept the lineage framing?
6. Does the domain reviewer accept the generalizability?

A claim that fails any of these panels must either be narrowed, caveated, or tested before publication.

Current status by panel:

| Reviewer | Current verdict |
|---|---|
| ML / RAG | Baseline too weak. Come back with nomic-embed and top-k. |
| Systems | Timing and metadata dependency unresolved. |
| Safety | No adversarial coverage. 0 FC errors on non-adversarial set is not safety evidence. |
| Statistician | 10 scenarios is exploratory, not findings. Pre-register next experiment. |
| Provenance | "Judgment lineage" conflates provenance and policy. Needs precise definition. |
| Domain | Meta-domain only. Unknown generalization. |
