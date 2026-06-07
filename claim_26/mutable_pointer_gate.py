"""
CLAIM-26 baseline 2: MutablePointerAuditGate.

Represents an audit system that logs authority records with source references
but accepts a mutable URI in place of a frozen snapshot hash.
Checks: authority exists, decision is ALLOW, has some source reference (hash OR uri).
Does NOT check: write order, snapshot hash required (accepts URI), immutability,
cross-record hash agreement, audit gap.

Expected failures: post_hoc, mutable_ptr, hash_mismatch, tampered, audit_gap.
"""

from typing import Optional
from gate_interface import Gate26, AuthorityRecord, ActionRecord, AuditContext, AuditResult


class MutablePointerAuditGate(Gate26):

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

        if authority_record.decision != "ALLOW":
            return AuditResult(
                "REFUSED_UNPAIRED",
                f"Authority record decision was not ALLOW: {authority_record.decision}",
            )

        has_source_ref = (
            authority_record.snapshot_hash is not None
            or authority_record.source_uri is not None
        )
        if not has_source_ref:
            return AuditResult(
                "REFUSED_MUTABLE_SOURCE",
                "Authority record has no source reference (no hash and no URI)",
            )

        return AuditResult(
            "ALLOW",
            "Source reference present (hash or URI accepted — no frozen snapshot required)",
            authority_record.authority_event_id,
        )
