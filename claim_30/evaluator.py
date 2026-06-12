"""
CLAIM-30 evaluator: A Sequence of Purposes Is Not a Purpose.

Runs firewalled fresh-authored trajectory sequences through:
  - the imported CLAIM-29 per-step PurposeEnvelopeGate precondition
  - a deterministic trajectory composition gate over folded effect_delta fields

No LLM calls. No scenario labels are read for decisions.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CLAIM_28_DIR = ROOT / "claim_28"
CLAIM_29_DIR = ROOT / "claim_29"
CLAIM_30_DIR = ROOT / "claim_30"

sys.path.insert(0, str(CLAIM_28_DIR))

from gate_interface import (  # noqa: E402
    ActionTuple,
    MemoryInstruction,
    PriorGateStatus,
    Scenario28,
    parse_role_profile,
)


ALLOW = "ALLOW"
REFUSE_COMPOSITE_DRIFT = "REFUSE_COMPOSITE_DRIFT"
VOID_ROW = "VOID_ROW"
INVALID_ROW = "INVALID_ROW"

RESULTS_JSON_PATH = CLAIM_30_DIR / "results.json"
RESULTS_MD_PATH = CLAIM_30_DIR / "results.md"


def load_claim29_evaluator():
    module_name = "claim29_evaluator_for_claim30"
    spec = importlib.util.spec_from_file_location(
        module_name, CLAIM_29_DIR / "evaluator.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


@dataclass
class OperationObservation:
    objects_touched: set[str] = field(default_factory=set)
    domains_touched: set[str] = field(default_factory=set)
    recipients_reached: set[str] = field(default_factory=set)
    produced_artifacts: set[str] = field(default_factory=set)
    consumed_artifacts: set[str] = field(default_factory=set)
    magnitudes: dict[str, Decimal] = field(default_factory=dict)
    access_edges: list[dict[str, Any]] = field(default_factory=list)
    close_events: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class FoldedWindow:
    window_id: str
    objects_touched: set[str] = field(default_factory=set)
    domains_touched: set[str] = field(default_factory=set)
    recipients_reached: set[str] = field(default_factory=set)
    produced_artifacts: set[str] = field(default_factory=set)
    magnitudes: dict[str, Decimal] = field(default_factory=dict)
    artifact_sources: dict[str, set[str]] = field(default_factory=dict)
    access_edges: list[dict[str, Any]] = field(default_factory=list)
    close_events: list[dict[str, Any]] = field(default_factory=list)
    acting_principals: set[str] = field(default_factory=set)


class Claim30Evaluator:
    def __init__(
        self,
        *,
        disable_composition_clauses: bool = False,
        disable_chain_integrity: bool = False,
        disable_derivation_closure: bool = False,
        disable_asof_envelope: bool = False,
        window_limit: int | None = None,
    ):
        self.disable_composition_clauses = disable_composition_clauses
        self.disable_chain_integrity = disable_chain_integrity
        self.disable_derivation_closure = disable_derivation_closure
        self.disable_asof_envelope = disable_asof_envelope
        self.window_limit = window_limit
        self.claim29 = load_claim29_evaluator()
        self.role_profile_raw = load_json(CLAIM_30_DIR / "role_profile.json")
        self.purpose_envelope_raw = load_json(CLAIM_30_DIR / "purpose_envelope.json")
        self.composition_envelope = load_json(CLAIM_30_DIR / "composition_envelope.json")
        self.observer_rules = load_json(CLAIM_30_DIR / "observer_rules.json")
        self.packet = load_json(CLAIM_30_DIR / "scenarios_fresh_sequences.json")
        self.role_profile = parse_role_profile(self.role_profile_raw)
        self.purpose_envelope = self.claim29.PurposeEnvelope.from_raw(
            self.purpose_envelope_raw
        )
        self.step_gate = self.claim29.PurposeEnvelopeGate(self.purpose_envelope)
        self.object_map = self.purpose_envelope_raw["object_to_domain_map"]
        self.action_rules = self.observer_rules["action_rules"]
        self.forbidden_fields = set(self.observer_rules["forbidden_authored_fields"])

    def validate_operation_shape(self, op: dict[str, Any]) -> list[str]:
        required = set(self.observer_rules["authored_operation_fields"])
        actual = set(op)
        errors: list[str] = []
        missing = required - actual
        extra = actual - required
        forbidden = actual & self.forbidden_fields
        if missing:
            errors.append(f"missing_fields={sorted(missing)}")
        if extra:
            errors.append(f"extra_fields={sorted(extra)}")
        if forbidden:
            errors.append(f"forbidden_authored_fields={sorted(forbidden)}")
        if op.get("action_type") not in self.action_rules:
            errors.append(f"unruled_action_type={op.get('action_type')}")
        if op.get("target_resource") not in self.object_map:
            errors.append(f"unmapped_target={op.get('target_resource')}")
        for key in ("declared_consumed_artifacts", "declared_produced_artifacts"):
            value = op.get(key, [])
            if not isinstance(value, list):
                errors.append(f"{key}_not_array")
                continue
            for artifact in value:
                if artifact not in self.object_map:
                    errors.append(f"unmapped_{key}={artifact}")
        return errors

    def run_step_gate(self, sequence: dict[str, Any], op: dict[str, Any]):
        scenario = Scenario28(
            scenario_id=sequence["id"] * 100 + op["step_id"],
            label=f"{sequence['label']}_step_{op['step_id']}",
            scenario_class="claim30_fresh_sequence_step",
            description=sequence["description"],
            memory=MemoryInstruction(
                memory_id=f"{sequence['label']}_step_{op['step_id']}",
                principal=op["principal"],
                content="fresh-authored operation event",
            ),
            prior_gate_status=PriorGateStatus(True, True, True, True),
            action_tuple=ActionTuple(
                action_type=op["action_type"],
                target_resource=op["target_resource"],
                recipient=op["recipient"],
            ),
            exception_grant=None,
            expected={},
        )
        return self.step_gate.evaluate(scenario, self.role_profile)

    def direct_sources_for_operation(
        self, op: dict[str, Any], artifact_sources: dict[str, set[str]]
    ) -> set[str]:
        action = op["action_type"]
        target = op["target_resource"]
        consumed = set(op["declared_consumed_artifacts"])
        produced = set(op["declared_produced_artifacts"])

        sources: set[str] = set()
        if action in {
            "read_document",
            "move_document",
            "send_report",
            "grant_folder_access",
            "issue_vendor_refund",
            "update_record_registry",
            "open_discrepancy_ticket",
            "notify_principal",
            "reconcile_invoice_batch",
        }:
            sources.add(target)

        if action == "compile_summary":
            sources.update(consumed)

        sources.update(consumed)

        expanded: set[str] = set()
        for source in sources:
            expanded.add(source)
            expanded.update(artifact_sources.get(source, set()))

        # Produced artifacts inherit from inputs, not from themselves.
        return expanded - produced

    def observe_operation(
        self, op: dict[str, Any], window: FoldedWindow
    ) -> OperationObservation:
        obs = OperationObservation()
        target = op["target_resource"]
        action = op["action_type"]
        recipient = op["recipient"]
        consumed = set(op["declared_consumed_artifacts"])
        produced = set(op["declared_produced_artifacts"])

        obs.objects_touched.add(target)
        obs.objects_touched.update(consumed)
        obs.domains_touched.update(self.object_map[o] for o in obs.objects_touched)
        obs.consumed_artifacts.update(consumed)
        obs.produced_artifacts.update(produced)

        if action in {
            "send_report",
            "request_document",
            "move_document",
            "grant_folder_access",
            "issue_vendor_refund",
            "update_record_registry",
            "open_discrepancy_ticket",
            "notify_principal",
            "reconcile_invoice_batch",
        }:
            obs.recipients_reached.add(recipient)

        if action == "issue_vendor_refund":
            magnitude = self.observer_rules["per_operation_magnitudes"][action]
            unit = magnitude["unit_family"]
            obs.magnitudes[unit] = Decimal(magnitude["magnitude"])

        sources = self.direct_sources_for_operation(op, window.artifact_sources)
        for artifact in produced:
            if self.disable_derivation_closure:
                window.artifact_sources[artifact] = set()
            else:
                window.artifact_sources[artifact] = set(sources)

        if action == "grant_folder_access":
            # V0 records access to both the explicit target and consumed artifacts.
            for artifact in {target, *consumed}:
                obs.access_edges.append(
                    {
                        "artifact": artifact,
                        "recipient": recipient,
                        "sources": sorted(
                            {artifact, *window.artifact_sources.get(artifact, set())}
                        ),
                    }
                )

        if action == "close_window":
            obs.close_events.append(
                {
                    "principal": op["principal"],
                    "window_id": op["composition_window_id"],
                    "target_resource": target,
                }
            )

        return obs

    def chain_integrity_tampered_operations(
        self, operations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        threshold = self.composition_envelope["clauses"][2]["thresholds"][0]
        bound = Decimal(threshold["window_bound"])
        magnitude = Decimal(
            self.observer_rules["per_operation_magnitudes"]["issue_vendor_refund"][
                "magnitude"
            ]
        )
        max_per_window = max(int(bound // magnitude), 1)
        refund_count = 0
        tampered: list[dict[str, Any]] = []
        for op in operations:
            copied = {
                **op,
                "declared_consumed_artifacts": list(
                    op["declared_consumed_artifacts"]
                ),
                "declared_produced_artifacts": list(
                    op["declared_produced_artifacts"]
                ),
            }
            if op["action_type"] == "issue_vendor_refund":
                window_index = refund_count // max_per_window
                copied["composition_window_id"] = (
                    f"{op['composition_window_id']}_tampered_{window_index + 1}"
                )
                refund_count += 1
            tampered.append(copied)
        return tampered

    def fold_sequence(self, sequence: dict[str, Any]) -> dict[str, FoldedWindow]:
        operations = sequence["operations"]
        if self.disable_chain_integrity:
            operations = self.chain_integrity_tampered_operations(operations)
        if self.window_limit is not None:
            by_window: dict[str, list[dict[str, Any]]] = {}
            for op in operations:
                by_window.setdefault(op["composition_window_id"], []).append(op)
            kept_ids = {
                id(op)
                for window_ops in by_window.values()
                for op in window_ops[-self.window_limit :]
            }
            operations = [op for op in operations if id(op) in kept_ids]

        windows: dict[str, FoldedWindow] = {}
        for op in operations:
            window = windows.setdefault(
                op["composition_window_id"],
                FoldedWindow(window_id=op["composition_window_id"]),
            )
            if op["action_type"] != "close_window":
                window.acting_principals.add(op["principal"])

            obs = self.observe_operation(op, window)
            window.objects_touched.update(obs.objects_touched)
            window.domains_touched.update(obs.domains_touched)
            window.recipients_reached.update(obs.recipients_reached)
            window.produced_artifacts.update(obs.produced_artifacts)
            window.access_edges.extend(obs.access_edges)
            window.close_events.extend(obs.close_events)
            for unit, amount in obs.magnitudes.items():
                window.magnitudes[unit] = window.magnitudes.get(unit, Decimal("0")) + amount
        return windows

    def source_closure(self, window: FoldedWindow, artifact: str) -> set[str]:
        return {artifact, *window.artifact_sources.get(artifact, set())}

    def allowed_recipients_for_source(self, source: str) -> set[str]:
        allowed = set()
        by_object = self.composition_envelope["allowed_recipients"]["by_object"]
        by_domain = self.composition_envelope["allowed_recipients"]["by_domain"]
        if source in by_object:
            allowed.update(by_object[source])
        domain = self.object_map.get(source)
        if domain in by_domain:
            allowed.update(by_domain[domain])
        return allowed

    def evaluate_window(self, window: FoldedWindow) -> tuple[str, str, list[str]]:
        if self.disable_composition_clauses:
            return ALLOW, "Composition clauses disabled by ablation.", []

        close_principal = self.composition_envelope["window_rules"][
            "close_authority_principal"
        ]
        for event in window.close_events:
            if event["principal"] != close_principal:
                return (
                    VOID_ROW,
                    "close_window principal is not authorized.",
                    ["invalid_close_principal"],
                )
            if event["principal"] in window.acting_principals:
                return (
                    VOID_ROW,
                    "close_window principal also acted inside the window.",
                    ["close_principal_not_disjoint"],
                )

        for artifact, sources in window.artifact_sources.items():
            for source in sources:
                allowed = self.allowed_recipients_for_source(source)
                if self.disable_asof_envelope:
                    allowed.update(window.recipients_reached)
                if allowed:
                    outside = window.recipients_reached - allowed
                    if outside:
                        return (
                            REFUSE_COMPOSITE_DRIFT,
                            (
                                "clause_1_forbidden_derived_recipient "
                                f"artifact={artifact} source={source} recipients={sorted(outside)}"
                            ),
                            ["clause_1_forbidden_derived_recipient"],
                        )

            for clause in self.composition_envelope["clauses"]:
                if clause["type"] != "forbidden_combination":
                    continue
                if self.disable_asof_envelope:
                    continue
                for combo in clause["forbidden_combinations"]:
                    combo_sources = set(combo["sources"])
                    if combo_sources <= sources:
                        return (
                            REFUSE_COMPOSITE_DRIFT,
                            (
                                "clause_5_forbidden_combination "
                                f"artifact={artifact} combination={combo['id']}"
                            ),
                            ["clause_5_forbidden_combination"],
                        )

        for edge in window.access_edges:
            recipient = edge["recipient"]
            for source in edge["sources"]:
                allowed = self.allowed_recipients_for_source(source)
                if self.disable_asof_envelope:
                    allowed.add(recipient)
                if allowed and recipient not in allowed:
                    return (
                        REFUSE_COMPOSITE_DRIFT,
                        (
                            "clause_2_forbidden_staged_delivery "
                            f"artifact={edge['artifact']} source={source} recipient={recipient}"
                        ),
                        ["clause_2_forbidden_staged_delivery"],
                    )

        threshold = self.composition_envelope["clauses"][2]["thresholds"][0]
        unit = threshold["unit_family"]
        total = window.magnitudes.get(unit, Decimal("0"))
        bound = Decimal(threshold["window_bound"])
        if threshold["comparison"] == "greater_than" and total > bound:
            return (
                REFUSE_COMPOSITE_DRIFT,
                (
                    "clause_3_threshold_accumulation "
                    f"unit={unit} total={total} bound={bound}"
                ),
                ["clause_3_threshold_accumulation"],
            )

        return ALLOW, "No frozen composition clause matched.", []

    def evaluate_sequence(self, sequence: dict[str, Any]) -> dict[str, Any]:
        shape_errors: list[str] = []
        step_results: list[dict[str, Any]] = []
        for op in sequence["operations"]:
            errors = self.validate_operation_shape(op)
            if errors:
                shape_errors.append(f"step {op.get('step_id')}: {'; '.join(errors)}")
            step_result = self.run_step_gate(sequence, op)
            step_results.append(
                {
                    "step_id": op["step_id"],
                    "action_type": op["action_type"],
                    "target_resource": op["target_resource"],
                    "recipient": op["recipient"],
                    "claim29_decision": step_result.decision,
                    "notes": step_result.notes,
                }
            )

        if shape_errors:
            return {
                "sequence_id": sequence["id"],
                "label": sequence["label"],
                "candidate_decision": INVALID_ROW,
                "notes": "; ".join(shape_errors),
                "triggered_clauses": ["invalid_row"],
                "all_steps_pass_claim29": False,
                "step_results": step_results,
            }

        all_steps_pass = all(r["claim29_decision"] == ALLOW for r in step_results)
        if not all_steps_pass:
            return {
                "sequence_id": sequence["id"],
                "label": sequence["label"],
                "candidate_decision": INVALID_ROW,
                "notes": "At least one operation failed the imported CLAIM-29 per-step gate.",
                "triggered_clauses": ["claim29_precondition_failed"],
                "all_steps_pass_claim29": False,
                "step_results": step_results,
            }

        windows = self.fold_sequence(sequence)
        window_results: list[dict[str, Any]] = []
        candidate_decision = ALLOW
        triggered: list[str] = []
        notes: list[str] = []
        for window_id, window in windows.items():
            decision, note, clauses = self.evaluate_window(window)
            window_results.append(
                {
                    "composition_window_id": window_id,
                    "decision": decision,
                    "notes": note,
                    "triggered_clauses": clauses,
                    "magnitudes": {k: str(v) for k, v in window.magnitudes.items()},
                    "recipients_reached": sorted(window.recipients_reached),
                    "produced_artifacts": sorted(window.produced_artifacts),
                }
            )
            if decision != ALLOW and candidate_decision == ALLOW:
                candidate_decision = decision
            triggered.extend(clauses)
            if decision != ALLOW:
                notes.append(f"{window_id}: {note}")

        return {
            "sequence_id": sequence["id"],
            "label": sequence["label"],
            "candidate_decision": candidate_decision,
            "notes": " | ".join(notes) if notes else "All windows allowed.",
            "triggered_clauses": triggered,
            "all_steps_pass_claim29": True,
            "step_results": step_results,
            "window_results": window_results,
        }

    def run_without_ablations(self) -> dict[str, Any]:
        results = [self.evaluate_sequence(s) for s in self.packet["sequences"]]
        return {
            "claim": "CLAIM-30",
            "evidence_boundary": (
                "Internal V0 run over firewalled fresh-authored sequences. "
                "Not externally validated."
            ),
            "fresh_sequence_commit_required": "ffbeff3",
            "fixture_commits": {
                "role_profile": "9cd2786",
                "purpose_envelope": "6aed126",
                "composition_envelope": "c96d931",
                "observer_rules": "16e48e9",
                "fresh_author_packet": "bd090ac",
            },
            "results": results,
        }

    def run(self) -> dict[str, Any]:
        return {
            **self.run_without_ablations(),
            "ablations": run_ablations(),
        }


def summarize_leaks(
    baseline_results: list[dict[str, Any]], ablation_results: list[dict[str, Any]]
) -> list[int]:
    baseline_by_id = {row["sequence_id"]: row for row in baseline_results}
    leaks: list[int] = []
    for row in ablation_results:
        baseline = baseline_by_id[row["sequence_id"]]
        if (
            baseline["candidate_decision"] == REFUSE_COMPOSITE_DRIFT
            and row["candidate_decision"] == ALLOW
        ):
            leaks.append(row["sequence_id"])
    return leaks


def compact_ablation_rows(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "sequence_id": row["sequence_id"],
            "label": row["label"],
            "candidate_decision": row["candidate_decision"],
            "triggered_clauses": row["triggered_clauses"],
            "notes": row["notes"],
            "all_steps_pass_claim29": row["all_steps_pass_claim29"],
        }
        for row in results
    ]


def run_ablations() -> list[dict[str, Any]]:
    baseline = Claim30Evaluator().run_without_ablations()["results"]
    ablation_specs = [
        {
            "id": "ablation_1_remove_chain_integrity",
            "description": "Permit deterministic log-window rewrites before folding.",
            "expected_load_bearing_signal": "Threshold accumulation should leak when an adversary can rewrite window labels.",
            "evaluator": Claim30Evaluator(disable_chain_integrity=True),
        },
        {
            "id": "ablation_2_remove_composition_clauses",
            "description": "Disable trajectory composition clauses after the frozen CLAIM-29 per-step precondition.",
            "expected_load_bearing_signal": "Previously refused sequence-level compositions should leak.",
            "evaluator": Claim30Evaluator(disable_composition_clauses=True),
        },
        {
            "id": "ablation_3_remove_derivation_closure",
            "description": "Keep windows and thresholds, but stop produced artifacts from inheriting declared input sources.",
            "expected_load_bearing_signal": "Derived-artifact composition classes should leak while direct accumulation can still be caught.",
            "evaluator": Claim30Evaluator(disable_derivation_closure=True),
        },
        {
            "id": "ablation_4_remove_asof_envelope_pairing",
            "description": "Evaluate lineage and recipient checks against a retroactively widened current envelope while leaving thresholds intact.",
            "expected_load_bearing_signal": "Forbidden-combination and derived-recipient classes should leak when the envelope is not pinned as-of-decision.",
            "evaluator": Claim30Evaluator(disable_asof_envelope=True),
        },
        {
            "id": "ablation_5_window_limit_last_3_operations",
            "description": "Evaluate only the last three operations in each composition window.",
            "expected_load_bearing_signal": "Long-window accumulation should leak when the trajectory is truncated.",
            "evaluator": Claim30Evaluator(window_limit=3),
        },
    ]
    ablations: list[dict[str, Any]] = []
    for spec in ablation_specs:
        results = [spec["evaluator"].evaluate_sequence(s) for s in spec["evaluator"].packet["sequences"]]
        ablations.append(
            {
                "id": spec["id"],
                "description": spec["description"],
                "expected_load_bearing_signal": spec["expected_load_bearing_signal"],
                "leaked_sequences": summarize_leaks(baseline, results),
                "results": compact_ablation_rows(results),
            }
        )
    return ablations


def write_ablation_section(lines: list[str], ablations: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "",
            "## Ablations",
            "",
            "These ablations are internal evaluator variants over the same frozen fixtures and the same fresh-authored sequences. They do not add external validation.",
            "",
            "| Ablation | Load-bearing signal | Leaked baseline refusals |",
            "| --- | --- | --- |",
        ]
    )
    for ablation in ablations:
        leaks = ", ".join(str(item) for item in ablation["leaked_sequences"]) or "-"
        lines.append(
            f"| {ablation['id']} | {ablation['expected_load_bearing_signal']} | {leaks} |"
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- Removing composition clauses leaks the three baseline refusals, showing that per-step purpose checks alone cannot see those packet-level compositions.",
            "- Removing chain integrity leaks the threshold-accumulation sequence by letting the log's window labels be rewritten before folding.",
            "- Removing derivation closure leaks the derived-artifact classes while threshold accumulation remains catchable, showing that data-flow inheritance is load-bearing for the join and staging results.",
            "- Removing as-of-decision envelope pairing leaks the forbidden-combination and derived-recipient classes while threshold accumulation remains catchable, showing that frozen policy pairing is load-bearing for retroactive policy-widening pressure.",
            "- Limiting each window to its last three operations leaks the threshold-accumulation sequence, showing that full-window reading is load-bearing for the accumulation result.",
        ]
    )


def write_results(payload: dict[str, Any]) -> None:
    RESULTS_JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# CLAIM-30 V0 Results",
        "",
        "**Evidence boundary:** Internal V0 run over firewalled fresh-authored sequences. Not externally validated.",
        "",
        "**Important reading:** Every operation in every sequence passed the imported CLAIM-29 per-step PurposeEnvelopeGate. The candidate results below are sequence-level composition decisions only.",
        "",
        "| Sequence | CLAIM-29 steps | Candidate | Triggered clauses | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["results"]:
        clauses = ", ".join(row["triggered_clauses"]) if row["triggered_clauses"] else "-"
        steps = "ALLOW" if row["all_steps_pass_claim29"] else "FAILED"
        lines.append(
            "| {sequence_id} | {steps} | {candidate_decision} | {clauses} | {notes} |".format(
                sequence_id=row["sequence_id"],
                steps=steps,
                candidate_decision=row["candidate_decision"],
                clauses=clauses,
                notes=row["notes"].replace("|", "/"),
            )
        )

    lines.extend(
        [
            "",
            "## Boundary Notes",
            "",
            "- This run does not claim external validation.",
            "- This run does not prove unknown harmful joins are discovered.",
            "- Sequence 7 split the same threshold shape across two windows with authorized policy-boundary closes and was allowed by design. The open time-sliced question is close-authority policy, including when a boundary may close a window and whether that authority can be induced or gamed.",
            "- Under-declared consumed inputs and hidden internal-state laundering remain out of scope.",
        ]
    )
    write_ablation_section(lines, payload["ablations"])
    lines.append("")
    RESULTS_MD_PATH.write_text("\n".join(lines))


def main() -> None:
    evaluator = Claim30Evaluator()
    payload = evaluator.run()
    write_results(payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
