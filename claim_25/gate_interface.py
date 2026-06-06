"""
CLAIM-25 gate interface.
Property under test: signed-AND-fresh (four required components).
All gates implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Grant25:
    grant_id: str
    recipient: str
    scope: str
    issued_at: datetime
    ttl_hours: int
    source_address: str
    sequence_at_issue: Optional[int]
    issuer_signature: str


@dataclass
class SourceResponse:
    sequence: int
    role: str
    scope_ceiling: str
    signature_valid: bool


@dataclass
class GateState:
    stored_mark: Optional[int]
    source_address_runtime: str
    mark_is_tampered: bool


@dataclass
class AuthorityEvent25:
    grant_id: Optional[str]
    decision: str
    decision_timestamp: datetime
    sequence_at_issue: Optional[int]
    response_sequence: Optional[int]
    stored_mark: Optional[int]
    signature_valid: Optional[bool]
    notes: str = ""


class Gate25(ABC):

    @abstractmethod
    def evaluate(
        self,
        grant: Optional[Grant25],
        source_response: Optional[SourceResponse],
        gate_state: GateState,
        operation_timestamp: datetime
    ) -> AuthorityEvent25:
        pass
