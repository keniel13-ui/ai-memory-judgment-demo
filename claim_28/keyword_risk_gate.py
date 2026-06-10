"""
CLAIM-28 weak baseline: KeywordRiskGate.

This gate preserves prior-gate refusals, then scans memory text for frozen keyword risk
terms from role_profile.json. It is intentionally shallow.
"""

from gate_interface import (
    ALLOW,
    CHALLENGE_KEYWORD_RISK,
    REFUSE_EXISTING_GATE,
    Gate28,
    Gate28Result,
    RoleProfile,
    Scenario28,
)


class KeywordRiskGate(Gate28):
    label = "KeywordRiskGate"

    def evaluate(self, scenario: Scenario28, role_profile: RoleProfile) -> Gate28Result:
        failures = scenario.prior_gate_status.failed_fields()
        if failures:
            return Gate28Result(
                decision=REFUSE_EXISTING_GATE,
                notes=f"Prior gate failure: {', '.join(failures)}",
                violated_norm_fields=failures,
            )

        content = scenario.memory.content.lower()
        matched_terms = [
            term for term in role_profile.keyword_risk_terms
            if term.lower() in content
        ]

        if matched_terms:
            return Gate28Result(
                decision=CHALLENGE_KEYWORD_RISK,
                notes=f"Keyword risk terms matched: {', '.join(matched_terms)}",
                violated_norm_fields=[f"keyword:{term}" for term in matched_terms],
            )

        return Gate28Result(
            decision=ALLOW,
            notes="No frozen keyword risk terms matched.",
            violated_norm_fields=[],
        )
