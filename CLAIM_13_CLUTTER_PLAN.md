# CLAIM-13 Clutter Plan

Status: packet built, fresh-author annotations pending. Not benchmark-grade.

## Question

Can fresh-authored jurisdiction metadata still support authority arbitration when the memory store contains semantically tempting unrelated and competing authority memories?

This is different from CLAIM-12. CLAIM-12 tested whether fresh authors could write usable `governs` metadata on a clean five-scenario packet. CLAIM-13 tests whether that authoring model survives realistic clutter.

## Built Packet

Source packet with hidden grading fields:

```text
external_scenarios/fresh_governs_clutter_v0_1_source.json
```

Fresh-author packet:

```text
external_scenarios/fresh_governs_clutter_authoring_packet_v0_1.json
```

The packet contains five scenarios:

- `clutter_dosage_refill_v0_1`
- `clutter_invoice_read_vs_payment_v0_1`
- `clutter_wifi_credential_v0_1`
- `clutter_donor_export_v0_1`
- `clutter_payment_access_v0_1`

Each store includes semantically close clutter, not random noise. Examples:

- donor export target vs auditor-release policy, consultant-NDA policy, aggregate donor-report policy,
- contractor payment access target vs read-only dashboard policy, break-glass payment policy, payroll-system policy,
- office Wi-Fi target vs guest Wi-Fi policy, VPN credential policy, device-onboarding policy.

## Baseline Pressure Check

Before fresh `governs` annotations, the cluttered source produces failures:

| Strategy | Target selected | Action correct | Trap failures | Downgrade | Overblocking |
|---|---:|---:|---:|---:|---:|
| `tfidf_text` | 2/5 | 4/5 | 3 | 1 | 0 |
| `tfidf_metadata_text` | 1/5 | 4/5 | 4 | 1 | 0 |
| `bm25_text` | 2/5 | 4/5 | 3 | 1 | 0 |
| `bm25_metadata_text` | 1/5 | 4/5 | 4 | 1 | 0 |
| `role_filter_bm25_metadata_text` | 2/5 | 3/5 | 3 | 1 | 1 |

This confirms the clutter is doing work. Unscoped role filtering now overblocks one case and selects distractors in three cases.

## Fresh-Author Procedure

Use two independent fresh-author passes before drawing a CLAIM-13 conclusion.

For each pass:

1. Open a fresh model/chat with no repo, project, or prior conversation context.
2. Paste the full contents of `EXTERNAL_GOVERNS_REQUEST.md`.
3. Paste the full contents of `external_scenarios/fresh_governs_clutter_authoring_packet_v0_1.json`.
4. Ask for only the JSON annotations object.
5. Save each output separately.

Recommended filenames:

```text
external_scenarios/fresh_governs_clutter_annotations_v0_1_author_a.json
external_scenarios/fresh_governs_clutter_annotations_v0_1_author_b.json
```

## Evaluation Commands

Author A:

```bash
python3 run_fresh_governs_eval.py \
  --source-scenarios external_scenarios/fresh_governs_clutter_v0_1_source.json \
  --governs external_scenarios/fresh_governs_clutter_annotations_v0_1_author_a.json \
  --results-md results/fresh_governs_clutter_eval_author_a.md \
  --results-json results/fresh_governs_clutter_eval_author_a.json
```

Author B:

```bash
python3 run_fresh_governs_eval.py \
  --source-scenarios external_scenarios/fresh_governs_clutter_v0_1_source.json \
  --governs external_scenarios/fresh_governs_clutter_annotations_v0_1_author_b.json \
  --results-md results/fresh_governs_clutter_eval_author_b.md \
  --results-json results/fresh_governs_clutter_eval_author_b.json
```

## Interpretation Rules

If both passes stay clean:

> Fresh-authored `governs` metadata preserved scoped role filtering under semantically tempting policy clutter in this packet.

If the result overblocks:

> Scope authoring under clutter surfaces the need for severity or specificity arbitration among in-scope policies.

If the result misses target policy jurisdiction:

> The `governs` authoring model is less stable under clutter than under the clean CLAIM-12 packet.

Any of those outcomes is useful. The test is designed to locate the next architectural pressure point, not to force a clean result.

## Author A Interim Result

Author A:

```text
external_scenarios/fresh_governs_clutter_annotations_v0_1_author_a.json
results/fresh_governs_clutter_results_v0_1_author_a.md
```

| Strategy | Target selected | Action correct | Trap failures | Downgrade | Overblocking |
|---|---:|---:|---:|---:|---:|
| `bm25_metadata_text` | 1/5 | 4/5 | 4 | 1 | 0 |
| `role_filter_bm25_metadata_text` | 2/5 | 3/5 | 3 | 1 | 1 |
| `scope_role_filter_bm25_metadata_text` | 4/5 | 5/5 | 1 | 0 | 0 |

Read:

- Fresh-authored scope restored action correctness to 5/5 and removed the dangerous invoice overblock.
- It did not restore target selection to 5/5.
- The remaining trap failure is `clutter_wifi_credential_v0_1`, where the scoped strategy selected `distractor_device_policy` instead of the active Wi-Fi credential memory. The action was still `verify_first`, but the governing memory was wrong.

This is a real partial result: scope metadata fixed the most harmful clutter behavior, but semantic overlap between new-laptop onboarding and office-network credential policy still caused wrong-memory governance.
