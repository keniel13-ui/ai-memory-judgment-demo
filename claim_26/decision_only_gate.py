"""
CLAIM-26 baseline 1: DecisionOnlyGate.

Represents an audit system that logs only the final decision.
Checks: authority record exists and says ALLOW.
Does NOT check: write order, snapshot hash, immutability, hash consistency, audit gap.

Expected failures: post_hoc, mutable_ptr, hash_mismatch, tampered, audit_gap.
"""

from typing import Optional
from gate_interface import Gate26, AuthorityRecord, ActionRecord, AuditContext, AuditResult


class DecisionOnlyGate(Gate26):

    def evaluate(
        self,
        authority_record: Optional[AuthorityRecord],
        action_record: ActionRecord,
        audit_context: AuditContext,
    ) -> AuditResult:

        if authority_record is None:
            return AuditResult(
                "REFUSED_UNPAIRED",
                "No authority record found",
            )

        if authority_record.decision == "ALLOW":
            return AuditResult(
                "ALLOW",
                "Decision: ALLOW (no structural audit checks performed)",
                authority_record.authority_event_id,
            )

        return AuditResult(
            "REFUSED_UNPAIRED",
            f"Authority record decision was not ALLOW: {authority_record.decision}",
        )
