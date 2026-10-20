# Contributing

Thanks for helping. This repository is a research evidence trail, so the rules
are mostly about keeping recorded results trustworthy.

## Branch workflow

- `main` holds published, recorded evidence.
- `dev` is the integration branch when it exists. Open feature and fix
  branches from `dev` and target pull requests at `dev`; `dev` is merged into
  `main` when a batch is ready to publish. If `dev` does not exist yet, target
  `main`.
- Name branches by intent, for example `claim-32/prereg`, `fix/eval-log`,
  `docs/architecture`.

```bash
git fetch origin
git switch -c fix/<topic> origin/dev      # or origin/main if there is no dev
# work, validate, commit
git push -u origin fix/<topic>
gh pr create --base dev
```

## What a pull request may change

- Harness code, tooling, tests, and documentation: yes.
- Recorded evidence: no. Do not edit `results/`, `claim_*/results.*`,
  scenario packets, fixtures, memory layers, pre-registrations, breaker
  verdicts, or `results/evaluation_log.jsonl` (append only, via
  `scripts/append_eval_log.py`). If you think a recorded result is wrong, say
  so in the PR description.
- Hash-pinned evaluator files (listed in `CLAUDE.md` and
  `docs/DEVELOPMENT.md`): no edits, not even formatting.

## Adding a new experiment

Follow `RESEARCH_PROTOCOL.md` and `.claude/claude-security-guidance.md`:

1. Write the pre-registration (hypothesis, predictions, packet authorship
   rules) and commit it before any run.
2. Lock the packet; do not edit it after authoring.
3. Implement the evaluator, run it, commit the results.
4. Append a log entry with `scripts/append_eval_log.py append` and verify the
   chain.
5. Add or update the `CLAIM_LEDGER.md` entry, including allowed and forbidden
   wording, before any article uses the claim.

## Before you open a PR

```bash
python3 scripts/append_eval_log.py verify                     # chain_ok=True
python3 scripts/check_authority_patterns.py --all --warn-only
cd claim_24 && python3 -m unittest test_mandate_cell7 && cd ..
```

If you touched evaluator code, confirm the committed artifacts still reproduce
using the scratch worktree procedure in `docs/DEVELOPMENT.md`, and describe any
drift in the PR.

Keep the project stdlib-only. Do not commit API keys, private capture
directories, or real memory files from other projects.
