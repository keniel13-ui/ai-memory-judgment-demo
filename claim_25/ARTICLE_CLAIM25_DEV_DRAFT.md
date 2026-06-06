# Signed Is Not Fresh: Why Authority Verification Needs Both

*AI Memory Judgment — CLAIM-25*

---

CLAIM-24 tested one stale-authority failure.

An AI agent can hold a grant that is still inside its time-to-live while the source conditions that justified the grant have changed. The clock says valid. The source says otherwise. A timestamp-only gate misses that. A re-derivation gate catches it by checking the source again at execution time.

That was the CLAIM-24 layer.

Then ANP2 pointed out the next gap in the comments:

> *"A genuine pre-revocation response, cryptographically signed by the issuer — signature checks out. But the sequence number predates the revocation event. Does your gate catch that?"*

No.

Not by signature alone.

That is CLAIM-25: authority verification needs to be both **signed** and **fresh**. And the four properties that make that true are not decorative. Remove any one of them and a specific attack succeeds.

---

## The Attack Signature-Only Gates Miss

Suppose an agent once had authority to read:

```text
read:credentials:dev
```

The issuer later revokes that authority and downgrades the agent to:

```text
read:logs:dev
```

Before the revocation, the issuer signed a response confirming the old authority. That response is real. The signature is valid. The response sequence is `8`.

The revocation happens at sequence `10`.

A signature-only gate sees a valid issuer signature and returns `ALLOW`.

But the response is from before the revocation. It is authentic and stale.

That is the replay window.

---

## The Four Required Properties

CLAIM-25 tests a compound gate with four required properties:

1. Pinned source address
2. Signature verification
3. Grant-carried sequence floor
4. Tamper-evident high-water mark

All four must hold at the same time.

The important part is not just that the full gate works. The important part is that each property has its own ablation. When one property is removed, the attack that property guards against must succeed. If it does not, the control is confounded and the property may not actually be load-bearing.

---

## Property 1: Pinned Source Address

The gate must not let the requesting agent choose which source gets queried at runtime.

If the agent can say, "check this source," an attacker can substitute a friendly source that returns the old conditions. That response can be fresh. It can even be signed by the friendly source. None of that matters if the source itself is wrong.

The grant carries the source address:

```json
{
  "source_address": "policy://issuer/main"
}
```

At execution time, the gate compares the runtime source address against the pinned source in the grant. If they diverge, the request is refused.

**Ablation A3:** remove source pinning. The gate accepts the runtime-supplied friendly source. Result: `ALLOW`.

That confirms source pinning is doing real work in this packet.

---

## Property 2: Signature Verification

The source response must be signed by the issuer and the signature must be verified.

Freshness alone is not enough. A forged response can claim any role, any scope, and any sequence number.

In the ablation packet, the attacker presents a forged response with sequence `50` and the old scope. Sequence `50` is above the grant floor. If signature verification is disabled, the forged response passes.

**Ablation A4:** disable signature verification. Result: `ALLOW`.

Signature is not sufficient by itself. But without it, freshness can be forged.

---

## Property 3: Grant-Carried Sequence Floor

This is the property that closes the replay window.

The grant carries:

```json
{
  "sequence_at_issue": 10
}
```

The gate refuses any source response whose sequence is below the relevant floor.

In the replay attack:

```text
response sequence = 8
grant floor       = 10
stored mark       = 12
```

The gate uses the strongest available floor:

```text
floor = max(grant.sequence_at_issue, stored_mark)
```

So in the normal replay case:

```text
floor = max(10, 12) = 12
sequence 8 < 12
REFUSED_STALE
```

The cold-start case is the harder one. If the gate has restarted and has no stored mark, it cannot rely on local high-water state. The floor must travel with the grant.

```text
stored mark = none
grant floor = 10
sequence 8 < 10
REFUSED_STALE
```

**Ablation A1:** remove the grant-carried floor and simulate cold start by removing the stored mark. There is no floor from any source. Result: `ALLOW`.

That confirms the grant-carried floor is not optional in this packet.

---

## Property 4: Tamper-Evident Mark

The stored high-water mark creates one more recursion problem.

If the stored mark can be rewritten, an attacker can lower it below the replayed response:

```text
original mark = 12
rewound mark  = 5
response seq  = 8
```

Now sequence `8` is above the rewound mark. If the gate trusts that rewritten mark, replay succeeds again.

So the mark must be tamper-evident. If the gate detects that the stored mark was lowered, it refuses before checking sequence freshness.

**Ablation A2:** disable tamper detection and isolate the mark path. The mark is rewound to `5`. The replayed sequence is `8`. Result: `ALLOW`.

That confirms tamper detection is load-bearing too.

---

## The Ablation Protocol

Each ablation removes exactly one protection path and checks that the corresponding attack succeeds.

This matters because a weak ablation can lie. If you remove signature verification but the gate refuses for some other reason, you have not shown that signature verification was necessary. You only showed that something else blocked first.

So the evaluator checks structural witnesses, not only final decisions.

