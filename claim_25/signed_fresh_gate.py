"""
CLAIM-25 — Signed-AND-Fresh Gate.
Implements all four required properties:
  1. Pinned source address (reads from grant.source_address, not runtime-supplied)
  2. Signature verification on source response
  3. Grant-carried sequence floor (floor = grant.sequence_at_issue, not stored_mark alone)
  4. Tamper-evident mark (refuses if stored_mark was lowered)
"""

from datetime import datetime, timezone
from typing import Optional

from gate_interface import Gate25, Grant25, SourceResponse, GateState, AuthorityEvent25


class SignedFreshGate(Gate25):

    def evaluate(
        self,
        grant: Optional[Grant25],
        source_response: Optional[SourceResponse],
        gate_state: GateState,
        operation_timestamp: datetime
    ) -> AuthorityEvent25:

        now = operation_timestamp

        if grant is None:
            return AuthorityEvent25(
                grant_id=None,
                decision="BLOCK",
                decision_timestamp=now,
                sequence_at_issue=None,
                response_sequence=None,
                stored_mark=gate_state.stored_mark,
                signature_valid=None,
                notes="No grant present."
            )

        ttl_expires = grant.issued_at.replace(tzinfo=timezone.utc) if grant.issued_at.tzinfo is None else grant.issued_at
        from datetime import timedelta
        expires_at = ttl_expires + timedelta(hours=grant.ttl_hours)
        if now > expires_at:
            return AuthorityEvent25(
                grant_id=grant.grant_id,
                decision="BLOCK",
                decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue,
                response_sequence=None,
                stored_mark=gate_state.stored_mark,
                signature_valid=None,
                notes="Grant expired."
            )

        # Property 1: Pinned source — gate reads from grant.source_address only.
        if gate_state.source_address_runtime != grant.source_address:
            return AuthorityEvent25(
                grant_id=grant.grant_id,
                decision="REFUSED_STALE",
                decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue,
                response_sequence=None,
                stored_mark=gate_state.stored_mark,
                signature_valid=None,
                notes=f"Source address mismatch. Grant pins {grant.source_address}, runtime supplied {gate_state.source_address_runtime}."
            )

        if source_response is None:
            return AuthorityEvent25(
                grant_id=grant.grant_id,
                decision="REFUSED_UNREACHABLE",
                decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue,
                response_sequence=None,
                stored_mark=gate_state.stored_mark,
                signature_valid=None,
                notes="Source unreachable."
            )

        # Property 2: Signature verification.
        if not source_response.signature_valid:
            return AuthorityEvent25(
                grant_id=grant.grant_id,
                decision="REFUSED_STALE",
                decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue,
                response_sequence=source_response.sequence,
                stored_mark=gate_state.stored_mark,
                signature_valid=False,
                notes="Response signature invalid. Possible forgery or tampering."
            )

        # Property 4: Tamper-evident mark — refuse if mark was lowered.
        if gate_state.mark_is_tampered:
            return AuthorityEvent25(
                grant_id=grant.grant_id,
                decision="REFUSED_TAMPERED",
                decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue,
                response_sequence=source_response.sequence,
                stored_mark=gate_state.stored_mark,
                signature_valid=True,
                notes="High-water mark storage tampered — mark was lowered. Refusing."
            )

        # Property 3: Grant-carried sequence floor.
        # Floor = max(grant.sequence_at_issue, stored_mark) if both exist.
        # On cold start (stored_mark=None), floor = grant.sequence_at_issue.
        # If grant.sequence_at_issue is None (ablation), floor = stored_mark only.
        grant_floor = grant.sequence_at_issue
        stored = gate_state.stored_mark

        if grant_floor is not None and stored is not None:
            floor = max(grant_floor, stored)
        elif grant_floor is not None:
            floor = grant_floor
        elif stored is not None:
            floor = stored
        else:
            floor = None

        if floor is not None and source_response.sequence < floor:
            return AuthorityEvent25(
                grant_id=grant.grant_id,
                decision="REFUSED_STALE",
                decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue,
                response_sequence=source_response.sequence,
                stored_mark=gate_state.stored_mark,
                signature_valid=True,
                notes=f"Response sequence {source_response.sequence} < floor {floor}. Replay or stale response rejected."
            )

        # All four properties satisfied. Check source conditions.
        grant_scope = grant.scope
        source_ceiling = source_response.scope_ceiling

        if source_ceiling != grant_scope:
            return AuthorityEvent25(
                grant_id=grant.grant_id,
                decision="REFUSED_STALE",
                decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue,
                response_sequence=source_response.sequence,
                stored_mark=gate_state.stored_mark,
                signature_valid=True,
                notes=f"Source conditions changed. Grant scope: {grant_scope}. Source ceiling now: {source_ceiling}."
            )

        return AuthorityEvent25(
            grant_id=grant.grant_id,
            decision="ALLOW",
            decision_timestamp=now,
            sequence_at_issue=grant.sequence_at_issue,
            response_sequence=source_response.sequence,
            stored_mark=gate_state.stored_mark,
            signature_valid=True,
            notes="All four properties satisfied. Signed, fresh, source pinned, mark current."
        )
