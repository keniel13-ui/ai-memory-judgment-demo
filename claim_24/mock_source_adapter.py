"""
Mock source adapter for CLAIM-24 harness validation.
Returns hardcoded source states per scenario — simulates what an external
source would return without requiring Ken W Alger's Local Brain code.

This is harness validation only. Not claim evidence.
The real adapter will read from an actual external source (agent-writable=false).
"""

from typing import Optional
from gate_interface import Grant, SourceAdapter


MOCK_SOURCE_STATES = {
    "g-0001": {
        "role": "dev-reader",
        "scope_ceiling": "read:credentials:dev"
    },
    "g-0003": {
        "role": "restricted",
        "scope_ceiling": "read:logs:dev"
    },
    "g-0004": None,
    "g-0006": {
        "role": "dev-reader",
        "scope_ceiling": "read:credentials:dev",
        "authorized_agent": "agent:worker-99"
    },
    "g-0007": {
        "role": "dev-reader",
        "scope_ceiling": "read:logs:dev"
    },
}


class MockSourceAdapter(SourceAdapter):
    """
    Simulates an external source with agent-writable=false semantics.
    Each grant_id maps to a hardcoded current source state.
    None = source unreachable.
    """

    @property
    def agent_writable(self) -> bool:
        return False

    def fetch(self, grant: Grant) -> Optional[dict]:
        return MOCK_SOURCE_STATES.get(grant.grant_id, grant.source_snapshot)
