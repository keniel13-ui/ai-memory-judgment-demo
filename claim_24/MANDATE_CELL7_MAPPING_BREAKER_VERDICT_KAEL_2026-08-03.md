# CLAIM-24 Mandate Cell 7 Mapping — Independent Breaker Verdict

**Date:** 2026-08-03 EDT
**Breaker:** Ka'el
**Maker:** Kairos
**Candidate SHA-256:** `ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6`

Candidate not edited. No adapter, fixture, credential, live call, or run opened.

## Verdict: **BLOCK** — one load-bearing, one that would misread the result.

The mapping is careful work. Volatile-field exclusion, cell 6 held as N/A, no
signature claim, outcome-neutral publication rules, and the refusal to change the
expected verdict after seeing the fixture are all correct and should survive into v2.

Two findings stop implementation.

---

## K1 (BLOCK) — read and write share one credential, so the source is not agent-unwritable

CLAIM-24's premise is that the gate re-derives against a source **the agent cannot
modify**. The prereg encodes this as precondition 9 — the agent under test holds no
project API key and cannot call PATCH.

The live FIPSign guide documents one credential for the entire Mandate API:

```text
Base URL: https://api.fipsign.dev · Auth: X-API-Key: pqa_your_key
  01 POST /mandate        02 POST /mandate/verify
  03 PATCH /mandate/:id   04 GET /mandate/:id      05 GET /mandate
```

`GET /mandate/:id` and `PATCH /mandate/:id` sit behind the **same** `X-API-Key`. No
read-only scope is documented.

That forces a dilemma with no good branch:

- **Give the agent the key** → the agent can PATCH. Precondition 9 fails. The source
  is agent-writable and cell 7 is void.
- **Withhold the key** → the agent cannot GET either. The operator fetches and hands
  the result to the gate. The gate is then re-deriving against **whatever the operator
  passed it**, not against an independent external source — which is the exact property
  cell 7 exists to test.

The prereg's own source-independence section takes the second branch ("the agent
receives only the Mandate token or the normalized grant record") without naming that it
dissolves the independence claim. A source you can only read by holding the key that
also rewrites it is not an unwritable source; it is a source you are trusting an
operator to report honestly.

**Repair required — pick one and freeze it:**

1. Establish a genuine read-only path. `POST /mandate/verify` may accept the
   agent-held Mandate token without the project key — **verify this against the live
   API before relying on it.** If it returns current `scopeCurrent` and `status` under
   token-only auth, that is the correct adapter path and K1 closes.
2. Ask FIPSign whether a read-scoped key exists or can be issued.
3. Or downgrade honestly: label the run a **controlled external-API fixture**, state in
   the prereg and the article that read/write credential separation was not achieved,
   and stop claiming agent-unwritable source independence for this cell.

Option 1 is worth checking first because it would make the result stronger, not weaker.

## K2 (BLOCK) — the gate compares the whole record, so `REFUSED_STALE` does not mean scope drift

`rederivation_gate.py` line 70:

```python
if current != grant.source_snapshot:
    ... decision="REFUSED_STALE"
```

That is a whole-dict inequality across all five normalized fields. The gate has no
scope-specific branch.

Consequence: **M1 (scope narrowed), M3 (status moved), and M4 (identity moved) all
return `REFUSED_STALE`.** The verdict is identical in all three cases. The control table
lists M3 and M4 as "invalid as cell 7," which is the right classification — but the
prereg never says that classification happens **entirely outside the gate**, using the
preconditions, and that the gate's verdict alone carries no information about *which*
field moved.

Left as written, a future session or a reader sees `REFUSED_STALE` and reads it as
confirmation of scope drift. It is not. It is confirmation that *something* in the
normalized record moved.

**Repair required:** state explicitly that `REFUSED_STALE` is necessary but not
sufficient for cell 7, and that the run is cell-7 evidence only when the recorded
before/after `condition_delta` shows `scope` as the **sole** differing key. Freeze that
as a post-run assertion on the raw delta, not as an assumption. The gate already stores
raw before/after rather than a derived label, so the evidence needed for this assertion
is present — it just has to be required.

## Advisory (not blocking) — excluding budget excludes real authority

The mapping excludes `budgetConsumed` and `budgetRemaining` because they "can move
without changing the scope authority tested by cell 7."

That is true of *scope* and false of *authority*. A mandate at zero remaining budget
cannot act regardless of scope. Under this mapping the gate returns `ALLOW` for a
mandate with full scope and no usable authority left.

Correct for a narrow scope-drift cell. But the article's working title is about
authority, and this exclusion should be named once as a scoped limitation rather than
justified away. Suggested wording: this cell tests scope drift only; budget exhaustion
is a separate authority-narrowing channel this gate does not observe.

## Confirmed sound — carry into v2 unchanged

- excluding `updatedAt`, `expiresInSeconds`, request ids and response metadata;
- cell 6 held as N/A with `N/A` never counted as a pass;
- no ML-DSA verification claim;
- the frozen refusal to change the expected verdict after fixture inspection;
- no reuse of the previously exposed test keys, and private disposable delivery;
- outcome classes including INVALID, and the forbidden-claims list.

The forbidden-claims list is the strongest part of this document and should be copied
forward verbatim.

## Conditions for re-review

1. Resolve K1 by establishing a real read-only path, or downgrade the independence
   claim explicitly in both the prereg and the article gate.
2. Freeze the `scope`-is-sole-differing-key assertion required to call a
   `REFUSED_STALE` result cell-7 evidence.
3. Name the budget exclusion as a scoped limitation.

No adapter code until a repaired mapping passes a clean seat.
