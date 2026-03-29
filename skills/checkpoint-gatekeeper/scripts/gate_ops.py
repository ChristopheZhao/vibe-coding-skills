#!/usr/bin/env python3
"""Deterministic checkpoint gate operations for checkpoint-gatekeeper.

This CLI manages checkpoint-side artifacts only. It never mutates plan
lifecycle state under docs/plans/PLAN_INDEX.json.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NoReturn


SPEC_MARKER_RE = re.compile(
    r"<!-- checkpoint-gatekeeper:spec\s*(\{.*?\})\s*-->",
    re.DOTALL,
)

DEFAULT_USER_CONFIRMATION_TRIGGERS = [
    "MANUAL_REVIEW_REQUIRED",
    "NEEDS_USER_CONFIRMATION",
    "SCOPE_CHANGE_REQUIRED",
]

VALID_PROFILES = {"default", "acceptance"}

NON_PASS_EXIT_CODES = {
    "pending": 4,
    "fail": 2,
    "needs_user_confirmation": 3,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fail(message: str) -> NoReturn:
    raise SystemExit(message)


def repo_root(value: str) -> Path:
    return Path(value).resolve()


def plan_index_path(root: Path) -> Path:
    return root / "docs" / "plans" / "PLAN_INDEX.json"


def checkpoints_dir(root: Path, plan_id: str) -> Path:
    return root / "docs" / "checkpoints" / plan_id


def checkpoint_slug(checkpoint: str) -> str:
    return checkpoint if checkpoint.startswith("CHK-") else f"CHK-{checkpoint}"


def checklist_path(root: Path, plan_id: str, checkpoint: str) -> Path:
    slug = checkpoint_slug(checkpoint)
    return checkpoints_dir(root, plan_id) / f"{slug}-checklist.md"


def gate_path(root: Path, plan_id: str, checkpoint: str) -> Path:
    slug = checkpoint_slug(checkpoint)
    return checkpoints_dir(root, plan_id) / f"{slug}-gate.json"


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid json in {path}: {exc}")


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def load_plan_index(root: Path) -> dict[str, Any]:
    payload = load_json(plan_index_path(root))
    if not isinstance(payload, dict):
        fail("PLAN_INDEX.json must be a JSON object")
    return payload


def find_plan(root: Path, plan_id: str) -> dict[str, Any]:
    payload = load_plan_index(root)
    plans = payload.get("plans", [])
    for item in plans:
        if item.get("id") == plan_id:
            return item
    fail(f"plan not found in PLAN_INDEX.json: {plan_id}")


def normalize_profile(value: Any) -> str:
    profile = str(value or "default")
    if profile not in VALID_PROFILES:
        fail(f"invalid profile: {profile}")
    return profile


def normalize_acceptance_fields(spec: dict[str, Any]) -> dict[str, Any]:
    profile = normalize_profile(spec.get("profile"))
    spec["profile"] = profile
    if profile == "acceptance":
        spec["acceptance_target"] = str(spec.get("acceptance_target") or "")
        spec["required_evidence"] = [str(item) for item in (spec.get("required_evidence") or [])]
    else:
        spec.pop("acceptance_target", None)
        spec.pop("required_evidence", None)
    return spec


def default_spec(args: argparse.Namespace) -> dict[str, Any]:
    auto_fix_commands = list(args.auto_fix_command or [])
    allow_auto_fix = args.allow_auto_fix or bool(auto_fix_commands)
    spec = {
        "plan_id": args.id,
        "checkpoint": checkpoint_slug(args.checkpoint),
        "title": args.title or checkpoint_slug(args.checkpoint),
        "profile": normalize_profile(args.profile),
        "allow_auto_fix": allow_auto_fix,
        "max_auto_fix_rounds": args.max_auto_fix_rounds,
        "validation_commands": list(args.validation_command or []),
        "auto_fix_commands": auto_fix_commands,
        "user_confirmation_triggers": list(
            args.user_confirmation_trigger or DEFAULT_USER_CONFIRMATION_TRIGGERS
        ),
    }
    if spec["profile"] == "acceptance":
        spec["acceptance_target"] = str(args.acceptance_target or "")
        spec["required_evidence"] = list(args.required_evidence or [])
    return normalize_acceptance_fields(spec)


def render_checklist(spec: dict[str, Any]) -> str:
    spec = normalize_acceptance_fields(dict(spec))
    validation_lines = spec["validation_commands"] or ["_Add validation commands before running gate check_"]
    auto_fix_lines = spec["auto_fix_commands"] or ["_No auto-fix commands configured_"]
    validation_md = "\n".join(f"- `{line}`" if not line.startswith("_") else f"- {line}" for line in validation_lines)
    auto_fix_md = "\n".join(f"- `{line}`" if not line.startswith("_") else f"- {line}" for line in auto_fix_lines)
    trigger_md = "\n".join(f"- `{line}`" for line in spec["user_confirmation_triggers"])
    acceptance_target = spec.get("acceptance_target", "_Not configured_")
    required_evidence_lines = spec.get("required_evidence") or ["_No required evidence declared_"]
    required_evidence_md = "\n".join(
        f"- `{line}`" if not line.startswith("_") else f"- {line}" for line in required_evidence_lines
    )
    spec_block = json.dumps(spec, indent=2, ensure_ascii=True)
    acceptance_block = ""
    if spec["profile"] == "acceptance":
        acceptance_block = (
            "## Acceptance Contract\n"
            f"- Acceptance Target: `{acceptance_target}`\n\n"
            "## Required Evidence\n"
            f"{required_evidence_md}\n\n"
        )
    return (
        f"# Checklist: {spec['title']}\n"
        f"- Linked Plan: `{spec['plan_id']}`\n"
        f"- Checkpoint: `{spec['checkpoint']}`\n"
        f"- Profile: `{spec['profile']}`\n"
        f"- Auto Fix Enabled: `{str(spec['allow_auto_fix']).lower()}`\n"
        f"- Max Auto Fix Rounds: `{spec['max_auto_fix_rounds']}`\n\n"
        f"<!-- checkpoint-gatekeeper:spec\n{spec_block}\n-->\n\n"
        "## Validation Commands\n"
        f"{validation_md}\n\n"
        f"{acceptance_block}"
        "## Auto-Fix Commands\n"
        f"{auto_fix_md}\n\n"
        "## User Confirmation Triggers\n"
        f"{trigger_md}\n\n"
        "## Evidence\n"
        "- Record relevant artifacts, logs, or screenshots here after each checkpoint run.\n"
    )


def parse_checklist_spec(path: Path) -> dict[str, Any]:
    try:
        markdown = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"missing checklist artifact: {path}")
    match = SPEC_MARKER_RE.search(markdown)
    if not match:
        fail(f"missing checkpoint-gatekeeper spec block: {path}")
    try:
        spec = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        fail(f"invalid checklist spec json in {path}: {exc}")
    if not isinstance(spec, dict):
        fail(f"invalid checklist spec payload in {path}")
    return normalize_acceptance_fields(spec)


def default_gate_payload(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    spec = normalize_acceptance_fields(dict(spec))
    payload = {
        "plan_id": spec["plan_id"],
        "checkpoint": spec["checkpoint"],
        "title": spec["title"],
        "profile": spec["profile"],
        "verdict": "pending",
        "summary": "Checkpoint artifacts initialized; gate check has not run yet.",
        "updated_at": utc_now(),
        "checklist_path": relpath(checklist_path(root, spec["plan_id"], spec["checkpoint"]), root),
        "attempts": [],
        "waiver": None,
    }
    if spec["profile"] == "acceptance":
        payload["acceptance_target"] = spec.get("acceptance_target", "")
        payload["acceptance_gaps"] = []
        payload["required_evidence"] = list(spec.get("required_evidence") or [])
    return payload


def load_gate_or_default(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    spec = normalize_acceptance_fields(dict(spec))
    path = gate_path(root, spec["plan_id"], spec["checkpoint"])
    if path.exists():
        payload = load_json(path)
        if not isinstance(payload, dict):
            fail(f"invalid gate payload in {path}")
        payload.setdefault("profile", spec["profile"])
        if spec["profile"] == "acceptance":
            payload.setdefault("acceptance_target", spec.get("acceptance_target", ""))
            payload.setdefault("acceptance_gaps", [])
            payload.setdefault("required_evidence", list(spec.get("required_evidence") or []))
        return payload
    return default_gate_payload(root, spec)


def acceptance_gaps_for(spec: dict[str, Any], verdict: str) -> list[str]:
    if normalize_profile(spec.get("profile")) != "acceptance":
        return []
    gaps: list[str] = []
    if not str(spec.get("acceptance_target") or "").strip():
        gaps.append("Missing acceptance target.")
    if not list(spec.get("required_evidence") or []):
        gaps.append("Missing required evidence list.")
    if verdict not in {"pass", "auto_fixed_pass", "waived"}:
        gaps.append("Semantic acceptance is not yet satisfied.")
    return gaps


def acceptance_summary_for(spec: dict[str, Any], verdict: str, summary: str) -> str:
    if normalize_profile(spec.get("profile")) != "acceptance":
        return summary
    gaps = acceptance_gaps_for(spec, verdict)
    if gaps:
        return f"{summary} Acceptance gaps: {' '.join(gaps)}"
    target = str(spec.get("acceptance_target") or "acceptance target").strip()
    return f"{summary} Acceptance target satisfied: {target}."


def run_shell(command: str, root: Path) -> dict[str, Any]:
    started_at = utc_now()
    completed = subprocess.run(
        ["/bin/bash", "-lc", command],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": command,
        "started_at": started_at,
        "finished_at": utc_now(),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_command_set(commands: list[str], root: Path) -> dict[str, Any]:
    results = [run_shell(command, root) for command in commands]
    matched = sorted({trigger for trigger in DEFAULT_USER_CONFIRMATION_TRIGGERS if trigger_in_results(trigger, results)})
    return {
        "commands": results,
        "passed": all(item["returncode"] == 0 for item in results),
        "matched_user_confirmation_triggers": matched,
    }


def trigger_in_results(trigger: str, results: list[dict[str, Any]]) -> bool:
    for item in results:
        haystack = f"{item.get('stdout', '')}\n{item.get('stderr', '')}"
        if trigger in haystack:
            return True
    return False


def matched_triggers(triggers: list[str], result_groups: list[dict[str, Any]]) -> list[str]:
    matched: list[str] = []
    for trigger in triggers:
        if any(trigger_in_results(trigger, group["commands"]) for group in result_groups):
            matched.append(trigger)
    return sorted(set(matched))


def write_gate(root: Path, spec: dict[str, Any], gate_payload: dict[str, Any]) -> Path:
    path = gate_path(root, spec["plan_id"], spec["checkpoint"])
    gate_payload["updated_at"] = utc_now()
    gate_payload["checklist_path"] = relpath(
        checklist_path(root, spec["plan_id"], spec["checkpoint"]),
        root,
    )
    dump_json(path, gate_payload)
    return path


def exit_code_for(verdict: str) -> int:
    return NON_PASS_EXIT_CODES.get(verdict, 0)


def command_init(args: argparse.Namespace) -> int:
    root = repo_root(args.root)
    find_plan(root, args.id)
    spec = default_spec(args)
    cpath = checklist_path(root, args.id, args.checkpoint)
    gpath = gate_path(root, args.id, args.checkpoint)

    if args.force or not cpath.exists():
        cpath.parent.mkdir(parents=True, exist_ok=True)
        cpath.write_text(render_checklist(spec), encoding="utf-8")

    gate_payload = load_gate_or_default(root, spec)
    if not gpath.exists():
        write_gate(root, spec, gate_payload)

    response = {
        "plan_id": spec["plan_id"],
        "checkpoint": spec["checkpoint"],
        "checklist_path": relpath(cpath, root),
        "gate_path": relpath(gpath, root),
        "verdict": gate_payload["verdict"],
    }
    print(json.dumps(response, indent=2, ensure_ascii=True))
    return 0


def command_check(args: argparse.Namespace) -> int:
    root = repo_root(args.root)
    find_plan(root, args.id)
    cpath = checklist_path(root, args.id, args.checkpoint)
    spec = parse_checklist_spec(cpath)
    validation_commands = list(spec.get("validation_commands") or [])
    auto_fix_commands = list(spec.get("auto_fix_commands") or [])
    triggers = list(spec.get("user_confirmation_triggers") or DEFAULT_USER_CONFIRMATION_TRIGGERS)
    allow_auto_fix = bool(spec.get("allow_auto_fix"))
    max_auto_fix_rounds = int(spec.get("max_auto_fix_rounds", 0))

    if spec.get("plan_id") != args.id:
        fail(f"checklist plan mismatch: expected {args.id}, got {spec.get('plan_id')}")
    if checkpoint_slug(spec.get("checkpoint", "")) != checkpoint_slug(args.checkpoint):
        fail(
            "checklist checkpoint mismatch: "
            f"expected {checkpoint_slug(args.checkpoint)}, got {spec.get('checkpoint')}"
        )
    if not validation_commands:
        fail(f"no validation commands configured in {cpath}")

    gate_payload = load_gate_or_default(root, spec)
    attempt: dict[str, Any] = {
        "attempt": len(gate_payload.get("attempts", [])) + 1,
        "started_at": utc_now(),
        "finished_at": None,
        "validation_results": [],
        "auto_fix_rounds": [],
        "matched_user_confirmation_triggers": [],
    }

    validation_result = run_command_set(validation_commands, root)
    validation_result["round"] = 0
    attempt["validation_results"].append(validation_result)
    matched = matched_triggers(triggers, [validation_result])

    verdict = "pass"
    summary = "Validation passed without remediation."

    if validation_result["passed"]:
        verdict = "pass"
    elif matched:
        verdict = "needs_user_confirmation"
        summary = "Validation matched a configured user-confirmation trigger."
    elif not allow_auto_fix or not auto_fix_commands or max_auto_fix_rounds <= 0:
        verdict = "fail"
        summary = "Validation failed and no bounded auto-remediation path is configured."
    else:
        verdict = "fail"
        summary = "Validation failed after bounded auto-remediation."
        for round_index in range(1, max_auto_fix_rounds + 1):
            auto_fix_result = run_command_set(auto_fix_commands, root)
            auto_fix_result["round"] = round_index
            attempt["auto_fix_rounds"].append(auto_fix_result)
            matched = matched_triggers(triggers, [validation_result, auto_fix_result])
            if matched:
                verdict = "needs_user_confirmation"
                summary = "Auto-remediation hit a configured user-confirmation trigger."
                break

            rerun_validation = run_command_set(validation_commands, root)
            rerun_validation["round"] = round_index
            attempt["validation_results"].append(rerun_validation)
            matched = matched_triggers(triggers, [rerun_validation])
            if matched:
                verdict = "needs_user_confirmation"
                summary = "Revalidation hit a configured user-confirmation trigger."
                break
            if rerun_validation["passed"]:
                verdict = "auto_fixed_pass"
                summary = f"Validation passed after {round_index} bounded auto-fix round(s)."
                break

    attempt["matched_user_confirmation_triggers"] = matched
    attempt["finished_at"] = utc_now()
    gate_payload["plan_id"] = spec["plan_id"]
    gate_payload["checkpoint"] = spec["checkpoint"]
    gate_payload["title"] = spec["title"]
    gate_payload["profile"] = spec["profile"]
    gate_payload["verdict"] = verdict
    gate_payload["summary"] = acceptance_summary_for(spec, verdict, summary)
    gate_payload["waiver"] = gate_payload.get("waiver")
    if spec["profile"] == "acceptance":
        gate_payload["acceptance_target"] = spec.get("acceptance_target", "")
        gate_payload["acceptance_gaps"] = acceptance_gaps_for(spec, verdict)
        gate_payload["required_evidence"] = list(spec.get("required_evidence") or [])
    gate_payload.setdefault("attempts", []).append(attempt)

    path = write_gate(root, spec, gate_payload)
    response = {
        "plan_id": spec["plan_id"],
        "checkpoint": spec["checkpoint"],
        "verdict": verdict,
        "summary": gate_payload["summary"],
        "gate_path": relpath(path, root),
    }
    print(json.dumps(response, indent=2, ensure_ascii=True))
    return exit_code_for(verdict)


def load_status_payload(root: Path, plan_id: str, checkpoint: str) -> dict[str, Any]:
    gpath = gate_path(root, plan_id, checkpoint)
    if gpath.exists():
        payload = load_json(gpath)
        if not isinstance(payload, dict):
            fail(f"invalid gate payload in {gpath}")
        return payload
    cpath = checklist_path(root, plan_id, checkpoint)
    if cpath.exists():
        spec = parse_checklist_spec(cpath)
        return default_gate_payload(root, spec)
    return {
        "plan_id": plan_id,
        "checkpoint": checkpoint_slug(checkpoint),
        "title": checkpoint_slug(checkpoint),
        "profile": "default",
        "verdict": "pending",
        "summary": "Checkpoint artifacts do not exist yet.",
        "updated_at": utc_now(),
        "checklist_path": relpath(cpath, root),
        "attempts": [],
        "waiver": None,
    }


def command_status(args: argparse.Namespace) -> int:
    root = repo_root(args.root)
    find_plan(root, args.id)
    payload = load_status_payload(root, args.id, args.checkpoint)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    else:
        print(
            f"{payload['plan_id']} {payload['checkpoint']} "
            f"{payload['verdict']}: {payload['summary']}"
        )
    return exit_code_for(payload["verdict"])


def command_waive(args: argparse.Namespace) -> int:
    root = repo_root(args.root)
    find_plan(root, args.id)
    cpath = checklist_path(root, args.id, args.checkpoint)
    if cpath.exists():
        spec = parse_checklist_spec(cpath)
    else:
        spec = {
            "plan_id": args.id,
            "checkpoint": checkpoint_slug(args.checkpoint),
            "title": checkpoint_slug(args.checkpoint),
        }
    gate_payload = load_gate_or_default(root, spec)
    gate_payload["verdict"] = "waived"
    gate_payload["summary"] = args.reason
    gate_payload["waiver"] = {
        "reason": args.reason,
        "at": utc_now(),
    }
    path = write_gate(root, spec, gate_payload)
    print(
        json.dumps(
            {
                "plan_id": spec["plan_id"],
                "checkpoint": spec["checkpoint"],
                "verdict": gate_payload["verdict"],
                "gate_path": relpath(path, root),
                "reason": args.reason,
            },
            indent=2,
            ensure_ascii=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Checkpoint gatekeeper CLI")
    parser.add_argument("--root", default=".", help="Repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize checklist and gate artifacts")
    init_parser.add_argument("--id", required=True, help="Plan ID")
    init_parser.add_argument("--checkpoint", required=True, help="Checkpoint name or CHK-* id")
    init_parser.add_argument("--title", help="Human-readable checkpoint title")
    init_parser.add_argument(
        "--profile",
        choices=sorted(VALID_PROFILES),
        default="default",
        help="Checkpoint profile. Default: default.",
    )
    init_parser.add_argument(
        "--acceptance-target",
        help="Semantic acceptance target summary for acceptance profile checkpoints",
    )
    init_parser.add_argument(
        "--required-evidence",
        action="append",
        default=[],
        help="Required evidence item for acceptance profile checkpoints",
    )
    init_parser.add_argument(
        "--validation-command",
        action="append",
        default=[],
        help="Validation command to run inside repo root",
    )
    init_parser.add_argument(
        "--auto-fix-command",
        action="append",
        default=[],
        help="Bounded auto-fix command to run inside repo root",
    )
    init_parser.add_argument(
        "--user-confirmation-trigger",
        action="append",
        default=[],
        help="Output token that forces needs_user_confirmation",
    )
    init_parser.add_argument(
        "--max-auto-fix-rounds",
        type=int,
        default=1,
        help="Maximum bounded auto-fix rounds",
    )
    init_parser.add_argument(
        "--allow-auto-fix",
        action="store_true",
        help="Allow bounded auto-fix even if only validation commands are configured",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Rewrite checklist skeleton if it already exists",
    )
    init_parser.set_defaults(func=command_init)

    check_parser = subparsers.add_parser("check", help="Run gate validation loop")
    check_parser.add_argument("--id", required=True, help="Plan ID")
    check_parser.add_argument("--checkpoint", required=True, help="Checkpoint name or CHK-* id")
    check_parser.set_defaults(func=command_check)

    status_parser = subparsers.add_parser("status", help="Inspect current gate verdict")
    status_parser.add_argument("--id", required=True, help="Plan ID")
    status_parser.add_argument("--checkpoint", required=True, help="Checkpoint name or CHK-* id")
    status_parser.add_argument("--json", action="store_true", help="Print full JSON payload")
    status_parser.set_defaults(func=command_status)

    waive_parser = subparsers.add_parser("waive", help="Explicitly waive a checkpoint")
    waive_parser.add_argument("--id", required=True, help="Plan ID")
    waive_parser.add_argument("--checkpoint", required=True, help="Checkpoint name or CHK-* id")
    waive_parser.add_argument("--reason", required=True, help="Explicit waiver reason")
    waive_parser.set_defaults(func=command_waive)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
