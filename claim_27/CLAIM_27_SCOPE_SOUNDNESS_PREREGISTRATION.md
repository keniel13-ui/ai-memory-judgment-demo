# CLAIM-27 Pre-Registration: Scope-Soundness Test for CLAIM-25

**Pre-registered:** 2026-06-07
**Status:** Pre-registered. Evaluator built. Not yet run.

---

## The Question

ANP2 (2026-06-07): the content-integrity boundary is only real if the signature covers
(source, sequence) but NOT the content body. If content is covered by the signature, the
attack is unreachable without key compromise and a separate claim would be vacuous. If it
covers only source+sequence, content is unprotected by construction and the boundary is
load-bearing.

The scope-soundness obligation: run A1, A3, A4, and clean-A2 from CLAIM-25 with a
content-forgery adversary active in the background of each control. If any verdict flips,
content-integrity was a hidden premise of the freshness/source claims and the boundary is
porous.

A passing scope-soundness test is a positive finding, not a non-event: "The four
properties held with a content-forgery adversary active" is evidence that content-integrity
is genuinely out of scope — different from quietly omitting it.

---

## Signing Decision (pinned before running)

In CLAIM-25's current implementation, `SourceResponse.signature_valid` is a boolean
simulation. It does not specify what bytes are signed. For this test, we explicitly pin the
signing scope:

**Assumption under test: signature covers (source_address, sequence) only.**
Content fields (role, scope_ceiling) are NOT covered by the signature.

This means:
- A content-forgery adversary can alter role or scope_ceiling while keeping
  signature_valid=True.
- If the signature covered content too, the attack would require key compromise and the
  boundary would be vacuous — no separate claim needed.
- The test only has bite under the first assumption.

---

## The Content-Forgery Adversary

For each ablation scenario, introduce an adversary that:
1. Alters `role` to a forged value.
2. Keeps `scope_ceiling` matching `grant.scope` so the condition check passes.
3. Keeps `signature_valid=True` (signature covers source+sequence only, not content).

The adversary is trying to make the gate ALLOW an action on forged role content while
satisfying all freshness and source checks. If any ablation verdict flips because of the
content forgery, content-integrity was a hidden premise.

---

## Pre-Registered Outcomes

**Outcome A — Boundary real and demonstrated:**
All four ablations (A1, A3, A4, clean-A2) produce the same verdict with and without the
content-forgery adversary active. The four CLAIM-25 properties hold independently of
content integrity. Content-integrity is genuinely out of scope under the stated signing
decision. Finding: positive — boundary demonstrated, not merely asserted.

**Outcome B — Hidden premise found:**
At least one ablation verdict flips when the content-forgery adversary is active. Content-
integrity was a load-bearing hidden premise of the freshness or source-pinning claims. The
CLAIM-25 boundary is porous. Finding: content-integrity must be brought in-scope or the
out-of-scope claim is retracted.

---

## Falsification Condition

If Outcome B occurs — any verdict flips — CLAIM-25's scope statement must be updated
before the next article. The boundary is not closeable by assertion. It is only closeable
by demonstration or by broadening the signing scope to cover content.

---

## Connection to CLAIM-25

CLAIM-25 property set: pinned source + signature + grant-carried sequence floor +
tamper-evident mark.

CLAIM-27 tests whether those four properties hold when a fifth property (content
integrity) is actively violated. If they do, the four are genuinely independent of content
integrity. If they don't, the architecture secretly requires five properties to hold and
the property set is understated.
