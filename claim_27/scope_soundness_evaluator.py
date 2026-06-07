"""
CLAIM-27: Scope-soundness test for CLAIM-25.

Runs A1, A3, A4, and clean-A2 from CLAIM-25 with a content-forgery adversary
active. Signing decision pinned: signature covers (source_address, sequence) only.
Content fields (role, scope_ceiling) are not covered.

The adversary alters role to a forged value while keeping scope_ceiling matching
grant.scope so the condition check passes, and keeps signature_valid=True.

Pre-registered outcomes:
  A — No verdict flips: boundary real and demonstrated.
  B — Any verdict flips: hidden premise found, boundary porous.

Usage:
  python3 scope_soundness_evaluator.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Import CLAIM-25 gate and interface from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent / "claim_25"))

from gate_interface import Grant25, SourceResponse, GateState
from signed_fresh_gate import SignedFreshGate


OPERATION_TIME = datetime(2026, 6, 7, 10, 0, 0, tzinfo=timezone.utc)
ISSUE_TIME     = datetime(2026, 6, 7,  8, 0, 0, tzinfo=timezone.utc)


def make_clean_grant(sequence_at_issue=10, source="auth.internal/policy"):
    return Grant25(
        grant_id="g-scope-test",
        recipient="agent:worker-1",
        scope="read:credentials:dev",
        issued_at=ISSUE_TIME,
        ttl_hours=4,
        source_address=source,
        sequence_at_issue=sequence_at_issue,
        issuer_signature="sig-valid"
    )


def make_clean_state(stored_mark=12, source="auth.internal/policy", tampered=False):
    return GateState(
        stored_mark=stored_mark,
        source_address_runtime=source,
        mark_is_tampered=tampered
    )


def apply_content_forgery(response: SourceResponse) -> SourceResponse:
    """
    Content-forgery adversary: alters role to a forged value.
    Keeps scope_ceiling matching grant.scope so condition check passes.
    Keeps signature_valid=True (signature covers source+sequence only).
    """
    return SourceResponse(
        sequence=response.sequence,
        role="admin:full-access",      # forged — attacker elevated the role
        scope_ceiling=response.scope_ceiling,   # kept matching grant.scope
        signature_valid=True           # signature covers source+sequence only
    )


def run_ablation_with_and_without_adversary(label, grant, response, state):
    gate = SignedFreshGate()

    # Baseline: ablation without content forgery
    result_clean = gate.evaluate(grant, response, state, OPERATION_TIME)

    # With content-forgery adversary active
    forged_response = apply_content_forgery(response)
    result_forged = gate.evaluate(grant, forged_response, state, OPERATION_TIME)

    verdict_flipped = result_clean.decision != result_forged.decision

    return {
        "label": label,
        "baseline_decision": result_clean.decision,
        "forged_decision": result_forged.decision,
        "verdict_flipped": verdict_flipped,
        "baseline_notes": result_clean.notes,
        "forged_notes": result_forged.notes,
    }


def run_all():
    print("="*72)
    print("CLAIM-27: Scope-Soundness Test")
    print("Signing scope pinned: signature covers (source, sequence) only.")
    print("Content-forgery adversary: role forged, scope_ceiling kept matching.")
    print("="*72)

    results = []

    # A1: no grant-carried floor (cold-start replay)
    # Remove sequence_at_issue from grant. stored_mark=None for cold start.
    a1_grant = Grant25(
        grant_id="g-a1", recipient="agent:worker-1", scope="read:credentials:dev",
        issued_at=ISSUE_TIME, ttl_hours=4, source_address="auth.internal/policy",
        sequence_at_issue=None, issuer_signature="sig-valid"
    )
    a1_response = SourceResponse(sequence=8, role="dev-reader",
                                  scope_ceiling="read:credentials:dev", signature_valid=True)
    a1_state = GateState(stored_mark=None, source_address_runtime="auth.internal/policy",
                          mark_is_tampered=False)
    results.append(run_ablation_with_and_without_adversary("A1 (no floor)", a1_grant, a1_response, a1_state))

    # A3: unpinned source (source substitution)
    # Simulate by making grant.source_address match the runtime (already matched in clean run).
    # For ablation: grant was issued pointing at attacker's source, gate accepts it.
    a3_grant = Grant25(
        grant_id="g-a3", recipient="agent:worker-1", scope="read:credentials:dev",
        issued_at=ISSUE_TIME, ttl_hours=4, source_address="attacker.copy/policy",
        sequence_at_issue=10, issuer_signature="sig-valid"
    )
    a3_response = SourceResponse(sequence=15, role="dev-reader",
                                  scope_ceiling="read:credentials:dev", signature_valid=True)
    a3_state = GateState(stored_mark=12, source_address_runtime="attacker.copy/policy",
                          mark_is_tampered=False)
    results.append(run_ablation_with_and_without_adversary("A3 (unpinned source)", a3_grant, a3_response, a3_state))

    # A4: no signature check (forged response accepted)
    # Simulate by passing signature_valid=True on a response that would be forged.
    # The ablation in CLAIM-25 patched signature_valid=True on a scenario where it was False.
    # Here: response has signature_valid=True already (adversary environment).
    a4_grant = make_clean_grant(sequence_at_issue=10)
    a4_response = SourceResponse(sequence=50, role="dev-reader",
                                  scope_ceiling="read:credentials:dev", signature_valid=True)
    a4_state = make_clean_state(stored_mark=12)
    results.append(run_ablation_with_and_without_adversary("A4 (no sig check)", a4_grant, a4_response, a4_state))

    # Clean A2: rewindable mark (tamper detection disabled, grant floor passes naturally)
    # grant.sequence_at_issue=5, replayed sequence=8 (8>=5, floor passes).
    # mark_is_tampered is the only property under test — but we run full gate here,
    # so we simulate tamper detection being disabled by setting mark_is_tampered=False
    # even though the mark was rewound (stored_mark=5 is a legitimately low value).
    a2_grant = Grant25(
        grant_id="g-a2", recipient="agent:worker-1", scope="read:credentials:dev",
        issued_at=ISSUE_TIME, ttl_hours=4, source_address="auth.internal/policy",
        sequence_at_issue=5, issuer_signature="sig-valid"
    )
    a2_response = SourceResponse(sequence=8, role="dev-reader",
                                  scope_ceiling="read:credentials:dev", signature_valid=True)
    a2_state = GateState(stored_mark=5, source_address_runtime="auth.internal/policy",
                          mark_is_tampered=False)
    results.append(run_ablation_with_and_without_adversary("Clean-A2 (rewindable mark)", a2_grant, a2_response, a2_state))

    # Print results
    print(f"\n{'Label':<28} {'Baseline':<22} {'With Forgery':<22} {'Flipped'}")
    print(f"{'-'*28} {'-'*22} {'-'*22} {'-'*7}")
    for r in results:
        flipped = "YES — HIDDEN PREMISE" if r["verdict_flipped"] else "No"
        print(f"{r['label']:<28} {r['baseline_decision']:<22} {r['forged_decision']:<22} {flipped}")

    any_flipped = any(r["verdict_flipped"] for r in results)

    print()
    if not any_flipped:
        print("OUTCOME A: Boundary real and demonstrated.")
        print("All four CLAIM-25 properties held with content-forgery adversary active.")
        print("Content-integrity is genuinely out of scope under signature covers")
        print("(source, sequence) only. Positive finding — not merely an omission.")
    else:
        print("OUTCOME B: Hidden premise found.")
        print("At least one verdict flipped. Content-integrity is load-bearing.")
        print("CLAIM-25 boundary is porous. Scope statement must be updated.")
        for r in results:
            if r["verdict_flipped"]:
                print(f"  Flipped: {r['label']}")
                print(f"    Baseline: {r['baseline_decision']} — {r['baseline_notes']}")
                print(f"    Forged:   {r['forged_decision']} — {r['forged_notes']}")

    return results


if __name__ == "__main__":
    run_all()
