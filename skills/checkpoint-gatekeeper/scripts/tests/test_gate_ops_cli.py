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

    def _evidence_path(self, checkpoint: str = "CHK-A") -> Path:
        return self.root / "docs" / "checkpoints" / "PLAN-T-001" / f"{checkpoint}-evidence.json"

    def _acceptance_review_path(self, checkpoint: str = "CHK-A") -> Path:
        return self.root / "docs" / "checkpoints" / "PLAN-T-001" / f"{checkpoint}-acceptance-review.json"

    def _init_acceptance_checkpoint(self, checkpoint: str = "CHK-B") -> None:
        run_cmd(
            [
                "init",
                "--id",
                "PLAN-T-001",
                "--checkpoint",
                checkpoint,
                "--title",
                f"{checkpoint} Acceptance",
                "--profile",
                "acceptance",
                "--acceptance-target",
                "semantic closure for sprint B",
                "--required-evidence",
                "smoke passed",
                "--required-evidence",
                "contract gaps empty",
                "--validation-command",
                "true",
            ],
            self.root,
        )

    def _write_acceptance_evidence(self, checkpoint: str = "CHK-B") -> None:
        payload = {
            "plan_id": "PLAN-T-001",
            "checkpoint": checkpoint,
            "acceptance_target": "semantic closure for sprint B",
            "contract_ref": "docs/contracts/CHK-B.json",
            "evidence_refs": ["results/CHK-B-smoke.txt"],
            "changed_artifact_paths": ["skills/checkpoint-gatekeeper/scripts/gate_ops.py"],
            "negative_cases": ["Do not create a second verdict owner."],
            "declared_out_of_scope": ["No standalone verifier skill."],
            "executor_summary": "Implemented the declared checkpoint scope and linked smoke output.",
        }
        self._evidence_path(checkpoint).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def _write_acceptance_review(
        self,
        checkpoint: str = "CHK-B",
        *,
        review_verdict: str = "accept",
        contract_closure: str = "satisfied",
        evidence_sufficiency: str = "sufficient",
        gap_severity: str = "none",
        gaps: list[str] | None = None,
    ) -> None:
        payload = {
            "plan_id": "PLAN-T-001",
            "checkpoint": checkpoint,
            "reviewer_kind": "peer_agent",
            "review_verdict": review_verdict,
            "contract_closure": contract_closure,
            "evidence_sufficiency": evidence_sufficiency,
            "gap_severity": gap_severity,
            "gaps": gaps or [],
            "cited_evidence": ["results/CHK-B-smoke.txt"],
            "summary": "Independent review completed.",
        }
        self._acceptance_review_path(checkpoint).write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

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

    def test_acceptance_init_creates_evidence_template(self) -> None:
        self._init_acceptance_checkpoint()

        evidence = read_json(self._evidence_path("CHK-B"))
        gate = read_json(self._gate_path("CHK-B"))

        self.assertEqual(evidence["plan_id"], "PLAN-T-001")
        self.assertEqual(evidence["checkpoint"], "CHK-B")
        self.assertEqual(evidence["acceptance_target"], "semantic closure for sprint B")
        self.assertEqual(gate["profile"], "acceptance")
        self.assertIn("evidence_path", gate)
        self.assertIn("acceptance_review_path", gate)

    def test_acceptance_check_requires_independent_review_artifact(self) -> None:
        self._init_acceptance_checkpoint()
        self._write_acceptance_evidence("CHK-B")

        completed = run_cmd(
            ["check", "--id", "PLAN-T-001", "--checkpoint", "CHK-B"],
            self.root,
            check=False,
        )

        self.assertEqual(completed.returncode, 3)
        gate = read_json(self._gate_path("CHK-B"))
        self.assertEqual(gate["verdict"], "needs_user_confirmation")
        self.assertTrue(
            any("acceptance-review.json" in gap for gap in gate["acceptance_gaps"]),
            gate["acceptance_gaps"],
        )

    def test_acceptance_check_passes_with_independent_review(self) -> None:
        self._init_acceptance_checkpoint()
        self._write_acceptance_evidence("CHK-B")
        self._write_acceptance_review("CHK-B")

        completed = run_cmd(
            ["check", "--id", "PLAN-T-001", "--checkpoint", "CHK-B"],
            self.root,
        )

        self.assertEqual(completed.returncode, 0)
        gate = read_json(self._gate_path("CHK-B"))
        self.assertEqual(gate["verdict"], "pass")
        self.assertEqual(gate["acceptance_gaps"], [])
        self.assertIn("Acceptance target satisfied", gate["summary"])

    def test_acceptance_review_revise_requests_user_confirmation(self) -> None:
        self._init_acceptance_checkpoint()
        self._write_acceptance_evidence("CHK-B")
        self._write_acceptance_review(
            "CHK-B",
            review_verdict="revise",
            contract_closure="partial",
            evidence_sufficiency="insufficient",
            gap_severity="cosmetic",
            gaps=["Clarify one remaining acceptance note."],
        )

        completed = run_cmd(
            ["check", "--id", "PLAN-T-001", "--checkpoint", "CHK-B"],
            self.root,
            check=False,
        )

        self.assertEqual(completed.returncode, 3)
        gate = read_json(self._gate_path("CHK-B"))
        self.assertEqual(gate["verdict"], "needs_user_confirmation")
        self.assertEqual(gate["acceptance_gaps"], ["Clarify one remaining acceptance note."])

    def test_acceptance_review_block_fails_gate(self) -> None:
        self._init_acceptance_checkpoint()
        self._write_acceptance_evidence("CHK-B")
        self._write_acceptance_review(
            "CHK-B",
            review_verdict="block",
            contract_closure="failed",
            evidence_sufficiency="conflicting",
            gap_severity="semantic",
            gaps=["Semantic closure is not achieved."],
        )

        completed = run_cmd(
            ["check", "--id", "PLAN-T-001", "--checkpoint", "CHK-B"],
            self.root,
            check=False,
        )

        self.assertEqual(completed.returncode, 2)
        gate = read_json(self._gate_path("CHK-B"))
        self.assertEqual(gate["verdict"], "fail")
        self.assertEqual(gate["acceptance_gaps"], ["Semantic closure is not achieved."])

    def test_acceptance_declared_out_of_scope_does_not_create_gap(self) -> None:
        self._init_acceptance_checkpoint()
        self._write_acceptance_evidence("CHK-B")
        evidence = read_json(self._evidence_path("CHK-B"))
        evidence["declared_out_of_scope"] = [
            "Follow-up workflow automation is intentionally deferred.",
            "Standalone verifier skill extraction is out of scope.",
        ]
        self._evidence_path("CHK-B").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        self._write_acceptance_review("CHK-B")

        completed = run_cmd(
            ["check", "--id", "PLAN-T-001", "--checkpoint", "CHK-B"],
            self.root,
        )

        self.assertEqual(completed.returncode, 0)
        gate = read_json(self._gate_path("CHK-B"))
        self.assertEqual(gate["verdict"], "pass")
        self.assertEqual(gate["acceptance_gaps"], [])

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
