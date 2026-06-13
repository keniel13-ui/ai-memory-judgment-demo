# Close Authority and Time-Sliced Composition: Design Brief

Status: design brief, authored after the CLAIM-30 V0 article and public comment
threads on 2026-06-12. This is not CLAIM-31, not a pre-registration, not a result,
and does not modify the frozen CLAIM-30 fixtures, rows, evaluator, or ledger.

## Why this brief exists

CLAIM-30 V0 showed that a per-step gate can allow every individual operation while a
trajectory-level gate refuses the composed outcome. It also exposed one open class:
time-sliced composition.

The clean example is sequence 7.

- Sequence 5 processed the threshold pattern inside one composition window. The
  trajectory gate refused it by `clause_3_threshold_accumulation`.
- Sequence 7 split the same total pattern across two windows. A `policy_boundary:harness`
  close event ended the first window before the second window began. The trajectory
  gate allowed it.

That allowance is correct under the frozen CLAIM-30 rules. The rule was per
composition window, and the close was emitted by the authorized policy boundary, not
by the acting agent. If a legitimate boundary closes a window, the window resets.

The open question is not whether sequence 7 was a bug. It was not. The open question
is who may close a window, when a window should close, and whether an agent can shape
the timing or conditions that cause an authorized boundary to close.

## What sequence 7 proved and did not prove

Sequence 7 proved that the frozen V0 gate treats authorized window closes as real
boundaries. The gate did not silently accumulate across a close that the envelope
declared valid.

Sequence 7 did not prove that time-sliced escape is solved. It showed that the V0
composition window is the unit of accumulation. If harmful accumulation can be spread
across legitimate windows, a second policy layer must decide whether state should
carry across those windows.

The honest reading is:

- The per-step gate is not enough.
- The trajectory gate is not enough if the window policy can be gamed.
- Close authority is its own policy surface.

## Why authorized closes are necessary

A system cannot treat every long workflow as one infinite window. Real work has
episodes: invoices close, batches settle, access reviews end, incidents resolve, and
policy boundaries need a way to declare that one composition context has ended.

If closes never reset anything, every normal workflow becomes progressively harder to
allow. That overblocks legitimate multi-step work and makes the gate operationally
unusable.

If closes reset everything without carryover checks, an agent can potentially shape a
trajectory so the dangerous total never appears inside one window.

The close rule therefore has to be strong in two directions:

- Legitimate closes must be honored.
- Close-triggered reset must not become a laundering mechanism.

## Adversary model

The acting agent cannot emit a valid close for its own composition window. CLAIM-30
already treats self-close as a void row.

The remaining adversary does not close directly. It may try to influence the
authorized closer:

- wait until an automated boundary closes the window;
- pad harmless work until a time-based close fires;
- split operations around batch boundaries;
- trigger benign-looking conditions that cause the policy boundary to close;
- route work across sessions or contexts where window identity changes;
- induce a human or scheduler to close the window without seeing the accumulated
  composition pressure.

The key distinction is observable influence, not hidden intent. The design cannot
depend on proving what the agent wanted. It must reason over event timing, close
reasons, accumulated state, and cross-window linkage.

## Candidate policy layers

### 1. Close Authority Registry

A close event should name the actor or boundary that closed the window and the rule
that made it eligible to close.

Minimum fields:

- `close_actor`
- `close_authority_id`
- `close_reason_code`
- `close_rule_ref`
- `window_id`
- `sequence_id`
- `closed_at_step`
- `prior_window_receipt_ref`

The registry is not a verdict engine by itself. It answers whether the close was
authorized and why the boundary believed the window could end.

### 2. Macro-Window or Rolling Velocity Cap

Some quantities should carry across windows for a wider horizon. A macro-window rule
does not erase local windows. It adds a second fold above them.

Examples:

- total refund magnitude over a rolling time horizon;
- repeated access grants across adjacent windows;
- joined source families across a broader session;
- repeated delivery to the same recipient through multiple windows.

This layer should be explicit. If the system wants refund magnitude to reset on every
valid window close, it should say so. If it wants rolling carryover, it should name the
horizon and bound before evaluation.

### 3. Close Reason Codes

Close events should not be anonymous. Reason codes make closes reviewable and
regression-testable.

Examples:

- `batch_completed`
- `human_review_completed`
- `timebox_expired`
- `incident_resolved`
- `policy_rotation`
- `manual_boundary_override`

Reason codes let reviewers distinguish ordinary operational boundaries from closes
that repeatedly appear immediately before a threshold would fire.

### 4. Carryover State

A close can reset local accumulation while still carrying selected state into the next
window.

Possible carryover fields:

- `rolling_threshold_state`
- `recent_recipients_reached`
- `recent_source_combinations`
- `derived_artifact_lineage_refs`
- `close_chain_history`

Carryover must be declared in the policy before evaluation. Retrofitting carryover
after seeing a row would be fold-shopping.

### 5. Cross-Window Receipt Linkage

Ken's (DEV user kenerator) fold-receipt comment named the replay artifact inside a
window. Close authority adds the boundary between windows.

Fold receipts answer:

> What happened inside this window?

Close receipts answer:

> Why was this window allowed to end, and what state carried forward?

The two artifacts should link. A close receipt should point to the fold receipt for
the window it closes and to the next window if the trajectory continues.

## Falsification risks

Any future close-authority claim should fail or narrow if:

1. It overblocks legitimate long workflows by treating ordinary task duration as
   suspicious.
2. It punishes lawful authorized closes that are required for business process,
   incident management, or human review.
3. It turns every long task into one infinite window, making the system impossible to
   operate.
4. It relies on inferred agent intent instead of observable events.
5. It can only catch the time-sliced pattern by adding a hand-written rule after
   seeing the row.
6. It collapses into threshold accumulation by making every macro-window equivalent
   to one ordinary window with a bigger label.

## Relationship to fold receipts

The fold-receipt spec is the immediate artifact layer for CLAIM-30 replay. It makes
the folded state inspectable: accumulated sources, derived artifacts, recipients,
threshold state, triggering clauses, and boundary references.

This brief is adjacent but different. It asks when a fold is allowed to stop and what
state survives the stop.

Fold receipts are about replaying a window. Close-authority design is about governing
the transition between windows.

## Boundary

This brief makes no new evidence claim.

It does not show that time-sliced escape can be caught. It does not show that a
macro-window policy works. It does not change the CLAIM-30 V0 result. It does not
alter the frozen fixtures, fresh-authored sequences, evaluator, results, or ledger.

If this becomes CLAIM-31, the next step is a frozen pre-registration before any rows,
fixtures, evaluator changes, or results exist.
