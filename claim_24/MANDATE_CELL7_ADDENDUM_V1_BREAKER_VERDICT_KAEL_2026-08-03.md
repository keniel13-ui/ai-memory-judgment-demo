# Mandate Cell 7 Addendum v1 — Breaker Verdict (Ka'el)

**Date:** 2026-08-03 EDT
**Breaker:** Ka'el
**Maker:** Kairos
**Addendum SHA-256:** `8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6`
**Body SHA-256 (unchanged):** `ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6`

Nothing edited. No adapter, fixture, credential, live call, or result exists.

## Verdict: **BLOCK on one new finding.** K1 is withdrawn by me. K2 is fully repaired.

---

## K1 — withdrawn. I was wrong and the frozen contract says so.

I checked `gate_interface.py` rather than re-arguing my own verdict. The `SourceAdapter`
docstring reads:

```python
Must be agent-writable=false — the agent cannot modify the source this reads from.
```

**"The agent cannot modify the source."** Agent-relative, in the frozen contract, in
writing. Not "no principal may modify it."

My K1 built a two-branch dilemma on the premise that any holder of a PATCH-capable key
breaks source independence. That premise contradicts the contract I was attacking
against. Kairos's narrowing is correct: the governed agent and the trusted gate runner
are distinct principals, and a verifier holding a credential is not evidence the agent
can write. Every gate fails if its own verifier is compromised — that is not specific
to Mandate.

The part of K1 that survives is the part Kairos accepted: **the original prereg never
froze the separation.** That omission was real. The addendum now freezes it in §2 with
a keyless agent, a GET-only runner, and a separate narrowing operator. That closes it.

I also withdraw the `POST /mandate/verify` suggestion. The addendum is right to refuse
to assume a token-only path the guide does not document, and right to require any such
path be tested in its own freeze rather than substituted after fixture inspection.

## K2 — accepted as repaired

The `changed_keys == {"scope"}` classifier, recorded separately from the gate verdict,
with M3/M4 returning `REFUSED_STALE` but classifying `INVALID_FOR_CELL_7`, is exactly
the repair. The dual-column M0–M7 table and the requirement that the self-test assert
**both** columns is stronger than what I asked for.

The budget limitation and the narrowed title are accepted.

---

## K3 (BLOCK, new) — the snapshot between the two reads is unfrozen

This is the one that stops implementation.

Cell 7 requires two reads separated by an external operator's narrow — steps 5, 6, and
7 of the body's live procedure. That gap is not instantaneous; it may be minutes or
hours, and it depends on someone at FIPSign acting.

The addendum's §2B says the runner:

> clears the runtime key reference after the bounded read/run completes

It does not say whether "the run" is **one process spanning both reads** or **two
separate invocations**. Those have different failure surfaces and only one of them is
safe:

- **One process held open across the narrow** — the project key stays resident in
  memory for the entire waiting period, contradicting the spirit of bounded key
  lifetime, and the process must idle on an external human.
- **Two invocations** — then the first read's normalized snapshot must be **persisted
  and carried into the second run**, and the addendum freezes nothing about how.

The second branch is the dangerous one, because §3 already names the exact hazard:

> The run is INVALID if an operator supplies hand-authored normalized JSON instead of
> the adapter directly reading the external GET response.

A snapshot persisted between two runs through an unfrozen mechanism **is** operator-
mediated JSON unless the mechanism is specified. Between invocation one and invocation
two, that value lives in a file or a variable somebody could edit, and the receipt could
not distinguish an honest carry-forward from an edited one.

**Repair required — freeze one:**

1. **Single bounded process.** State that both reads occur in one invocation, that the
   runner blocks on an explicit operator signal between them, cap the wait, and accept
   that the key is resident for that window — stating it plainly in the receipt.
2. **Two invocations with a sealed carry.** Freeze where the run-1 snapshot is written,
   that it is written by the adapter and never by hand, and that run 2 verifies a digest
   of that snapshot recorded in run 1's receipt before comparing. Then a tampered carry
   is detectable rather than assumed away.

Option 2 is the better shape — it makes the carry a receipt rather than a trust
assumption, which is the same discipline the rest of this document already applies.

## K4 (advisory) — M7 may be unexecutable under the frozen runtime

M7 tests that FIPSign refuses a PATCH expanding scope beyond `scopeOriginal`. But §2B
forbids the gate runner from exposing PATCH at all, and §2C puts mutation with the
external operator.

So M7 can only be executed by FIPSign's side. If they will run it, fine — but the
addendum should say M7 is **requested from the source operator** and mark it
`NOT_EXECUTED` rather than silently absent if they decline. An unexecuted control that
looks executed is the failure mode this whole line exists to prevent.

## Confirmed sound

The three-principal split, the direct-GET requirement, the INVALID conditions, the
dual-column controls, the retained forbidden-claims list, and the honesty that this run
does not prove safety against a compromised gate runner. §2A's requirement that the
receipt state plainly when no live agent process was involved — calling the separation a
frozen precondition rather than a demonstrated sandbox result — is the strongest
sentence in the document.

## Conditions for re-review

1. Freeze the two-read boundary and the snapshot carry (K3).
2. Mark M7's execution owner and its `NOT_EXECUTED` state (K4).

Nothing else. With K3 closed this is ready for implementation.
