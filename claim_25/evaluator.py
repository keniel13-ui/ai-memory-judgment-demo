"""
CLAIM-25 evaluator.
Runs 5 core scenarios + 4 ablation variants through the signed-AND-fresh gate
and the signature-only baseline. Ablations must return ALLOW to prove each
property is independently load-bearing.

Usage:
  python3 evaluator.py                  # runs SignedFreshGate on core scenarios
  python3 evaluator.py full             # runs both gates on all 9 scenarios
  python3 evaluator.py ablations        # runs ablation gate variants only
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from gate_interface import Grant25, SourceResponse, GateState, AuthorityEvent25
from signed_fresh_gate import SignedFreshGate
from signature_only_gate import SignatureOnlyGate


SCENARIOS_PATH = Path(__file__).parent / "scenarios.json"
OPERATION_TIME = datetime(2026, 6, 6, 12, 0, 0, tzinfo=timezone.utc)


def load_scenarios():
    with open(SCENARIOS_PATH) as f:
        return json.load(f)


def parse_grant(raw: Optional[dict]) -> Optional[Grant25]:
    if raw is None:
        return None
    return Grant25(
        grant_id=raw["grant_id"],
        recipient=raw["recipient"],
        scope=raw["scope"],
        issued_at=datetime.fromisoformat(raw["issued_at"].replace("Z", "+00:00")),
        ttl_hours=raw["ttl_hours"],
        source_address=raw["source_address"],
        sequence_at_issue=raw.get("sequence_at_issue"),
        issuer_signature=raw["issuer_signature"]
    )


def parse_source(raw: Optional[dict]) -> Optional[SourceResponse]:
    if raw is None:
        return None
    return SourceResponse(
        sequence=raw["sequence"],
        role=raw["role"],
        scope_ceiling=raw["scope_ceiling"],
        signature_valid=raw["signature_valid"]
    )


def parse_state(raw: dict) -> GateState:
    return GateState(
        stored_mark=raw.get("stored_mark"),
        source_address_runtime=raw["source_address_runtime"],
        mark_is_tampered=raw.get("mark_is_tampered", False)
    )


def run_gate(gate, gate_label: str, scenarios: list, filter_ids: Optional[list] = None):
    targets = [s for s in scenarios if filter_ids is None or s["id"] in filter_ids]

    print(f"\n{'='*70}")
    print(f"Gate: {gate_label}")
    print(f"Run time: {OPERATION_TIME.isoformat()}")
    print(f"{'='*70}")
    print(f"{'ID':<4} {'Label':<5} {'Expected':<22} {'Got':<22} {'Pass':<6} Notes")
    print(f"{'-'*4} {'-'*5} {'-'*22} {'-'*22} {'-'*6} {'-'*30}")

    all_pass = True
    results = []

    for s in targets:
        is_ablation = s["id"] >= 6 and s.get("ablation") != "overlap_assertion"
        is_overlap = s.get("ablation") == "overlap_assertion"
        grant = parse_grant(s.get("grant"))
        source = parse_source(s.get("source_response"))
        state = parse_state(s["gate_state"])

        # For ablation scenarios, use the ablation-specific gate behavior
        if is_ablation:
            ablation_type = s.get("ablation", "")
            event = run_ablation(gate, ablation_type, grant, source, state, OPERATION_TIME)
        else:
            event = gate.evaluate(grant, source, state, OPERATION_TIME)

        expected = s["expected"]
        got = event.decision
        decision_pass = got == expected

        # For ablations: verify the structural condition that proves the specific
        # failure mode fired — not a string match against gate notes (the gate doesn't
        # know it's being ablated). Each ablation type has a structural witness.
        failure_mode = s.get("failure_mode")
        ablation_type = s.get("ablation", "")
        if is_ablation and decision_pass:
            mode_confirmed = _confirm_failure_mode(ablation_type, grant, source, state, event)
        else:
            mode_confirmed = True  # non-ablation or decision already wrong — handled above

        passed = decision_pass and mode_confirmed
        if not passed:
            all_pass = False

        marker = "PASS" if passed else "FAIL"
        ablation_flag = " [ABLATION]" if is_ablation else (" [OVERLAP]" if is_overlap else "")
        label = s.get("label", "")
        mode_note = f" | mode: {failure_mode[:35]}" if (is_ablation and failure_mode) else ""
        print(f"{s['id']:<4} {label:<5} {expected:<22} {got:<22} {marker:<6} {event.notes[:40]}{ablation_flag}{mode_note}")

        results.append({
            "id": s["id"],
            "label": label,
            "expected": expected,
            "got": got,
            "passed": passed,
            "decision_pass": decision_pass,
            "mode_confirmed": mode_confirmed,
            "failure_mode": failure_mode,
            "is_ablation": is_ablation,
            "notes": event.notes
        })

    print(f"\nAll passed: {all_pass}")

    ablation_results = [r for r in results if r["is_ablation"]]
    if ablation_results:
        ablation_failures = [r for r in ablation_results if not r["passed"]]
        print(f"Ablations: {len(ablation_results)} run, {len(ablation_failures)} did not produce expected failure")
        if ablation_failures:
            for f in ablation_failures:
                if not f.get("decision_pass"):
                    print(f"  *** Ablation {f['label']} (id={f['id']}) expected {f['expected']} but got {f['got']} — property may not be load-bearing in this implementation")
                elif not f.get("mode_confirmed"):
                    print(f"  *** Ablation {f['label']} (id={f['id']}) correct decision but structural witness FAILED — possible confounded control")
                    print(f"      Named failure_mode: {f.get('failure_mode')}")
                    print(f"      Gate notes: {f['notes'][:100]}")

    return results


def _confirm_failure_mode(ablation_type: str, grant, source, state, event) -> bool:
    """
    Structural witness check: verify the specific attack succeeded for the right reason.
    Gate notes say 'All four properties satisfied' on any ALLOW path — they don't embed
    ablation context. Instead we inspect the structural conditions that prove the named
    failure mode fired, not a different property accidentally blocking first.
    """
    if ablation_type == "no_sequence_floor":
        # Confirmed: gate had no floor from any source (both were None after ablation)
        return event.sequence_at_issue is None and event.stored_mark is None

    elif ablation_type == "rewindable_mark":
        # Confirmed: mark was stored, floor passed (sequence_at_issue=5 <= 8),
        # tamper path bypassed (mark_is_tampered patched False), gate returned ALLOW.
        # sequence_at_issue is NOT None — floor is still active, just not the guard here.
        return event.stored_mark is not None and event.sequence_at_issue is not None and event.decision == "ALLOW"

    elif ablation_type == "unpinned_source":
        # Confirmed: grant.source_address was replaced with runtime address (attacker's)
        # Gate accepted because it now "matches" — source pinning was bypassed
        return event.decision == "ALLOW"

    elif ablation_type == "no_signature":
        # Confirmed: forged response (original signature_valid=False) was accepted as ALLOW
        # The ablation patched signature_valid=True before calling gate, so gate passed it
        return event.signature_valid is True and event.decision == "ALLOW"

    return True  # unknown ablation type — don't fail on it


def run_ablation(full_gate, ablation_type: str, grant, source, state, now):
    """
    Run the signed-AND-fresh gate with one property intentionally disabled.
    Each ablation must produce ALLOW (or REFUSED_TAMPERED for A2 with detection disabled)
    to prove the removed property was load-bearing.
    """
    if ablation_type == "no_sequence_floor":
        # Remove grant-carried floor: set sequence_at_issue to None in grant
        if grant:
            grant = Grant25(
                grant_id=grant.grant_id, recipient=grant.recipient, scope=grant.scope,
                issued_at=grant.issued_at, ttl_hours=grant.ttl_hours,
                source_address=grant.source_address, sequence_at_issue=None,
                issuer_signature=grant.issuer_signature
            )
        return full_gate.evaluate(grant, source, state, now)

    elif ablation_type == "rewindable_mark":
        # Disable tamper detection only. Grant floor is NOT removed — the clean A2
        # scenario sets sequence_at_issue=5 so the floor already passes (8 >= 5).
        # Only tamper detection is stripped. This is the clean isolation.
        ablated_state = GateState(
            stored_mark=state.stored_mark,
            source_address_runtime=state.source_address_runtime,
            mark_is_tampered=False
        )
        return full_gate.evaluate(grant, source, ablated_state, now)

    elif ablation_type == "unpinned_source":
        # Disable source pinning: let gate use runtime address regardless of grant address
        # We simulate by making grant.source_address match the runtime address
        if grant:
            grant = Grant25(
                grant_id=grant.grant_id, recipient=grant.recipient, scope=grant.scope,
                issued_at=grant.issued_at, ttl_hours=grant.ttl_hours,
                source_address=state.source_address_runtime,
                sequence_at_issue=grant.sequence_at_issue,
                issuer_signature=grant.issuer_signature
            )
        return full_gate.evaluate(grant, source, state, now)

    elif ablation_type == "no_signature":
        # Disable signature check: mark the forged response as signature_valid=True
        if source:
            source = SourceResponse(
                sequence=source.sequence,
                role=source.role,
                scope_ceiling=source.scope_ceiling,
                signature_valid=True
            )
        return full_gate.evaluate(grant, source, state, now)

    elif ablation_type == "overlap_assertion":
        # Not an ablation — run full gate unmodified. Both guards are active.
        # Expected result is REFUSED_TAMPERED (tamper check fires before floor check).
        # This documents the defense-in-depth zone: either guard dropped = regression.
        return full_gate.evaluate(grant, source, state, now)

    else:
        return full_gate.evaluate(grant, source, state, now)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "core"
    data = load_scenarios()
    scenarios = data["scenarios"]

    gate = SignedFreshGate()
    baseline = SignatureOnlyGate()

    if mode == "core":
        print("\nRunning core scenarios (1-5) on SignedFreshGate")
        run_gate(gate, "SignedFreshGate", scenarios, filter_ids=[1, 2, 3, 4, 5])

    elif mode == "ablations":
        print("\nRunning ablation variants (6-9) + overlap assertion (10)")
        run_gate(gate, "SignedFreshGate (ablation mode)", scenarios, filter_ids=[6, 7, 8, 9, 10])

    elif mode == "full":
        print("\nFull run: SignedFreshGate (core + ablations + overlap) vs SignatureOnlyGate (baseline)")
        run_gate(gate, "SignedFreshGate — core", scenarios, filter_ids=[1, 2, 3, 4, 5])
        run_gate(baseline, "SignatureOnlyGate — baseline (no freshness)", scenarios, filter_ids=[1, 2, 3, 4, 5])
        run_gate(gate, "SignedFreshGate — ablations + overlap", scenarios, filter_ids=[6, 7, 8, 9, 10])

    else:
        print(f"Unknown mode: {mode}. Use 'core', 'ablations', or 'full'.")
        sys.exit(1)
