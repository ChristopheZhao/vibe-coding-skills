#!/usr/bin/env python3
"""Plan operations for SDD plan-driven development."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

VALID_STATUSES: Set[str] = {
    "draft",
    "in_progress",
    "testing",
    "awaiting_user_confirmation",
    "completed",
    "archived",
    "blocked",
}

MANAGED_STATUSES: Set[str] = VALID_STATUSES - {"archived"}

ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "draft": {"in_progress", "blocked"},
    "in_progress": {"testing", "awaiting_user_confirmation", "blocked"},
    "testing": {"in_progress", "awaiting_user_confirmation", "completed", "blocked"},
    "awaiting_user_confirmation": {"completed", "in_progress", "blocked"},
    "blocked": {"in_progress"},
    "completed": {"in_progress"},
    "archived": set(),
}

STATUS_ORDER: List[str] = [
    "draft",
    "in_progress",
    "testing",
    "awaiting_user_confirmation",
    "blocked",
    "completed",
    "archived",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_structure(root: Path) -> Dict[str, Path]:
    plans_root = root / "docs" / "plans"
    active_dir = plans_root / "active"
    archive_dir = plans_root / "archive"
    index_file = plans_root / "PLAN_INDEX.json"

    active_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    if not index_file.exists():
        index_file.write_text(json.dumps({"version": 1, "plans": []}, indent=2), encoding="utf-8")

    return {
        "plans_root": plans_root,
        "active_dir": active_dir,
        "archive_dir": archive_dir,
        "index_file": index_file,
    }


def load_index(index_file: Path) -> Dict[str, Any]:
    try:
        return json.loads(index_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"version": 1, "plans": []}


def save_index(index_file: Path, payload: Dict[str, Any]) -> None:
    index_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def find_plan(index: Dict[str, Any], plan_id: str) -> Dict[str, Any] | None:
    for item in index.get("plans", []):
        if item.get("id") == plan_id:
            return item
    return None


def feature_template(plan_id: str, title: str, priority: str, owner: str, created: str) -> str:
    return f"""# Plan: {title}
- Plan ID: {plan_id}
- Type: feature
- Status: draft
- Priority: {priority}
- Owner: {owner}
- Created At: {created}

## 1. Requirement Analysis
- User intent:
- Scope in:
- Scope out:
- Acceptance criteria:

## 2. Functional Decomposition
- Module A:
- Module B:
- Module C:

## 3. Implementation Approach
- Data flow:
- API/contract changes:
- Migration or compatibility notes:

## 4. Technical Solution
- Key design choices:
- Trade-offs:
- Risks and mitigations:

## 5. Execution List (Priority Ordered)
- [ ] P0 Task 1
- [ ] P0 Task 2
- [ ] P1 Task 3

## 6. Test and Acceptance
- Unit tests:
- Integration tests:
- Manual verification:

## 7. Status Log
- {created} draft created
"""


def fix_template(plan_id: str, title: str, priority: str, owner: str, created: str) -> str:
    return f"""# Plan: {title}
- Plan ID: {plan_id}
- Type: fix
- Status: draft
- Priority: {priority}
- Owner: {owner}
- Created At: {created}

## 1. Current Problem
- Symptom:
- Impact:
- Reproduction:

## 2. Deviation Analysis
- Expected behavior:
- Actual behavior:
- Root cause hypothesis:

## 3. Implementation Approach
- Patch strategy:
- Compatibility considerations:
- Rollback plan:

## 4. Execution Checklist
- [ ] Reproduce issue
- [ ] Implement fix/refactor
- [ ] Add or update tests
- [ ] Verify in target flow

## 5. Test and Validation
- Test cases:
- Regression checks:
- User-facing validation points:

