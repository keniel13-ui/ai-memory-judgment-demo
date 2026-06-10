"""
CLAIM-28 baseline: AuthorityOnlyGate.

This gate checks only whether the prior authority/freshness/verification/audit-pairing
layer passed. It intentionally ignores content and behavioral norms.
"""

from gate_interface import (
    ALLOW,
    REFUSE_EXISTING_GATE,
    Gate28,
    Gate28Result,
    RoleProfile,
    Scenario28,
)


class AuthorityOnlyGate(Gate28):
    label = "AuthorityOnlyGate"

    def evaluate(self, scenario: Scenario28, role_profile: RoleProfile) -> Gate28Result:
        failures = scenario.prior_gate_status.failed_fields()
        if failures:
            return Gate28Result(
                decision=REFUSE_EXISTING_GATE,
                notes=f"Prior gate failure: {', '.join(failures)}",
                violated_norm_fields=failures,
            )

        return Gate28Result(
            decision=ALLOW,
            notes="Prior authority/freshness/verification/audit-pairing checks passed; content ignored.",
            violated_norm_fields=[],
        )
