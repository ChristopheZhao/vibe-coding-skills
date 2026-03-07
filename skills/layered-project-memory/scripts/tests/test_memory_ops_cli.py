#!/usr/bin/env python3
"""CLI regression tests for layered project memory.

Tests are intentionally black-box (CLI-level) to keep functional code and test code decoupled.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "memory_ops.py"


def run_cmd(args: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", str(SCRIPT_PATH), *args, "--root", str(root)]
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


class MemoryOpsCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="layered-memory-test-")
        self.root = Path(self.tmp.name)
        run_cmd(["init"], self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _capture(
        self,
        *,
        event_type: str,
        summary: str,
        plan_id: str | None = None,
        topic_id: str | None = None,
        impact: str = "medium",
        result: str = "unknown",
        problem_key: str | None = None,
        next_action: str | None = None,
        extra: list[str] | None = None,
    ) -> None:
        args = [
            "capture",
            "--event-type",
            event_type,
            "--summary",
            summary,
            "--impact",
            impact,
            "--result",
            result,
        ]
        if plan_id:
            args += ["--plan-id", plan_id]
        if topic_id:
            args += ["--topic-id", topic_id]
        if problem_key:
            args += ["--problem-key", problem_key]
        if next_action:
            args += ["--next-action", next_action]
        if extra:
            args += extra
        run_cmd(args, self.root)

    def _retrieve(self, profile: str, plan_id: str | None = None, topic_id: str | None = None) -> dict:
        args = ["retrieve", "--profile", profile, "--format", "json"]
        if plan_id:
            args += ["--plan-id", plan_id]
        if topic_id:
            args += ["--topic-id", topic_id]
        output = run_cmd(args, self.root)
        return json.loads(output.stdout)

    def _summarize(
        self,
        *,
        profile: str = "resume",
        mode: str = "incremental",
        plan_id: str | None = None,
        topic_id: str | None = None,
        max_events: int = 10,
    ) -> dict:
        args = [
            "summarize",
            "--profile",
            profile,
            "--mode",
            mode,
            "--max-events",
            str(max_events),
            "--json",
        ]
        if plan_id:
            args += ["--plan-id", plan_id]
        if topic_id:
            args += ["--topic-id", topic_id]
        output = run_cmd(args, self.root)
        return json.loads(output.stdout)

    def _event_ids(self) -> list[str]:
        events_path = self.root / "docs" / "memory" / "events" / "events.jsonl"
        ids: list[str] = []
        for line in events_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            event_id = payload.get("id")
            if isinstance(event_id, str):
                ids.append(event_id)
        return ids

    def test_repeated_failure_promotes_key_signal(self) -> None:
        plan_id = "PLAN-T-001"
        self._capture(
            plan_id=plan_id,
            event_type="experiment",
            summary="first failed attempt",
            impact="medium",
            result="failed",
            problem_key="same-problem",
        )
        self._capture(
            plan_id=plan_id,
            event_type="experiment",
            summary="second failed attempt",
            impact="medium",
            result="failed",
            problem_key="same-problem",
        )

        pack = self._retrieve("debug", plan_id)
        self.assertGreaterEqual(len(pack["events"]), 1)
        # second attempt should be promoted by repeat-failure bonus and debug profile.
        self.assertEqual(pack["events"][0]["summary"], "second failed attempt")
        self.assertTrue(pack["events"][0]["is_key_event"])
        self.assertEqual(pack["plan_id"], plan_id)

    def test_strategy_switch_and_handoff_resume_pack(self) -> None:
        plan_id = "PLAN-T-002"
        self._capture(
            plan_id=plan_id,
            event_type="decision",
            summary="switch from sync API to async queue",
            impact="high",
            result="mixed",
            next_action="migrate producer interface",
        )
        self._capture(
            plan_id=plan_id,
            event_type="milestone",
            summary="vertical slice ready for handoff",
            impact="high",
            result="success",
            next_action="handoff integration checklist",
        )

        pack = self._retrieve("resume", plan_id)
        self.assertEqual(pack["profile"], "resume")
        self.assertIn("state", pack)
        self.assertIn("events", pack)
        self.assertIn("next_actions", pack)
        self.assertGreaterEqual(len(pack["events"]), 1)
        self.assertIn("handoff integration checklist", pack["next_actions"])

    def test_gc_compacts_records_with_retention(self) -> None:
        plan_id = "PLAN-T-003"
        for i in range(8):
            self._capture(
                plan_id=plan_id,
                event_type="note",
                summary=f"note-{i}",
                impact="low",
                result="unknown",
                extra=["--hypothesis", f"h-{i}"],
            )

        run_cmd(["snapshot", "--plan-id", plan_id, "--profile", "resume", "--top-k", "2"], self.root)
        run_cmd(["snapshot", "--plan-id", plan_id, "--profile", "debug", "--top-k", "2"], self.root)
        run_cmd(["gc", "--retain-events", "3", "--retain-key-events", "1", "--retain-snapshots", "1"], self.root)

        doctor = subprocess.run(
            ["python3", str(SCRIPT_PATH), "doctor", "--root", str(self.root)],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)

        events_path = self.root / "docs" / "memory" / "events" / "events.jsonl"
        lines = [line for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertLessEqual(len(lines), 4)

    def test_topic_scope_without_plan_and_doc_pointer(self) -> None:
        topic_id = "checkout-timeout"
        self._capture(
            topic_id=topic_id,
            event_type="decision",
            summary="switch retry strategy to capped exponential backoff",
            impact="high",
            result="mixed",
            next_action="tune retry cap and rerun chaos tests",
            extra=["--doc-ref", "docs/adr/0012-retry-policy.md#decision", "--evidence", "logs/chaos-01.txt"],
        )
        self._capture(
            topic_id=topic_id,
            event_type="milestone",
            summary="timeout issue stabilized in staging",
            impact="high",
            result="success",
            next_action="prepare release checklist",
            extra=["--doc-ref", "docs/runbooks/checkout-timeout.md#staging-result"],
        )

        pack = self._retrieve("resume", topic_id=topic_id)
        self.assertEqual(pack["topic_id"], topic_id)
        self.assertIsNone(pack["plan_id"])
        self.assertGreaterEqual(len(pack["events"]), 1)
        self.assertIn("doc_refs", pack["events"][0])
        self.assertIn("prepare release checklist", pack["next_actions"])

    def test_summarize_incremental_updates_summary_files(self) -> None:
        topic_id = "payment-timeout"
        self._capture(
            topic_id=topic_id,
            event_type="decision",
            summary="switch timeout retry to bounded exponential backoff",
            impact="high",
            result="mixed",
            next_action="update retry middleware config",
            extra=["--doc-ref", "docs/adr/0042-retry-policy.md#decision"],
        )
        first = self._summarize(topic_id=topic_id, mode="incremental")
        self.assertEqual(first["event_count"], 1)

        self._capture(
            topic_id=topic_id,
            event_type="blocker",
            summary="staging still hits transient gateway timeout spikes",
            impact="high",
            result="failed",
            next_action="add circuit-breaker threshold tuning",
            extra=["--evidence", "logs/staging-timeout-20260307.txt"],
        )
        second = self._summarize(topic_id=topic_id, mode="incremental")
        self.assertEqual(second["event_count"], 2)
        self.assertGreaterEqual(second["last_event_seq"], first["last_event_seq"])
        self.assertEqual(second["last_event_id"], self._event_ids()[-1])
        self.assertIn("add circuit-breaker threshold tuning", second["highlights"]["next_actions"])

        summary_md = self.root / "docs" / "memory" / "summary" / "current.md"
        self.assertTrue(summary_md.exists())
        self.assertIn("## Next Actions", summary_md.read_text(encoding="utf-8"))

    def test_summarize_incremental_falls_back_to_rebuild_when_anchor_is_stale(self) -> None:
        topic_id = "build-cache"
        self._capture(
            topic_id=topic_id,
            event_type="decision",
            summary="switch cache key to include lockfile hash",
            impact="high",
            result="success",
        )
        self._capture(
            topic_id=topic_id,
            event_type="milestone",
            summary="cache hit ratio stabilized above 85 percent",
            impact="high",
            result="success",
        )
        self._summarize(topic_id=topic_id, mode="rebuild")

        summary_json = self.root / "docs" / "memory" / "summary" / "current.json"
        payload = json.loads(summary_json.read_text(encoding="utf-8"))
        payload["last_event_id"] = "EVT-MISSING-9999"
        payload["last_event_seq"] = 9999
        summary_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        refreshed = self._summarize(topic_id=topic_id, mode="incremental")
        self.assertEqual(refreshed["mode"], "rebuild")
        self.assertEqual(refreshed["event_count"], 2)
        self.assertEqual(refreshed["last_event_id"], self._event_ids()[-1])


if __name__ == "__main__":
    unittest.main()
