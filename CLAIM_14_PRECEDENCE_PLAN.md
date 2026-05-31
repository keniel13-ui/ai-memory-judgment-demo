# CLAIM-14 Precedence Plan

Status: two-pass fresh-author result on the clutter packet. Not a general reliability claim.

## Why This Exists

CLAIM-13 showed that fresh-authored `governs` improves clutter handling, but scope matching alone does not fully resolve clutter.

Two failure modes surfaced:

1. **Same-action-class ambiguity** — both fresh authors let the new-laptop device policy compete with the Wi-Fi credential policy. Both return `verify_first`, but only one governs the requested object.
2. **Process-context overblock** — Author B let the bank-reconciliation process policy govern a read-only invoice-total lookup.

## New Strategy

The evaluator now includes:

```text
scope_precedence_role_filter_bm25_metadata_text
```

This strategy keeps the existing role lane and scope filter, then adds:

- **specificity precedence**: when multiple scoped authority memories match, prefer the one with more query-term overlap in its `governs` terms;
- **optional action-type gating**: `governs.action_types` can limit a memory to `read`, `write`, or `execute` query actions before specificity ranking.

## Probe Results With Existing CLAIM-13 Annotations

These probes reuse the Author A/B clutter annotations, which do **not** yet include `action_types`. This isolates the effect of specificity precedence.

| Author | Scoped role-filter | Scope + precedence |
|---|---|---|
| A | 4/5 target, 5/5 action, 1 trap, 0 OB | 5/5 target, 5/5 action, 0 trap, 0 OB |
| B | 3/5 target, 4/5 action, 2 trap, 1 OB | 4/5 target, 4/5 action, 1 trap, 1 OB |

Files:

```text
results/fresh_governs_clutter_precedence_probe_author_a.md
results/fresh_governs_clutter_precedence_probe_author_b.md
```

Read:

- Specificity precedence fixes the repeated Wi-Fi/device ambiguity for both authors.
- It fully cleans Author A.
- It does not fix Author B's invoice overblock because that failure needs action-type distinction: a read-only invoice lookup should not be governed by a bank-reconciliation completion policy.

## Action-Type Authoring

`EXTERNAL_GOVERNS_REQUEST.md` now allows optional:

```json
"action_types": ["read", "write", "execute"]
```

A new authoring packet with this schema is generated here:

```text
external_scenarios/fresh_governs_clutter_authoring_packet_v0_2_action_types.json
```

Next test: have fresh authors annotate the clutter packet again with `action_types`, then evaluate whether `scope_precedence_role_filter_bm25_metadata_text` removes both CLAIM-13 failure modes.

## First Action-Type Authoring Result

Fresh action-type annotations:

```text
external_scenarios/fresh_governs_clutter_action_types_annotations_v0_1.json
results/fresh_governs_clutter_action_types_results_v0_1.md
```

| Strategy | Target selected | Action correct | Trap failures | Downgrade | Overblocking |
|---|---:|---:|---:|---:|---:|
| `bm25_metadata_text` | 1/5 | 4/5 | 4 | 1 | 0 |
| `role_filter_bm25_metadata_text` | 2/5 | 3/5 | 3 | 1 | 1 |
| `scope_role_filter_bm25_metadata_text` | 4/5 | 5/5 | 1 | 0 | 0 |
| `scope_precedence_role_filter_bm25_metadata_text` | 5/5 | 5/5 | 0 | 0 | 0 |

Read:

- The fresh author used `action_types` on 22 non-empty annotations.
- Scope alone again fixed action correctness but still selected the wrong Wi-Fi/device memory.
- Scope plus specificity precedence selected the target in all five scenarios.
- The invoice overblock did not recur in this pass because the bank-reconciliation policy was tagged as `write`, while the invoice-total query is read-like.

## Second Action-Type Authoring Result

Fresh action-type annotations:

```text
external_scenarios/fresh_governs_clutter_action_types_annotations_v0_2.json
results/fresh_governs_clutter_action_types_results_v0_2.md
```

| Strategy | Target selected | Action correct | Trap failures | Downgrade | Overblocking |
|---|---:|---:|---:|---:|---:|
| `bm25_metadata_text` | 1/5 | 4/5 | 4 | 1 | 0 |
| `role_filter_bm25_metadata_text` | 2/5 | 3/5 | 3 | 1 | 1 |
| `scope_role_filter_bm25_metadata_text` | 4/5 | 5/5 | 1 | 0 | 0 |
| `scope_precedence_role_filter_bm25_metadata_text` | 5/5 | 5/5 | 0 | 0 | 0 |

Read:

- The second fresh author also used `action_types` to separate read, write, and execute jurisdictions.
- Scope alone again preserved action correctness but left one wrong target selection.
- Scope plus specificity precedence and action-type gating again selected the target in all five scenarios.
- The result repeated the first pass: `5/5` target selected, `5/5` action correct, `0` trap failures, and `0` overblocking.

Status: two independent fresh action-type passes on the same clutter packet. This supports CLAIM-14 on this packet only; it is not a general reliability claim.
