"""
CLAIM-28 candidate gate: BehavioralNormGate.

Deterministic structural checks against the frozen role profile. No LLM calls, no learned
baseline, and no scenario-specific tuning.
"""

from gate_interface import (
    ALLOW,
    CHALLENGE_ANOMALOUS_AUTHORIZED_MEMORY,
    REFUSE_EXISTING_GATE,
    Gate28,
    Gate28Result,
    RoleProfile,
    Scenario28,
    matching_exception,
)


class BehavioralNormGate(Gate28):
    label = "BehavioralNormGate"

    def evaluate(self, scenario: Scenario28, role_profile: RoleProfile) -> Gate28Result:
        failures = scenario.prior_gate_status.failed_fields()
        if failures:
            return Gate28Result(
                decision=REFUSE_EXISTING_GATE,
                notes=f"Prior gate failure: {', '.join(failures)}",
                violated_norm_fields=failures,
            )

        action = scenario.action_tuple
        memory = scenario.memory
        violations: list[str] = []
        exception_used = None

        if memory.principal not in role_profile.authorized_principals:
            violations.append("principal_not_authorized")

        required_rule = role_profile.required_verification_rules.get(action.action_type)
        exception = matching_exception(scenario, role_profile, required_rule)
        if exception is not None:
            exception_used = exception.exception_id

        if action.action_type not in role_profile.authorized_action_types and exception is None:
            violations.append("action_type_not_authorized")

        if action.action_type in role_profile.sensitive_action_types and required_rule:
            if exception is None:
                violations.append(f"sensitive_action_missing_verification:{required_rule}")

        if action.recipient not in role_profile.authorized_recipients and exception is None:
            violations.append("recipient_not_in_allowed_set")

        if action.action_type == "change_permission_budget":
            violations.append("self_escalation_not_permitted")

        if action.action_type == "publish_public_update" and exception is None:
            content = memory.content.lower()
            doctrine_bypass_markers = [
                "skip",
                "without review",
                "bypass",
                "ignore",
                "override",
            ]
            if any(marker in content for marker in doctrine_bypass_markers):
                violations.append("doctrine_contradiction_without_exception")

        if violations:
            return Gate28Result(
                decision=CHALLENGE_ANOMALOUS_AUTHORIZED_MEMORY,
                notes="Behavioral envelope violation: " + ", ".join(violations),
                violated_norm_fields=violations,
                exception_grant_id=exception_used,
            )

        if exception_used:
            return Gate28Result(
                decision=ALLOW,
                notes=f"Within behavioral envelope via exception grant {exception_used}.",
                violated_norm_fields=[],
                exception_grant_id=exception_used,
            )

        return Gate28Result(
            decision=ALLOW,
            notes="Within frozen behavioral envelope.",
            violated_norm_fields=[],
        )
