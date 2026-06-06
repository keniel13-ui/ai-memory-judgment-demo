# CLAIM-25 Pre-Registration — Signed-AND-Fresh

Status: pre-registered before packet or evaluator implementation.
Date: 2026-06-05
Series: Self-Correcting Systems — authority freshness layer

---

## Research Question

Does a re-derivation gate that enforces signed-AND-fresh — not signed alone — close the replay and cold-start attack windows that a signature-only gate leaves open?

CLAIM-24 established: a timestamp-only gate returns ALLOW on a TTL-valid grant whose underlying conditions have changed. The re-derivation gate fixed that by reading a live source.

ANP2 architecture review (public comment thread, CLAIM-24 article) identified two residual gaps in the signed-only framing:

**Gap 1 — Replay attack.** A gate that only verifies "is this a validly-signed response" can be defeated by replaying a genuinely-signed pre-revocation entry. The signature is authentic. The state is stale. The gate returns ALLOW.

**Gap 2 — Cold-start window.** A high-water mark works once it's running. On the gate's very first read, or after any restart that drops state, there is no mark to compare against. A replayed pre-revocation entry has nothing to be rejected against.

CLAIM-25 tests whether a gate implementing the full four-component stack closes both windows.

---

## The Property Under Test

**CLAIM-24 property:** agent-writable=false source + re-derivation on execution.

**CLAIM-25 property:** signed-AND-fresh.

These are different. Unforgeable proves the issuer committed to that value. Fresh proves it is the current commitment. A gate needs both or replay defeats it.

The full four-component stack required:

1. **Pinned source address** — the source address lives inside the signed grant at issue time. The gate reads from that address, not from any address the runtime supplies at execution time. Source substitution fails because the address is bound to the signature.

2. **Signature over the response value** — the issuer signs the response. Forging a response from a substituted source fails at the signature layer.

3. **Sequence floor carried by the grant** — the source's sequence-at-issue is recorded inside the signed grant alongside the source address. "Fresh" means the response's sequence number is ≥ the offset the grant recorded. The gate's floor is grant-derived on every read, including cold start, restart, and first-ever read. A runtime-supplied floor can be manipulated. A grant-carried floor cannot be undercut because it rode in on the same signature that authorized the action.

4. **Tamper-evident mark in monotonic storage** — the gate tracks the highest sequence offset it has seen. That mark must be stored in append-only storage the acting agent cannot rewind. If the mark can be rewound, the rollback attack moves one level down: replay a pre-revocation entry, then rewind the mark below it. Same attack, different layer. Append-only on the mark closes the recursion.

---

## Attack Scenarios the Gate Must Catch

**Scenario A — TTL-valid drift (inherited from CLAIM-24):**
Grant is within its time-to-live. Source conditions changed after issuance. Timestamp-only gate returns ALLOW. Signed-AND-fresh gate must return REFUSED_STALE.

**Scenario B — Replay attack:**
Gate receives a genuinely-signed response from before the revocation event. Signature verification passes. Sequence number is below the grant's sequence floor. Gate must return REFUSED_STALE, not ALLOW. This is the window a signature-only gate cannot close.

**Scenario C — Cold-start replay:**
Gate has no mark (first read or post-restart). Attacker replays a pre-revocation entry. No runtime-supplied floor exists. Gate must derive the floor from the grant's sequence-at-issue field and reject the entry. Gate must not fall through to ALLOW in the absence of a stored mark.

**Scenario D — Mark rewind:**
Attacker rewinds the gate's high-water mark to a value below a pre-revocation entry's sequence number. Gate sees the replayed entry and its sequence number appears above the rewound mark. Gate must detect the mark has been tampered with (not append-only) and refuse. If the mark storage is truly append-only and monotonic, this attack surface does not exist.

**Scenario E — Clean grant, current source:**
Grant is valid. Source conditions are unchanged. Sequence number is ≥ the grant's sequence floor. Mark is current. Gate must return ALLOW. This is the non-divergence confirmation scenario.

---

## Gate Implementation Requirements

The gate under test must implement all four components:

```json
{
  "grant": {
    "agent_id": "string",
    "role": "string",
    "scope_ceiling": "string",
    "issued_at": "ISO8601",
    "expires_at": "ISO8601",
    "source_address": "string",
    "sequence_at_issue": "integer",
    "issuer_signature": "string"
  },
  "gate_behavior": {
    "source_lookup": "reads from grant.source_address only — never runtime-supplied address",
    "freshness_check": "response.sequence >= grant.sequence_at_issue",
    "mark_update": "append-only monotonic store — gate refuses to lower the mark",
    "cold_start": "floor derived from grant.sequence_at_issue when no mark exists"
  }
}
```

The timestamp-only gate (CLAIM-24 baseline) must also be run on the same packet for comparison. Expected: ALLOW on scenarios A and B. The signed-AND-fresh gate is the only gate that should catch scenarios B and C.

---

## Acceptance Criteria

The claim is supported if:

