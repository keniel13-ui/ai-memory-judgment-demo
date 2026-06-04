# CLAIM-15B Preregistration — Ablation Run on Held-Out Packet

Status: PREREGISTERED — written before the held-out packet is authored or the ablations are run.

Date: 2026-06-02

---

## Purpose

CLAIM-15 showed that the governance-adjusted scoring formula matches the best prior strategy
on the stress packet (4/6) and fails the same two scenarios. The audit identified two
unresolved vulnerabilities:

1. The packets were self-designed, creating a self-validation risk.
2. No ablation run confirmed which terms in the formula are doing the actual work.

CLAIM-15B addresses both. It runs the existing ablation evaluator against a held-out packet
authored with no knowledge of the formula or expected results, and pre-registers predictions
before seeing the output.

If predictions are wrong, admit it. If the formula fails on the held-out packet, say so.

---

## Frozen Baseline

From CLAIM-15 stress packet run (already recorded, not to be revised):

| Strategy | Target | Action |
|---|---:|---:|
| bm25_metadata_text (relevance-only) | 3/6 | 4/6 |
| scope_precedence_role_filter_bm25_metadata_text | 4/6 | 4/6 |
| governance_adjusted_bm25_metadata_text (full scorer) | 4/6 | 4/6 |

These numbers are frozen. The held-out packet results will be compared against these
baselines, not against the held-out packet's own expected values.

---

## Held-Out Packet Requirements

The held-out packet must be authored by a fresh model instance that receives:

- A scenario-writing prompt only (see `CLAIM15B_HELDOUT_PACKET_PROMPT.md`)
- No description of the governance-adjusted scoring formula
- No description of the `governs` field's role in the scorer
- No hints about which scenarios are expected to pass or fail
- No reference to the CLAIM-15 stress packet scenarios

The prompt may tell the model that the research studies agent memory authority and
retrieval. It may not tell the model what the scorer is expected to do with the output.

Disclose: which model was used, the exact prompt, and that the author had no expected
result context.

---

## Ablation Conditions

Run `run_claim15_ablation_eval.py` against the held-out packet using the following
strategies (already defined in the evaluator):

| Run | Strategy name | What it tests |
|-----|--------------|---------------|
| A1 | `governance_adjusted_bm25_metadata_text` | Full scorer (primary claim) |
| A2 | `governance_no_scope_bm25_metadata_text` | Remove scope term |
| A3 | `governance_no_governs_bm25_metadata_text` | Remove governs-dependent terms |
| A4 | `governance_scope_weak_bm25_metadata_text` | Weakened scope weight |
| A5 | `authority_signal_fallback_bm25_metadata_text` | Authority signal without scope |
| A6 | `governs_trust_gated_bm25_metadata_text` | Gate on governs presence |
| A7 | `bm25_metadata_text` | Relevance-only baseline (floor) |
| A8 | `scope_precedence_role_filter_bm25_metadata_text` | Best prior strategy (control) |

Do not add or modify strategies before running. Do not modify the held-out packet after
authoring.

---

## Pre-Registered Predictions

These predictions are written before the held-out packet is authored or run.

**A1 (full scorer):**
Expected to match or exceed A8 (scope-precedence baseline) on scenarios with well-formed
`governs` metadata. Expected to fail scenarios where the target memory lacks `governs`,
consistent with CLAIM-15 findings. Prediction: 4/6 or 5/6 depending on how many
held-out scenarios involve missing `governs`.

**A2 (no scope term):**
Expected to drop below A1. Scope is the primary differentiator between authority-bearing
and relevance-bearing memories. Without it, the scorer should degrade toward the
relevance-only baseline on scenarios involving distractors with partial relevance.

**A3 (no governs-dependent terms):**
Expected to drop most sharply of all ablations. Removing the governs-dependent terms
eliminates scope, specificity, and action_type simultaneously. On scenarios with
authority distractors, this should fall below A7 (relevance-only) in action correctness.

**A4 (weak scope):**
Expected to fall between A1 and A2. Weakening scope reduces the formula's ability to
differentiate well-tagged distractors from ungoverned targets, but does not eliminate it.

**A5 (authority fallback):**
Expected to match A8 on authority-clear scenarios. Expected to fail on scenarios where
authority signals are absent or misleading, without scope to compensate.

**A6 (governs trust gate):**
Expected to perform well on scenarios where the target has well-formed `governs` and
fall sharply on scenarios where the target lacks it. This is the clearest test of whether
the gate is conservative enough.

**A7 (relevance-only baseline):**
Expected to reproduce the CLAIM-15 baseline: 3/6 or lower on scenarios designed with
authority distractors. This is the floor. If A7 matches A1, the governance terms are not
doing the work they claim.

**A8 (scope-precedence control):**
Expected to reproduce the CLAIM-15 result: 4/6 on the stress packet family. On the
held-out packet, this is the primary comparison point for A1.

---

## Falsification Conditions

The scoring model is falsified if:

1. **A7 (relevance-only) matches A1 (full scorer):** The governance terms add nothing.
   The formula is not doing the work it claims.

2. **A2 (no scope) does not drop below A1:** Scope is not the primary driver. The post-hoc
   explanation in Article A needs revision.

3. **A8 (scope-precedence) outperforms A1 on the held-out packet:** The additive formula
   is worse than the best prior strategy on unseen data. This would require updating
   the CLAIM-15 claim from equivalence to inferiority.

