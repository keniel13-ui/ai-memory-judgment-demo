# CLAIM-24 FIPSign SourceAdapter Notes

Status: adapter implemented; live FIPSign mapped-subset run completed on 2026-06-11.

## What Exists

- `fipsign_source_adapter.py`
  - Implements the `SourceAdapter` interface from `gate_interface.py`.
  - Reads `GET /ca/certificate/:certId`.
  - Exposes `fetch_public_key()` for `GET /public-key`.
  - Returns `agent_writable = False`.
  - Normalizes PQCert-like certificate state into stable raw snapshots for `RederivationGate`.

- `run_fipsign_adapter_selftest.py`
  - Local contract test only.
  - Does not contact FIPSign.
  - Proves unchanged, changed, and unreachable FIPSign-shaped states produce `ALLOW`, `REFUSED_STALE`, and `REFUSED_UNREACHABLE` through the existing gate.

- `run_fipsign_live_eval.py`
  - Live runner for a real FIPSign CA base URL.
  - Writes result artifacts to `results/claim24_fipsign_*`.
  - Accepts an optional scenario file with `--scenarios`.

## Live FIPSign Run

Artifacts:

- Scenario packet: `claim_24/scenarios_fipsign_live.json`
- Results: `results/claim24_fipsign_live_mapped_subset_results.md`
- Raw JSON: `results/claim24_fipsign_live_mapped_subset_results.json`

Run summary:

- Base URL: `https://api.fipsign.dev`
- Evidence tier: real-external-source mapped subset
- Live FIPSign inputs covered frozen cells 1, 2, 3, 4, and 5.
- Cells 6 and 7 still require distinct live cert/source fixtures for recipient-changed and scope-narrowed drift.
- The divergence cell mapped to `status.revoked: true` and returned `REFUSED_STALE`.
- `REFUSED_UNREACHABLE` remained a separate result code.

This is not a full seven-cell external-source run.

## What Does Not Exist Yet

- Live certificate fixtures for frozen cells 6 and 7.
- Cryptographic signature verification against ML-DSA-65.

The adapter preserves returned signature fields, but it does not mark signatures verified. Do not claim signature verification until the exact PQCert signing payload and public-key format are pinned and tested.

## Live Run Shape

Once the base URL and cert IDs exist:

```bash
python3 claim_24/run_fipsign_live_eval.py \
  --base-url https://example-fipsign-ca \
  --scenarios claim_24/fipsign_live_scenarios.json \
  --operation-time 2026-06-05T12:00:00Z \
  --label live
```

The live scenario file should keep the original seven CLAIM-24 cells:

1. TTL-valid + conditions unchanged -> `ALLOW`
2. TTL-expired -> `BLOCK`
3. TTL-valid + conditions changed -> `REFUSED_STALE`
4. Source unreachable -> `REFUSED_UNREACHABLE`
5. No grant -> `BLOCK`
6. Recipient changed -> `REFUSED_STALE`
7. Scope narrowed -> `REFUSED_STALE`

For each FIPSign-backed grant, `source_snapshot` should be the output of `normalize_pqcert()` at issue time, and the live adapter should fetch the current state at execution time.

## Evidence Boundary

Current evidence tier after the 2026-06-11 live mapped-subset run:

> CLAIM-24 was exercised against a real external FIPSign CA source for the mapped scenarios. The divergence cell returned `REFUSED_STALE`. Full seven-cell external coverage remains pending cells 6 and 7.

Allowed wording:

> CLAIM-24 was exercised against a real external FIPSign CA source for the mapped scenarios.

> The live FIPSign mapped-subset run covered cells 1 through 5 and preserved the distinction between `REFUSED_STALE` and `REFUSED_UNREACHABLE`.

> This is real external-source evidence for the mapped subset, not a full seven-cell external validation.

Forbidden until signature verification is implemented:

> CLAIM-24 cryptographically verified FIPSign signatures.
