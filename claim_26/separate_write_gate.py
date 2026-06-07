"""
CLAIM-26 baseline 3: SeparateWriteAuditGate.

Represents an audit system that logs both authority and action records with
snapshot hashes and checks immutability — but does not enforce write order
and does not check the audit gap against an external verification context.
Checks: authority exists, snapshot_hash present, cross-record hash match, immutable.
Does NOT check: write order (authority before action), audit gap.

Expected failures: post_hoc, audit_gap.
"""

from typing import Optional
from gate_interface import Gate26, AuthorityRecord, ActionRecord, AuditContext, AuditResult


class SeparateWriteGate(Gate26):

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

        if authority_record.snapshot_hash is None:
            return AuditResult(
                "REFUSED_MUTABLE_SOURCE",
                "Authority record contains no snapshot hash — mutable source reference only",
            )

        if not authority_record.is_immutable:
            return AuditResult(
                "REFUSED_TAMPERED",
                "Authority record is mutable — not append-only",
            )

        if (
            action_record.snapshot_hash is not None
            and authority_record.snapshot_hash != action_record.snapshot_hash
        ):
            return AuditResult(
                "REFUSED_SNAPSHOT_MISMATCH",
                "Authority and action snapshot hashes disagree",
            )

        return AuditResult(
            "ALLOW",
            "Hash present, immutable, hashes agree (write order not enforced; no audit gap check)",
            authority_record.authority_event_id,
        )