- Signed-AND-fresh gate returns REFUSED_STALE on scenarios A, B, and C.
- Signed-AND-fresh gate returns ALLOW on scenario E.
- Timestamp-only gate returns ALLOW on scenarios A and B (confirming the baseline gap).
- Signature-only gate (no freshness check) returns ALLOW on scenario B (confirming replay is not caught by signing alone).

The claim is falsified if:

- Signed-AND-fresh gate returns ALLOW on any of scenarios A, B, or C.
- Cold-start window is not closed (scenario C falls through to ALLOW when no mark exists).
- Mark rewind produces a passing result, indicating monotonic storage was not enforced.

---

## Known Weaknesses (Pre-Registered)

- Scenarios are internally authored. External replication requires an adversary constructing signed grants over drifted conditions without knowing expected results.
- Signature implementation in the test harness is simulated, not cryptographically enforced at the protocol layer. Real-world enforcement requires HSM or equivalent. Harness validation is not protocol validation.
- Scenario D (mark rewind) requires the test harness to simulate non-monotonic mark storage. This is a controlled violation — the test proves the gate detects it, but real enforcement depends on the storage layer's actual append-only guarantees.
- The four-component stack is described at the architecture level. Implementation complexity grows at each layer. CLAIM-25 tests the logic, not the implementation cost.

---

## Ablation Protocol — Negative Controls (Added 2026-06-06, per ANP2 review)

Running the full four-component stack and getting a green result proves the design works end-to-end. It does not prove each layer is load-bearing. An experiment that cannot fail when weakened is describing the design, not testing it.

Four ablation variants must be run alongside the five core scenarios. Each ablation removes exactly one property. The specific attack that property was built to block must succeed in the ablated version. If it does not, that property was never carrying the weight credited to it.

**Ablation 1 — Drop grant-carried floor:**
Remove `sequence_at_issue` from the signed grant. The gate has no grant-derived baseline. On cold start, no floor exists from any source. Scenario C (cold-start replay) must return ALLOW. If the gate still refuses, the grant-carried floor was not load-bearing in the implementation — the gate found another floor somewhere, which is itself a gap to investigate.

**Ablation 2 — Make mark rewindable:**
Allow the gate's high-water mark to be lowered by the acting agent. Rewind the mark below a pre-revocation entry's sequence number. Re-run scenario A (TTL-valid drift) and scenario B (replay). Both must return ALLOW after the mark is rewound. If they still refuse, the monotonic mark storage was not actually enforcing the constraint.

**Ablation 3 — Unpin source address:**
Remove the `source_address` field from the signed grant. Allow the runtime to supply the source address at execution time. Substitute a friendly source that returns the pre-revocation state. The gate must read from the substituted source and return ALLOW. If it still refuses, the pinning was not enforced — the gate was using a hardcoded address or another mechanism not captured in the spec.

**Ablation 4 — Strip signature:**
Remove signature verification from the gate. Present a forged response with a fabricated sequence number above the real high-water mark. The gate must return ALLOW. If it still refuses, the signature check was not the load-bearing layer — something else was blocking the forged response.

**Ablation acceptance rule:**
Each ablated variant must produce the failure it was designed to catch. If all four ablations produce the expected failures, the pre-registration can state: "each of the four properties is independently necessary — removing any single one reopens the specific attack it was built to close."

**What a failed ablation means:**
If an ablation does not produce the expected failure, the claim must be revised. Either the property is redundant (another layer is carrying the weight), or the test harness is not isolating the ablation cleanly. Both outcomes must be published.

---

## Relationship to Prior Claims

| Claim | Property tested | Residual gap |
|-------|----------------|--------------|
| CLAIM-24 | Agent-writable=false source + re-derivation | Signed-only gate leaves replay window open |
| CLAIM-25 | Signed-AND-fresh (four-component stack) | Implementation complexity, protocol-layer enforcement |

---

## Forbidden Wording

- "Signed-AND-fresh eliminates stale grant failures." — It closes replay and cold-start. It does not eliminate all possible staleness paths.
- "This is cryptographically proven." — Harness validation, not protocol proof.
- "CLAIM-25 supersedes CLAIM-24." — CLAIM-25 extends CLAIM-24. Both constraints are required.
- "The mark makes the gate secure." — The mark must itself be in tamper-evident storage. A rewindable mark is the same attack one level down.

---

## Allowed Wording (Subject to Revision After Results)

> "On a five-scenario internally authored packet, the signed-AND-fresh gate refused N/3 attack-surface cases that the timestamp-only gate allowed and that the signature-only gate allowed on scenario B."

> "The cold-start window was [closed / not closed]: the gate [derived its floor from the grant / fell through to ALLOW] when no stored mark existed."

> "Scenario D (mark rewind) [was / was not] caught: the gate [detected tampered mark storage / returned ALLOW on a replayed entry below the rewound mark]."

---

*Pre-registered: 2026-06-05. Results to follow after packet implementation and evaluator build.*
*Previous: CLAIM-24 — "The Clock Said Valid. The World Said Otherwise."*
*Full ledger: CLAIM_LEDGER.md*
