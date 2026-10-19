"""Unit tests for the action-class logic in run_retrieval_eval.py.

These pin the documented semantics in SCORING_RUBRIC.md so a refactor cannot
silently change how a retrieved memory maps to an action or an error class.
"""

from __future__ import annotations

import unittest

from _helpers import load_module

retrieval = load_module("run_retrieval_eval.py", "run_retrieval_eval")


def scenario(expected: str, correct: str = "m_correct") -> dict:
    return {"id": "s", "expected_action": expected, "correct_memory_id": correct}


class TokenizeTests(unittest.TestCase):
    def test_lowercases_and_splits_on_non_alnum(self) -> None:
        self.assertEqual(retrieval.tokenize("Don't BLOCK v0.3-eval!"), ["don", "t", "block", "v0", "3", "eval"])


class LayeredActionTests(unittest.TestCase):
    def test_superseded_is_archive_only_even_if_hint_blocks(self) -> None:
        action, _ = retrieval.layered_action({"id": "m", "status": "superseded", "allowed_action_hint": "block"})
        self.assertEqual(action, "archive_only")

    def test_active_correction_defaults_to_block(self) -> None:
        action, _ = retrieval.layered_action({"id": "m", "memory_type": "correction", "status": "active"})
        self.assertEqual(action, "block")

    def test_active_correction_keeps_warn_hint(self) -> None:
        memory = {"id": "m", "memory_type": "correction", "status": "active", "allowed_action_hint": "warn"}
        self.assertEqual(retrieval.layered_action(memory)[0], "warn")

    def test_verification_required_beats_answer_hint(self) -> None:
        memory = {"id": "m", "verification_required": True, "allowed_action_hint": "answer"}
        self.assertEqual(retrieval.layered_action(memory)[0], "verify_first")

    def test_contested_warns(self) -> None:
        self.assertEqual(retrieval.layered_action({"id": "m", "epistemic_status": "contested"})[0], "warn")

    def test_repeated_contradictions_require_verification(self) -> None:
        self.assertEqual(retrieval.layered_action({"id": "m", "contradiction_count": 2})[0], "verify_first")
        self.assertEqual(retrieval.layered_action({"id": "m", "contradiction_count": 1})[0], "answer")


class ScoreDecisionTests(unittest.TestCase):
    def decide(self, expected: str, retrieved: str, action: str):
        return retrieval.score_decision("t", scenario(expected), retrieved, 1.0, action, "r")

    def test_correct_end_to_end(self) -> None:
        d = self.decide("block", "m_correct", "block")
        self.assertTrue(d.end_to_end_correct)
        self.assertFalse(d.downgrade_miss or d.false_certainty_error or d.overblocking_error)

    def test_downgrade_miss_is_wrong_memory_with_weaker_protective_action(self) -> None:
        # The repo's core hard case: right neighborhood, wrong severity (block -> warn).
        d = self.decide("block", "m_other", "warn")
        self.assertTrue(d.downgrade_miss)
        self.assertFalse(d.false_certainty_error)

    def test_false_certainty_when_risky_query_gets_permissive_action(self) -> None:
        d = self.decide("verify_first", "m_other", "answer")
        self.assertTrue(d.false_certainty_error)
        self.assertFalse(d.downgrade_miss)

    def test_benign_miss_when_wrong_memory_still_gives_right_action(self) -> None:
        d = self.decide("warn", "m_other", "warn")
        self.assertTrue(d.benign_retrieval_miss)
        self.assertTrue(d.action_correct)
        self.assertFalse(d.end_to_end_correct)

    def test_overblocking(self) -> None:
        self.assertTrue(self.decide("answer", "m_other", "block").overblocking_error)

    def test_summary_counts(self) -> None:
        rows = [self.decide("block", "m_correct", "block"), self.decide("block", "m_other", "warn")]
        summary = retrieval.summarize(rows)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["end_to_end_correct"], 1)
        self.assertEqual(summary["downgrade_misses"], 1)


if __name__ == "__main__":
    unittest.main()
