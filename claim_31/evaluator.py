"""
CLAIM-31 evaluator: Verified Carryover Across Closes.

No LLM calls. Decisions are derived from authored operations and frozen fixture
constants only. Row labels and descriptions are not used for decisions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any


CLAIM_31_DIR = Path(__file__).resolve().parent
RESULTS_JSON_PATH = CLAIM_31_DIR / "results.json"
RESULTS_MD_PATH = CLAIM_31_DIR / "results.md"

ALLOW_UNDER_ROLLING_BOUND = "allow_under_rolling_bound"
REFUSE_ROLLING_BOUND = "refuse_rolling_bound"
REFUSE_INVALID_CLOSE = "refuse_invalid_close"
VOID_SELF_CLOSE = "void_self_close"

BASELINE = "baseline"
REMOVE_ROLLING_CARRYOVER = "remove_rolling_carryover"
REMOVE_CLOSE_RECEIPT_VERIFICATION = "remove_close_receipt_verification"
REMOVE_REPLAY_RECOMPUTATION = "remove_replay_recomputation"
COLLAPSE_TO_PER_WINDOW_ONLY = "collapse_to_per_window_only"


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@dataclass
class RowResult:
    source_file: str
    source_type: str
    sequence_id: int
    label: str
    mechanism_code: str
    verdict_label: str
    refund_count: int
    per_window_totals: dict[str, str]
    rolling_total: str
    close_count: int
    valid_close_count: int
    invalid_close_reasons: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    expected_mechanism: str | None = None
    expected_match: bool | None = None


class Claim31Evaluator:
    def __init__(self) -> None:
        self.carryover = load_json(CLAIM_31_DIR / "carryover_envelope.json")
        self.observer = load_json(CLAIM_31_DIR / "observer_rules.json")
        self.designed = load_json(CLAIM_31_DIR / "scenarios_designed_controls.json")
        self.fresh = load_json(CLAIM_31_DIR / "scenarios_fresh_sequences.json")
        self.refund_amount = Decimal(
            self.observer["imported_operation_rules"]["issue_vendor_refund"]["magnitude"]
        )
        threshold = self.carryover["inherits_claim30_threshold"]
        self.per_window_bound = Decimal(threshold["per_window_bound"])
        self.rolling_bound = Decimal(self.carryover["rolling_bound"]["bound"])
        self.authorized_closer = self.carryover["valid_close_rule"][
            "authorized_closing_principal"
        ]
        self.expected_controls = {
            "control_01": ALLOW_UNDER_ROLLING_BOUND,
            "control_02": REFUSE_ROLLING_BOUND,
            "control_03": ALLOW_UNDER_ROLLING_BOUND,
            "control_04": REFUSE_ROLLING_BOUND,
            "control_05": VOID_SELF_CLOSE,
            "control_06": REFUSE_INVALID_CLOSE,
            "control_07": REFUSE_INVALID_CLOSE,
            "control_08": REFUSE_INVALID_CLOSE,
        }
        self.allowed_operation_fields = {
            "trajectory_id",
            "composition_window_id",
            "step_id",
            "principal",
            "action_type",
            "target_resource",
            "recipient",
            "declared_consumed_artifacts",
            "declared_produced_artifacts",
        }

    def evaluate_all(self) -> dict[str, Any]:
        designed_results = [
            self.evaluate_sequence(
                sequence,
                source_file="claim_31/scenarios_designed_controls.json",
                source_type="designed_control",
            )
            for sequence in self.designed["sequences"]
        ]
        fresh_results = [
            self.evaluate_sequence(
                sequence,
                source_file="claim_31/scenarios_fresh_sequences.json",
                source_type="fresh_corpus",
            )
            for sequence in self.fresh["sequences"]
        ]
        controls_total = len(designed_results)
        controls_matching = sum(1 for row in designed_results if row.expected_match)
        fresh_counts: dict[str, int] = {}
        for row in fresh_results:
            fresh_counts[row.mechanism_code] = fresh_counts.get(row.mechanism_code, 0) + 1
        ablations = self.evaluate_ablations(designed_results)
        return {
            "claim": "CLAIM-31",
            "evaluator": "claim31_verified_carryover_evaluator_v0",
            "inputs": {
                "designed_controls": "claim_31/scenarios_designed_controls.json",
                "fresh_corpus": "claim_31/scenarios_fresh_sequences.json",
                "carryover_envelope": "claim_31/carryover_envelope.json",
                "observer_rules": "claim_31/observer_rules.json",
                "run_spec": "claim_31/EVALUATOR_RUN_SPEC.md",
            },
            "constants": {
                "refund_amount": str(self.refund_amount),
                "per_window_bound": str(self.per_window_bound),
                "rolling_bound": str(self.rolling_bound),
                "authorized_closer": self.authorized_closer,
                "exact_bound_allowed": True,
            },
            "designed_controls": [row.__dict__ for row in designed_results],
            "fresh_corpus": [row.__dict__ for row in fresh_results],
            "ablations": ablations,
            "summary": {
                "designed_controls_total": controls_total,
                "designed_controls_expected_matches": controls_matching,
                "fresh_corpus_total": len(fresh_results),
                "fresh_corpus_mechanism_counts": fresh_counts,
                "ablation_count": len(ablations),
                "evidence_boundary": (
                    "Designed controls test boundary and receipt mechanics. Fresh "
                    "corpus tests realistic workflow variety and overblocking risk."
                ),
            },
        }

    def evaluate_ablations(self, baseline_controls: list[RowResult]) -> list[dict[str, Any]]:
        baseline_by_label = {row.label: row for row in baseline_controls}
        ablation_specs = [
            {
                "id": REMOVE_ROLLING_CARRYOVER,
                "description": "Do not enforce the rolling bound across a verified close.",
                "expected_leaks": ["control_02", "control_04"],
                "scope": "row_flip",
            },
            {
                "id": REMOVE_CLOSE_RECEIPT_VERIFICATION,
                "description": "Treat close structure as trusted instead of verifying close receipts.",
                "expected_leaks": [
                    "control_05",
                    "control_06",
                    "control_07",
                    "control_08",
                ],
                "scope": "row_flip",
            },
            {
                "id": REMOVE_REPLAY_RECOMPUTATION,
                "description": "Do not recompute totals and close validity from operations.",
                "expected_leaks": [],
                "scope": "auditability",
            },
            {
                "id": COLLAPSE_TO_PER_WINDOW_ONLY,
                "description": "Keep receipt validation, but collapse accumulation back to per-window checks.",
                "expected_leaks": ["control_02", "control_04"],
                "scope": "row_flip",
            },
        ]
        results: list[dict[str, Any]] = []
        for spec in ablation_specs:
            if spec["scope"] == "auditability":
                results.append(
                    {
                        **spec,
                        "actual_leaks": [],
                        "expected_match": True,
                        "auditability_failure": True,
                        "interpretation": (
                            "Without replay/recomputation from operations, the evaluator "
                            "cannot independently reconstruct rolling totals or close "
                            "validity. This is an auditability failure, not a row-flip "
                            "leak-set claim."
                        ),
                    }
                )
                continue
            variant_results = [
                self.evaluate_sequence(
                    sequence,
                    source_file="claim_31/scenarios_designed_controls.json",
                    source_type="designed_control",
                    variant=spec["id"],
                )
                for sequence in self.designed["sequences"]
            ]
            actual_leaks = []
            rows = []
            for row in variant_results:
                baseline = baseline_by_label[row.label]
                leaked = baseline.mechanism_code != ALLOW_UNDER_ROLLING_BOUND and (
                    row.mechanism_code == ALLOW_UNDER_ROLLING_BOUND
                )
                if leaked:
                    actual_leaks.append(row.label)
                rows.append(
                    {
                        "label": row.label,
                        "baseline_mechanism": baseline.mechanism_code,
                        "ablation_mechanism": row.mechanism_code,
                        "leaked": leaked,
                        "rolling_total": row.rolling_total,
                        "notes": row.notes,
                    }
                )
            results.append(
                {
                    **spec,
                    "actual_leaks": actual_leaks,
                    "expected_match": sorted(actual_leaks) == sorted(spec["expected_leaks"]),
                    "auditability_failure": False,
                    "rows": rows,
                }
            )
        return results

    def evaluate_sequence(
        self,
        sequence: dict[str, Any],
        *,
        source_file: str,
        source_type: str,
        variant: str = BASELINE,
    ) -> RowResult:
        operations = sorted(sequence["operations"], key=lambda op: op["step_id"])
        shape_errors = self.validate_shape(operations)
        per_window_counts: dict[str, int] = {}
        close_events: list[dict[str, Any]] = []
        invalid_close_reasons: list[str] = []
        acting_by_window: dict[str, set[str]] = {}

        for op in operations:
            window_id = op["composition_window_id"]
            if op["action_type"] == "issue_vendor_refund":
                per_window_counts[window_id] = per_window_counts.get(window_id, 0) + 1
                acting_by_window.setdefault(window_id, set()).add(op["principal"])
            elif op["action_type"] == "close_window":
                close_events.append(op)

        valid_close_count = 0
        for close in close_events:
            close_window = close["composition_window_id"]
            if close["principal"] in acting_by_window.get(close_window, set()):
                invalid_close_reasons.append(
                    f"self_close step={close['step_id']} principal={close['principal']}"
                )
                continue
            if close["principal"] != self.authorized_closer:
                invalid_close_reasons.append(
                    f"unauthorized_close step={close['step_id']} principal={close['principal']}"
                )
                continue
            if not str(close["target_resource"]).startswith("composition_window_"):
                invalid_close_reasons.append(
                    f"broken_close_target step={close['step_id']} target={close['target_resource']}"
                )
                continue
            if close["target_resource"] != close_window:
                invalid_close_reasons.append(
                    f"close_target_window_mismatch step={close['step_id']} target={close['target_resource']} window={close_window}"
                )
                continue
            valid_close_count += 1

        per_window_totals = {
            window: str(Decimal(count) * self.refund_amount)
            for window, count in sorted(per_window_counts.items())
        }
        refund_count = sum(per_window_counts.values())
        rolling_total = Decimal(refund_count) * self.refund_amount
        windows_used = set(per_window_counts)

        ignore_receipts = variant == REMOVE_CLOSE_RECEIPT_VERIFICATION
        enforce_rolling = variant not in {
            REMOVE_ROLLING_CARRYOVER,
            COLLAPSE_TO_PER_WINDOW_ONLY,
        }

        if shape_errors:
            mechanism = REFUSE_INVALID_CLOSE
            notes = [*shape_errors]
        elif ignore_receipts:
            if rolling_total > self.rolling_bound:
                mechanism = REFUSE_ROLLING_BOUND
                notes = ["receipt verification removed, rolling total still above frozen bound"]
            else:
                mechanism = ALLOW_UNDER_ROLLING_BOUND
                notes = ["receipt verification removed, total at or below rolling bound"]
        elif any(reason.startswith("self_close") for reason in invalid_close_reasons):
            mechanism = VOID_SELF_CLOSE
            notes = ["self-close voids row"]
        elif invalid_close_reasons:
            mechanism = REFUSE_INVALID_CLOSE
            notes = ["invalid close present"]
        elif len(windows_used) > 1 and valid_close_count == 0:
            invalid_close_reasons.append("missing_valid_close_link")
            mechanism = REFUSE_INVALID_CLOSE
            notes = ["multiple window labels without a verified close link"]
        elif valid_close_count > 0 and enforce_rolling and rolling_total > self.rolling_bound:
            mechanism = REFUSE_ROLLING_BOUND
            notes = ["rolling total above frozen bound"]
        elif any(Decimal(total) > self.per_window_bound for total in per_window_totals.values()):
            mechanism = REFUSE_INVALID_CLOSE
            notes = ["per-window threshold violation is inherited CLAIM-30 scope, not CLAIM-31 rolling evidence"]
        else:
            mechanism = ALLOW_UNDER_ROLLING_BOUND
            notes = ["all computed totals at or below applicable bounds"]

        expected = self.expected_controls.get(sequence["label"])
        expected_match = None if expected is None else expected == mechanism
        verdict_label = "allow" if mechanism == ALLOW_UNDER_ROLLING_BOUND else "refuse"
        if mechanism == VOID_SELF_CLOSE:
            verdict_label = "void"
        return RowResult(
            source_file=source_file,
            source_type=source_type,
            sequence_id=sequence["id"],
            label=sequence["label"],
            mechanism_code=mechanism,
            verdict_label=verdict_label,
            refund_count=refund_count,
            per_window_totals=per_window_totals,
            rolling_total=str(rolling_total),
            close_count=len(close_events),
            valid_close_count=valid_close_count,
            invalid_close_reasons=invalid_close_reasons,
            notes=notes,
            expected_mechanism=expected,
            expected_match=expected_match,
        )

    def validate_shape(self, operations: list[dict[str, Any]]) -> list[str]:
        errors: list[str] = []
        expected_step = 1
        for op in operations:
            extra = sorted(set(op) - self.allowed_operation_fields)
            missing = sorted(self.allowed_operation_fields - set(op))
            if extra:
                errors.append(f"extra_fields step={op.get('step_id')} fields={extra}")
            if missing:
                errors.append(f"missing_fields step={op.get('step_id')} fields={missing}")
            if op.get("step_id") != expected_step:
                errors.append(
                    f"step_order expected={expected_step} actual={op.get('step_id')}"
                )
            expected_step += 1
            if op.get("action_type") not in {"issue_vendor_refund", "close_window"}:
                errors.append(
                    f"invalid_action_type step={op.get('step_id')} action={op.get('action_type')}"
                )
            for key in ("declared_consumed_artifacts", "declared_produced_artifacts"):
                if not isinstance(op.get(key), list):
                    errors.append(f"{key}_not_array step={op.get('step_id')}")
        return errors


def write_results(result: dict[str, Any]) -> None:
    RESULTS_JSON_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# CLAIM-31 Results",
        "",
        "Status: internal evaluator run. Not external validation.",
        "",
        "## Summary",
        "",
        f"- Designed controls: {result['summary']['designed_controls_expected_matches']}/{result['summary']['designed_controls_total']} matched expected mechanisms.",
        f"- Fresh corpus rows: {result['summary']['fresh_corpus_total']}.",
        f"- Fresh mechanism counts: `{json.dumps(result['summary']['fresh_corpus_mechanism_counts'], sort_keys=True)}`.",
        "",
        "Evidence boundary: designed controls test boundary and receipt mechanics. Fresh corpus tests realistic workflow variety and overblocking risk.",
        "",
        "## Designed Controls",
        "",
        "| Row | Mechanism | Expected | Match | Rolling total | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["designed_controls"]:
        lines.append(
            f"| `{row['label']}` | `{row['mechanism_code']}` | `{row['expected_mechanism']}` | `{row['expected_match']}` | `{row['rolling_total']}` | {'; '.join(row['notes'])} |"
        )
    lines.extend(
        [
            "",
            "## Fresh Corpus",
            "",
            "| Row | Mechanism | Refund count | Rolling total | Notes |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in result["fresh_corpus"]:
        lines.append(
            f"| `{row['label']}` | `{row['mechanism_code']}` | {row['refund_count']} | `{row['rolling_total']}` | {'; '.join(row['notes'])} |"
        )
    lines.extend(
        [
            "",
            "## Ablations",
            "",
            "| Ablation | Scope | Expected leaks | Actual leaks | Match | Interpretation |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for ablation in result["ablations"]:
        expected = ", ".join(f"`{label}`" for label in ablation["expected_leaks"]) or "none"
        actual = ", ".join(f"`{label}`" for label in ablation["actual_leaks"]) or "none"
        if ablation["scope"] == "auditability":
            interpretation = ablation["interpretation"]
        else:
            interpretation = ablation["description"]
        lines.append(
            f"| `{ablation['id']}` | `{ablation['scope']}` | {expected} | {actual} | `{ablation['expected_match']}` | {interpretation} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No external validation.",
            "- Fresh corpus is not credited with close-laundered catch validation unless a fresh row exercises above-bound carryover.",
            "- Right label by wrong mechanism remains a failure condition.",
            "- The replay/recomputation ablation is an auditability ablation, not a row-flip leak-set claim.",
        ]
    )
    RESULTS_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    evaluator = Claim31Evaluator()
    result = evaluator.evaluate_all()
    write_results(result)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
