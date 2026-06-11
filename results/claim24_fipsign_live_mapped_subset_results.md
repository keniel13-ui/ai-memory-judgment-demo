# CLAIM-24 FIPSign Live SourceAdapter Results

- Evidence tier: real-external-source mapped subset
- Source adapter: `FIPSignSourceAdapter`
- Base URL: `https://api.fipsign.dev`
- Operation time: `2026-06-11T17:50:00+00:00`
- All scenarios passed: `True`
- Frozen cells covered by live FIPSign inputs: `[1, 2, 3, 4, 5]`
- Frozen cells not covered by this live input set: `{'6': 'recipient-changed requires a distinct live cert/source state fixture', '7': 'scope-narrowed requires a distinct live cert/source state fixture'}`

Boundary: this run uses live FIPSign CA reads for the mapped cells. It is not a full seven-cell external run.

| ID | Expected | Got | Pass | Notes |
| --- | --- | --- | --- | --- |
| 1 | ALLOW | ALLOW | True | ttl valid, source conditions unchanged |
| 2 | BLOCK | BLOCK | True | ttl expired |
| 3 | REFUSED_STALE | REFUSED_STALE | True | source conditions changed since grant issuance |
| 4 | REFUSED_UNREACHABLE | REFUSED_UNREACHABLE | True | source unreachable at execution time |
| 5 | BLOCK | BLOCK | True | no grant present |
