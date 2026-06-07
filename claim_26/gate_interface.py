"""
CLAIM-26 gate interface.
Property under test: paired authority-action events for auditability.
All gates implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AuthorityRecord:
    authority_event_id: str
    grant_id: str
    decision: str
    decision_timestamp: datetime
    snapshot_hash: Optional[str]
    source_sequence: Optional[int]
    policy_version: Optional[str]
    run_id: str
    is_immutable: bool
    written_at: datetime
    source_uri: Optional[str] = None


@dataclass
class ActionRecord:
    action_id: str
    authority_event_id: Optional[str]
    action_type: str
    run_id: str
    snapshot_hash: Optional[str]
    written_at: datetime


@dataclass
class AuditContext:
    # Ground truth: what the source was actually serving at decision time.
    # Used to detect audit gaps — authority hashes that don't correspond to
    # any real source state.
    active_snapshot_hash: Optional[str]


@dataclass
class AuditResult:
    decision: str
    notes: str
    authority_event_id: Optional[str] = None


class Gate26(ABC):

    @abstractmethod
    def evaluate(
        self,
        authority_record: Optional[AuthorityRecord],
        action_record: ActionRecord,
        audit_context: AuditContext,
    ) -> AuditResult:
        pass
