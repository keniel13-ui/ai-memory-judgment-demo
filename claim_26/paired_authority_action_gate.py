"""
CLAIM-26 closing gate: PairedAuthorityActionGate.

Enforces all four required properties for audit-safe actions:
  1. Pairing      — authority event must exist and link to action by ID
  2. Write order  — authority written before or simultaneously with action
  3. Snapshot hash — authority contains a frozen snapshot hash, not a mutable pointer
  4. Immutability  — authority record is append-only

Plus two consistency checks:
  5. Cross-record hash match — authority and action snapshot hashes agree
  6. Audit gap check         — authority hash matches source state at decision time
"""

from typing import Optional
from gate_interface import Gate26, AuthorityRecord, ActionRecord, AuditContext, AuditResult


class PairedAuthorityActionGate(Gate26):

    def evaluate(
        self,
        authority_record: Optional[AuthorityRecord],
        action_record: ActionRecord,
        audit_context: AuditContext,
    ) -> AuditResult:

        # 1. Pairing
        if authority_record is None or action_record.authority_event_id is None:
            return AuditResult(
                "REFUSED_UNPAIRED",
                "No authority event linked to this action",
            )

        if authority_record.authority_event_id != action_record.authority_event_id:
            return AuditResult(
                "REFUSED_UNPAIRED",
                "Authority event ID does not match action record reference",
            )

        # 2. Write order — authority must precede or match action write time
        if authority_record.written_at > action_record.written_at:
            return AuditResult(
                "REFUSED_POST_HOC",
                "Authority event written after action — post-hoc reconstruction, not prior authorization",
            )

        # 3. Snapshot hash required
        if authority_record.snapshot_hash is None:
            return AuditResult(
                "REFUSED_MUTABLE_SOURCE",
                "Authority record contains no snapshot hash — cannot reconstruct what was read at decision time",
            )

        # 4. Immutability
        if not authority_record.is_immutable:
            return AuditResult(
                "REFUSED_TAMPERED",
                "Authority record is mutable — evidence may have been altered after the action",
            )

        # 5. Cross-record hash consistency
        if (
            action_record.snapshot_hash is not None
            and authority_record.snapshot_hash != action_record.snapshot_hash
        ):
            return AuditResult(
                "REFUSED_SNAPSHOT_MISMATCH",
                "Authority and action snapshot hashes disagree — action taken against different evidence than recorded",
            )

        # 6. Audit gap — authority hash must match source state at decision time
        if (
            audit_context.active_snapshot_hash is not None
            and authority_record.snapshot_hash != audit_context.active_snapshot_hash
        ):
            return AuditResult(
                "REFUSED_AUDIT_GAP",
                "Authority snapshot hash does not match source state at decision time — evidence does not correspond to a real source state",
            )

        return AuditResult(
            "ALLOW",
            "Audit-safe: paired, write-ordered, hash-bound, immutable, consistent",
            authority_record.authority_event_id,
        )
