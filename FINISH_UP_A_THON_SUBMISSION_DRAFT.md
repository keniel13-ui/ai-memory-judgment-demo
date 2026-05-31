# I Published an AI Memory Result. Then Real Retrieval Broke Everything.

This is a submission for the [GitHub Finish-Up-A-Thon Challenge](https://dev.to/challenges/github-2026-05-21).

## What I Built

I built the **AI Memory Judgment Demo**, a public research framework for testing whether AI agent memory can govern actions correctly.

The question is not only:

> Did the system retrieve the closest memory?

The harder question is:

> Did the retrieved memory have authority to determine the action?

The demo tests whether memory systems answer when safe, verify when uncertain, and block when required.

Repository:

https://github.com/keniel13-ui/ai-memory-judgment-demo

The public repo includes:

- structured memory stores with policy, correction, credential, and context layers,
- adversarial scenarios with semantically tempting distractors,
- deterministic evaluators for TF-IDF, BM25, local embeddings, role filtering, scope filtering, and action-type precedence,
- a public claim ledger that tracks each finding with evidence, weaknesses, allowed wording, and forbidden overclaims,
- fresh-author `governs` tests that check whether separate model instances can write useful jurisdiction metadata before seeing the evaluator result.

The project started privately before the public repo existed.

The file-backed timeline is:

- **April 30:** portable AI memory transfer pack existed (`AI_MEMORY/README.md`, `AI_MEMORY/Identity.md`).
- **May 22:** correction-memory artifacts and playbook files existed.
- **May 24:** first private reset-evaluation harness existed (`run_ai_memory_reset_eval.py`, `AI_MEMORY_RESET_EVAL_SCENARIOS_2026-05-24.json`, `AI_MEMORY_RESET_EVAL_RESULTS_2026-05-24.md`).
- **May 25:** blind packet and v0.3 eval artifacts existed.
- **May 26:** six-file demo became the bridge toward a public inspectable artifact.
- **May 29-31:** the public repo grew into the authority-arbitration research arc: CLAIM-08 through CLAIM-14, plus Article 09.

So the real "before" was not an abandoned public repo. It was private diagnostic work that was not packaged, reproducible, or public.

The finish-up was turning that work into an inspectable public framework.

## Demo

Clone and run the main scenario-local evaluator:

```bash
git clone https://github.com/keniel13-ui/ai-memory-judgment-demo.git
cd ai-memory-judgment-demo
python3 run_memory_store_eval.py
```

No API key is required for the deterministic lexical and role-filter runs.

Local embedding strategies use Ollama if available:

```bash
OLLAMA_EMBED_MODEL=nomic-embed-text:latest python3 run_memory_store_eval.py
```

Recent writeup:

[In This Memory Test, Relevance Wasn't Authority](https://dev.to/zep1997/in-this-memory-test-relevance-wasnt-authority-3d05)

## The Comeback Story

The first private result was encouraging.

On May 24, the reset-evaluation harness compared a summary-only memory baseline against layered memory. In six reset/recovery scenarios, summary-only memory scored `3/12` while layered memory scored `9/12`.

That was useful, but it was not enough.

The early harness mostly tested whether memory could preserve safer action boundaries after a reset. It did not yet test the harder retrieval problem:

> What happens when the agent has to find the right memory instead of being handed it?

When retrieval entered the loop, the work changed.

Related memories started winning over stricter memories. Concrete operational distractors beat abstract safety policies. Sometimes the system produced the right action from the wrong memory, which meant action correctness alone could hide a bad retrieval.

The first big lesson was:

> Retrieval accuracy and action correctness can diverge.

Then a harder result appeared:

> Relevance is not authority.

I tested lexical retrieval and local embedding retrieval on fresh-authored scenario-local stores. One embedding model did not fix the failure family. In two cases, it regressed because the semantically close memory answered the surface question, while the correct memory was the one authorized to govern the action.

That led to the architecture change.

Instead of asking retrieval to solve everything, I separated the problem:

- relevance: which memory is close to the query?
- authority: which memory is allowed to govern the action?

The first role-filter strategy created an authority lane for active policy, credential, and correction memories. On the five-scenario adversarial packet, it reached:

| Strategy | Target selected | Action correct | Trap failures |
|---|---:|---:|---:|
| `bm25_metadata_text` | 3/5 | 4/5 | 2 |
| `nomic_embed_metadata_text` | 1/5 | 3/5 | 4 |
| `role_filter_bm25_metadata_text` | 5/5 | 5/5 | 0 |

Then the project had to get more honest.

Metadata-noise tests showed the role filter could overblock when broad or competing policies polluted the authority lane. Scope-aware `governs` metadata fixed those controlled overblocks, but only when the scope metadata was good.

So I tested fresh-authored scope metadata.

Three separate fresh model passes all preserved the clean result on the first packet. Then a harder clutter packet exposed two new failures:

- adjacent policies with overlapping vocabulary,
- read-only queries accidentally triggering write/execute policies.

That led to CLAIM-14: specificity precedence plus `action_types`.

Two separate fresh action-type passes on the clutter packet both reached:

| Strategy | Target selected | Action correct | Trap failures | Overblocking |
|---|---:|---:|---:|---:|
| `scope_precedence_role_filter_bm25_metadata_text` | 5/5 | 5/5 | 0 | 0 |

The point is not that this solves AI memory.

It does not.

The strongest remaining threat is architecture-overfitting to the clutter packet family. The next meaningful test is a genuinely new held-out clutter packet authored without knowledge of the observed failures or the resulting architecture.

But the project is now public, reproducible, and honest about its own limits.

Before:

> private memory/reset experiments, article drafts, and a local eval harness that were not packaged or public.

After:

> a public repo with deterministic evaluators, adversarial stores, fresh-author tests, a claim ledger, audit protocols, and a nine-article research arc.

That is the finish-up.

## My Experience with GitHub Copilot

I need to be direct here: GitHub Copilot was not part of this build.

The AI development partners were Claude Code and Codex. The subject of the research was also AI agents: how memory, retrieval, corrections, and authority rules change what an agent is allowed to do.

What GitHub provided was the part I did not realize I needed at the beginning: accountability.

GitHub made the work inspectable:

- every result is tied to a file,
- every claim is tied to a commit,
- every overclaim is written down in `CLAIM_LEDGER.md`,
- every evaluator can be rerun,
- every public article points back to the artifacts that produced it.

That changed the project.

Without GitHub, this could have stayed a collection of private notes and confident claims.

With GitHub, it became something other people can inspect, rerun, criticize, and build on.

That is also why the repo includes uncomfortable files: validity threats, forbidden wording, skeptical audit prompts, and failed intermediate strategies. The purpose was not to look clean. The purpose was to make the research harder to fool.

## What Changed

I started with a question:

> Can AI memory survive a reset?

I ended with a harder one:

> Can an AI system distinguish the memory that answers a query from the memory that is allowed to govern the action?

That second question is where the project became worth finishing.

It is not benchmark-grade validation. It is a public, inspectable research note about failure, correction, and architecture.

That is what I finished.

---

Tags: `devchallenge`, `githubchallenge`, `ai`, `machinelearning`

