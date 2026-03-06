#!/usr/bin/env python3
"""Experience capture operations.

This script manages reusable experience cards. It is intentionally focused on
storage and retrieval contracts (init/create/list/link) and does not implement
runtime trigger scoring.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_TRIGGER_MODES = {"manual-explicit", "suggest-once"}
SOURCE_EVENT_ID_PATTERN = re.compile(r"^MEM-EVT-[A-Za-z0-9][A-Za-z0-9._:-]*$")
WINDOWS_ABS_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def is_absolute_ref(value: str) -> bool:
    stripped = value.strip()
    return stripped.startswith("/") or bool(WINDOWS_ABS_PATTERN.match(stripped))


def validate_doc_refs(doc_refs: List[str]) -> None:
    for ref in doc_refs:
        if is_absolute_ref(ref):
            raise ValueError(f"doc ref must be repo-relative (not absolute): {ref}")


def validate_source_event_refs(source_event_refs: List[str]) -> None:
    for ref in source_event_refs:
        if SOURCE_EVENT_ID_PATTERN.fullmatch(ref):
            continue
        if is_absolute_ref(ref):
            raise ValueError(f"source event ref must be repo-relative or MEM-EVT id: {ref}")
        if "/" in ref and "#" in ref:
            continue
        raise ValueError(
            "source event ref must be MEM-EVT-* or relative path with #anchor, got: "
            + ref
        )


def get_paths(root: Path) -> Dict[str, Path]:
    base = root / "docs" / "experience"
    return {
        "base": base,
        "index": base / "EXPERIENCE_INDEX.json",
        "cards": base / "cards",
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_storage(root: Path) -> Dict[str, Path]:
    paths = get_paths(root)
    paths["base"].mkdir(parents=True, exist_ok=True)
    paths["cards"].mkdir(parents=True, exist_ok=True)

    now = utc_now()
    if not paths["index"].exists():
        write_json(
            paths["index"],
            {
                "version": 1,
                "schema_version": "2026-03-06",
                "created_at": now,
                "updated_at": now,
                "card_seq": 0,
                "card_count": 0,
                "last_card_id": None,
            },
        )

    return paths


def require_initialized(root: Path) -> Dict[str, Path]:
    paths = get_paths(root)
    required = [paths["index"], paths["cards"]]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise ValueError("experience storage not initialized, run `init` first: " + ", ".join(missing))
    return paths


def load_cards(paths: Dict[str, Path]) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for file in sorted(paths["cards"].glob("EXP-*.json")):
        try:
            cards.append(read_json(file))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid card JSON: {file}: {exc}") from exc
    return cards


def dedupe_list(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for raw in items:
        item = raw.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def next_card_id(index: Dict[str, Any]) -> str:
    seq = int(index.get("card_seq", 0)) + 1
    index["card_seq"] = seq
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"EXP-{stamp}-{seq:04d}"


def card_path(paths: Dict[str, Path], card_id: str) -> Path:
    return paths["cards"] / f"{card_id}.json"


def get_card(paths: Dict[str, Path], card_id: str) -> Dict[str, Any]:
    target = card_path(paths, card_id)
    if not target.exists():
        raise ValueError(f"card not found: {card_id}")
    return read_json(target)


def update_index_after_write(paths: Dict[str, Path], index: Dict[str, Any], card_id: str) -> None:
    cards = load_cards(paths)
    index["card_count"] = len(cards)
    index["last_card_id"] = card_id
    index["updated_at"] = utc_now()
    write_json(paths["index"], index)


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_storage(root)
    print(f"initialized: {paths['base']}")
    print(f"index: {paths['index']}")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = ensure_storage(root)
    index = read_json(paths["index"])

    title = args.title.strip()
    problem_signature = args.problem_signature.strip()
    decision_rules = dedupe_list(args.decision_rule)
    review_checklist = dedupe_list(args.review_item)
    source_event_refs = dedupe_list(args.source_event_ref)
    doc_refs = dedupe_list(args.doc_ref)
    tags = dedupe_list(args.tag)
    context_constraints = dedupe_list(args.context_constraint)
    anti_patterns = dedupe_list(args.anti_pattern)

    if len(decision_rules) < 2:
        raise ValueError("at least 2 --decision-rule entries are required")
    if len(review_checklist) < 3:
        raise ValueError("at least 3 --review-item entries are required")
    if len(source_event_refs) < 1:
        raise ValueError("at least 1 --source-event-ref entry is required")
    validate_source_event_refs(source_event_refs)
    validate_doc_refs(doc_refs)

    card_id = args.id.strip() if args.id else next_card_id(index)
    if not re.fullmatch(r"EXP-[0-9]{8}-[0-9]{4}", card_id):
        raise ValueError("card id must match EXP-YYYYMMDD-NNNN")

    target = card_path(paths, card_id)
    if target.exists():
        raise ValueError(f"card id already exists: {card_id}")

    now = utc_now()
    card: Dict[str, Any] = {
        "id": card_id,
        "created_at": now,
        "updated_at": now,
        "title": title,
        "problem_signature": problem_signature,
        "problem_signature_norm": normalize_text(problem_signature),
        "decision_rules": decision_rules,
        "review_checklist": review_checklist,
        "source_event_refs": source_event_refs,
        "doc_refs": doc_refs,
        "tags": tags,
    }

    if context_constraints:
        card["context_constraints"] = context_constraints
    if anti_patterns:
        card["anti_patterns"] = anti_patterns
    if args.outcome:
        card["outcome"] = args.outcome.strip()
    if args.confidence:
        card["confidence"] = args.confidence
    if args.owner:
        card["owner"] = args.owner.strip()

    confirmation_note = args.confirmation_note.strip() if args.confirmation_note else ""
    if not confirmation_note:
        confirmation_note = (
            "User confirmation obtained during experience capture."
            if args.confirmed_by_user
            else "Pending explicit user confirmation."
        )
    capture_meta: Dict[str, Any] = {
        "trigger_mode": args.trigger_mode,
        "confirmed_by_user": bool(args.confirmed_by_user),
        "confirmation_note": confirmation_note,
    }
    if args.confirmed_by_user:
        capture_meta["confirmed_at"] = now
    card["capture_meta"] = capture_meta

    write_json(target, card)
    update_index_after_write(paths, index, card_id)

    if args.json:
        print(json.dumps(card, indent=2, ensure_ascii=False))
    else:
        print(f"created: {card_id}")
        print(f"path: {target}")
    return 0


def filter_cards(
    cards: List[Dict[str, Any]],
    *,
    tags: List[str],
    problem_signature: str | None,
) -> List[Dict[str, Any]]:
    filtered = cards

    if tags:
        required = set(tags)
        filtered = [
            card
            for card in filtered
            if required.issubset(set(card.get("tags", [])))
        ]

    if problem_signature:
        needle = normalize_text(problem_signature)
        filtered = [
            card
            for card in filtered
            if needle in normalize_text(card.get("problem_signature", ""))
            or needle in normalize_text(card.get("title", ""))
        ]

    return filtered


def summarize_card(card: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": card.get("id"),
        "created_at": card.get("created_at"),
        "title": card.get("title"),
        "problem_signature": card.get("problem_signature"),
        "tags": card.get("tags", []),
        "source_event_refs": card.get("source_event_refs", []),
    }


def render_table(cards: List[Dict[str, Any]]) -> str:
    lines = ["id | title | tags", "--- | --- | ---"]
    if not cards:
        lines.append("(none) | (none) | (none)")
    for card in cards:
        tags = ",".join(card.get("tags", []))
        lines.append(f"{card.get('id')} | {card.get('title')} | {tags}")
    return "\n".join(lines)


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = require_initialized(root)
    cards = load_cards(paths)

    cards = filter_cards(cards, tags=dedupe_list(args.tag), problem_signature=args.problem_signature)
    cards.sort(key=lambda item: (item.get("created_at", ""), item.get("id", "")), reverse=True)

    if args.limit is not None:
        cards = cards[: max(args.limit, 0)]

    payload_cards = cards if args.full else [summarize_card(card) for card in cards]
    payload = {
        "count": len(payload_cards),
        "cards": payload_cards,
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        table_cards = cards if args.full else payload_cards
        print(render_table(table_cards))
    return 0


def cmd_link(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = require_initialized(root)
    index = read_json(paths["index"])

    source_event_refs = dedupe_list(args.source_event_ref)
    doc_refs = dedupe_list(args.doc_ref)
    experience_refs = dedupe_list(args.experience_ref)

    if not (source_event_refs or doc_refs or experience_refs):
        raise ValueError("provide at least one link: --source-event-ref / --doc-ref / --experience-ref")
    if source_event_refs:
        validate_source_event_refs(source_event_refs)
    if doc_refs:
        validate_doc_refs(doc_refs)

    card = get_card(paths, args.id)
    card["source_event_refs"] = dedupe_list(card.get("source_event_refs", []) + source_event_refs)
    card["doc_refs"] = dedupe_list(card.get("doc_refs", []) + doc_refs)
    card["experience_refs"] = dedupe_list(card.get("experience_refs", []) + experience_refs)
    card["updated_at"] = utc_now()

    target = card_path(paths, args.id)
    write_json(target, card)
    update_index_after_write(paths, index, args.id)

    if args.json:
        print(json.dumps(card, indent=2, ensure_ascii=False))
    else:
        print(f"linked: {args.id}")
        print(
            "added: source_event_refs={s} doc_refs={d} experience_refs={e}".format(
                s=len(source_event_refs),
                d=len(doc_refs),
                e=len(experience_refs),
            )
        )
    return 0


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Experience capture operations")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize experience storage")
    init.add_argument("--root", default=".", help="Repository root (default: .)")

    create = sub.add_parser("create", help="Create an experience card")
    create.add_argument("--root", default=".", help="Repository root (default: .)")
    create.add_argument("--id", help="Optional explicit card ID (EXP-YYYYMMDD-NNNN)")
    create.add_argument("--title", required=True, help="Card title")
    create.add_argument("--problem-signature", required=True, help="Reusable problem signature")
    create.add_argument("--decision-rule", action="append", default=[], help="Decision rule (repeatable)")
    create.add_argument("--review-item", action="append", default=[], help="Review checklist item (repeatable)")
    create.add_argument(
        "--source-event-ref",
        action="append",
        default=[],
        help="Source event pointer (repeatable)",
    )
    create.add_argument("--doc-ref", action="append", default=[], help="Document pointer (repeatable)")
    create.add_argument("--tag", action="append", default=[], help="Tag (repeatable)")
    create.add_argument(
        "--context-constraint",
        action="append",
        default=[],
        help="Context constraint (repeatable)",
    )
    create.add_argument("--anti-pattern", action="append", default=[], help="Anti-pattern (repeatable)")
    create.add_argument("--outcome", help="Outcome summary")
    create.add_argument("--confidence", choices=sorted(VALID_CONFIDENCE), help="Confidence level")
    create.add_argument(
        "--trigger-mode",
        choices=sorted(VALID_TRIGGER_MODES),
        default="manual-explicit",
        help="Trigger path used for this capture",
    )
    create.add_argument(
        "--confirmed-by-user",
        dest="confirmed_by_user",
        action="store_true",
        help="Mark capture as explicitly confirmed by user (default)",
    )
    create.add_argument(
        "--unconfirmed",
        dest="confirmed_by_user",
        action="store_false",
        help="Mark capture as not yet explicitly confirmed by user",
    )
    create.set_defaults(confirmed_by_user=True)
    create.add_argument("--confirmation-note", help="Confirmation context note")
    create.add_argument("--owner", default="codex", help="Recorder identity")
    create.add_argument("--json", action="store_true", help="Print JSON output")

    list_cmd = sub.add_parser("list", help="List experience cards")
    list_cmd.add_argument("--root", default=".", help="Repository root (default: .)")
    list_cmd.add_argument("--tag", action="append", default=[], help="Tag filter (repeatable, AND semantics)")
    list_cmd.add_argument("--problem-signature", help="Problem signature keyword filter")
    list_cmd.add_argument("--limit", type=int, help="Result limit")
    list_cmd.add_argument("--full", action="store_true", help="Return full card payload")
    list_cmd.add_argument("--format", choices=["json", "table"], default="json")

    link = sub.add_parser("link", help="Append references to an existing card")
    link.add_argument("--root", default=".", help="Repository root (default: .)")
    link.add_argument("--id", required=True, help="Card ID")
    link.add_argument(
        "--source-event-ref",
        action="append",
        default=[],
        help="Source event pointer to append",
    )
    link.add_argument("--doc-ref", action="append", default=[], help="Doc pointer to append")
    link.add_argument("--experience-ref", action="append", default=[], help="Cross-experience pointer to append")
    link.add_argument("--json", action="store_true", help="Print JSON output")

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "init":
            return cmd_init(args)
        if args.command == "create":
            return cmd_create(args)
        if args.command == "list":
            return cmd_list(args)
        if args.command == "link":
            return cmd_link(args)
        parser.error(f"unknown command: {args.command}")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
