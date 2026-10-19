# Local Development

This repository is a research lab artifact. Most files are evidence: memory
layers, scenario packets, pre-registrations, recorded results, and an
append-only evaluation log. The Python code is a set of small, deterministic,
stdlib-only evaluators that regenerate those results.

## Requirements

- Python 3.9 or newer. The code uses only the standard library; there is no
  `requirements.txt` and nothing to `pip install`.
- `git` (the reproduction workflow below uses a scratch worktree).
- Optional: [Ollama](https://ollama.com/) for the embedding strategies
  (`run_embedding_eval.py`, and the `nomic_embed_*` strategies inside
  `run_memory_store_eval.py`).
- Optional: network access and a FIPSign key for the CLAIM-24 live runs.

All commands below were run from the repository root on macOS with Python
3.9.6, 3.10, 3.11, 3.12, and 3.13.

## Read this first: evaluators overwrite committed results

Every `run_*.py` script and every `claim_2x/evaluator.py` that writes files
writes **directly over the committed artifact** in `results/` or in its claim
folder. Several committed artifacts were produced under conditions that the
current default command no longer recreates (see the table below). Running
those commands in your working copy silently rewrites recorded evidence.

Run evaluators in a scratch worktree instead:

```bash
git worktree add --detach ../amj-repro HEAD
cd ../amj-repro
OLLAMA_BASE_URL=http://127.0.0.1:9 python3 run_retrieval_eval.py
git status --short        # empty output means the committed artifact reproduced
cd -
git worktree remove --force ../amj-repro
```

`OLLAMA_BASE_URL=http://127.0.0.1:9` points the Ollama probe at a closed port,
so evaluators that optionally add embedding strategies run lexical-only. Leave
it unset (or point it at your Ollama) when you intend to run embeddings.

## Reproduction status of committed artifacts

Observed on 2026-10-19 against `main` at `1959a55`, Ollama unreachable.

### Reproduce byte-for-byte

| Command | Artifacts |
|---|---|
| `python3 run_retrieval_eval.py` | `results/retrieval_eval_results.{md,json}` |
| `python3 run_topk_inspection.py` | `results/topk_inspection_results.{md,json}` |
| `python3 run_fresh_governs_eval.py` | `results/fresh_governs_eval_results.{md,json}` |
| `python3 run_claim15_score_decomposition.py` | `results/claim15_score_decomposition.{md,json}` |
| `python3 run_action_type_diagnostic.py` | `results/action_type_diagnostic_results.{md,json}` |
| `python3 run_split_architecture_eval.py` | `results/split_architecture_eval_results.{md,json}` |
| `python3 run_claim17_resource_sensitivity_eval.py` | `results/claim17_resource_sensitivity_v0_1_results.md` (the `.json` differs, see below) |
| `python3 run_claim21_external_cert_policy_eval.py` | `results/claim21_external_cert_policy_packet_v0_1_results.{md,json}` |
| `python3 run_claim23_tool_call_authorization_eval.py` | `results/claim23_tool_call_authorization_v0_1_results.{md,json}` |
| `cd claim_28 && python3 evaluator.py` | `claim_28/results.{md,json}` |
| `cd claim_29 && python3 evaluator.py` | `claim_29/results.{md,json}` |
| `cd claim_30 && python3 evaluator.py` | `claim_30/results.{md,json}` |
| `cd claim_31 && python3 evaluator.py` | `claim_31/results.{md,json}` |

### Do not reproduce from the current default command

None of these change a recorded verdict that a claim depends on, except where
noted. They are listed so nobody "fixes" them by overwriting the artifact.

| Command | What differs | Why |
|---|---|---|
| `run_topk_eval.py`, `run_topk_aggregation_eval.py`, `run_aligned_topk_aggregation_eval.py` | Totals go from 10 to 12 scenarios | Artifacts were recorded on s01 to s10. `scenarios/retrieval_scenarios.json` gained s11 and s12 later (commit `434632a`). The s01 to s10 rows are identical. |
| `run_memory_store_eval.py` (default packet), `run_role_filter_noise_eval.py`, `run_claim17_resource_sensitivity_eval.py` (`.json`) | Extra `gate_*`, `attribution_status`, `action_authorized_by`, `pre_gate_action` fields | Artifacts predate the attribution trace and execution gate (commits `8a78c16`, `e177ca4`). All recorded decisions are identical. |
| `run_claim15_ablation_eval.py` | 54 extra rows, plus one changed row | Default packet list now includes `claim15b_heldout_v0_1`. One recorded row changes under current code: `claim15_stress_v0_1` / `bm25_metadata_text` / `claim15_multiple_in_scope_policies_v0_1` goes from `answer_context` to `verify_first`. |
| `run_claim17_authority_absent_boundary_eval.py`, `run_claim18_metadata_precondition_eval.py` | Different file format and strategy set | These scripts write to the **same paths** as `run_memory_store_eval.py --scenarios external_scenarios/<packet>.json`, which is what produced the committed artifacts (with Ollama running, so they include `nomic_embed_*` rows). CLAIM-19 cites those artifacts. Running the dedicated scripts overwrites that evidence. |
| `run_embedding_eval.py`, `run_memory_store_eval.py` with Ollama | Depends on local Ollama and model version | Embedding output is not pinned. |
| `claim_24/run_fipsign_live_eval.py`, `claim_24/run_mandate_cell7.py` | Network | Live external source; not reproducible offline by design. |

## Gate evaluators that print instead of writing files

```bash
cd claim_24 && python3 evaluator.py timestamp            # baseline; prints "All scenarios passed: False" by design
cd claim_24 && python3 run_fipsign_adapter_selftest.py   # local adapter self-test (needs Python 3.10+ on main)
cd claim_24 && python3 -m unittest test_mandate_cell7    # 23 tests
cd claim_25 && python3 evaluator.py full                 # compare with results/claim25_full_run_2026-06-06.txt
cd claim_26 && python3 evaluator.py full                 # compare with results/claim26_full_run_2026-06-06.txt
cd claim_27 && python3 scope_soundness_evaluator.py
cd claim_29 && python3 verify_frozen28_must_pass.py
```

Notes observed on 2026-10-19:

- `claim_25/evaluator.py full` matches every recorded verdict row and summary
  line in `results/claim25_full_run_2026-06-06.txt`. It now prints one extra
  row (`10 A2-overlap REFUSED_TAMPERED`) that is not in the recorded run. The
  Notes column is truncated at a different width than the recorded file.
- `claim_26/evaluator.py full` matches the recorded `Result: 7/7`, `2/7`,
  `2/7`, `5/7` lines.
- `claim_24/run_fipsign_adapter_selftest.py` raises `TypeError` on Python 3.9
  (`dict | None` annotation); it passes on 3.10 and newer.

## Evaluation log

```bash
python3 scripts/append_eval_log.py verify
```

Expected output on `main`: `events_checked=7` and `chain_ok=True`. See
`results/EVALUATION_LOG_README.md` for appending a run. The log hashes the
evaluator and scenario files of each logged run, so editing a logged file
breaks the link between the log and the code that produced the result. Files
hashed by the log include `claim_24/fipsign_source_adapter.py`,
`claim_24/run_fipsign_live_eval.py`, `claim_24/rederivation_gate.py`,
`claim_29/evaluator.py`, `claim_30/evaluator.py`, and `claim_31/evaluator.py`.
The `claim_24` breaker verdicts additionally pin `claim_24/mandate_cell7.py`,
`claim_24/run_mandate_cell7.py`, `claim_24/test_mandate_cell7.py`,
`claim_24/gate_interface.py`, and `claim_24/scenarios.json` by sha256.

## Authority pattern scan

```bash
python3 scripts/check_authority_patterns.py --all --warn-only
sh scripts/install_authority_hooks.sh    # optional pre-commit hook
```

The scan is a deterministic substring/regex check driven by
`.claude/security-patterns.json`. On `main` it reports findings on several
existing negative-control packets; that is expected, which is why the hook runs
with `--warn-only`.
