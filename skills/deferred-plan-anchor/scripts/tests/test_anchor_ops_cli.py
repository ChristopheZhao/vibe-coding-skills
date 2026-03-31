#!/usr/bin/env python3
"""Black-box CLI regression tests for deferred-plan-anchor."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "anchor_ops.py"


def run_cmd(args: list[str], root: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", str(SCRIPT_PATH), "--root", str(root), *args]
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


class DeferredPlanAnchorCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="deferred-plan-anchor-test-")
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _create(self, plan_id: str, activate: bool = False, review_after: str | None = None) -> None:
        args = [
            "create",
            "--id",
            plan_id,
            "--title",
            f"Deferred {plan_id}",
            "--goal",
            "Converge to only-A authority",
            "--why-not-now",
            "Immediate migration cost is too high",
            "--current-deviation",
            "Temporary dual-write still exists",
            "--scope-tags",
            "backend,planning",
            "--topic-tags",
            "sot,authority",
            "--plan-kinds",
            "feature,fix",
            "--do-not",
            "Do not add new authority semantics on B",
            "--allowed-now",
            "Compatibility reads only",
            "--reopen-trigger",
            "Create a dedicated migration plan before touching the boundary",
        ]
        if review_after:
            args += ["--review-after", review_after]
        if activate:
            args.append("--activate")
        run_cmd(["ensure"], self.root)
        run_cmd(args, self.root)

    def test_resolve_noops_when_root_absent(self) -> None:
        completed = run_cmd(["resolve-for-planning", "--json"], self.root)
        payload = json.loads(completed.stdout)

        self.assertFalse(payload["enabled"])
        self.assertFalse(payload["applies"])
        self.assertEqual(payload["reason"], "deferred-plan root not enabled")

    def test_resolve_applies_for_matching_active_plan(self) -> None:
        self._create("DP-T-001", activate=True)
        completed = run_cmd(
            [
                "resolve-for-planning",
                "--scope-tags",
                "backend",
                "--topic-tags",
                "authority",
                "--plan-kind",
                "feature",
                "--json",
            ],
            self.root,
        )
        payload = json.loads(completed.stdout)

        self.assertTrue(payload["enabled"])
        self.assertTrue(payload["active"])
        self.assertTrue(payload["applies"])
        self.assertIn("Do not add new authority semantics on B", payload["do_not"])

    def test_second_activation_is_rejected(self) -> None:
        self._create("DP-T-001", activate=True)
        self._create("DP-T-002", activate=False)

        failed = run_cmd(["activate", "--id", "DP-T-002"], self.root, check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("already active", failed.stderr)

    def test_completed_then_archived_plan_stops_affecting_current(self) -> None:
        self._create("DP-T-001", activate=True)
        run_cmd(["complete", "--id", "DP-T-001"], self.root)
        run_cmd(["archive", "--id", "DP-T-001"], self.root)

        completed = run_cmd(["resolve-for-planning", "--scope-tags", "backend", "--topic-tags", "authority", "--json"], self.root)
        payload = json.loads(completed.stdout)
        current = (self.root / "docs" / "deferred-plans" / "CURRENT.md").read_text(encoding="utf-8")
        archived = self.root / "docs" / "deferred-plans" / "archive"

        self.assertFalse(payload["applies"])
        self.assertIn("no active deferred plan", payload["reason"])
        self.assertIn("No active deferred plan", current)
        self.assertTrue(any(archived.rglob("DP-T-001.md")))

    def test_stale_active_plan_does_not_apply(self) -> None:
        self._create("DP-T-001", activate=True, review_after="2000-01-01")

        completed = run_cmd(
            ["resolve-for-planning", "--scope-tags", "backend", "--topic-tags", "authority", "--plan-kind", "feature", "--json"],
            self.root,
        )
        payload = json.loads(completed.stdout)

        self.assertTrue(payload["enabled"])
        self.assertTrue(payload["active"])
        self.assertTrue(payload["stale"])
        self.assertFalse(payload["applies"])
        self.assertEqual(payload["reason"], "active deferred plan is stale")


if __name__ == "__main__":
    unittest.main()