## 6. Status Log
- {created} draft created
"""


def allowed_targets(current: str) -> List[str]:
    return sorted(ALLOWED_TRANSITIONS.get(current, set()))


def is_active_plan_path(file_path: str) -> bool:
    return Path(file_path).parts[:3] == ("docs", "plans", "active")


def is_archive_plan_path(file_path: str) -> bool:
    return Path(file_path).parts[:3] == ("docs", "plans", "archive")


def extract_plan_doc_status(content: str) -> Tuple[str | None, bool]:
    for line in content.splitlines():
        if line.strip().startswith("- Status:"):
            return line.split(":", 1)[1].strip(), True
    return None, False


def replace_plan_doc_status(content: str, status: str) -> Tuple[str, bool]:
    lines = content.splitlines(keepends=True)
    for idx, line in enumerate(lines):
        if line.strip().startswith("- Status:"):
            newline = ""
            if line.endswith("\r\n"):
                newline = "\r\n"
            elif line.endswith("\n"):
                newline = "\n"
            indent = line[: len(line) - len(line.lstrip())]
            lines[idx] = f"{indent}- Status: {status}{newline}"
            return "".join(lines), True
    return content, False


def sync_plan_doc_status(root: Path, item: Dict[str, Any], status: str) -> Tuple[bool, str | None]:
    file_path = str(item.get("file_path", ""))
    if not file_path:
        return False, "missing file_path in index"

    plan_path = root / file_path
    if not plan_path.exists():
        return False, f"plan file not found: {plan_path}"

    content = plan_path.read_text(encoding="utf-8")
    updated, replaced = replace_plan_doc_status(content, status)
    if not replaced:
        return False, f"plan file missing '- Status:' header: {plan_path}"

    if updated != content:
        plan_path.write_text(updated, encoding="utf-8")
        return True, None

    return False, None


def detect_git_repo(root: Path) -> bool:
    git_path = root / ".git"
    return git_path.is_dir() or git_path.is_file()


def make_issue(
    *,
    code: str,
    message: str,
    plan_id: str | None = None,
    file_path: str | None = None,
    fixable: bool = False,
) -> Dict[str, Any]:
    item: Dict[str, Any] = {"code": code, "message": message, "fixable": fixable}
    if plan_id:
        item["plan_id"] = plan_id
    if file_path:
        item["file_path"] = file_path
    return item


def gather_consistency_issues(
    root: Path, paths: Dict[str, Path], index: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    issues: List[Dict[str, Any]] = []
    plans = index.get("plans", [])
    if not isinstance(plans, list):
        return [make_issue(code="invalid_index_schema", message="index field 'plans' must be a list")], []

    seen_ids: Set[str] = set()
    referenced_paths: Set[str] = set()
    for raw in plans:
        if not isinstance(raw, dict):
            issues.append(make_issue(code="invalid_plan_item", message="index plan entry must be an object"))
            continue

        plan_id = str(raw.get("id", "")).strip()
        if not plan_id:
            issues.append(make_issue(code="missing_plan_id", message="index plan entry is missing id"))
            continue

        if plan_id in seen_ids:
            issues.append(make_issue(code="duplicate_plan_id", plan_id=plan_id, message="duplicate plan id in index"))
            continue
        seen_ids.add(plan_id)

        status = str(raw.get("status", "")).strip()
        if status not in VALID_STATUSES:
            issues.append(
                make_issue(
                    code="invalid_status",
                    plan_id=plan_id,
                    message=f"invalid status in index: {status or '<empty>'}",
                )
            )
            continue

        file_path = str(raw.get("file_path", "")).strip()
        if not file_path:
            issues.append(make_issue(code="missing_file_path", plan_id=plan_id, message="missing file_path in index"))
            continue

        referenced_paths.add(file_path)
        plan_path = root / file_path
        if not plan_path.exists():
            issues.append(
                make_issue(
                    code="missing_plan_file",
                    plan_id=plan_id,
                    file_path=file_path,
                    message=f"plan file not found: {file_path}",
                )
            )
            continue

        if status == "archived":
            if not is_archive_plan_path(file_path):
                issues.append(
                    make_issue(
                        code="archived_path_mismatch",
                        plan_id=plan_id,
                        file_path=file_path,
                        message="status archived but file_path is not under docs/plans/archive",
                    )
                )
        else:
            if not is_active_plan_path(file_path):
                issues.append(
                    make_issue(
                        code="active_path_mismatch",
                        plan_id=plan_id,
                        file_path=file_path,
                        message=f"status {status} but file_path is not under docs/plans/active",
                    )
                )

        try:
            content = plan_path.read_text(encoding="utf-8")
        except OSError as exc:
            issues.append(
                make_issue(
                    code="plan_read_error",
                    plan_id=plan_id,
                    file_path=file_path,
                    message=f"failed to read plan file: {exc}",
                )
            )
            continue

        doc_status, has_status = extract_plan_doc_status(content)
        if not has_status:
            issues.append(
                make_issue(
                    code="missing_doc_status_header",
                    plan_id=plan_id,
                    file_path=file_path,
                    message="plan markdown is missing '- Status:' header",
                )
            )
            continue

        if doc_status != status:
            issues.append(
                make_issue(
                    code="doc_status_mismatch",
                    plan_id=plan_id,
                    file_path=file_path,
                    message=f"index status '{status}' != doc status '{doc_status}'",
                    fixable=True,
                )
            )

    discovered_paths: Set[str] = set()
    for base in (paths["active_dir"], paths["archive_dir"]):
        if not base.exists():
            continue
        for file in base.rglob("*"):
            if file.is_file():
                discovered_paths.add(str(file.relative_to(root)))

    orphan_paths = sorted(discovered_paths - referenced_paths)
    for file_path in orphan_paths:
        issues.append(
            make_issue(
                code="orphan_plan_file",
                file_path=file_path,
                message="plan file exists on disk but is not registered in PLAN_INDEX",
            )
        )

    return issues, [p for p in plans if isinstance(p, dict)]


def apply_doc_status_fixes(root: Path, plans: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    fixed: List[Dict[str, Any]] = []
    unresolved: List[Dict[str, Any]] = []

    for item in plans:
        plan_id = str(item.get("id", "")).strip()
        status = str(item.get("status", "")).strip()
        if not plan_id or status not in VALID_STATUSES:
            continue

        changed, err = sync_plan_doc_status(root, item, status)
        if err:
            unresolved.append(
                make_issue(
                    code="doc_sync_failed",
                    plan_id=plan_id,
                    file_path=str(item.get("file_path", "")).strip() or None,
                    message=err,
                )
            )
            continue

        if changed:
            fixed.append(
                {
                    "plan_id": plan_id,
                    "file_path": str(item.get("file_path", "")).strip(),
                    "status": status,
                }
            )

    return fixed, unresolved


def truncate_text(text: str, limit: int = 80) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3]}..."


def md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


def render_markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md_cell(v) for v in row) + " |")
    return lines


def add_root_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="Repository root (default: .)")


def cmd_ensure(args: argparse.Namespace) -> int:
    paths = ensure_structure(Path(args.root).resolve())
    print(f"initialized: {paths['plans_root']}")
    print(f"index: {paths['index_file']}")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_structure(root)
    index = load_index(paths["index_file"])

    if find_plan(index, args.id):
        print(f"error: plan id already exists: {args.id}", file=sys.stderr)
        return 1

    created = now_iso()
    filename = args.file if args.file else f"{args.id}.md"
    plan_path = paths["active_dir"] / filename
    if plan_path.exists():
        print(f"error: plan file already exists: {plan_path}", file=sys.stderr)
        return 1

    if args.kind == "feature":
        content = feature_template(args.id, args.title, args.priority, args.owner, created)
    else:
        content = fix_template(args.id, args.title, args.priority, args.owner, created)

    plan_path.write_text(content, encoding="utf-8")

    index.setdefault("plans", []).append(
        {
            "id": args.id,
            "title": args.title,
            "kind": args.kind,
            "status": "draft",
            "priority": args.priority,
            "owner": args.owner,
            "file_path": str(plan_path.relative_to(root)),
            "confirmed_by_user": False,
            "created_at": created,
            "updated_at": created,
            "archived_at": None,
            "notes": [],
        }
    )
    save_index(paths["index_file"], index)
    print(f"created: {plan_path}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    if args.status not in MANAGED_STATUSES:
        if args.status == "archived":
            print("error: use 'archive' command instead of setting archived via status", file=sys.stderr)
        else:
            print(f"error: invalid status: {args.status}", file=sys.stderr)
        return 1

    root = Path(args.root).resolve()
    paths = ensure_structure(root)
    index = load_index(paths["index_file"])
    item = find_plan(index, args.id)
    if not item:
        print(f"error: plan id not found: {args.id}", file=sys.stderr)
        return 1

    current = str(item.get("status", "draft"))
    if current not in VALID_STATUSES:
        print(f"error: current status is invalid in index: {current}", file=sys.stderr)
        return 1

    if current == "archived":
        print("error: archived plans are immutable; reopen from archive manually if needed", file=sys.stderr)
        return 1

    if args.status == "blocked" and not args.note:
        print("error: blocked requires --note with blocker details", file=sys.stderr)
        return 1

    if args.confirmed_by_user and args.status != "completed":
        print("error: --confirmed-by-user is only valid when setting status completed", file=sys.stderr)
        return 1

    if current != args.status:
        allowed = ALLOWED_TRANSITIONS.get(current, set())
        if args.status not in allowed:
            targets = ", ".join(allowed_targets(current)) or "<none>"
            print(
                f"error: invalid transition {current} -> {args.status}; allowed: {targets}",
                file=sys.stderr,
            )
            return 1

    if args.status == "completed" and not args.confirmed_by_user:
        print("error: completed requires --confirmed-by-user", file=sys.stderr)
        return 1

    ts = now_iso()
    item["status"] = args.status

    if current == "completed" and args.status == "in_progress":
        item["confirmed_by_user"] = False

    if args.status == "completed":
        item["confirmed_by_user"] = True

    item["updated_at"] = ts

    if args.note:
        item.setdefault("notes", []).append({"at": ts, "text": args.note})

    save_index(paths["index_file"], index)
    _, sync_err = sync_plan_doc_status(root, item, args.status)
    if sync_err:
        print(f"warning: status updated but doc sync failed: {sync_err}", file=sys.stderr)
    print(f"updated: {args.id} -> {args.status}")
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_structure(root)
    index = load_index(paths["index_file"])
    item = find_plan(index, args.id)
    if not item:
        print(f"error: plan id not found: {args.id}", file=sys.stderr)
        return 1

    if item.get("status") != "completed":
        print("error: archive requires current status completed", file=sys.stderr)
        return 1

    if not args.confirmed_by_user and not item.get("confirmed_by_user"):
        print("error: archive requires user confirmation (--confirmed-by-user)", file=sys.stderr)
        return 1

    file_path = str(item.get("file_path", ""))
    if not is_active_plan_path(file_path):
        print("error: archive source must be under docs/plans/active", file=sys.stderr)
        return 1

    src = root / file_path
    if not src.exists():
        print(f"error: source plan file not found: {src}", file=sys.stderr)
        return 1

    month_dir = datetime.now(timezone.utc).strftime("%Y-%m")
    dst_dir = paths["archive_dir"] / month_dir
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dst.exists():
        print(f"error: archive destination already exists: {dst}", file=sys.stderr)
        return 1

    shutil.move(str(src), str(dst))

    ts = now_iso()
    item["status"] = "archived"
    item["confirmed_by_user"] = True
    item["archived_at"] = ts
    item["updated_at"] = ts
    item["file_path"] = str(dst.relative_to(root))

    save_index(paths["index_file"], index)
    _, sync_err = sync_plan_doc_status(root, item, "archived")
    if sync_err:
        print(f"warning: plan archived but doc sync failed: {sync_err}", file=sys.stderr)
    print(f"archived: {args.id} -> {dst}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_structure(root)
    index = load_index(paths["index_file"])
    plans: List[Dict[str, Any]] = index.get("plans", [])

    if args.status:
        plans = [p for p in plans if p.get("status") == args.status]

    if args.json:
        print(json.dumps(plans, ensure_ascii=False, indent=2))
        return 0

    if not plans:
        print("no plans")
        return 0

    print("id | status | priority | kind | title")
    print("-" * 72)
    for p in plans:
        print(
            f"{p.get('id','')} | {p.get('status','')} | {p.get('priority','')} | "
            f"{p.get('kind','')} | {p.get('title','')}"
        )
    return 0


def cmd_sync_doc(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_structure(root)
    index = load_index(paths["index_file"])

    plans = [p for p in index.get("plans", []) if isinstance(p, dict)]
    if args.id:
        plans = [p for p in plans if p.get("id") == args.id]
        if not plans:
            print(f"error: plan id not found: {args.id}", file=sys.stderr)
            return 1

    changed = 0
    unchanged = 0
    failed = 0

    for item in plans:
        status = str(item.get("status", "")).strip()
        if status not in VALID_STATUSES:
            failed += 1
            plan_id = str(item.get("id", "<unknown>"))
            print(f"error: skip {plan_id}, invalid status in index: {status or '<empty>'}", file=sys.stderr)
            continue

        updated, err = sync_plan_doc_status(root, item, status)
        if err:
            failed += 1
            plan_id = str(item.get("id", "<unknown>"))
            print(f"error: sync failed for {plan_id}: {err}", file=sys.stderr)
            continue

        if updated:
            changed += 1
        else:
            unchanged += 1

    target = args.id if args.id else "all plans"
    print(f"synced: {target}; changed={changed}, unchanged={unchanged}, failed={failed}")
    return 1 if failed else 0


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_structure(root)
    index = load_index(paths["index_file"])

    issues, plans = gather_consistency_issues(root, paths, index)
    fixed: List[Dict[str, Any]] = []
    fix_errors: List[Dict[str, Any]] = []

    if args.fix:
        fix_targets = {
            str(issue.get("plan_id", ""))
            for issue in issues
            if issue.get("code") == "doc_status_mismatch" and issue.get("plan_id")
        }
        target_plans = [p for p in plans if str(p.get("id", "")) in fix_targets]
        fixed, fix_errors = apply_doc_status_fixes(root, target_plans)
        issues, _ = gather_consistency_issues(root, paths, index)

    result = {
        "ok": len(issues) == 0,
        "issue_count": len(issues),
        "fixed_count": len(fixed),
        "fix_error_count": len(fix_errors),
        "issues": issues,
        "fixed": fixed,
        "fix_errors": fix_errors,
        "git_repo_detected": detect_git_repo(root),
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        repo_note = "git repo detected" if result["git_repo_detected"] else "not a git repo"
        print(f"doctor: {repo_note}")
        if fixed:
            print(f"fixed: {len(fixed)} doc status mismatch(es)")
            for item in fixed:
                print(f"- {item['plan_id']}: synced doc status -> {item['status']}")
        if fix_errors:
            print(f"fix-errors: {len(fix_errors)}")
            for issue in fix_errors:
                plan_id = issue.get("plan_id", "-")
                file_path = issue.get("file_path", "-")
                print(f"- [{issue['code']}] plan={plan_id} file={file_path} :: {issue['message']}")
        if issues:
            print(f"issues: {len(issues)}")
            for issue in issues:
                plan_id = issue.get("plan_id", "-")
                file_path = issue.get("file_path", "-")
                print(f"- [{issue['code']}] plan={plan_id} file={file_path} :: {issue['message']}")
        else:
            print("issues: 0")

    return 0 if result["ok"] else 1


def cmd_dashboard(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_structure(root)
    index = load_index(paths["index_file"])
    plans = [p for p in index.get("plans", []) if isinstance(p, dict)]
    issues, _ = gather_consistency_issues(root, paths, index)

    counts = {status: 0 for status in STATUS_ORDER}
    for item in plans:
        status = str(item.get("status", "")).strip()
        if status in counts:
            counts[status] += 1

    active_plans = [p for p in plans if str(p.get("status")) != "archived"]
    active_plans.sort(key=lambda p: str(p.get("updated_at", "")), reverse=True)

    attention_plans = [
        p for p in plans if str(p.get("status")) in {"awaiting_user_confirmation", "blocked"}
    ]
    attention_plans.sort(key=lambda p: str(p.get("updated_at", "")), reverse=True)

    archived_plans = [p for p in plans if str(p.get("status")) == "archived"]
    archived_plans.sort(
        key=lambda p: str(p.get("archived_at") or p.get("updated_at") or ""),
        reverse=True,
    )

    drift_issues = [i for i in issues if i.get("code") == "doc_status_mismatch"]
    structure_issues = [i for i in issues if i.get("code") != "doc_status_mismatch"]

    output = Path(args.output) if args.output else paths["plans_root"] / "views" / "dashboard.md"
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("# Plan Dashboard")
    lines.append("")
    lines.append(f"_Generated at: {now_iso()}_")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    summary_rows = [[status, counts[status]] for status in STATUS_ORDER]
    lines.extend(render_markdown_table(["Status", "Count"], summary_rows))
    lines.append("")
    lines.append("## Active Plans")
    lines.append("")
    if active_plans:
        rows = [
            [
                p.get("id", ""),
                p.get("status", ""),
                p.get("priority", ""),
                p.get("owner", ""),
                p.get("updated_at", ""),
                p.get("title", ""),
            ]
            for p in active_plans
        ]
        lines.extend(
            render_markdown_table(
                ["Plan ID", "Status", "Priority", "Owner", "Updated At", "Title"], rows
            )
        )
    else:
        lines.append("_No active plans._")
    lines.append("")
    lines.append("## Needs Attention")
    lines.append("")
    if attention_plans:
        rows = [
            [
                p.get("id", ""),
                p.get("status", ""),
                p.get("updated_at", ""),
                truncate_text(str((p.get("notes") or [{}])[-1].get("text", "") or "-"), 96),
            ]
            for p in attention_plans
        ]
        lines.extend(render_markdown_table(["Plan ID", "Status", "Updated At", "Latest Note"], rows))
    else:
        lines.append("_No blocked or awaiting-user-confirmation plans._")
    lines.append("")
    lines.append("## Recent Archives")
    lines.append("")
    if archived_plans:
        rows = [
            [
                p.get("id", ""),
                p.get("archived_at", "") or p.get("updated_at", ""),
                p.get("file_path", ""),
                p.get("title", ""),
            ]
            for p in archived_plans[:10]
        ]
        lines.extend(render_markdown_table(["Plan ID", "Archived At", "File", "Title"], rows))
    else:
        lines.append("_No archived plans._")
    lines.append("")
    lines.append("## Drift Alerts")
    lines.append("")
    if drift_issues:
        for issue in drift_issues:
            lines.append(
                f"- `{issue.get('plan_id', '-')}`: {issue.get('message', '')} (`{issue.get('file_path', '-')}`)"
            )
    else:
        lines.append("_No index/doc status drift detected._")
    lines.append("")
    if structure_issues:
        lines.append("## Structure Alerts")
        lines.append("")
        for issue in structure_issues:
            lines.append(
                f"- `{issue.get('code', 'unknown')}`: {issue.get('message', '')} "
                f"(plan={issue.get('plan_id', '-')}, file=`{issue.get('file_path', '-')}`)"
            )
        lines.append("")
    lines.append("## Compare-File Commands")
    lines.append("")
    if detect_git_repo(root):
        lines.append("```bash")
        lines.append("git diff -- docs/plans/PLAN_INDEX.json")
        lines.append("git diff -- docs/plans/active docs/plans/archive")
        lines.append("```")
    else:
        lines.append("_Not a git repository: compare-file git commands are unavailable in this root._")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated: {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDD plan operations")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ensure = sub.add_parser("ensure", help="Create plan folders and index")
    add_root_arg(p_ensure)
    p_ensure.set_defaults(func=cmd_ensure)

    p_create = sub.add_parser("create", help="Create a new plan doc and register it")
    add_root_arg(p_create)
    p_create.add_argument("--id", required=True, help="Plan ID")
    p_create.add_argument("--title", required=True, help="Plan title")
    p_create.add_argument("--kind", required=True, choices=["feature", "fix"], help="Plan kind")
    p_create.add_argument("--priority", default="P1", help="Plan priority, e.g. P0/P1/P2")
    p_create.add_argument("--owner", default="codex", help="Plan owner")
    p_create.add_argument("--file", help="Optional markdown filename")
    p_create.set_defaults(func=cmd_create)

    p_status = sub.add_parser("status", help="Update plan status")
    add_root_arg(p_status)
    p_status.add_argument("--id", required=True, help="Plan ID")
    p_status.add_argument("--status", required=True, help="Target status")
    p_status.add_argument("--confirmed-by-user", action="store_true", help="Mark as user-confirmed")
    p_status.add_argument("--note", help="Optional status note")
    p_status.set_defaults(func=cmd_status)

    p_archive = sub.add_parser("archive", help="Archive a completed plan")
    add_root_arg(p_archive)
    p_archive.add_argument("--id", required=True, help="Plan ID")
    p_archive.add_argument("--confirmed-by-user", action="store_true", help="Confirm user approval")
    p_archive.set_defaults(func=cmd_archive)

    p_list = sub.add_parser("list", help="List plans")
    add_root_arg(p_list)
    p_list.add_argument("--status", help="Filter by status")
    p_list.add_argument("--json", action="store_true", help="Output JSON")
    p_list.set_defaults(func=cmd_list)

    p_sync_doc = sub.add_parser("sync-doc", help="Sync markdown '- Status:' from index")
    add_root_arg(p_sync_doc)
    p_sync_doc.add_argument("--id", help="Optional plan ID to sync one plan only")
    p_sync_doc.set_defaults(func=cmd_sync_doc)

    p_doctor = sub.add_parser("doctor", help="Check plan/index consistency and drift")
    add_root_arg(p_doctor)
    p_doctor.add_argument("--fix", action="store_true", help="Auto-fix doc status mismatch where possible")
    p_doctor.add_argument("--json", action="store_true", help="Output JSON")
    p_doctor.set_defaults(func=cmd_doctor)

    p_dashboard = sub.add_parser("dashboard", help="Generate human-readable plan status dashboard")
    add_root_arg(p_dashboard)
    p_dashboard.add_argument(
        "--output",
        help="Output markdown path (default: docs/plans/views/dashboard.md under --root)",
    )
    p_dashboard.set_defaults(func=cmd_dashboard)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
