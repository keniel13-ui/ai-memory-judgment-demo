"""
CLAIM-28 gate interface.

Property under test: behavioral norm detection for authorized memory.

The scenario packet and frozen role profile are authored before these gates.
All gates are deterministic; no LLM calls or learned baselines are used.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


ALLOW = "ALLOW"
REFUSE_EXISTING_GATE = "REFUSE_EXISTING_GATE"
CHALLENGE_KEYWORD_RISK = "CHALLENGE_KEYWORD_RISK"
CHALLENGE_ANOMALOUS_AUTHORIZED_MEMORY = "CHALLENGE_ANOMALOUS_AUTHORIZED_MEMORY"


@dataclass
class PriorGateStatus:
    authority_valid: bool
    freshness_valid: bool
    verification_valid: bool
    audit_pairing_valid: bool

    @property
    def all_valid(self) -> bool:
        return (
            self.authority_valid
            and self.freshness_valid
            and self.verification_valid
            and self.audit_pairing_valid
        )

    def failed_fields(self) -> list[str]:
        failures: list[str] = []
        if not self.authority_valid:
            failures.append("authority_valid")
        if not self.freshness_valid:
            failures.append("freshness_valid")
        if not self.verification_valid:
            failures.append("verification_valid")
        if not self.audit_pairing_valid:
            failures.append("audit_pairing_valid")
        return failures


@dataclass
class MemoryInstruction:
    memory_id: str
    principal: str
    content: str


@dataclass
class ActionTuple:
    action_type: str
    target_resource: str
    recipient: str


@dataclass
class ExceptionGrant:
    exception_id: str
    granted_by: str
    allowed_action_type: str
    allowed_target_resource: str
    allowed_recipient: str
    verification_rule_satisfied: str


@dataclass
class Scenario28:
    scenario_id: int
    label: str
    scenario_class: str
    description: str
    memory: MemoryInstruction
    prior_gate_status: PriorGateStatus
    action_tuple: ActionTuple
    exception_grant: Optional[ExceptionGrant]
    expected: dict[str, str]


@dataclass
class RoleProfile:
    profile_id: str
    agent_name: str
    purpose: str
    authorized_principals: set[str]
    authorized_recipients: set[str]
    authorized_action_types: set[str]
    sensitive_action_types: set[str]
    permission_ceiling: set[str]
    required_verification_rules: dict[str, str]
    prohibited_patterns: list[dict[str, Any]]
    keyword_risk_terms: list[str]
    operating_doctrine: list[str]


@dataclass
class Gate28Result:
    decision: str
    notes: str
    violated_norm_fields: list[str]
    exception_grant_id: Optional[str] = None


class Gate28(ABC):
    label: str

    @abstractmethod
    def evaluate(self, scenario: Scenario28, role_profile: RoleProfile) -> Gate28Result:
        pass


def parse_prior_gate_status(raw: dict[str, Any]) -> PriorGateStatus:
    return PriorGateStatus(
        authority_valid=raw["authority_valid"],
        freshness_valid=raw["freshness_valid"],
        verification_valid=raw["verification_valid"],
        audit_pairing_valid=raw["audit_pairing_valid"],
    )


def parse_exception_grant(raw: Optional[dict[str, Any]]) -> Optional[ExceptionGrant]:
    if raw is None:
        return None
    return ExceptionGrant(
        exception_id=raw["exception_id"],
        granted_by=raw["granted_by"],
        allowed_action_type=raw["allowed_action_type"],
        allowed_target_resource=raw["allowed_target_resource"],
        allowed_recipient=raw["allowed_recipient"],
        verification_rule_satisfied=raw["verification_rule_satisfied"],
    )


def parse_scenario(raw: dict[str, Any]) -> Scenario28:
    return Scenario28(
        scenario_id=raw["id"],
        label=raw["label"],
        scenario_class=raw["class"],
        description=raw["description"],
        memory=MemoryInstruction(
            memory_id=raw["memory"]["memory_id"],
            principal=raw["memory"]["principal"],
            content=raw["memory"]["content"],
        ),
        prior_gate_status=parse_prior_gate_status(raw["prior_gate_status"]),
        action_tuple=ActionTuple(
            action_type=raw["action_tuple"]["action_type"],
            target_resource=raw["action_tuple"]["target_resource"],
            recipient=raw["action_tuple"]["recipient"],
        ),
        exception_grant=parse_exception_grant(raw.get("exception_grant")),
        expected=raw["expected"],
    )


def parse_role_profile(raw: dict[str, Any]) -> RoleProfile:
    return RoleProfile(
        profile_id=raw["profile_id"],
        agent_name=raw["agent_name"],
        purpose=raw["purpose"],
        authorized_principals=set(raw["authorized_principals"]),
        authorized_recipients=set(raw["authorized_recipients"]),
        authorized_action_types=set(raw["authorized_action_types"]),
        sensitive_action_types=set(raw["sensitive_action_types"]),
        permission_ceiling=set(raw["permission_ceiling"]),
        required_verification_rules=raw["required_verification_rules"],
        prohibited_patterns=raw["prohibited_patterns"],
        keyword_risk_terms=raw["keyword_risk_terms"],
        operating_doctrine=raw["operating_doctrine"],
    )


def matching_exception(
    scenario: Scenario28,
    role_profile: RoleProfile,
    required_rule: Optional[str] = None,
) -> Optional[ExceptionGrant]:
    grant = scenario.exception_grant
    if grant is None:
        return None
    action = scenario.action_tuple
    if grant.granted_by not in role_profile.authorized_principals:
        return None
    if grant.allowed_action_type != action.action_type:
        return None
    if grant.allowed_target_resource != action.target_resource:
        return None
    if grant.allowed_recipient != action.recipient:
        return None
    if required_rule is not None and grant.verification_rule_satisfied != required_rule:
        return None
    return grant