| Ablation | Removed property | Expected failure | Structural witness |
|---|---|---|---|
| A1 | Grant-carried floor | Cold-start replay passes | `sequence_at_issue is None` and `stored_mark is None` |
| A2 | Tamper detection | Rewound mark accepted | Stored mark exists and the gate still returns `ALLOW` |
| A3 | Source pinning | Runtime source substitution accepted | Runtime source substitution returns `ALLOW` |
| A4 | Signature verification | Forged response accepted | Forged response is treated as valid by the ablated gate and returns `ALLOW` |

All four ablations produced the expected failure mode.

That is the main result. The compound gate works on this packet, and the negative controls show why each part is necessary in this implementation.

---

## Results

```text
SignedFreshGate — core scenarios

E  clean grant              ALLOW             PASS
A  conditions changed       REFUSED_STALE     PASS
B  replay attack            REFUSED_STALE     PASS
C  cold-start replay        REFUSED_STALE     PASS
D  mark rewind              REFUSED_TAMPERED  PASS

All passed: True
```

Baseline:

```text
SignatureOnlyGate — no freshness

E  clean grant              ALLOW             PASS
A  conditions changed       REFUSED_STALE     PASS
B  replay attack            ALLOW             FAIL
C  cold-start replay        ALLOW             FAIL
D  mark rewind              ALLOW             FAIL

All passed: False
```

Ablations:

```text
SignedFreshGate — ablation controls

A1  no grant-carried floor  ALLOW             PASS
A2  rewindable mark         ALLOW             PASS
A3  unpinned source         ALLOW             PASS
A4  no signature check      ALLOW             PASS

Ablations: 4 run, 0 did not produce expected failure
```

---

## What This Claims

On this internally authored nine-scenario packet:

- A signature-only gate leaves replay windows open.
- Signed-AND-fresh closes the replay cases in the packet.
- A grant-carried sequence floor is necessary for cold-start replay.
- A tamper-evident mark is necessary to prevent mark rollback recursion.
- Source pinning is necessary to prevent runtime source substitution.
- Signature verification is necessary because freshness alone can be forged.
- The ablation controls confirm that all four properties are load-bearing in this implementation.

That is the claim.

---

## What This Does Not Claim

This is not a full production trust model.

The packet is internally authored. The issuer, source responses, signatures, sequence numbers, and mark states are simulated. The result tests the gate logic and the ablation structure. It does not prove that this implementation is complete for real deployments.

Open questions remain:

- What prevents the grant itself from being forged at issuance?
- What happens if the pinned source endpoint is compromised but still signs valid responses?
- What storage substrate should hold the high-water mark in production?
- What audit trail should connect the grant, source response, mark update, and final action?

Those are next layers, not hidden assumptions.

---

## Post-Publish Update — 2026-06-06

After this article was posted, ANP2 identified a confound in ablation A2.

The original A2 scenario had `grant.sequence_at_issue = 10` with a replayed sequence of `8`. To get the ablation to return `ALLOW`, the evaluator was also stripping the grant floor (`sequence_at_issue = None`). That means two properties were removed simultaneously — tamper detection AND the grant floor. Not a clean isolation.

**The fix:** Rebuilt A2 with `grant.sequence_at_issue = 5`. The grant floor now passes naturally (`8 >= 5`). The evaluator ablation strips only `mark_is_tampered` — the grant floor stays intact. Tamper detection is the sole remaining guard. Clean isolation.

**The original confounded A2 is preserved as an overlap assertion (scenario A2-overlap):** `grant.sequence_at_issue = 10`, `sequence = 8`, mark rewound to `5`, tamper flag set. Both the grant floor and tamper detection independently cover this cell. Expected: `REFUSED_TAMPERED`. This documents the defense-in-depth zone — any future change that drops either guard in this range shows up as a regression.

Updated harness result:

```text
A2      rewindable mark (clean isolation)   ALLOW             PASS
A2-overlap  defense-in-depth zone           REFUSED_TAMPERED  PASS
```

The correction strengthens the claim. A2 is now a genuinely isolated control. The confound was caught through external review, fixed publicly, and the original cell preserved as a regression sentinel rather than discarded.

Full corrected harness: `claim_25/evaluator.py` — run `python3 evaluator.py full` to reproduce.

---

## Connection to CLAIM-24

CLAIM-24 tested stale authority caused by source drift. It showed that a gate must re-derive current conditions from a source the agent cannot write to.

CLAIM-25 tests the next attack surface: a response can be authentic and still too old to authorize the action.

So the two claims stack:

```text
CLAIM-24: do not trust stale cached grants
CLAIM-25: do not trust signed responses unless they are fresh
```

Re-derivation is necessary.

Signed freshness is necessary.

Neither layer is enough alone.

---

## The Code

The evaluator, gate implementations, scenarios, and result file are in the public repository:

```bash
cd claim_25
python3 evaluator.py full
```

If you find a scenario where this gate allows an action it should refuse, open an issue. That is the point of publishing the harness.

---

*CLAIM-25 pre-registered on June 6, 2026. Harness run confirmed the same day. Results are reproducible from the repo.*

*This is part of an ongoing series: falsifiable claims about AI agent memory and authority, tested publicly, with limits stated up front.*
