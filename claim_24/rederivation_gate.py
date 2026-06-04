"""
CLAIM-24 re-derivation gate.
Reads current source state at execution time from an agent-writable=false source.
Compares against what the grant recorded at issue time.
If conditions diverged: REFUSED_STALE.
If source unreachable: REFUSED_UNREACHABLE (separate cell — not REFUSED_STALE).
"""

from datetime import datetime, timedelta
from typing import Optional

from gate_interface import Gate, Grant, AuthorityEvent, SourceAdapter


class RederivationGate(Gate):

    def __init__(self, source: SourceAdapter):
        assert not source.agent_writable, (
            "Source adapter must be agent-writable=false. "
            "Re-deriving from agent-authored state is self-description one level up."
        )
        self.source = source

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

        # TTL valid — now re-derive from external source
        current = self.source.fetch(grant)

        if current is None:
            return AuthorityEvent(
                grant_id=grant.grant_id,
                decision="REFUSED_UNREACHABLE",
                decision_timestamp=now,
                source_snapshot=grant.source_snapshot,
                source_current=None,
                condition_delta=None,
                ttl_remaining_hours=round(ttl_remaining, 2),
                notes="source unreachable at execution time"
            )

        # Compare source_snapshot (at issue time) vs current (at execution time)
        if current != grant.source_snapshot:
            # Store raw before/after — never a derived "stale: true" label
            delta = {
                "before": grant.source_snapshot,
                "after": current
            }
            return AuthorityEvent(
                grant_id=grant.grant_id,
                decision="REFUSED_STALE",
                decision_timestamp=now,
                source_snapshot=grant.source_snapshot,
                source_current=current,
                condition_delta=delta,
                ttl_remaining_hours=round(ttl_remaining, 2),
                notes="source conditions changed since grant issuance"
            )

        return AuthorityEvent(
            grant_id=grant.grant_id,
            decision="ALLOW",
            decision_timestamp=now,
            source_snapshot=grant.source_snapshot,
            source_current=current,
            condition_delta=None,
            ttl_remaining_hours=round(ttl_remaining, 2),
            notes="ttl valid, source conditions unchanged"
        )