4. **A1 drops below 3/6 on the held-out packet:** The full scorer fails at a rate worse
   than the known relevance-only floor on novel scenarios. This would indicate the formula
   is overfit to the stress packet.

If any of these conditions are met, publish the falsification result before publishing
Article A. Do not suppress it.

---

## Success Criteria

CLAIM-15B is useful if it produces any of the following:

- A1 matches or exceeds A8 on the held-out packet, and A2/A3 drop below A1 (confirms
  scope and governs terms are load-bearing, not decorative)
- A7 reproduces the relevance-only floor on unseen data (validates the baseline)
- Any ablation reveals an unexpected term contribution (e.g., authority alone outperforms
  scope alone)
- A falsification condition is triggered and reported honestly

CLAIM-15B does not need to be a positive result to be useful. A null result or
falsification result is more valuable than a withheld positive result.

---

## Output Format

For each strategy on the held-out packet, record:

- `target_selected`: X/N
- `action_correct`: X/N
- `trap_failures`: list of scenario IDs
- `false_certainty_errors`: count
- `downgrade_misses`: count
- `overblocking_errors`: count

Compile into a single table comparing all 8 ablation conditions side by side.

Include the score decomposition for at least one success and one failure case from A1,
matching the format used in CLAIM-15.

---

## After Running

Update `CLAIM_LEDGER.md` with CLAIM-15B entry.

Fold the ablation results and held-out packet results into Article A before publishing.

Do not publish Article A until this run is complete and the results section is updated.

---

## Authoring Record

- **Packet ID:** `claim15b_heldout_v0_1`
- **Packet path:** `external_scenarios/claim15b_heldout_v0_1.json`
- **Schema version:** `claim15b_heldout_v0_1`
- **Model used:** `claude-opus-4-8`
  - Note: this is the model identifier surfaced by the authoring session environment. If a more canonical runtime string is later available, prefer that value.
- **Date authored:** 2026-06-02
- **Authored by tag in packet:** `fresh_model_no_formula_context`
- **No-formula-context confirmation:** the authoring model received the scenario-writing prompt only. It did not receive the governance-adjusted scoring formula, retrieval logic, expected strategy behavior, or CLAIM-15 stress packet results.
- **Lock status:** copied unchanged from the Claude local-agent output path into `external_scenarios/claim15b_heldout_v0_1.json` before evaluator run. Treat as locked.

## Run Record

- **Date run:** 2026-06-03
- **Results:**
  - `results/claim15b_heldout_v0_1_results.md`
  - `results/claim15b_heldout_v0_1_results.json`
- **Score decomposition:**
  - `results/claim15b_score_decomposition.md`
  - `results/claim15b_score_decomposition.json`

### Held-Out Packet Summary

| Strategy | Target | Action | Trap failures | FC errors | OB errors |
|---|---:|---:|---:|---:|---:|
| A1 `governance_adjusted_bm25_metadata_text` | 5/6 | 5/6 | 1 | 1 | 0 |
| A2 `governance_no_scope_bm25_metadata_text` | 4/6 | 4/6 | 2 | 1 | 1 |
| A3 `governance_no_governs_bm25_metadata_text` | 4/6 | 4/6 | 2 | 0 | 2 |
| A4 `governance_scope_weak_bm25_metadata_text` | 5/6 | 5/6 | 1 | 1 | 0 |
| A5 `authority_signal_fallback_bm25_metadata_text` | 4/6 | 4/6 | 2 | 0 | 2 |
| A6 `governs_trust_gated_bm25_metadata_text` | 5/6 | 5/6 | 1 | 1 | 0 |
| A7 `bm25_metadata_text` | 6/6 | 6/6 | 0 | 0 | 0 |
| A8 `scope_precedence_role_filter_bm25_metadata_text` | 3/6 | 3/6 | 3 | 3 | 0 |

Exploratory extra strategy already present in evaluator:

| Strategy | Target | Action | Trap failures | FC errors | OB errors |
|---|---:|---:|---:|---:|---:|
| `directional_action_governance_bm25_metadata_text` | 5/6 | 5/6 | 1 | 0 | 1 |

### Falsification Check

1. **A7 matches A1:** Triggered more strongly than written. A7 did not merely match A1; A7 outperformed it (`6/6` vs `5/6`). This means the held-out packet does not support a claim that the full governance-adjusted scorer improves over relevance-only retrieval.
2. **A2 does not drop below A1:** Not triggered. A2 dropped from A1's `5/6` to `4/6`, supporting that scope is load-bearing in the formula.
3. **A8 outperforms A1:** Not triggered. A8 performed worse (`3/6`) than A1 (`5/6`).
4. **A1 drops below 3/6:** Not triggered. A1 held at `5/6`.

### Interpretation

CLAIM-15B partially falsifies the stronger version of Article A. On this held-out packet, plain BM25 metadata retrieval selected the expected target and action in every scenario. The full governance-adjusted scorer selected the wrong memory on `s04`, producing one false-certainty error.

The A1 failure was not a missing-`governs` problem. It was an action-type inference problem. In `s04`, the query asks to delete litigation-hold documents. The target governs deletion/destruction (`execute`) and should win. The scorer penalized the target's action-type match (`-2.0`) while rewarding the read-access distractor (`+1.25`), so the read-access policy won despite lower authority and lower relevance.

This result strengthens the critique that governance scoring depends on shallow query-action inference. The article must be revised before publication: the held-out packet shows the scoring formula is diagnostic, not an improvement claim, and the next fix is not more weighting but better operation/action extraction.
