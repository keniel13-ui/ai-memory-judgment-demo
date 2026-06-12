# CLAIM-24 Mutable Identity Registry: Source Contract for Cells 6 and 7

Status: contract specification, derived from the frozen CLAIM-24 artifacts and the
2026-06-12 source-contract finding. This document defines what kind of external source
can produce clean-status drift evidence. It changes nothing in the frozen harness.

## 1. Why this document exists

CLAIM-24 pre-registered seven scenario cells. A live FIPSign CA run produced real
external-source evidence for cells 1 through 5. Cells 6 (recipient changed) and 7
(scope narrowed) require a source where attributes drift on a stable identifier while
status stays clean.

The FIPSign maintainer confirmed that a certificate authority cannot provide this by
design: certificate fields are immutable after issuance because mutability would break
the ML-DSA-65 signature that covers them. Revoke and reissue is correct CA behavior,
not a limitation. The finding is recorded in CLAIM_LEDGER.md at commit `0656c66`.

Conclusion: the seven cells span two source contracts.

| Source contract | Speaks in | Covers |
| --- | --- | --- |
| Immutable credential source (CA) | status signals (revoked, expired, missing) | cells 1 through 5 |
| Mutable identity registry | drift signals (subject or scope change, status clean) | cells 6 and 7 |

A re-derivation gate needs to know which contract its source speaks. This document
specifies the second contract.

## 2. The contract

A conforming registry source provides:

1. **Stable identifier.** An `entity_id` that never changes across attribute updates.
   The grant records this identifier at issuance; the gate fetches it at execution time.
2. **Read endpoint.** A GET-style read for one entity returning, at minimum:
   - `subject` (who the entity is bound to; aliases: holder, owner, assignee)
   - `scope` (what the entity authorizes; aliases: role, permissions, scope_ceiling)
   - `status` (lifecycle state with a clean value, e.g. `active`, distinguishable from
     revoked/suspended/expired states)
3. **Post-issue attribute mutability.** `subject` and `scope` can change through
   legitimate registry operations after the grant is recorded, while `status` remains
   clean. Attribute drift and revocation are separate operations.
4. **Agent-writable = false.** The agent under test has no write path to the registry.
   This is the pre-registered source-independence constraint: if the agent can write to
   the source it is re-derived against, the check is self-description moved upstream.
5. **Two observable states per lifecycle, repeatable.** The fixture must expose a
   before state and an after state on the same `entity_id`, reachable on demand, so the
   run can capture the grant-time snapshot and the drifted execution-time snapshot.

## 3. Normalization requirement (learned from the live CA run)

The re-derivation gate compares the whole normalized snapshot for equality. Volatile
metadata that changes on every read or every write (timestamps such as `updated_at`,
etags, version counters, server time) must be excluded from the normalized snapshot by
the adapter. Otherwise every read diverges and every cell collapses into REFUSED_STALE
for the wrong reason. The normalized snapshot should contain exactly the
authority-relevant fields: identifier, subject, scope, status, and any
signature/standard fields preserved without verification claims.

## 4. Cell mapping under this contract

| Cell | Moving raw field in condition_delta | Status during the move | Expected verdict |
| --- | --- | --- | --- |
| 6 (recipient changed) | `subject` only | clean | REFUSED_STALE |
| 7 (scope narrowed) | `scope` only | clean | REFUSED_STALE |

The verdict is the same as cell 3. The evidence distinction is which raw field moved
while status stayed clean. A fixture where `status` moves is cell-3-class evidence
regardless of what else changed; that is the boundary this contract protects.

## 5. Candidate source types

Real post-issue mechanisms preferred, in rough order of fit:

- a user or service directory where an account's owner or role assignment changes
- a device registry where a device is reassigned to a different holder
- a role or permission store where a role's scope is narrowed by policy update
- an IAM-style policy binding where a principal's allowed actions contract

A purpose-built test registry is the named fallback. To preserve external authorship,
the state mutations in a test registry should be performed by the external collaborator,
not by this project: the project supplies the contract, the external side supplies the
lifecycle. The FIPSign side has offered equivalent fixtures once a fitting source type
exists; that offer is the intended first use of this contract.

## 6. What running it would and would not show

Would show: real external-source evidence for cells 6 and 7, completing the seven-cell
matrix across two source contracts, with condition_delta rows any reader can recompute.

Would not show: external validation of CLAIM-24 as a whole (scenarios remain internally
authored), signature verification (preserved, not verified), or anything about source
types not exercised.
