"""
CLAIM-25 — Signature-Only Gate (baseline).
Verifies signature but does NOT check freshness.
Demonstrates that signing alone leaves the replay window open (scenario 3).
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

from gate_interface import Gate25, Grant25, SourceResponse, GateState, AuthorityEvent25


class SignatureOnlyGate(Gate25):

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
                grant_id=None, decision="BLOCK", decision_timestamp=now,
                sequence_at_issue=None, response_sequence=None,
                stored_mark=None, signature_valid=None, notes="No grant."
            )

        ttl_expires = grant.issued_at.replace(tzinfo=timezone.utc) if grant.issued_at.tzinfo is None else grant.issued_at
        if now > ttl_expires + timedelta(hours=grant.ttl_hours):
            return AuthorityEvent25(
                grant_id=grant.grant_id, decision="BLOCK", decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue, response_sequence=None,
                stored_mark=None, signature_valid=None, notes="Expired."
            )

        if source_response is None:
            return AuthorityEvent25(
                grant_id=grant.grant_id, decision="REFUSED_UNREACHABLE", decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue, response_sequence=None,
                stored_mark=None, signature_valid=None, notes="Unreachable."
            )

        # Checks signature — but NOT sequence floor, NOT mark, NOT source pinning.
        if not source_response.signature_valid:
            return AuthorityEvent25(
                grant_id=grant.grant_id, decision="REFUSED_STALE", decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue, response_sequence=source_response.sequence,
                stored_mark=None, signature_valid=False, notes="Invalid signature."
            )

        if source_response.scope_ceiling != grant.scope:
            return AuthorityEvent25(
                grant_id=grant.grant_id, decision="REFUSED_STALE", decision_timestamp=now,
                sequence_at_issue=grant.sequence_at_issue, response_sequence=source_response.sequence,
                stored_mark=None, signature_valid=True,
                notes=f"Conditions changed: {grant.scope} -> {source_response.scope_ceiling}."
            )

        return AuthorityEvent25(
            grant_id=grant.grant_id, decision="ALLOW", decision_timestamp=now,
            sequence_at_issue=grant.sequence_at_issue, response_sequence=source_response.sequence,
            stored_mark=None, signature_valid=True,
            notes="Signature valid, conditions match. No freshness check — replay window open."
        )
