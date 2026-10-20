# CLAUDE.md

Guidance for Claude Code (and other coding agents) working in this repository.

## What this repo is

A public, sanitized research trail on AI agent memory reliability: which
memory is allowed to govern an action, not just which memory is relevant.
Every public claim is tracked in `CLAIM_LEDGER.md` with evidence, status,
weaknesses, and allowed and forbidden wording. The code is a set of small,
deterministic, stdlib-only Python evaluators. See `docs/ARCHITECTURE.md`.

## Ground rules (evaluation validity comes first)

1. **Do not edit recorded evidence.** That includes `results/`,
   `claim_*/results.{md,json}`, `results/*_full_run_*.txt`, scenario packets
   in `scenarios/` and `external_scenarios/`, claim folder fixtures
   (`scenarios*.json`, `*_envelope.json`, `role_profile.json`,
   `observer_rules.json`, `fixture_manifest.json`), the memory layers
   `01_persistence.md` to `06_access_policy.md`, pre-registrations, breaker
   verdicts, and `results/evaluation_log.jsonl` (append only, via the script).
2. **Do not run evaluators in the working copy unless you mean to record a new
   run.** They overwrite committed artifacts, and several no longer reproduce
   from the default command. Use a scratch worktree; see
   `docs/DEVELOPMENT.md` and the `reproduce-results` skill.
3. **Hash-pinned code.** These files are pinned by sha256 in
   `results/evaluation_log.jsonl` or in `claim_24` breaker verdicts. Editing
   them, even cosmetically, breaks the evidence link:
   `claim_24/{fipsign_source_adapter,run_fipsign_live_eval,rederivation_gate,mandate_cell7,run_mandate_cell7,test_mandate_cell7,gate_interface}.py`,
   `claim_24/scenarios.json`, `claim_29/evaluator.py`,
   `claim_29/verify_frozen28_must_pass.py`, `claim_30/evaluator.py`,
   `claim_31/evaluator.py`. Raise problems in a PR description instead.
4. **Pre-register before running.** A new strategy or packet gets its
   prediction written down first, the packet is locked, then it is run. See
   `.claude/claude-security-guidance.md`.
5. **Claim wording.** Never write "solves", "proves", "production-ready", or
   "improves over" without a held-out result. Every public statement must map
   to a `CLAIM_LEDGER.md` entry and respect its forbidden wording.
6. **Stdlib only.** Do not add runtime dependencies.

## Commands

```bash
python3 scripts/append_eval_log.py verify                   # expect chain_ok=True
python3 scripts/check_authority_patterns.py --all --warn-only
cd claim_24 && python3 -m unittest test_mandate_cell7        # CLAIM-24 unit tests
```

Reproduce an evaluator without touching the working copy:

```bash
git worktree add --detach ../amj-repro HEAD
cd ../amj-repro && OLLAMA_BASE_URL=http://127.0.0.1:9 python3 run_retrieval_eval.py && git status --short
cd - && git worktree remove --force ../amj-repro
```

## Layout

- `0N_*.md`: memory layers; memory objects are fenced JSON blocks.
- `scenarios/retrieval_scenarios.json`: current 12-scenario set. The
  root-level `retrieval_scenarios.json` and `retrieval_eval_results.*` are an
  early 10-scenario upload (2026-05-26, three TF-IDF strategies); current code
  does not read or write them.
- `run_retrieval_eval.py`: TF-IDF and BM25 top-1, `layered_action()`,
  `score_decision()`. Other top-k scripts import from it.
- `run_memory_store_eval.py`: scenario-local stores and every authority
  strategy; most `run_claim*.py` scripts import from it.
- `external_scenarios/`: fresh-authored and stress packets.
- `claim_24/` to `claim_31/`: self-contained gate experiments; run files as
  scripts (sibling imports by bare name).
- `scripts/`: evaluation log and authority pattern tooling.
- Planning, findings, article drafts, and protocol documents are Markdown at
  the root; `README.md` lists the important ones.

## Gotchas

- `run_memory_store_eval.py` adds `nomic_embed_*` strategies only when Ollama
  answers at `OLLAMA_BASE_URL`, so its output depends on your machine.
- `run_claim17_authority_absent_boundary_eval.py` and
  `run_claim18_metadata_precondition_eval.py` write to the same result paths
  that `run_memory_store_eval.py --scenarios <packet>` produced for CLAIM-19.
- `claim_24/evaluator.py` (timestamp baseline) prints
  `All scenarios passed: False` by design.
- `claim_24/run_fipsign_live_eval.py` and `run_mandate_cell7.py` hit a real
  external service and read API keys from environment variables. Never commit
  keys or private capture directories.
