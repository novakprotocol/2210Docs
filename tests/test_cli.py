from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "iatdocs", "--repo", str(ROOT), *args],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class IaTDocsCliTests(unittest.TestCase):
    def test_doctor_json(self) -> None:
        completed = run_cli("doctor", "--json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["product"], "IaT Docs Engine")
        self.assertEqual(result["engine_version"], "0.08.2")
        self.assertEqual(result["configuration"]["status"], "valid")

    def test_profiles_json(self) -> None:
        completed = run_cli("profiles", "--json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["count"], 22)
        self.assertIn("iop", {item["id"] for item in result["profiles"]})

    def test_validate_template(self) -> None:
        completed = run_cli("validate", "--built")
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        self.assertIn("Result: PASS", completed.stdout)


if __name__ == "__main__":
    unittest.main()
