"""
CLAIM-24 gate interface.
Both gates (timestamp-only baseline and re-derivation) implement this interface.
When Ken W Alger's Local Brain source is available, write a source adapter
that conforms to SourceAdapter and pass it to RederivationGate.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Grant:
    grant_id: str
    recipient: str
    scope: str
    issued_at: datetime
    ttl_hours: int
    source_snapshot: dict


@dataclass
class AuthorityEvent:
    """Frozen at decision time. Raw values only — no derived labels."""
    grant_id: Optional[str]
    decision: str                    # ALLOW | BLOCK | REFUSED_STALE | REFUSED_UNREACHABLE
    decision_timestamp: datetime
    source_snapshot: Optional[dict]  # what grant recorded at issue time
    source_current: Optional[dict]   # what source returned at execution time
    condition_delta: Optional[dict]  # {"before": {...}, "after": {...}} — raw, never "stale: true"
    ttl_remaining_hours: Optional[float]
    notes: str = ""


class SourceAdapter(ABC):
    """
    Plug in the external source here.
    Must be agent-writable=false — the agent cannot modify the source this reads from.
    """

    @abstractmethod
    def fetch(self, grant: Grant) -> Optional[dict]:
        """
        Fetch current source state for the given grant.
        Returns None if source is unreachable.
        """
        pass

    @property
    @abstractmethod
    def agent_writable(self) -> bool:
        """Must return False. Re-derivation on agent-authored state is self-description."""
        pass


class Gate(ABC):

    @abstractmethod
    def evaluate(self, grant: Optional[Grant], operation_timestamp: datetime) -> AuthorityEvent:
        pass
