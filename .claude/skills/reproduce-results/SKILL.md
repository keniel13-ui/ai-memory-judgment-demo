---
name: reproduce-results
description: Re-run one or more evaluators in this repo without overwriting committed evidence, and judge whether the committed artifacts still reproduce. Use before changing evaluator code, when asked whether a result reproduces, or when reviewing a PR that touches run_*.py or claim_*/ code.
---

# Reproduce recorded results safely

Evaluators in this repo write straight over committed artifacts. Never run
them in the main working copy unless the user wants a new recorded run.

## Steps

1. Create a scratch worktree at the commit under test:

   ```bash
   git worktree add --detach ../amj-repro HEAD
   ```

2. Run the evaluator(s) there with Ollama forced off (unless the user asked
   for embedding runs):

   ```bash
   cd ../amj-repro
   OLLAMA_BASE_URL=http://127.0.0.1:9 python3 run_retrieval_eval.py
   cd claim_31 && python3 evaluator.py && cd ..
   ```

3. Inspect drift:

   ```bash
   git status --short
   git diff --stat
   ```

   Empty output means byte-for-byte reproduction.

4. If files changed, classify before reporting. Compare against the table
   "Do not reproduce from the current default command" in
   `docs/DEVELOPMENT.md`. Known, explained drift (scenario set grew from 10 to
   12, attribution trace fields added later, shared output paths for CLAIM-17
   and CLAIM-18) is not a new finding. Anything else is: report which rows,
   which fields, and whether any `action`, `selected_memory_id`, verdict, or
   summary count changed.

5. Clean up:

   ```bash
   cd -
   git worktree remove --force ../amj-repro
   ```

## Rules

- Do not copy regenerated files back into the main working copy.
- A changed verdict is reported, never "fixed" by editing the artifact or the
  ledger. If the user wants a new run recorded, it gets a pre-registration
  note, a new artifact or clearly labeled re-run, and an
  `scripts/append_eval_log.py append` entry.
- Gate folders under `claim_2x/` and `claim_3x/` must be run as scripts so
  their sibling imports resolve.
