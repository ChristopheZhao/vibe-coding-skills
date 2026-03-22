#!/usr/bin/env python3
"""Black-box CLI regression tests for checkpoint-gatekeeper."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "gate_ops.py"


def run_cmd(args: list[str], root: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", str(SCRIPT_PATH), "--root", str(root), *args]
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class GateOpsCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="checkpoint-gatekeeper-test-")
        self.root = Path(self.tmp.name)
        self._create_plan("PLAN-T-001")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _create_plan(self, plan_id: str) -> None:
        (self.root / "docs" / "plans" / "active").mkdir(parents=True, exist_ok=True)
        index = {
            "plans": [
                {
                    "id": plan_id,
                    "title": "Checkpoint Gatekeeper Test",
                    "kind": "feature",
                    "status": "in_progress",
                    "priority": "P0",
                    "owner": "codex",
                    "file_path": f"docs/plans/active/{plan_id}.md",
                    "confirmed_by_user": False,
                    "created_at": "2026-03-22T00:00:00Z",
                    "updated_at": "2026-03-22T00:00:00Z",
                    "archived_at": None,
                    "notes": [],
                }
            ]
        }
        (self.root / "docs" / "plans" / "PLAN_INDEX.json").write_text(
            json.dumps(index, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.root / "docs" / "plans" / "active" / f"{plan_id}.md").write_text(
            f"# {plan_id}\n",
            encoding="utf-8",
        )

    def _gate_path(self, checkpoint: str = "CHK-A") -> Path:
        return self.root / "docs" / "checkpoints" / "PLAN-T-001" / f"{checkpoint}-gate.json"

    def _checklist_path(self, checkpoint: str = "CHK-A") -> Path:
        return self.root / "docs" / "checkpoints" / "PLAN-T-001" / f"{checkpoint}-checklist.md"

    def test_init_creates_independent_checkpoint_artifacts(self) -> None:
        run_cmd(
            [
                "init",
                "--id",
                "PLAN-T-001",
                "--checkpoint",
                "CHK-A",
                "--title",
                "Checkpoint A",
                "--validation-command",
                "true",
            ],
            self.root,
        )

        checklist = self._checklist_path()
        gate = self._gate_path()
        self.assertTrue(checklist.is_file())
        self.assertTrue(gate.is_file())
        self.assertIn("docs/checkpoints/PLAN-T-001", str(checklist))
        self.assertEqual(read_json(gate)["verdict"], "pending")

    def test_check_pass_does_not_mutate_plan_index(self) -> None:
        run_cmd(
            [
                "init",
                "--id",
                "PLAN-T-001",
                "--checkpoint",
                "CHK-A",
                "--validation-command",
                "true",
            ],
            self.root,
        )
        index_before = (self.root / "docs" / "plans" / "PLAN_INDEX.json").read_text(encoding="utf-8")

        completed = run_cmd(
            ["check", "--id", "PLAN-T-001", "--checkpoint", "CHK-A"],
            self.root,
        )

        self.assertEqual(completed.returncode, 0)
        gate = read_json(self._gate_path())
        self.assertEqual(gate["verdict"], "pass")
        self.assertEqual(
            (self.root / "docs" / "plans" / "PLAN_INDEX.json").read_text(encoding="utf-8"),
            index_before,
        )

    def test_check_auto_fix_pass(self) -> None:
        run_cmd(
            [
                "init",
                "--id",
                "PLAN-T-001",
                "--checkpoint",
                "CHK-A",
                "--validation-command",
                "test -f fixed.flag",
                "--auto-fix-command",
                "touch fixed.flag",
            ],
            self.root,
        )

        completed = run_cmd(
            ["check", "--id", "PLAN-T-001", "--checkpoint", "CHK-A"],
            self.root,
        )

        self.assertEqual(completed.returncode, 0)
        gate = read_json(self._gate_path())
        self.assertEqual(gate["verdict"], "auto_fixed_pass")
        self.assertTrue((self.root / "fixed.flag").is_file())

    def test_check_escalates_to_user_confirmation(self) -> None:
        run_cmd(
            [
                "init",
                "--id",
                "PLAN-T-001",
                "--checkpoint",
                "CHK-A",
                "--validation-command",
                "printf 'NEEDS_USER_CONFIRMATION\\n' && exit 1",
            ],
            self.root,
        )

        completed = run_cmd(
            ["check", "--id", "PLAN-T-001", "--checkpoint", "CHK-A"],
            self.root,
            check=False,
        )

        self.assertEqual(completed.returncode, 3)
        gate = read_json(self._gate_path())
        self.assertEqual(gate["verdict"], "needs_user_confirmation")
        self.assertIn("NEEDS_USER_CONFIRMATION", gate["attempts"][-1]["matched_user_confirmation_triggers"])

    def test_waive_records_reason(self) -> None:
        run_cmd(
            [
                "init",
                "--id",
                "PLAN-T-001",
                "--checkpoint",
                "CHK-A",
                "--validation-command",
                "true",
            ],
            self.root,
        )

        completed = run_cmd(
            [
                "waive",
                "--id",
                "PLAN-T-001",
                "--checkpoint",
                "CHK-A",
                "--reason",
                "Manual override for exploratory spike",
            ],
            self.root,
        )

        self.assertEqual(completed.returncode, 0)
        gate = read_json(self._gate_path())
        self.assertEqual(gate["verdict"], "waived")
        self.assertEqual(gate["waiver"]["reason"], "Manual override for exploratory spike")


if __name__ == "__main__":
    unittest.main()
