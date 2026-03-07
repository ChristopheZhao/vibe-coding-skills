#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  smoke.sh [--repo-root PATH] [--skill-root PATH] [--python BIN] [--tmp-root PATH]

Options:
  --repo-root PATH  Repository root (optional; not required by this smoke flow).
  --skill-root PATH Skill root. Defaults to script parent.
  --python BIN      Python executable. Default: python3.
  --tmp-root PATH   Temporary test root. If omitted, mktemp is used.
  -h, --help        Show this help message.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_ROOT="$DEFAULT_SKILL_ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TMP_ROOT="${TMP_ROOT:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --repo-root requires a value" >&2
        exit 1
      fi
      shift 2
      ;;
    --skill-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --skill-root requires a value" >&2
        exit 1
      fi
      SKILL_ROOT="$2"
      shift 2
      ;;
    --python)
      if [[ $# -lt 2 ]]; then
        echo "error: --python requires a value" >&2
        exit 1
      fi
      PYTHON_BIN="$2"
      shift 2
      ;;
    --tmp-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --tmp-root requires a value" >&2
        exit 1
      fi
      TMP_ROOT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ "$SKILL_ROOT" != /* ]]; then
  SKILL_ROOT="$(cd "$SKILL_ROOT" && pwd)"
fi

if [[ -z "$TMP_ROOT" ]]; then
  TMP_ROOT="$(mktemp -d /tmp/layered-memory-smoke-XXXXXX)"
fi
mkdir -p "$TMP_ROOT"

export PYTHONPYCACHEPREFIX="$TMP_ROOT/.pycache"
MEMORY_OPS="$SKILL_ROOT/scripts/memory_ops.py"

if [[ ! -f "$MEMORY_OPS" ]]; then
  echo "error: memory ops script not found: $MEMORY_OPS" >&2
  exit 1
fi

"$PYTHON_BIN" -m py_compile "$MEMORY_OPS"
"$PYTHON_BIN" "$MEMORY_OPS" --help >/dev/null

"$PYTHON_BIN" "$MEMORY_OPS" init --root "$TMP_ROOT" >/dev/null
"$PYTHON_BIN" "$MEMORY_OPS" capture --root "$TMP_ROOT" \
  --topic-id smoke-topic \
  --event-type decision \
  --summary "select pointer-first memory capture policy" \
  --impact high \
  --result mixed \
  --problem-key smoke-pointer-policy \
  --doc-ref docs/adr/0001-memory-policy.md#decision \
  --evidence logs/smoke-capture.txt \
  --next-action "run resume retrieval profile" >/dev/null

RETRIEVE_OUTPUT="$("$PYTHON_BIN" "$MEMORY_OPS" retrieve --root "$TMP_ROOT" --profile resume --topic-id smoke-topic --format json)"
if ! printf '%s' "$RETRIEVE_OUTPUT" | grep -q '"topic_id": "smoke-topic"'; then
  echo "error: retrieve output missing topic_id scope" >&2
  exit 1
fi

"$PYTHON_BIN" "$MEMORY_OPS" summarize --root "$TMP_ROOT" --topic-id smoke-topic --profile resume --mode incremental >/dev/null
if [[ ! -f "$TMP_ROOT/docs/memory/summary/current.json" ]]; then
  echo "error: summary JSON not generated" >&2
  exit 1
fi

"$PYTHON_BIN" "$MEMORY_OPS" doctor --root "$TMP_ROOT" >/dev/null

echo "layered-project-memory smoke passed: $TMP_ROOT"
