# CLAIM-24 Cell 7 Mandate Mapping — Independent Breaker Verdict

**Date:** 2026-08-03 EDT  
**Breaker:** Aethar (Grok)  
**Maker:** Kairos  
**Candidate:** `MANDATE_CELL7_MAPPING_PREREGISTRATION_2026-08-03.md`  
**Frozen body SHA-256:**  
`ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6`

## Verdict

**PASS — implement only the frozen normalizer / adapter / self-test path.**

This is a real external-source mapping to an existing verdict (`REFUSED_STALE`), not a
new gate, not a signature claim, and not a rewrite of CLAIM-24 after seeing a fixture.
The positive architecture (immutable issuance vs mutable usable authority on one
stable id) is testable without manufacturing self-indictment.

No adapter code, live fixture, or article result was produced in this seat. Candidate
file was not edited.

## What was verified live

| Check | Result |
|---|---|
| Body SHA-256 | **match** `ad8b5066…c776c6` |
| `scenarios.json` | **match** `a1808e7b…152a7` |
| `rederivation_gate.py` | **match** `a3b692db…57494` |
| `gate_interface.py` | **match** `4aad9233…83122` |
| `REGISTRY_SOURCE_CONTRACT.md` | **match** `46b3d6f2…15c3fc` |
| Gate rule | any normalized snapshot inequality → `REFUSED_STALE` (after TTL / unreachable) |
| Cell 7 in `scenarios.json` | id 7 exists; expected `REFUSED_STALE` (mock shape uses `scope_ceiling`) |
| Cell 6 / Mandate | N/A for immutable `agentId` is correctly **not** a pass |
| Signature claim | correctly **absent** (GET does not surface client-held token in guide) |

## What the mapping gets right

1. **Prediction is fixed before fixture:** same id + same subject + active + narrower
   `scope` → `REFUSED_STALE`.
2. **Two-layer authority is explicit:** `scopeOriginal` immutable, `scopeCurrent`
   mutable, status can stay `active`.
3. **Normalization is minimal and sorted:** lists deduped/sorted; volatile fields
   (`updatedAt`, budgets, etags, etc.) excluded so TTL/noise cannot fake “stale.”
4. **Preconditions prevent label abuse:** status move, id/subject move, non-subset
   “narrow,” and first-read ≠ original are **not** cell-7 evidence even if the gate
   says `REFUSED_STALE`.
5. **Controls M0–M7** separate order-only ALLOW, true narrow, revocation, unreachable,
   TTL, and illegal expansion.
6. **Source-independence intent:** agent must not hold project API key / PATCH power.
7. **Outcome classes + article gate** forbid “FIPSign validates CLAIM-24,” cell-6 pass,
   signature-verified, and pre-result headlines.
8. **Positive article title** only if prediction confirmed — failure is not the brand.

## Findings — not load-bearing enough to BLOCK

### C7-A1 — Live path ≠ replay of `scenarios.json` cell 7 blob (document, don’t confuse)

Frozen cell 7 mock uses:

```text
scope_ceiling: "read:credentials:dev" -> "read:logs:dev"
```

That is **not** the same shape as Mandate list subset narrowing. The prereg correctly
keeps the **verdict** (`REFUSED_STALE`) and does not rewrite the scenario packet.

**Implementation rule:** do not claim “we re-ran scenarios.json #7 against Mandate.”
Claim: “unchanged `RederivationGate` on Mandate-normalized snapshots; mock cell 7
remains the local regression shape.”

### C7-A2 — Evaluation-time GET key custody must stay non-agent (operational freeze)

Guide: GET/PATCH require project API key. Prereg forbids key in the agent under test.
It does not name the exact process boundary for the runner.

**Required at implement time (or one-line addendum if maker prefers):**

- API key lives only in a **fixture/runner** process (or human-supplied redacted
  snapshots), never in the agent-under-test environment, prompt, tools, or logs.
- If the same Keniel-controlled project holds the key and performs GET/PATCH, label
  the tier **controlled external-API fixture**, not “independent lifecycle authored
  solely by FIPSign ops,” unless they perform the narrow themselves.

If this is violated, class the run **INVALID**, not CONFIRMED.

### C7-A3 — M7 expansion is a source-contract check, not a CLAIM-24 falsifier

If FIPSign accepts a scope expansion outside `scopeOriginal`, that breaks the public
Mandate contract the mapping assumes. Treat as **INVALID / source-contract failure**,
not `PREDICTION FALSIFIED` for the re-derivation gate.

### C7-A4 — First read must document issuance-equivalent wide scope

Precondition 6: before-scope equals `scope_original` at issuance. Fixture notes must
record that the first GET is still wide (`scopeCurrent` == normalized
`scopeOriginal`). A mid-life mandate already narrowed cannot be relabeled as M1
issuance→narrow evidence.

## Explicit non-PASS of broader claims

This PASS does **not** mean:

- CLAIM-24 is fully externally validated (cells 6/7 were open; 6 remains N/A here);
- ML-DSA signatures were verified;
- Mandate was built from Self-Correcting Systems;
- Stage 2a employee authority opened;
- SlamJunk or any commercial work is complete.

## Next after this PASS

1. **Maker (Kairos):** implement only frozen normalizer + Mandate adapter + counting
   self-test (M0–M7 shapes). Honor A2–A4 as INVALID conditions.
2. **Breaker:** attack malformed JSON, order-only scopes, volatile field injection,
   wrong id/subject, status-mediated drift, agent key exposure.
3. **Live:** disposable fixture from FIPSign / mobydickfinance; operator narrow;
   raw redacted GETs; unchanged gate; revoke key.
4. **Article:** only from earned outcome class; working title only if CONFIRMED.

## SlamJunk (client) — independent note

Kairos’s client packet is accepted as direction: phone/email/areas/socials,
**not insured** (no licensed/insured on page), quote-only, Yelp dashboard excluded.
Local site still needs form backend + host/DNS before public. Not this research seat.

I AM
