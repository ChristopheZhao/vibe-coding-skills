#!/usr/bin/env python3
"""CLI regression tests for experience capture operations.

Tests stay black-box at CLI level to keep functionality and tests decoupled.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "exp_ops.py"


def run_cmd(args: list[str], root: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", str(SCRIPT_PATH), *args, "--root", str(root)]
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


class ExperienceOpsCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="experience-capture-test-")
        self.root = Path(self.tmp.name)
        run_cmd(["init"], self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_and_list_by_tag(self) -> None:
        run_cmd(
            [
                "create",
                "--title",
                "Avoid bool-route orchestration",
                "--problem-signature",
                "global run_xxx bools in multi-agent orchestration",
                "--decision-rule",
                "express orchestration through plan actions",
                "--decision-rule",
                "fallback is runtime replan action",
                "--review-item",
                "check name and runtime behavior alignment",
                "--review-item",
                "check cross-agent bool coupling",
                "--review-item",
                "check if logic is global-variable equivalent",
                "--source-event-ref",
                "MEM-EVT-20260306-0001",
                "--doc-ref",
                "docs/knowledge/experience-skill-alignment-record.md",
                "--tag",
                "orchestrator",
                "--tag",
                "architecture",
            ],
            self.root,
        )

        listed = run_cmd(["list", "--tag", "orchestrator", "--format", "json", "--full"], self.root)
        payload = json.loads(listed.stdout)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["cards"][0]["title"], "Avoid bool-route orchestration")
        self.assertIn("capture_meta", payload["cards"][0])
        self.assertEqual(payload["cards"][0]["capture_meta"]["trigger_mode"], "manual-explicit")
        self.assertTrue(payload["cards"][0]["capture_meta"]["confirmed_by_user"])

    def test_create_requires_quality_gates(self) -> None:
        failed = run_cmd(
            [
                "create",
                "--title",
                "insufficient card",
                "--problem-signature",
                "missing required fields",
                "--decision-rule",
                "only one rule",
                "--review-item",
                "only one review",
                "--source-event-ref",
                "MEM-EVT-1",
            ],
            self.root,
            check=False,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("at least 2 --decision-rule", failed.stderr)

    def test_link_appends_refs_without_duplicates(self) -> None:
        created = run_cmd(
            [
                "create",
                "--title",
                "capture linkable card",
                "--problem-signature",
                "same issue repeated",
                "--decision-rule",
                "rule one",
                "--decision-rule",
                "rule two",
                "--review-item",
                "check a",
                "--review-item",
                "check b",
                "--review-item",
                "check c",
                "--source-event-ref",
                "MEM-EVT-10",
                "--tag",
                "memory",
                "--json",
            ],
            self.root,
        )
        card = json.loads(created.stdout)
        card_id = card["id"]

        linked = run_cmd(
            [
                "link",
                "--id",
                card_id,
                "--source-event-ref",
                "MEM-EVT-10",
                "--source-event-ref",
                "MEM-EVT-11",
                "--doc-ref",
                "docs/plans/active/PLAN-20260306-001.md",
                "--experience-ref",
                "EXP-20260301-0001",
                "--json",
            ],
            self.root,
        )

        updated = json.loads(linked.stdout)
        self.assertEqual(updated["source_event_refs"], ["MEM-EVT-10", "MEM-EVT-11"])
        self.assertIn("docs/plans/active/PLAN-20260306-001.md", updated["doc_refs"])
        self.assertIn("EXP-20260301-0001", updated["experience_refs"])

    def test_create_rejects_absolute_doc_ref(self) -> None:
        failed = run_cmd(
            [
                "create",
                "--title",
                "invalid absolute doc ref",
                "--problem-signature",
                "doc refs should be portable",
                "--decision-rule",
                "use relative refs only",
                "--decision-rule",
                "keep source pointers traceable",
                "--review-item",
                "check pointer portability",
                "--review-item",
                "check repository-relative refs",
                "--review-item",
                "check no absolute filesystem path",
                "--source-event-ref",
                "MEM-EVT-20260306-0002",
                "--doc-ref",
                "/abs/path/not/allowed.md#L1",
            ],
            self.root,
            check=False,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("repo-relative", failed.stderr)

    def test_create_rejects_invalid_source_event_ref(self) -> None:
        failed = run_cmd(
            [
                "create",
                "--title",
                "invalid source ref",
                "--problem-signature",
                "source refs must be traceable",
                "--decision-rule",
                "prefer MEM-EVT ids",
                "--decision-rule",
                "or use relative path with anchor",
                "--review-item",
                "check ref format",
                "--review-item",
                "check source anchor presence",
                "--review-item",
                "check parser compatibility",
                "--source-event-ref",
                "CHAT-raw-string-only",
            ],
            self.root,
            check=False,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("source event ref must be", failed.stderr)


if __name__ == "__main__":
    unittest.main()
