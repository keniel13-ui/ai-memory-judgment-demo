"""Recorded result artifacts must still reproduce byte-for-byte from current code.

Each evaluator below is run inside a throwaway copy of the repository, so the
committed artifacts are never overwritten. The test then compares every output
the evaluator wrote with the committed file.

Only evaluators whose committed outputs reproduce exactly today are listed.
Several older artifacts do NOT reproduce from current defaults (scenario sets
grew, attribution fields were added later, or two scripts share an output
path); they are documented in docs/DEVELOPMENT.md and deliberately not checked
here, because "fixing" them would mean rewriting recorded evidence.

Ollama is forced unreachable so embedding strategies are skipped, which is the
condition the committed lexical results were produced under.
"""

from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _helpers import ROOT

# (working directory relative to repo root, script, args, outputs relative to repo root)
CASES = [
    (".", "run_retrieval_eval.py", [], ["results/retrieval_eval_results.md", "results/retrieval_eval_results.json"]),
    (".", "run_topk_inspection.py", [], ["results/topk_inspection_results.md", "results/topk_inspection_results.json"]),
    (
        ".",
        "run_fresh_governs_eval.py",
        [],
        ["results/fresh_governs_eval_results.md", "results/fresh_governs_eval_results.json"],
    ),
    (
        ".",
        "run_claim15_score_decomposition.py",
        [],
        ["results/claim15_score_decomposition.md", "results/claim15_score_decomposition.json"],
    ),
    (
        ".",
        "run_action_type_diagnostic.py",
        [],
        ["results/action_type_diagnostic_results.md", "results/action_type_diagnostic_results.json"],
    ),
    (
        ".",
        "run_split_architecture_eval.py",
        [],
        ["results/split_architecture_eval_results.md", "results/split_architecture_eval_results.json"],
    ),
    (".", "run_claim17_resource_sensitivity_eval.py", [], ["results/claim17_resource_sensitivity_v0_1_results.md"]),
    (
        ".",
        "run_claim21_external_cert_policy_eval.py",
        [],
        [
            "results/claim21_external_cert_policy_packet_v0_1_results.md",
            "results/claim21_external_cert_policy_packet_v0_1_results.json",
        ],
    ),
    (
        ".",
        "run_claim23_tool_call_authorization_eval.py",
        [],
        [
            "results/claim23_tool_call_authorization_v0_1_results.md",
            "results/claim23_tool_call_authorization_v0_1_results.json",
        ],
    ),
    ("claim_28", "evaluator.py", [], ["claim_28/results.md", "claim_28/results.json"]),
    ("claim_29", "evaluator.py", [], ["claim_29/results.md", "claim_29/results.json"]),
    ("claim_30", "evaluator.py", [], ["claim_30/results.md", "claim_30/results.json"]),
    ("claim_31", "evaluator.py", [], ["claim_31/results.md", "claim_31/results.json"]),
]


def tracked_files() -> list[str]:
    proc = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=False)
    if proc.returncode != 0:
        return []
    return [name for name in proc.stdout.decode("utf-8").split("\0") if name]


def copy_repo(dest: Path) -> None:
    files = tracked_files()
    if not files:  # not a git checkout (for example a source archive)
        shutil.copytree(ROOT, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return
    for name in files:
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)


class RecordedResultsReproduceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.copy = Path(cls.tmp.name) / "repo"
        copy_repo(cls.copy)
        cls.env = {
            **os.environ,
            # Port 9 (discard) refuses fast, so the Ollama probe fails without waiting.
            "OLLAMA_BASE_URL": "http://127.0.0.1:9",
            "PYTHONDONTWRITEBYTECODE": "1",
        }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_outputs_match_committed_artifacts(self) -> None:
        for cwd, script, args, outputs in CASES:
            with self.subTest(script=f"{cwd}/{script}"):
                proc = subprocess.run(
                    [sys.executable, script, *args],
                    cwd=self.copy / cwd,
                    env=self.env,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    check=False,
                )
                self.assertEqual(proc.returncode, 0, proc.stdout[-2000:] + proc.stderr[-2000:])
                for rel in outputs:
                    regenerated = self.copy / rel
                    self.assertTrue(regenerated.exists(), f"{script} did not write {rel}")
                    self.assertTrue(
                        filecmp.cmp(ROOT / rel, regenerated, shallow=False),
                        f"{rel} no longer reproduces from {cwd}/{script}. If this is an intended "
                        "evaluator change, record it as a new run; do not edit the committed artifact.",
                    )


if __name__ == "__main__":
    unittest.main()
