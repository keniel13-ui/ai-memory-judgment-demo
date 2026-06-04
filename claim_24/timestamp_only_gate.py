"""
CLAIM-24 baseline: timestamp-only gate.
Does not re-derive. Only checks whether the grant's TTL has expired.
This is the gate that CLAIM-24 argues is insufficient.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

from gate_interface import Gate, Grant, AuthorityEvent


class TimestampOnlyGate(Gate):

    def evaluate(self, grant: Optional[Grant], operation_timestamp: datetime) -> AuthorityEvent:
        now = operation_timestamp

        if grant is None:
            return AuthorityEvent(
                grant_id=None,
                decision="BLOCK",
                decision_timestamp=now,
                source_snapshot=None,
                source_current=None,
                condition_delta=None,
                ttl_remaining_hours=None,
                notes="no grant present"
            )

        expiry = grant.issued_at + timedelta(hours=grant.ttl_hours)
        ttl_remaining = (expiry - now).total_seconds() / 3600

        if now > expiry:
            return AuthorityEvent(
                grant_id=grant.grant_id,
                decision="BLOCK",
                decision_timestamp=now,
                source_snapshot=grant.source_snapshot,
                source_current=None,
                condition_delta=None,
                ttl_remaining_hours=round(ttl_remaining, 2),
                notes="ttl expired"
            )

        # TTL still valid — timestamp-only gate allows without checking source
        return AuthorityEvent(
            grant_id=grant.grant_id,
            decision="ALLOW",
            decision_timestamp=now,
            source_snapshot=grant.source_snapshot,
            source_current=None,
            condition_delta=None,
            ttl_remaining_hours=round(ttl_remaining, 2),
            notes="ttl valid — source not checked"
        )
