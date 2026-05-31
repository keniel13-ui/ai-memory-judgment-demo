# CLAIM-14 Precedence Plan

Status: implementation scaffold and probe. Not a validated result.

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
