#!/usr/bin/env python3
"""CLI regression tests for sdd plan operations.

Tests stay black-box at CLI level so lifecycle behavior is verified through the
public command surface instead of internal helper coupling.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "plan_ops.py"


def run_cmd(args: list[str], root: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", str(SCRIPT_PATH), *args, "--root", str(root)]
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def read_index(root: Path) -> dict:
    index_path = root / "docs" / "plans" / "PLAN_INDEX.json"
    return json.loads(index_path.read_text(encoding="utf-8"))


def find_plan(index: dict, plan_id: str) -> dict:
    for item in index.get("plans", []):
        if item.get("id") == plan_id:
            return item
    raise AssertionError(f"plan not found in index: {plan_id}")


def section_body(markdown: str, heading: str) -> str:
    marker = f"## {heading}\n"
    if marker not in markdown:
        raise AssertionError(f"missing dashboard section: {heading}")
    tail = markdown.split(marker, 1)[1]
    return tail.split("\n## ", 1)[0]


class PlanOpsCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="sdd-plan-maintainer-test-")
        self.root = Path(self.tmp.name)
        run_cmd(["ensure"], self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _create_plan(self, plan_id: str, title: str = "Plan Ops Test") -> None:
        run_cmd(
            ["create", "--id", plan_id, "--title", title, "--kind", "fix", "--priority", "P1"],
            self.root,
        )

    def _status(self, plan_id: str, status: str, note: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
        args = ["status", "--id", plan_id, "--status", status]
        if note:
            args += ["--note", note]
        return run_cmd(args, self.root, check=check)

    def test_superseded_requires_note_and_updates_doc_status(self) -> None:
        self._create_plan("PLAN-T-001")
        self._status("PLAN-T-001", "in_progress", note="start work")

        failed = self._status("PLAN-T-001", "superseded", check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("superseded requires --note", failed.stderr)

        note = "Superseded by queue/runtime boundary diagnosis"
        self._status("PLAN-T-001", "superseded", note=note)

        item = find_plan(read_index(self.root), "PLAN-T-001")
        self.assertEqual(item["status"], "superseded")
        self.assertEqual(item["notes"][-1]["text"], note)

        plan_doc = (self.root / item["file_path"]).read_text(encoding="utf-8")
        self.assertIn("- Status: superseded", plan_doc)

    def test_dashboard_excludes_superseded_from_active_and_lists_it_separately(self) -> None:
        self._create_plan("PLAN-T-002", title="Still Active")
        self._status("PLAN-T-002", "in_progress", note="active execution")

        self._create_plan("PLAN-T-003", title="Old Wrong Direction")
        self._status("PLAN-T-003", "in_progress", note="initial execution")
        self._status(
            "PLAN-T-003",
            "superseded",
            note="Superseded by newer root-cause diagnosis",
        )

        run_cmd(["dashboard"], self.root)
        dashboard = (self.root / "docs" / "plans" / "views" / "dashboard.md").read_text(encoding="utf-8")

        active_section = section_body(dashboard, "Active Plans")
        superseded_section = section_body(dashboard, "Superseded Plans")
        attention_section = section_body(dashboard, "Needs Attention")

        self.assertIn("PLAN-T-002", active_section)
        self.assertNotIn("PLAN-T-003", active_section)
        self.assertIn("PLAN-T-003", superseded_section)
        self.assertNotIn("PLAN-T-003", attention_section)

    def test_archive_accepts_superseded_plan_with_confirmation(self) -> None:
        self._create_plan("PLAN-T-004", title="Archiveable Wrong Plan")
        self._status("PLAN-T-004", "in_progress", note="started")
        self._status(
            "PLAN-T-004",
            "superseded",
            note="Superseded by successor plan PLAN-T-005",
        )

        run_cmd(["archive", "--id", "PLAN-T-004", "--confirmed-by-user"], self.root)

        item = find_plan(read_index(self.root), "PLAN-T-004")
        self.assertEqual(item["status"], "archived")
        self.assertIsNotNone(item["archived_at"])
        self.assertTrue(item["file_path"].startswith("docs/plans/archive/"))

        archived_doc = (self.root / item["file_path"]).read_text(encoding="utf-8")
        self.assertIn("- Status: archived", archived_doc)


if __name__ == "__main__":
    unittest.main()
