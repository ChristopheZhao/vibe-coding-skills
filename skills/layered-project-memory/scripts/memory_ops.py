#!/usr/bin/env python3
"""Layered project memory operations."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


EVENT_TYPES = {"decision", "experiment", "blocker", "fix", "rollback", "milestone", "note"}
IMPACTS = {"low", "medium", "high"}
RESULTS = {"unknown", "success", "failed", "mixed"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(root: Path, args: List[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git"] + args,
            cwd=str(root),
            check=True,
            text=True,
            capture_output=True,
        )
        return completed.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def detect_git_anchor(root: Path) -> Dict[str, Any]:
    branch = run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    head_sha = run_git(root, ["rev-parse", "HEAD"])
    status_short = run_git(root, ["status", "--short"])
    fingerprint = None
    if status_short is not None:
        normalized = "\n".join(sorted(line.strip() for line in status_short.splitlines() if line.strip()))
        fingerprint = "clean" if not normalized else hashlib.sha1(normalized.encode("utf-8")).hexdigest()
    anchor = {
        "branch": branch,
        "head_sha": head_sha,
        "files_fingerprint": fingerprint,
    }
    if branch is None or head_sha is None:
        anchor["source"] = "non_git"
    return anchor


def get_paths(root: Path) -> Dict[str, Path]:
    base = root / "docs" / "memory"
    return {
        "base": base,
        "index": base / "MEMORY_INDEX.json",
        "state_dir": base / "state",
        "state": base / "state" / "current.json",
        "events_dir": base / "events",
        "events": base / "events" / "events.jsonl",
        "insights_dir": base / "insights",
        "snapshots_dir": base / "snapshots",
    }


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    events: List[Dict[str, Any]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at {path}:{line_no}: {exc}") from exc
    return events


def write_events(path: Path, events: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(event, ensure_ascii=False, sort_keys=True) for event in events]
    content = "\n".join(lines)
    if content:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def ensure_storage(root: Path) -> Dict[str, Path]:
    paths = get_paths(root)
    paths["base"].mkdir(parents=True, exist_ok=True)
    paths["state_dir"].mkdir(parents=True, exist_ok=True)
    paths["events_dir"].mkdir(parents=True, exist_ok=True)
    paths["insights_dir"].mkdir(parents=True, exist_ok=True)
    paths["snapshots_dir"].mkdir(parents=True, exist_ok=True)

    now = utc_now()
    if not paths["index"].exists():
        write_json(
            paths["index"],
            {
                "version": 1,
                "schema_version": "2026-02-26",
                "created_at": now,
                "updated_at": now,
                "event_seq": 0,
                "snapshot_seq": 0,
                "event_count": 0,
                "key_event_count": 0,
                "last_event_id": None,
                "last_snapshot_id": None,
            },
        )

    if not paths["state"].exists():
        anchor = detect_git_anchor(root)
        write_json(
            paths["state"],
            {
                "version": 1,
                "updated_at": now,
                "plan_id": None,
                "topic_id": None,
                "stage": None,
                "goal": None,
                "blockers": [],
                "next_action": None,
                "last_event_id": None,
                "anchors": anchor,
            },
        )

    if not paths["events"].exists():
        paths["events"].write_text("", encoding="utf-8")

    return paths


def require_initialized(root: Path) -> Dict[str, Path]:
    paths = get_paths(root)
    required = [paths["index"], paths["state"], paths["events"]]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise ValueError("memory storage not initialized, run `init` first: " + ", ".join(missing))
    return paths


def next_event_id(index: Dict[str, Any]) -> str:
    seq = int(index.get("event_seq", 0)) + 1
    index["event_seq"] = seq
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"EVT-{stamp}-{seq:04d}"


def next_snapshot_id(index: Dict[str, Any]) -> str:
    seq = int(index.get("snapshot_seq", 0)) + 1
    index["snapshot_seq"] = seq
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"SNAP-{stamp}-{seq:04d}"


def impact_weight(impact: str) -> int:
    return {"low": 1, "medium": 2, "high": 3}[impact]


def type_weight(event_type: str) -> int:
    return {
        "decision": 1,
        "experiment": 1,
        "blocker": 2,
        "fix": 1,
        "rollback": 3,
        "milestone": 2,
        "note": 0,
    }.get(event_type, 0)


def result_weight(result: str) -> int:
    return {"unknown": 0, "success": 0, "failed": 2, "mixed": 1}[result]


def repeat_failure_bonus(events: List[Dict[str, Any]], problem_key: str | None) -> int:
    if not problem_key:
        return 0
    count = 0
    for event in reversed(events):
        if event.get("problem_key") == problem_key and event.get("result") == "failed":
            count += 1
    return min(count, 3)


def score_for_key_event(
    event: Dict[str, Any],
    existing_events: List[Dict[str, Any]],
) -> int:
    score = 0
    score += impact_weight(event["impact"])
    score += type_weight(event["event_type"])
    score += result_weight(event["result"])
    score += repeat_failure_bonus(existing_events, event.get("problem_key"))
    if event.get("evidence"):
        score += 1
    return score


def update_index_stats(index: Dict[str, Any], events: List[Dict[str, Any]]) -> None:
    index["event_count"] = len(events)
    index["key_event_count"] = sum(1 for event in events if event.get("is_key_event"))
    index["updated_at"] = utc_now()


def sanitize_events_for_pack(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    allowed = [
        "id",
        "timestamp",
        "plan_id",
        "topic_id",
        "milestone_id",
        "event_type",
        "summary",
        "impact",
        "priority",
        "result",
        "problem_key",
        "next_action",
        "is_key_event",
        "key_score",
        "doc_refs",
        "evidence",
        "anchors",
        "insight_ref",
    ]
    sanitized: List[Dict[str, Any]] = []
    for event in events:
        sanitized.append({key: event.get(key) for key in allowed if key in event})
    return sanitized


def profile_config(profile: str) -> Dict[str, Any]:
    configs = {
        "resume": {
            "default_limit": 8,
            "event_weights": {
                "milestone": 5,
                "decision": 4,
                "blocker": 4,
                "fix": 3,
                "rollback": 3,
                "experiment": 2,
                "note": 1,
            },
            "result_weights": {"failed": 1, "mixed": 1},
        },
        "debug": {
            "default_limit": 10,
            "event_weights": {
                "blocker": 5,
                "experiment": 5,
                "rollback": 5,
                "fix": 4,
                "decision": 2,
                "milestone": 2,
                "note": 1,
            },
            "result_weights": {"failed": 3, "mixed": 2},
        },
        "release": {
            "default_limit": 6,
            "event_weights": {
                "milestone": 5,
                "decision": 4,
                "fix": 4,
                "rollback": 4,
                "blocker": 3,
                "experiment": 1,
                "note": 1,
            },
            "result_weights": {"failed": 2, "mixed": 2},
        },
    }
    return configs[profile]


def rank_events(
    events: List[Dict[str, Any]],
    profile: str,
    plan_id: str | None,
    topic_id: str | None,
) -> List[Dict[str, Any]]:
    cfg = profile_config(profile)
    total = len(events)
    ranked: List[Tuple[float, int, Dict[str, Any]]] = []
    for idx, event in enumerate(events):
        score = 0.0
        score += event.get("key_score", 0) * 2
        if event.get("is_key_event"):
            score += 6
        score += impact_weight(event.get("impact", "low"))
        score += cfg["event_weights"].get(event.get("event_type"), 0)
        score += cfg["result_weights"].get(event.get("result"), 0)
        if plan_id and event.get("plan_id") == plan_id:
            score += 8
        if topic_id and event.get("topic_id") == topic_id:
            score += 6
        recency_bonus = ((idx + 1) / max(total, 1)) * 5
        score += recency_bonus
        ranked.append((score, idx, event))
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in ranked]


def read_insights(root: Path, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    insight_payloads: List[Dict[str, Any]] = []
    for event in events:
        ref = event.get("insight_ref")
        if not ref:
            continue
        path = root / ref
        if path.exists():
            try:
                insight_payloads.append(read_json(path))
            except json.JSONDecodeError:
                continue
    return insight_payloads


def event_matches_scope(event: Dict[str, Any], plan_id: str | None, topic_id: str | None) -> bool:
    if plan_id is not None and event.get("plan_id") != plan_id:
        return False
    if topic_id is not None and event.get("topic_id") != topic_id:
        return False
    return True


def update_state_after_capture(
    state: Dict[str, Any],
    event: Dict[str, Any],
    args: argparse.Namespace,
) -> None:
    state["updated_at"] = event["timestamp"]
    if args.plan_id is not None:
        state["plan_id"] = args.plan_id
    if args.topic_id is not None:
        state["topic_id"] = args.topic_id
    state["last_event_id"] = event["id"]
    if args.stage:
        state["stage"] = args.stage
    if args.goal:
        state["goal"] = args.goal
    if args.next_action:
        state["next_action"] = args.next_action
    if args.clear_blockers:
        state["blockers"] = []
    if args.blocker:
        blockers = list(state.get("blockers", []))
        for blocker in args.blocker:
            if blocker not in blockers:
                blockers.append(blocker)
        state["blockers"] = blockers
    state["anchors"] = event["anchors"]


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Layered project memory operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize memory storage")
    init_parser.add_argument("--root", default=".", help="Repository root (default: .)")

    capture = subparsers.add_parser("capture", help="Capture an L2 event and optional L3 insight")
    capture.add_argument("--root", default=".", help="Repository root (default: .)")
    capture.add_argument("--plan-id", help="Optional plan ID linkage")
    capture.add_argument("--topic-id", help="Optional topic scope when no plan is used")
    capture.add_argument("--event-type", required=True, choices=sorted(EVENT_TYPES))
    capture.add_argument("--summary", required=True, help="High-signal event summary")
    capture.add_argument("--milestone-id", help="Optional milestone ID")
    capture.add_argument("--impact", choices=sorted(IMPACTS), default="medium")
    capture.add_argument("--priority", choices=["P0", "P1", "P2"], default="P1")
    capture.add_argument("--result", choices=sorted(RESULTS), default="unknown")
    capture.add_argument("--problem-key", help="Stable problem fingerprint")
    capture.add_argument("--stage", help="Current project stage for L1")
    capture.add_argument("--goal", help="Current project goal for L1")
    capture.add_argument("--next-action", help="Recommended next action")
    capture.add_argument("--blocker", action="append", help="Blocker item to append")
    capture.add_argument("--clear-blockers", action="store_true", help="Clear blocker list in L1")
    capture.add_argument("--evidence", action="append", default=[], help="Evidence path or reference")
    capture.add_argument(
        "--doc-ref",
        action="append",
        default=[],
        help="Pointer to key document section/path, e.g. docs/adr/0003.md#decision",
    )
    capture.add_argument("--hypothesis", help="L3 hypothesis")
    capture.add_argument("--attempt", help="L3 attempt description")
    capture.add_argument("--outcome", help="L3 outcome summary")
    capture.add_argument("--lesson", help="L3 lesson")
    capture.add_argument("--branch", help="Override Git branch anchor")
    capture.add_argument("--head-sha", help="Override Git HEAD SHA anchor")
    capture.add_argument("--base-sha", help="Optional base SHA anchor")
    capture.add_argument("--created-by", default="codex", help="Recorder identity")
    capture.add_argument("--force-key", action="store_true", help="Force key-event promotion")
    capture.add_argument("--promote-threshold", type=int, default=6)
    capture.add_argument("--json", action="store_true", help="Print created event as JSON")

    promote = subparsers.add_parser("promote", help="Promote an existing event to key event")
    promote.add_argument("--root", default=".", help="Repository root (default: .)")
    promote.add_argument("--event-id", required=True, help="Event ID to promote")
    promote.add_argument("--reason", required=True, help="Promotion reason")

    snapshot = subparsers.add_parser("snapshot", help="Create a snapshot from current memory state")
    snapshot.add_argument("--root", default=".", help="Repository root (default: .)")
    snapshot.add_argument("--plan-id", help="Plan scope for snapshot")
    snapshot.add_argument("--topic-id", help="Topic scope for snapshot")
    snapshot.add_argument("--title", default="Memory snapshot")
    snapshot.add_argument("--summary", default="")
    snapshot.add_argument("--profile", choices=["resume", "debug", "release"], default="resume")
    snapshot.add_argument("--top-k", type=int, default=8)
    snapshot.add_argument("--next-action", help="Override next action in snapshot")

    retrieve = subparsers.add_parser("retrieve", help="Retrieve context pack from layered memory")
    retrieve.add_argument("--root", default=".", help="Repository root (default: .)")
    retrieve.add_argument("--profile", required=True, choices=["resume", "debug", "release"])
    retrieve.add_argument("--plan-id", help="Plan scope")
    retrieve.add_argument("--topic-id", help="Topic scope")
    retrieve.add_argument("--limit", type=int, help="Override profile default limit")
    retrieve.add_argument("--format", choices=["json", "markdown"], default="json")

    doctor = subparsers.add_parser("doctor", help="Check storage consistency and schema integrity")
    doctor.add_argument("--root", default=".", help="Repository root (default: .)")
    doctor.add_argument("--json", action="store_true", help="Print report as JSON")

    gc = subparsers.add_parser("gc", help="Apply retention policy and compact memory records")
    gc.add_argument("--root", default=".", help="Repository root (default: .)")
    gc.add_argument("--retain-events", type=int, default=200, help="Keep latest N events")
    gc.add_argument("--retain-key-events", type=int, default=100, help="Keep latest N key events")
    gc.add_argument("--retain-snapshots", type=int, default=50, help="Keep latest N snapshots")
    gc.add_argument("--dry-run", action="store_true", help="Preview GC result without file changes")
    gc.add_argument("--json", action="store_true", help="Print GC report as JSON")

    return parser


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_storage(root)
    print(f"initialized: {paths['base']}")
    print(f"index: {paths['index']}")
    return 0


def cmd_capture(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_storage(root)
    index = read_json(paths["index"])
    state = read_json(paths["state"])
    events = read_events(paths["events"])

    now = utc_now()
    event_id = next_event_id(index)
    auto_anchor = detect_git_anchor(root)
    anchors = {
        "branch": args.branch or auto_anchor.get("branch"),
        "head_sha": args.head_sha or auto_anchor.get("head_sha"),
        "base_sha": args.base_sha,
        "files_fingerprint": auto_anchor.get("files_fingerprint"),
        "source": auto_anchor.get("source", "git"),
    }
    if anchors["branch"] and anchors["head_sha"]:
        anchors["source"] = "git"

    event: Dict[str, Any] = {
        "id": event_id,
        "timestamp": now,
        "plan_id": args.plan_id,
        "topic_id": args.topic_id,
        "milestone_id": args.milestone_id,
        "event_type": args.event_type,
        "summary": args.summary,
        "impact": args.impact,
        "priority": args.priority,
        "result": args.result,
        "problem_key": args.problem_key,
        "next_action": args.next_action,
        "doc_refs": args.doc_ref,
        "evidence": args.evidence,
        "anchors": anchors,
        "created_by": args.created_by,
        "is_key_event": False,
        "key_score": 0,
    }

    if any([args.hypothesis, args.attempt, args.outcome, args.lesson, args.next_action]):
        insight_path = paths["insights_dir"] / f"{event_id}.json"
        insight_payload = {
            "id": f"INS-{event_id}",
            "event_id": event_id,
            "timestamp": now,
            "hypothesis": args.hypothesis,
            "attempt": args.attempt,
            "outcome": args.outcome,
            "lesson": args.lesson,
            "next_action": args.next_action,
            "doc_refs": args.doc_ref,
            "evidence": args.evidence,
        }
        write_json(insight_path, insight_payload)
        event["insight_ref"] = str(insight_path.relative_to(root))

    event["key_score"] = score_for_key_event(event, events)
    if args.force_key or event["key_score"] >= args.promote_threshold:
        event["is_key_event"] = True
        event["promoted_at"] = now
        event["promotion_reason"] = "force-key" if args.force_key else "score-threshold"
    if event["is_key_event"] and not (event.get("plan_id") or event.get("topic_id")):
        # Keep capture non-blocking in no-scope mode while enforcing scope on key-event promotion.
        event["is_key_event"] = False
        event["promotion_reason"] = "scope-missing-demoted"

    events.append(event)
    write_events(paths["events"], events)

    update_state_after_capture(state, event, args)
    write_json(paths["state"], state)

    index["last_event_id"] = event_id
    update_index_stats(index, events)
    write_json(paths["index"], index)

    if args.json:
        print(json.dumps(event, indent=2, ensure_ascii=False))
    else:
        print(f"captured: {event_id}")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = require_initialized(root)
    index = read_json(paths["index"])
    events = read_events(paths["events"])

    target = None
    for event in events:
        if event.get("id") == args.event_id:
            target = event
            break
    if target is None:
        print(f"error: event not found: {args.event_id}", file=sys.stderr)
        return 1

    target["is_key_event"] = True
    target["promoted_at"] = utc_now()
    target["promotion_reason"] = args.reason
    if target.get("key_score", 0) < 1:
        target["key_score"] = 1

    write_events(paths["events"], events)
    update_index_stats(index, events)
    index["last_event_id"] = target.get("id")
    write_json(paths["index"], index)
    print(f"promoted: {args.event_id}")
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = require_initialized(root)
    index = read_json(paths["index"])
    state = read_json(paths["state"])
    events = read_events(paths["events"])

    plan_id = args.plan_id if args.plan_id is not None else state.get("plan_id")
    topic_id = args.topic_id if args.topic_id is not None else state.get("topic_id")
    scoped = [event for event in events if event_matches_scope(event, plan_id, topic_id)]
    ranked = rank_events(scoped if scoped else events, args.profile, plan_id, topic_id)
    selected = ranked[: max(args.top_k, 1)]

    now = utc_now()
    snapshot_id = next_snapshot_id(index)
    payload = {
        "id": snapshot_id,
        "timestamp": now,
        "title": args.title,
        "summary": args.summary,
        "profile": args.profile,
        "plan_id": plan_id,
        "topic_id": topic_id,
        "state": state,
        "selected_event_ids": [event.get("id") for event in selected],
        "next_action": args.next_action or state.get("next_action"),
    }
    snapshot_path = paths["snapshots_dir"] / f"{snapshot_id}.json"
    write_json(snapshot_path, payload)

    index["last_snapshot_id"] = snapshot_id
    index["updated_at"] = now
    write_json(paths["index"], index)
    print(f"snapshot: {snapshot_path}")
    return 0


def build_pack(
    root: Path,
    state: Dict[str, Any],
    events: List[Dict[str, Any]],
    profile: str,
    plan_id: str | None,
    topic_id: str | None,
    limit: int,
) -> Dict[str, Any]:
    scoped = [event for event in events if event_matches_scope(event, plan_id, topic_id)]
    ranked = rank_events(scoped if scoped else events, profile, plan_id, topic_id)

    selected = ranked[:limit]
    fallback_used = False
    if not selected:
        fallback_used = True
        selected = [event for event in reversed(events) if event.get("is_key_event")][:limit]
        if not selected:
            selected = list(reversed(events))[: min(limit, 3)]

    if not selected and (state.get("plan_id") or state.get("topic_id") or state.get("next_action")):
        fallback_used = True

    selected = sanitize_events_for_pack(selected)
    insights = read_insights(root, selected)

    next_actions: List[str] = []
    if state.get("next_action"):
        next_actions.append(state["next_action"])
    for event in selected:
        action = event.get("next_action")
        if action and action not in next_actions:
            next_actions.append(action)

    pack = {
        "profile": profile,
        "generated_at": utc_now(),
        "plan_id": plan_id or state.get("plan_id"),
        "topic_id": topic_id or state.get("topic_id"),
        "fallback_used": fallback_used,
        "state": state,
        "events": selected,
        "insights": insights,
        "next_actions": next_actions,
        "contract": {
            "ordering": "score_desc_then_recency_desc",
            "max_events": limit,
            "fields": [
                "profile",
                "generated_at",
                "plan_id",
                "topic_id",
                "fallback_used",
                "state",
                "events",
                "insights",
                "next_actions",
                "contract",
            ],
        },
    }
    return pack


def render_markdown(pack: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Memory Pack ({pack['profile']})")
    lines.append(f"- Generated At: {pack['generated_at']}")
    lines.append(f"- Plan ID: {pack.get('plan_id')}")
    lines.append(f"- Topic ID: {pack.get('topic_id')}")
    lines.append(f"- Fallback Used: {str(pack.get('fallback_used')).lower()}")
    lines.append("")
    lines.append("## State")
    state = pack.get("state", {})
    lines.append(f"- Stage: {state.get('stage')}")
    lines.append(f"- Goal: {state.get('goal')}")
    lines.append(f"- Next Action: {state.get('next_action')}")
    blockers = state.get("blockers", [])
    lines.append(f"- Blockers: {', '.join(blockers) if blockers else '(none)'}")
    lines.append("")
    lines.append("## Events")
    events = pack.get("events", [])
    if not events:
        lines.append("- (no event)")
    for event in events:
        lines.append(
            "- [{id}] {etype} | {impact} | key={is_key} | {summary}".format(
                id=event.get("id"),
                etype=event.get("event_type"),
                impact=event.get("impact"),
                is_key=str(event.get("is_key_event")).lower(),
                summary=event.get("summary"),
            )
        )
    lines.append("")
    lines.append("## Next Actions")
    next_actions = pack.get("next_actions", [])
    if not next_actions:
        lines.append("- (none)")
    for action in next_actions:
        lines.append(f"- {action}")
    return "\n".join(lines) + "\n"


def cmd_retrieve(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = require_initialized(root)
    state = read_json(paths["state"])
    events = read_events(paths["events"])

    cfg = profile_config(args.profile)
    limit = args.limit if args.limit is not None else cfg["default_limit"]
    limit = max(limit, 1)
    plan_id = args.plan_id if args.plan_id is not None else state.get("plan_id")
    topic_id = args.topic_id if args.topic_id is not None else state.get("topic_id")
    pack = build_pack(root, state, events, args.profile, plan_id, topic_id, limit)

    if args.format == "json":
        print(json.dumps(pack, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(pack), end="")
    return 0


def validate_event_schema(event: Dict[str, Any], root: Path) -> List[str]:
    issues: List[str] = []
    required = [
        "id",
        "timestamp",
        "event_type",
        "summary",
        "impact",
        "result",
        "is_key_event",
        "key_score",
        "anchors",
    ]
    for field in required:
        if field not in event:
            issues.append(f"{event.get('id', '<unknown>')}: missing field `{field}`")
    if event.get("event_type") and event.get("event_type") not in EVENT_TYPES:
        issues.append(f"{event.get('id', '<unknown>')}: invalid event_type `{event.get('event_type')}`")
    if event.get("impact") and event.get("impact") not in IMPACTS:
        issues.append(f"{event.get('id', '<unknown>')}: invalid impact `{event.get('impact')}`")
    if event.get("result") and event.get("result") not in RESULTS:
        issues.append(f"{event.get('id', '<unknown>')}: invalid result `{event.get('result')}`")

    evidence = event.get("evidence")
    if evidence is not None and not isinstance(evidence, list):
        issues.append(f"{event.get('id', '<unknown>')}: evidence must be a list")

    doc_refs = event.get("doc_refs")
    if doc_refs is not None and not isinstance(doc_refs, list):
        issues.append(f"{event.get('id', '<unknown>')}: doc_refs must be a list")

    if event.get("is_key_event") and not (event.get("plan_id") or event.get("topic_id")):
        issues.append(f"{event.get('id', '<unknown>')}: key event missing scope (`plan_id` or `topic_id`)")
    if event.get("is_key_event") and not (evidence or doc_refs):
        issues.append(f"{event.get('id', '<unknown>')}: key event missing pointer (`evidence` or `doc_refs`)")

    anchors = event.get("anchors")
    if isinstance(anchors, dict):
        source = anchors.get("source", "git")
        if source == "git":
            if not anchors.get("branch"):
                issues.append(f"{event.get('id', '<unknown>')}: missing anchors.branch for git source")
            if not anchors.get("head_sha"):
                issues.append(f"{event.get('id', '<unknown>')}: missing anchors.head_sha for git source")
    else:
        issues.append(f"{event.get('id', '<unknown>')}: anchors must be object")

    insight_ref = event.get("insight_ref")
    if insight_ref:
        insight_path = root / insight_ref
        if not insight_path.exists():
            issues.append(f"{event.get('id', '<unknown>')}: missing insight_ref file `{insight_ref}`")
    return issues


def list_snapshot_files(paths: Dict[str, Path]) -> List[Path]:
    return sorted(paths["snapshots_dir"].glob("SNAP-*.json"))


def parse_snapshot(path: Path) -> Dict[str, Any] | None:
    try:
        return read_json(path)
    except Exception:  # noqa: BLE001
        return None


def event_id_set(events: List[Dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for event in events:
        event_id = event.get("id")
        if isinstance(event_id, str):
            ids.add(event_id)
    return ids


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = get_paths(root)
    issues: List[str] = []

    required_dirs = [paths["base"], paths["state_dir"], paths["events_dir"], paths["insights_dir"], paths["snapshots_dir"]]
    for directory in required_dirs:
        if not directory.exists():
            issues.append(f"missing directory: {directory}")
    required_files = [paths["index"], paths["state"], paths["events"]]
    for path in required_files:
        if not path.exists():
            issues.append(f"missing file: {path}")

    index: Dict[str, Any] | None = None
    state: Dict[str, Any] | None = None
    events: List[Dict[str, Any]] = []

    if paths["index"].exists():
        try:
            index = read_json(paths["index"])
        except Exception as exc:  # noqa: BLE001
            issues.append(f"invalid index JSON: {exc}")
    if paths["state"].exists():
        try:
            state = read_json(paths["state"])
        except Exception as exc:  # noqa: BLE001
            issues.append(f"invalid state JSON: {exc}")
    if paths["events"].exists():
        try:
            events = read_events(paths["events"])
        except Exception as exc:  # noqa: BLE001
            issues.append(f"invalid events JSONL: {exc}")

    if index is not None:
        if index.get("event_count") != len(events):
            issues.append(
                "index event_count mismatch: index={idx} actual={actual}".format(
                    idx=index.get("event_count"),
                    actual=len(events),
                )
            )
        key_count = sum(1 for event in events if event.get("is_key_event"))
        if index.get("key_event_count") != key_count:
            issues.append(
                "index key_event_count mismatch: index={idx} actual={actual}".format(
                    idx=index.get("key_event_count"),
                    actual=key_count,
                )
            )
        last_event_id = index.get("last_event_id")
        if last_event_id and all(event.get("id") != last_event_id for event in events):
            issues.append(f"index last_event_id not found in events: {last_event_id}")

    seen_ids = set()
    for event in events:
        event_id = event.get("id")
        if event_id in seen_ids:
            issues.append(f"duplicate event id: {event_id}")
        else:
            seen_ids.add(event_id)
        issues.extend(validate_event_schema(event, root))

    if state is not None:
        if "anchors" not in state or not isinstance(state.get("anchors"), dict):
            issues.append("state missing valid anchors object")
        state_last = state.get("last_event_id")
        if state_last and state_last not in seen_ids:
            issues.append(f"state last_event_id not found in events: {state_last}")

    snapshot_files = list_snapshot_files(paths)
    if index is not None:
        last_snapshot_id = index.get("last_snapshot_id")
        if last_snapshot_id and not (paths["snapshots_dir"] / f"{last_snapshot_id}.json").exists():
            issues.append(f"index last_snapshot_id file missing: {last_snapshot_id}")

    known_ids = event_id_set(events)
    for snapshot_file in snapshot_files:
        payload = parse_snapshot(snapshot_file)
        if payload is None:
            issues.append(f"invalid snapshot JSON: {snapshot_file}")
            continue
        selected = payload.get("selected_event_ids", [])
        if isinstance(selected, list):
            for event_id in selected:
                if isinstance(event_id, str) and event_id not in known_ids:
                    issues.append(f"snapshot references missing event id: {snapshot_file.name}:{event_id}")

    referenced_insights: set[str] = set()
    for event in events:
        insight_ref = event.get("insight_ref")
        if isinstance(insight_ref, str):
            referenced_insights.add(insight_ref)
    for insight_path in paths["insights_dir"].glob("*.json"):
        rel = str(insight_path.relative_to(root))
        if rel not in referenced_insights:
            issues.append(f"orphan insight file: {rel}")

    report = {
        "root": str(root),
        "issue_count": len(issues),
        "issues": issues,
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        if issues:
            for issue in issues:
                print(f"issue: {issue}")
        print(f"issues: {len(issues)}")

    return 1 if issues else 0


def cmd_gc(args: argparse.Namespace) -> int:
    if args.retain_events < 0 or args.retain_key_events < 0 or args.retain_snapshots < 0:
        print("error: retention values must be non-negative", file=sys.stderr)
        return 1

    root = Path(args.root).resolve()
    paths = require_initialized(root)
    index = read_json(paths["index"])
    state = read_json(paths["state"])
    events = read_events(paths["events"])

    original_event_count = len(events)
    original_key_count = sum(1 for event in events if event.get("is_key_event"))

    keep_ids: set[str] = set()
    if args.retain_events > 0:
        keep_ids.update(
            event.get("id")
            for event in events[-args.retain_events :]
            if isinstance(event.get("id"), str)
        )
    if args.retain_key_events > 0:
        key_events = [event for event in events if event.get("is_key_event")]
        keep_ids.update(
            event.get("id")
            for event in key_events[-args.retain_key_events :]
            if isinstance(event.get("id"), str)
        )
    for pinned in [state.get("last_event_id"), index.get("last_event_id")]:
        if isinstance(pinned, str):
            keep_ids.add(pinned)

    snapshot_files = list_snapshot_files(paths)
    if args.retain_snapshots == 0:
        keep_snapshot_files: List[Path] = []
    else:
        keep_snapshot_files = snapshot_files[-args.retain_snapshots :]

    for snapshot_file in keep_snapshot_files:
        payload = parse_snapshot(snapshot_file)
        if not payload:
            continue
        selected = payload.get("selected_event_ids", [])
        if isinstance(selected, list):
            for event_id in selected:
                if isinstance(event_id, str):
                    keep_ids.add(event_id)

    retained_events = [event for event in events if event.get("id") in keep_ids]
    removed_events = [event for event in events if event.get("id") not in keep_ids]

    kept_snapshot_names = {path.name for path in keep_snapshot_files}
    removed_snapshots = [path for path in snapshot_files if path.name not in kept_snapshot_names]

    retained_insight_refs: set[str] = set()
    for event in retained_events:
        insight_ref = event.get("insight_ref")
        if isinstance(insight_ref, str):
            retained_insight_refs.add(insight_ref)
    all_insights = list(paths["insights_dir"].glob("*.json"))
    removed_insights = [
        path
        for path in all_insights
        if str(path.relative_to(root)) not in retained_insight_refs
    ]

    latest_event_id = retained_events[-1]["id"] if retained_events else None
    state_last_event = state.get("last_event_id")
    if state_last_event and state_last_event not in event_id_set(retained_events):
        state["last_event_id"] = latest_event_id
    if index.get("last_event_id") and index.get("last_event_id") not in event_id_set(retained_events):
        index["last_event_id"] = latest_event_id

    last_snapshot_id = index.get("last_snapshot_id")
    if isinstance(last_snapshot_id, str) and f"{last_snapshot_id}.json" not in kept_snapshot_names:
        index["last_snapshot_id"] = None

    update_index_stats(index, retained_events)

    report = {
        "root": str(root),
        "dry_run": bool(args.dry_run),
        "events_before": original_event_count,
        "events_after": len(retained_events),
        "events_removed": len(removed_events),
        "key_events_before": original_key_count,
        "key_events_after": sum(1 for event in retained_events if event.get("is_key_event")),
        "snapshots_before": len(snapshot_files),
        "snapshots_after": len(keep_snapshot_files),
        "snapshots_removed": len(removed_snapshots),
        "insights_before": len(all_insights),
        "insights_after": len(all_insights) - len(removed_insights),
        "insights_removed": len(removed_insights),
    }

    if not args.dry_run:
        write_events(paths["events"], retained_events)
        write_json(paths["state"], state)
        write_json(paths["index"], index)
        for snapshot_path in removed_snapshots:
            snapshot_path.unlink(missing_ok=True)
        for insight_path in removed_insights:
            insight_path.unlink(missing_ok=True)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            "gc: events {before}->{after}, snapshots {sbefore}->{safter}, insights {ibefore}->{iafter}".format(
                before=report["events_before"],
                after=report["events_after"],
                sbefore=report["snapshots_before"],
                safter=report["snapshots_after"],
                ibefore=report["insights_before"],
                iafter=report["insights_after"],
            )
        )
    return 0


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    try:
        if args.command == "init":
            return cmd_init(args)
        if args.command == "capture":
            return cmd_capture(args)
        if args.command == "promote":
            return cmd_promote(args)
        if args.command == "snapshot":
            return cmd_snapshot(args)
        if args.command == "retrieve":
            return cmd_retrieve(args)
        if args.command == "doctor":
            return cmd_doctor(args)
        if args.command == "gc":
            return cmd_gc(args)
        parser.error(f"unknown command: {args.command}")
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
