#!/usr/bin/env python3
"""Black-box CLI regression tests for checkpoint-commit-advisor."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "commit_advisor.py"


def run_cmd(args: list[str], root: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", str(SCRIPT_PATH), "--root", str(root), *args]
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, text=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Checkpoint Test"], cwd=root, check=True, text=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "checkpoint@example.com"], cwd=root, check=True, text=True, capture_output=True)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, text=True, capture_output=True)


class CommitAdvisorCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="checkpoint-commit-advisor-test-")
        self.root = Path(self.tmp.name)
        init_repo(self.root)
        (self.root / "README.md").write_text("# Test Repo\n", encoding="utf-8")
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-m", "base")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_analyze_recommends_two_layer_for_governance_plus_code(self) -> None:
        (self.root / "docs" / "plans" / "active").mkdir(parents=True, exist_ok=True)
        (self.root / "src").mkdir(parents=True, exist_ok=True)
        (self.root / "docs" / "plans" / "PLAN_INDEX.json").write_text(
            json.dumps(
                {
                    "plans": [
                        {
                            "id": "PLAN-T-001",
                            "title": "Test Plan",
                            "kind": "feature",
                            "status": "in_progress",
                            "priority": "P0",
                            "owner": "codex",
                            "file_path": "docs/plans/active/PLAN-T-001.md",
                        }
                    ]
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "docs" / "plans" / "active" / "PLAN-T-001.md").write_text(
            "# Plan\n- Status: testing\n",
            encoding="utf-8",
        )
        (self.root / "src" / "app.py").write_text("print('changed')\n", encoding="utf-8")

        completed = run_cmd(["analyze", "--json", "--plan-id", "PLAN-T-001"], self.root)
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["decision"], "commit_now")
        self.assertEqual(payload["strategy"], "two-layer")
        bucket_kinds = [bucket["kind"] for bucket in payload["buckets"]]
        self.assertIn("governance_anchor", bucket_kinds)
        self.assertIn("implementation_snapshot", bucket_kinds)
        messages = {item["bucket"]: item["commit_message"] for item in payload["messages"]}
        self.assertEqual(messages["governance_anchor"], "chore(plan): align governance for PLAN-T-001")

    def test_analyze_defers_small_focused_change(self) -> None:
        (self.root / "src").mkdir(parents=True, exist_ok=True)
        (self.root / "src" / "app.py").write_text("print('small change')\n", encoding="utf-8")

        completed = run_cmd(["analyze", "--json"], self.root)
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["decision"], "defer")
        self.assertIsNone(payload["strategy"])
        self.assertIn("small and focused", payload["decision_reason"])

    def test_analyze_blocks_on_conflict_markers(self) -> None:
        (self.root / "src").mkdir(parents=True, exist_ok=True)
        conflicted = "<<<<<<< HEAD\nvalue = 1\n=======\nvalue = 2\n>>>>>>> branch\n"
        (self.root / "src" / "app.py").write_text(conflicted, encoding="utf-8")

        completed = run_cmd(["analyze", "--json", "--explicit-checkpoint"], self.root)
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["decision"], "defer")
        self.assertTrue(payload["health_flags"]["has_conflict_markers"])
        self.assertIn("conflict markers found in changed files", payload["health_flags"]["blocking_issues"])

    def test_analyze_does_not_mutate_worktree(self) -> None:
        (self.root / "src").mkdir(parents=True, exist_ok=True)
        (self.root / "src" / "app.py").write_text("print('change')\n", encoding="utf-8")
        before = git(self.root, "status", "--short").stdout

        completed = run_cmd(["analyze", "--json", "--explicit-checkpoint"], self.root)
        after = git(self.root, "status", "--short").stdout

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
