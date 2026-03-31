#!/usr/bin/env python3
"""Deterministic deferred-plan operations and planning resolution."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NoReturn


ROOT_REL = Path("docs/deferred-plans")
INDEX_REL = ROOT_REL / "DEFERRED_PLAN_INDEX.json"
CURRENT_REL = ROOT_REL / "CURRENT.md"
ACTIVE_REL = ROOT_REL / "active"
ARCHIVE_REL = ROOT_REL / "archive"


def fail(message: str) -> NoReturn:
    raise SystemExit(message)


def repo_root(value: str) -> Path:
    return Path(value).resolve()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def utc_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    items: list[str] = []
    seen: set[str] = set()
    for raw in value.split(","):
        item = raw.strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(item)
    return items


def dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = item.strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(text)
    return result


def ensure_layout(root: Path) -> None:
    (root / ACTIVE_REL).mkdir(parents=True, exist_ok=True)
    (root / ARCHIVE_REL).mkdir(parents=True, exist_ok=True)
    index_path = root / INDEX_REL
    if not index_path.exists():
        write_index(root, {"version": 1, "plans": []})
    current_path = root / CURRENT_REL
    if not current_path.exists():
        current_path.write_text(render_no_active_current(), encoding="utf-8")


def is_enabled(root: Path) -> bool:
    return (root / INDEX_REL).exists()


def load_index(root: Path, create: bool = False) -> dict[str, Any]:
    if create:
        ensure_layout(root)
    index_path = root / INDEX_REL
    if not index_path.exists():
        fail(f"deferred-plan root not enabled: {root / ROOT_REL}")
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid deferred-plan index JSON: {exc}")
    if not isinstance(payload, dict) or not isinstance(payload.get("plans"), list):
        fail("invalid deferred-plan index structure")
    payload.setdefault("version", 1)
    return payload


def write_index(root: Path, payload: dict[str, Any]) -> None:
    (root / INDEX_REL).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def find_item(index: dict[str, Any], plan_id: str) -> tuple[int, dict[str, Any]]:
    for pos, item in enumerate(index.get("plans", [])):
        if item.get("id") == plan_id:
            return pos, item
    fail(f"deferred plan not found: {plan_id}")


def active_items(index: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in index.get("plans", []) if item.get("status") == "active"]


def ensure_single_active(index: dict[str, Any], except_id: str | None = None) -> None:
    others = [
        item["id"]
        for item in active_items(index)
        if except_id is None or item.get("id") != except_id
    ]
    if others:
        fail("another deferred plan is already active: " + ", ".join(others))


def markdown_list(items: list[str], none_text: str = "none") -> str:
    if not items:
        return f"- {none_text}\n"
    return "".join(f"- {item}\n" for item in items)


def render_doc(item: dict[str, Any]) -> str:
    lines = [
        f"# Deferred Plan: {item['title']}",
        f"- Deferred Plan ID: {item['id']}",
        f"- Status: {item['status']}",
        f"- Owner: {item['owner']}",
        f"- Created At: {item['created_at']}",
        f"- Updated At: {item['updated_at']}",
    ]
    optional_scalars = [
        ("Activated At", item.get("activated_at")),
        ("Completed At", item.get("completed_at")),
        ("Archived At", item.get("archived_at")),
        ("Review After", item.get("review_after")),
        ("Supersedes", item.get("supersedes")),
        ("Superseded By", item.get("superseded_by")),
    ]
    for label, value in optional_scalars:
        if value:
            lines.append(f"- {label}: {value}")
    lines.extend(
        [
            f"- Scope Tags: {', '.join(item.get('scope_tags', [])) or 'none'}",
            f"- Topic Tags: {', '.join(item.get('topic_tags', [])) or 'none'}",
            f"- Plan Kinds: {', '.join(item.get('plan_kinds', [])) or 'none'}",
            "",
            "## Goal",
            markdown_list([item.get("goal", "none")]).rstrip(),
            "",
            "## Why Not Now",
            markdown_list([item.get("why_not_now", "none")]).rstrip(),
            "",
            "## Current Deviation",
            markdown_list([item.get("current_deviation", "none")]).rstrip(),
            "",
            "## Do Not",
            markdown_list(item.get("do_not", []), none_text="none").rstrip(),
            "",
            "## Allowed Now",
            markdown_list(item.get("allowed_now", []), none_text="none").rstrip(),
            "",
            "## Reopen Trigger",
            markdown_list(item.get("reopen_trigger", []), none_text="none").rstrip(),
            "",
            "## Evidence Refs",
            markdown_list(item.get("evidence_refs", []), none_text="none").rstrip(),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_no_active_current() -> str:
    return "# Current Deferred Plan\n\n- No active deferred plan.\n"


def render_current_for_item(item: dict[str, Any]) -> str:
    lines = [
        "# Current Deferred Plan",
        "",
        f"- Deferred Plan ID: {item['id']}",
        f"- Title: {item['title']}",
        f"- Status: {item['status']}",
        f"- Scope Tags: {', '.join(item.get('scope_tags', [])) or 'none'}",
        f"- Topic Tags: {', '.join(item.get('topic_tags', [])) or 'none'}",
        f"- Plan Kinds: {', '.join(item.get('plan_kinds', [])) or 'none'}",
        "",
        "## Goal",
        markdown_list([item.get("goal", "none")]).rstrip(),
        "",
        "## Why Not Now",
        markdown_list([item.get("why_not_now", "none")]).rstrip(),
        "",
        "## Do Not",
        markdown_list(item.get("do_not", []), none_text="none").rstrip(),
        "",
        "## Allowed Now",
        markdown_list(item.get("allowed_now", []), none_text="none").rstrip(),
        "",
        "## Reopen Trigger",
        markdown_list(item.get("reopen_trigger", []), none_text="none").rstrip(),
        "",
        "## Source",
        f"- {item['file_path']}",
        "",
    ]
    return "\n".join(lines)


def sync_current(root: Path, index: dict[str, Any]) -> None:
    current_path = root / CURRENT_REL
    actives = active_items(index)
    if len(actives) == 1:
        current_path.write_text(render_current_for_item(actives[0]), encoding="utf-8")
        return
    if len(actives) > 1:
        ids = ", ".join(item["id"] for item in actives)
        current_path.write_text(
            "# Current Deferred Plan\n\n"
            "- Invalid state: multiple active deferred plans detected.\n"
            f"- Active IDs: {ids}\n",
            encoding="utf-8",
        )
        return
    current_path.write_text(render_no_active_current(), encoding="utf-8")


def write_doc(root: Path, item: dict[str, Any]) -> None:
    target = root / item["file_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_doc(item), encoding="utf-8")


def status_json(root: Path, item: dict[str, Any]) -> dict[str, Any]:
    payload = dict(item)
    payload["source"] = str(root / item["file_path"])
    return payload


def item_is_stale(item: dict[str, Any]) -> bool:
    review_after = item.get("review_after")
    if not review_after:
        return False
    return utc_date() > review_after


def tag_match(requested: list[str], owned: list[str]) -> bool:
    if not owned:
        return True
    if not requested:
        return False
    owned_lower = {value.lower() for value in owned}
    return any(value.lower() in owned_lower for value in requested)


def plan_kind_match(requested: str | None, owned: list[str]) -> bool:
    if not owned:
        return True
    if not requested:
        return False
    return requested.lower() in {value.lower() for value in owned}


def noop_payload(reason: str, enabled: bool = False) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "active": False,
        "applies": False,
        "stale": False,
        "deferred_plan_id": None,
        "title": None,
        "goal": None,
        "do_not": [],
        "allowed_now": [],
        "reopen_trigger": [],
        "source": None,
        "reason": reason,
    }


def print_payload(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    for key, value in payload.items():
        if isinstance(value, list):
            print(f"{key}: {', '.join(value) if value else '[]'}")
        else:
            print(f"{key}: {value}")


def cmd_ensure(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    ensure_layout(root)
    index = load_index(root)
    sync_current(root, index)
    print(f"ensured: {root / ROOT_REL}")


def build_item(args: argparse.Namespace) -> dict[str, Any]:
    now = utc_now()
    return {
        "id": args.id,
        "title": args.title,
        "status": "draft",
        "owner": args.owner,
        "file_path": str(ACTIVE_REL / f"{args.id}.md"),
        "scope_tags": parse_csv(args.scope_tags),
        "topic_tags": parse_csv(args.topic_tags),
        "plan_kinds": parse_csv(args.plan_kinds),
        "goal": args.goal,
        "why_not_now": args.why_not_now,
        "current_deviation": args.current_deviation,
        "do_not": dedupe(args.do_not or []),
        "allowed_now": dedupe(args.allowed_now or []),
        "reopen_trigger": dedupe(args.reopen_trigger or []),
        "evidence_refs": dedupe(args.evidence_ref or []),
        "review_after": args.review_after,
        "supersedes": args.supersedes,
        "superseded_by": None,
        "created_at": now,
        "updated_at": now,
        "activated_at": None,
        "completed_at": None,
        "archived_at": None,
    }


def cmd_create(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    ensure_layout(root)
    index = load_index(root)
    for item in index["plans"]:
        if item.get("id") == args.id:
            fail(f"deferred plan already exists: {args.id}")
    item = build_item(args)
    if args.activate:
        ensure_single_active(index)
        item["status"] = "active"
        item["activated_at"] = utc_now()
        item["updated_at"] = item["activated_at"]
    index["plans"].append(item)
    write_doc(root, item)
    write_index(root, index)
    sync_current(root, index)
    print(f"created: {args.id} -> {item['status']}")


def cmd_status(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    if not is_enabled(root):
        print_payload(noop_payload("deferred-plan root not enabled"), args.json)
        return
    index = load_index(root)
    if args.id:
        _, item = find_item(index, args.id)
        print_payload(status_json(root, item), args.json)
        return
    payload = {"plans": index["plans"]}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for item in index["plans"]:
            print(f"{item['id']}: {item['status']} -> {item['title']}")


def cmd_activate(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    index = load_index(root, create=True)
    pos, item = find_item(index, args.id)
    if item["status"] == "archived":
        fail("cannot activate an archived deferred plan")
    if item["status"] == "active":
        print(f"already active: {args.id}")
        return
    ensure_single_active(index, except_id=args.id)
    now = utc_now()
    item["status"] = "active"
    item["updated_at"] = now
    item["activated_at"] = now
    index["plans"][pos] = item
    write_doc(root, item)
    write_index(root, index)
    sync_current(root, index)
    print(f"activated: {args.id}")


def cmd_supersede(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    index = load_index(root)
    pos, item = find_item(index, args.id)
    if item["status"] != "active":
        fail("only an active deferred plan can be superseded")
    item["status"] = "superseded"
    item["superseded_by"] = args.superseded_by
    item["updated_at"] = utc_now()
    index["plans"][pos] = item
    write_doc(root, item)
    write_index(root, index)
    sync_current(root, index)
    print(f"superseded: {args.id}")


def cmd_complete(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    index = load_index(root)
    pos, item = find_item(index, args.id)
    if item["status"] != "active":
        fail("only an active deferred plan can be completed")
    now = utc_now()
    item["status"] = "completed"
    item["updated_at"] = now
    item["completed_at"] = now
    index["plans"][pos] = item
    write_doc(root, item)
    write_index(root, index)
    sync_current(root, index)
    print(f"completed: {args.id}")


def cmd_archive(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    index = load_index(root)
    pos, item = find_item(index, args.id)
    if item["status"] not in {"completed", "superseded"}:
        fail("archive requires deferred plan status completed or superseded")
    month = utc_month()
    archived_rel = ARCHIVE_REL / month / f"{args.id}.md"
    old_path = root / item["file_path"]
    item["status"] = "archived"
    item["file_path"] = str(archived_rel)
    item["archived_at"] = utc_now()
    item["updated_at"] = item["archived_at"]
    index["plans"][pos] = item
    write_doc(root, item)
    if old_path.exists() and old_path.resolve() != (root / archived_rel).resolve():
        old_path.unlink()
    write_index(root, index)
    sync_current(root, index)
    print(f"archived: {args.id}")


def cmd_sync_current(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    index = load_index(root, create=True)
    sync_current(root, index)
    print(f"synced: {root / CURRENT_REL}")


def cmd_resolve_for_planning(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    if not is_enabled(root):
        print_payload(noop_payload("deferred-plan root not enabled"), args.json)
        return
    index = load_index(root)
    actives = active_items(index)
    if len(actives) != 1:
        reason = "no active deferred plan" if not actives else "multiple active deferred plans detected"
        print_payload(noop_payload(reason, enabled=True), args.json)
        return
    item = actives[0]
    stale = item_is_stale(item)
    requested_scope = parse_csv(args.scope_tags)
    requested_topic = parse_csv(args.topic_tags)
    scope_match = tag_match(requested_scope, item.get("scope_tags", []))
    topic_match = tag_match(requested_topic, item.get("topic_tags", []))
    kind_match = plan_kind_match(args.plan_kind, item.get("plan_kinds", []))
    applies = not stale and scope_match and topic_match and kind_match
    reason = "active deferred plan matches provided planning context"
    if stale:
        reason = "active deferred plan is stale"
    elif not scope_match:
        reason = "scope tags do not match active deferred plan"
    elif not topic_match:
        reason = "topic tags do not match active deferred plan"
    elif not kind_match:
        reason = "plan kind does not match active deferred plan"
    payload = {
        "enabled": True,
        "active": True,
        "applies": applies,
        "stale": stale,
        "deferred_plan_id": item["id"],
        "title": item["title"],
        "goal": item["goal"],
        "do_not": item.get("do_not", []),
        "allowed_now": item.get("allowed_now", []),
        "reopen_trigger": item.get("reopen_trigger", []),
        "source": item["file_path"],
        "reason": reason,
    }
    print_payload(payload, args.json)


def cmd_doctor(args: argparse.Namespace) -> None:
    root = repo_root(args.root)
    if not is_enabled(root):
        print("deferred-plan root not enabled")
        print("issues: 0")
        return
    index = load_index(root)
    issues: list[str] = []
    actives = active_items(index)
    if len(actives) > 1:
        issues.append("multiple active deferred plans: " + ", ".join(item["id"] for item in actives))
    expected_current = (
        render_current_for_item(actives[0])
        if len(actives) == 1
        else (
            "# Current Deferred Plan\n\n"
            "- Invalid state: multiple active deferred plans detected.\n"
            f"- Active IDs: {', '.join(item['id'] for item in actives)}\n"
            if len(actives) > 1
            else render_no_active_current()
        )
    )
    current_path = root / CURRENT_REL
    if not current_path.exists():
        issues.append("CURRENT.md missing")
    elif current_path.read_text(encoding="utf-8") != expected_current:
        issues.append("CURRENT.md out of sync with deferred-plan index")
    for item in index["plans"]:
        path = root / item["file_path"]
        if not path.exists():
            issues.append(f"missing deferred plan file: {item['file_path']}")
        if item["status"] == "archived" and not item["file_path"].startswith(str(ARCHIVE_REL)):
            issues.append(f"archived plan not stored under archive/: {item['id']}")
        if item["status"] != "archived" and not item["file_path"].startswith(str(ACTIVE_REL)):
            issues.append(f"non-archived plan not stored under active/: {item['id']}")
    for issue in issues:
        print(f"- {issue}")
    print(f"issues: {len(issues)}")
    if issues:
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deferred-plan artifact operations.")
    parser.add_argument("--root", default=".", help="target repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("ensure", "init"):
        sub = subparsers.add_parser(name, help="ensure deferred-plan root exists")
        sub.set_defaults(func=cmd_ensure)

    create = subparsers.add_parser("create", help="create a deferred plan")
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--goal", required=True)
    create.add_argument("--why-not-now", required=True)
    create.add_argument("--current-deviation", required=True)
    create.add_argument("--owner", default="codex")
    create.add_argument("--scope-tags")
    create.add_argument("--topic-tags")
    create.add_argument("--plan-kinds")
    create.add_argument("--do-not", action="append", default=[])
    create.add_argument("--allowed-now", action="append", default=[])
    create.add_argument("--reopen-trigger", action="append", default=[])
    create.add_argument("--evidence-ref", action="append", default=[])
    create.add_argument("--review-after")
    create.add_argument("--supersedes")
    create.add_argument("--activate", action="store_true")
    create.set_defaults(func=cmd_create)

    status = subparsers.add_parser("status", help="show deferred-plan status")
    status.add_argument("--id")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=cmd_status)

    activate = subparsers.add_parser("activate", help="activate a deferred plan")
    activate.add_argument("--id", required=True)
    activate.set_defaults(func=cmd_activate)

    supersede = subparsers.add_parser("supersede", help="supersede an active deferred plan")
    supersede.add_argument("--id", required=True)
    supersede.add_argument("--superseded-by", required=True)
    supersede.set_defaults(func=cmd_supersede)

    complete = subparsers.add_parser("complete", help="complete an active deferred plan")
    complete.add_argument("--id", required=True)
    complete.set_defaults(func=cmd_complete)

    archive = subparsers.add_parser("archive", help="archive a completed or superseded deferred plan")
    archive.add_argument("--id", required=True)
    archive.set_defaults(func=cmd_archive)

    sync_current_parser = subparsers.add_parser("sync-current", help="regenerate CURRENT.md")
    sync_current_parser.set_defaults(func=cmd_sync_current)

    resolve = subparsers.add_parser("resolve-for-planning", help="resolve whether current planning should inherit guardrails")
    resolve.add_argument("--scope-tags")
    resolve.add_argument("--topic-tags")
    resolve.add_argument("--plan-kind")
    resolve.add_argument("--json", action="store_true")
    resolve.set_defaults(func=cmd_resolve_for_planning)

    doctor = subparsers.add_parser("doctor", help="check deferred-plan invariants")
    doctor.set_defaults(func=cmd_doctor)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
