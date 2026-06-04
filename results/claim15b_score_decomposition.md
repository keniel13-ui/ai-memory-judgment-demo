# CLAIM-15 Score Decomposition

CLAIM-15 governance-adjusted score decomposition for targeted stress failures.

## s03

Expected action: `verify_first`

Winner: `s03::target` (target)

Target: `s03::target` (target)

### Winner Minus Target

| Component | Delta |
|---|---:|
| relevance | 0.0 |
| authority | 0.0 |
| scope | 0.0 |
| specificity | 0.0 |
| action_type | 0.0 |
| status | 0.0 |
| conflict_penalty | 0.0 |
| total | 0.0 |

### Ranked Components

| Rank | Memory | Role | Trap | Relevance | Authority | Scope | Specificity | Action type | Status | Conflict penalty | Total |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | s03::target | target |  | 1.0 | 3.5 | -3.0 | 1.75 | 1.25 | 1.0 | 0.0 | 5.5 |
| 2 | s03::domestic_wire_policy | domestic_wire_policy | should_not_fire | 0.563951 | 1.75 | -3.0 | 1.75 | 1.25 | 1.0 | 0.0 | 3.313951 |
| 3 | s03::general_payment_approval_policy | general_payment_approval_policy | should_not_fire | 0.421702 | 1.75 | -3.0 | 0.35 | 1.25 | 1.0 | 0.0 | 1.771702 |
| 4 | s03::ach_policy_context | ach_policy_context | should_not_fire | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 1.0 |

## s04

Expected action: `verify_first`

Winner: `s04::litigation_hold_read_access_policy` (litigation_hold_read_access_policy)

Target: `s04::target` (target)

### Winner Minus Target

| Component | Delta |
|---|---:|
| relevance | -0.22016 |
| authority | -1.75 |
| scope | 0.0 |
| specificity | 0.0 |
| action_type | 3.25 |
| status | 0.0 |
| conflict_penalty | 0.0 |
| total | 1.27984 |

### Ranked Components

| Rank | Memory | Role | Trap | Relevance | Authority | Scope | Specificity | Action type | Status | Conflict penalty | Total |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | s04::litigation_hold_read_access_policy | litigation_hold_read_access_policy | should_not_fire | 0.77984 | 1.75 | -3.0 | 0.7 | 1.25 | 1.0 | 0.0 | 2.47984 |
| 2 | s04::henderson_closed_context | henderson_closed_context | should_not_fire | 0.667017 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 1.667017 |
| 3 | s04::retention_schedule_preference | retention_schedule_preference | should_not_fire | 0.312235 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 1.312235 |
| 4 | s04::target | target |  | 1.0 | 3.5 | -3.0 | 0.7 | -2.0 | 1.0 | 0.0 | 1.2 |
