"""claim_24/run_fipsign_adapter_selftest.py must run on every supported Python.

Failure mode covered: a `dict | None` annotation raised TypeError at import on
Python 3.9 (PEP 604 unions in annotations need 3.10 or postponed evaluation).
"""

from __future__ import annotations

import subprocess
import sys
import unittest

from _helpers import ROOT


class FipsignSelftestTests(unittest.TestCase):
    def test_selftest_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, "run_fipsign_adapter_selftest.py"],
            cwd=ROOT / "claim_24",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("FAIL", proc.stdout)
        self.assertIn("agent_writable=false: True", proc.stdout)


if __name__ == "__main__":
    unittest.main()
