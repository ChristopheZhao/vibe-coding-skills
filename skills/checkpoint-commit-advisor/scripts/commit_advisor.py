#!/usr/bin/env python3
"""Deterministic dirty-worktree advisory for checkpoint commits."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, NoReturn


def fail(message: str) -> NoReturn:
    raise SystemExit(message)


def repo_root(value: str) -> Path:
    return Path(value).resolve()


def run_git(root: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        command = "git " + " ".join(args)
        fail(f"{command} failed: {completed.stderr.strip() or completed.stdout.strip()}")
    return completed


def ensure_git_repo(root: Path) -> None:
    probe = run_git(root, ["rev-parse", "--show-toplevel"], check=False)
    if probe.returncode != 0:
        fail(f"not a git repository: {root}")


def parse_status(root: Path) -> list[dict[str, Any]]:
    completed = run_git(root, ["status", "--short", "--untracked-files=all"])
    entries: list[dict[str, Any]] = []
    for raw_line in completed.stdout.splitlines():
        if not raw_line.strip():
            continue
        status = raw_line[:2]
        path_text = raw_line[3:] if len(raw_line) > 3 else ""
        path = path_text.split(" -> ", 1)[-1]
        entries.append(
            {
                "status": status,
                "path": path,
                "tracked": status != "??",
                "untracked": status == "??",
            }
        )
    return entries


def classify_path(path: str) -> str:
    lower = path.lower()
    if path == "AGENTS.md" or path.startswith("docs/plans/") or path.startswith("docs/session-handoff/"):
        return "governance_anchor"
    if path.startswith("docs/") or lower.endswith((".md", ".rst", ".txt")):
        return "supporting_docs_snapshot"
    return "implementation_snapshot"


def top_level_counts(paths: list[str]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for path in paths:
        root = path.split("/", 1)[0] if "/" in path else path
        counts[root] += 1
    return [{"root": key, "count": counts[key]} for key in sorted(counts)]


def read_text_if_possible(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def has_conflict_markers(root: Path, changed_paths: list[str]) -> tuple[bool, list[str]]:
    flagged: list[str] = []
    markers = ("<<<<<<<", "=======", ">>>>>>>")
    for rel in changed_paths:
        text = read_text_if_possible(root / rel)
        if text is None:
            continue
        for line in text.splitlines():
            if line.startswith(markers):
                flagged.append(rel)
                break
    return bool(flagged), flagged


def git_diff_check_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for args in (["diff", "--check"], ["diff", "--cached", "--check"]):
        completed = run_git(root, args, check=False)
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        if stdout:
            issues.extend(line for line in stdout.splitlines() if line.strip())
        if stderr:
            issues.extend(line for line in stderr.splitlines() if line.strip())
    return issues


def health_flags(root: Path, changed_paths: list[str]) -> dict[str, Any]:
    diff_check = git_diff_check_issues(root)
    conflict, conflict_paths = has_conflict_markers(root, changed_paths)
    blocking: list[str] = []
    if diff_check:
        blocking.append("git diff --check reported blocking issues")
    if conflict:
        blocking.append("conflict markers found in changed files")
    return {
        "diff_check_clean": not diff_check,
        "diff_check_issues": diff_check,
        "has_conflict_markers": conflict,
        "conflict_marker_paths": conflict_paths,
        "blocking_issues": blocking,
    }


def summarize_dirty_tree(entries: list[dict[str, Any]]) -> dict[str, Any]:
    paths = [entry["path"] for entry in entries]
    tracked = sum(1 for entry in entries if entry["tracked"])
    untracked = sum(1 for entry in entries if entry["untracked"])
    return {
        "changed_files": len(entries),
        "tracked_files": tracked,
        "untracked_files": untracked,
        "top_level_counts": top_level_counts(paths),
        "paths": paths,
    }


def build_buckets(paths: list[str]) -> dict[str, list[str]]:
    buckets = {
        "governance_anchor": [],
        "implementation_snapshot": [],
        "supporting_docs_snapshot": [],
    }
    for path in paths:
        buckets[classify_path(path)].append(path)
    return {key: value for key, value in buckets.items() if value}


def choose_strategy(decision: str, buckets: dict[str, list[str]]) -> str | None:
    if decision != "commit_now":
        return None
    present = sum(1 for paths in buckets.values() if paths)
    if present >= 3:
        return "three-layer"
    if present == 2:
        return "two-layer"
    return "single-snapshot"


def choose_decision(
    summary: dict[str, Any],
    health: dict[str, Any],
    buckets: dict[str, list[str]],
    explicit: bool,
) -> tuple[str, str, list[str]]:
    risks: list[str] = []
    if summary["changed_files"] == 0:
        return "defer", "No dirty worktree exists, so a checkpoint commit is not needed.", risks
    if health["blocking_issues"]:
        risks.extend(health["blocking_issues"])
        return "defer", "Worktree health issues block checkpoint commit advice until the tree is cleaned up.", risks
    category_count = sum(1 for paths in buckets.values() if paths)
    if category_count >= 2:
        return "commit_now", "Dirty worktree spans multiple buckets and should be frozen before the next phase continues.", risks
    if summary["changed_files"] <= 3 and not explicit:
        risks.append("Checkpoint strategy may add process noise for a very small, focused dirty tree.")
        return "defer", "Dirty worktree is small and focused enough that a checkpoint strategy is probably unnecessary.", risks
    return "commit_now", "Dirty worktree is large or mixed enough that a checkpoint commit strategy should be considered now.", risks


def governance_message(plan_id: str | None) -> str:
    if plan_id:
        return f"chore(plan): align governance for {plan_id}"
    return "chore(plan): align governance before next phase"


def implementation_message(plan_id: str | None, layered: bool) -> str:
    if layered and plan_id:
        return f"checkpoint(wip): known-bad implementation snapshot before {plan_id} next phase"
    if layered:
        return "checkpoint(wip): known-bad implementation snapshot before next phase"
    return "checkpoint(wip): working snapshot before next phase"


def docs_message() -> str:
    return "docs(snapshot): preserve supporting context before next phase"


def bucket_purpose(kind: str) -> str:
    if kind == "governance_anchor":
        return "Freeze plan, handoff, and governance truth separately from code snapshot work."
    if kind == "implementation_snapshot":
        return "Freeze the current implementation and test state, even if it is not yet correct."
    if kind == "supporting_docs_snapshot":
        return "Keep optional supporting docs or import history out of the main code snapshot."
    return "Freeze the current mixed worktree state."


def suggested_messages(buckets: dict[str, list[str]], strategy: str | None, plan_id: str | None) -> list[dict[str, str]]:
    layered = strategy in {"two-layer", "three-layer"}
    messages: list[dict[str, str]] = []
    if "governance_anchor" in buckets:
        messages.append({"bucket": "governance_anchor", "commit_message": governance_message(plan_id)})
    if "implementation_snapshot" in buckets:
        messages.append(
            {
                "bucket": "implementation_snapshot",
                "commit_message": implementation_message(plan_id, layered),
            }
        )
    if "supporting_docs_snapshot" in buckets:
        messages.append({"bucket": "supporting_docs_snapshot", "commit_message": docs_message()})
    if not messages and buckets:
        messages.append({"bucket": "mixed_snapshot", "commit_message": implementation_message(plan_id, False)})
    return messages


def build_bucket_models(
    buckets: dict[str, list[str]],
    messages: list[dict[str, str]],
) -> list[dict[str, Any]]:
    message_map = {item["bucket"]: item["commit_message"] for item in messages}
    ordered = ["governance_anchor", "implementation_snapshot", "supporting_docs_snapshot"]
    models: list[dict[str, Any]] = []
    for kind in ordered:
        if kind not in buckets:
            continue
        models.append(
            {
                "kind": kind,
                "purpose": bucket_purpose(kind),
                "paths": buckets[kind],
                "commit_message": message_map.get(kind, ""),
            }
        )
    return models


def suggested_commands(bucket_models: list[dict[str, Any]]) -> list[str]:
    commands: list[str] = []
    for bucket in bucket_models:
        add_cmd = "git add " + " ".join(shlex.quote(path) for path in bucket["paths"])
        commit_cmd = "git commit -m " + shlex.quote(bucket["commit_message"])
        commands.extend([add_cmd, commit_cmd])
    return commands


def confirmation_points(decision: str, strategy: str | None) -> list[str]:
    if decision != "commit_now":
        return ["Confirm whether checkpoint commit strategy should be skipped for this worktree."]
    points = [
        "Confirm that the proposed layer split matches the current task boundary.",
        "Confirm before running any real git add or git commit command.",
    ]
    if strategy in {"two-layer", "three-layer"}:
        points.insert(1, "Confirm that a known-bad or not-yet-validated snapshot is acceptable for this checkpoint.")
    return points


def advisory_risks(
    risks: list[str],
    buckets: dict[str, list[str]],
    summary: dict[str, Any],
) -> list[str]:
    items = list(risks)
    if "governance_anchor" in buckets and "implementation_snapshot" in buckets:
        items.append("A single mixed commit would blur governance truth and implementation snapshot boundaries.")
    if "supporting_docs_snapshot" in buckets and "implementation_snapshot" in buckets:
        items.append("Supporting docs may add noise if mixed into the main implementation snapshot.")
    if summary["changed_files"] > 25:
        items.append("Large dirty trees increase the chance of accidental over-grouping; review the proposed buckets before executing.")
    return items


def build_report(root: Path, plan_id: str | None, explicit: bool) -> dict[str, Any]:
    entries = parse_status(root)
    summary = summarize_dirty_tree(entries)
    changed_paths = summary["paths"]
    health = health_flags(root, changed_paths)
    buckets = build_buckets(changed_paths)
    decision, reason, base_risks = choose_decision(summary, health, buckets, explicit)
    strategy = choose_strategy(decision, buckets)
    messages = suggested_messages(buckets, strategy, plan_id)
    bucket_models = build_bucket_models(buckets, messages)
    risks = advisory_risks(base_risks, buckets, summary)

    return {
        "decision": decision,
        "decision_reason": reason,
        "strategy": strategy,
        "plan_id": plan_id,
        "dirty_tree_summary": summary,
        "health_flags": health,
        "buckets": bucket_models,
        "messages": messages,
        "confirmation_points": confirmation_points(decision, strategy),
        "risks": risks,
        "suggested_commands": suggested_commands(bucket_models) if decision == "commit_now" else [],
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"Decision: {report['decision']}",
        f"Reason: {report['decision_reason']}",
        f"Strategy: {report['strategy'] if report['strategy'] is not None else 'n/a'}",
        (
            "Dirty tree: "
            f"{report['dirty_tree_summary']['changed_files']} files "
            f"({report['dirty_tree_summary']['tracked_files']} tracked, "
            f"{report['dirty_tree_summary']['untracked_files']} untracked)"
        ),
    ]

    blocking = report["health_flags"]["blocking_issues"]
    if blocking:
        lines.append("Blocking issues:")
        lines.extend(f"- {item}" for item in blocking)

    if report["buckets"]:
        lines.append("Buckets:")
        for bucket in report["buckets"]:
            lines.append(f"- {bucket['kind']}: {bucket['purpose']}")
            lines.append(f"  message: {bucket['commit_message']}")
            lines.extend(f"  path: {path}" for path in bucket["paths"])

    if report["risks"]:
        lines.append("Risks:")
        lines.extend(f"- {item}" for item in report["risks"])

    if report["confirmation_points"]:
        lines.append("Confirmation points:")
        lines.extend(f"- {item}" for item in report["confirmation_points"])

    if report["suggested_commands"]:
        lines.append("Suggested commands:")
        lines.extend(f"- {item}" for item in report["suggested_commands"])

    return "\n".join(lines)


def command_analyze(args: argparse.Namespace) -> int:
    root = repo_root(args.root)
    ensure_git_repo(root)
    report = build_report(root, args.plan_id, args.explicit_checkpoint)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        print(render_text(report))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Checkpoint commit advisory CLI")
    parser.add_argument("--root", default=".", help="Repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze dirty worktree and propose checkpoint commit strategy")
    analyze.add_argument("--json", action="store_true", help="Emit JSON output")
    analyze.add_argument("--plan-id", help="Optional plan identifier used for labeling commit messages")
    analyze.add_argument(
        "--explicit-checkpoint",
        action="store_true",
        help="Treat the current request as an explicit checkpoint-commit ask, even for small worktrees",
    )
    analyze.set_defaults(func=command_analyze)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
