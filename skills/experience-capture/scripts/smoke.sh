#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  smoke.sh [--repo-root PATH] [--skill-root PATH] [--python BIN] [--tmp-root PATH]

Options:
  --repo-root PATH  Repository root (optional; not required by this smoke flow).
  --skill-root PATH Skill root. Defaults to script parent.
  --python BIN      Python executable. Default: python3.
  --tmp-root PATH   Temporary test root. If omitted, mktemp is used.
  -h, --help        Show this help message.
USAGE
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
  TMP_ROOT="$(mktemp -d /tmp/experience-capture-smoke-XXXXXX)"
fi
mkdir -p "$TMP_ROOT"

export PYTHONPYCACHEPREFIX="$TMP_ROOT/.pycache"
EXP_OPS="$SKILL_ROOT/scripts/exp_ops.py"

if [[ ! -f "$EXP_OPS" ]]; then
  echo "error: experience ops script not found: $EXP_OPS" >&2
  exit 1
fi

"$PYTHON_BIN" -m py_compile "$EXP_OPS"
"$PYTHON_BIN" "$EXP_OPS" --help >/dev/null

"$PYTHON_BIN" "$EXP_OPS" init --root "$TMP_ROOT" >/dev/null
"$PYTHON_BIN" "$EXP_OPS" create --root "$TMP_ROOT" \
  --title "smoke card" \
  --problem-signature "orchestration bool route drift" \
  --decision-rule "use action-level plan params" \
  --decision-rule "treat fallback as runtime replan" \
  --review-item "name-behavior alignment" \
  --review-item "no cross-agent bool coupling" \
  --review-item "not global-variable equivalent" \
  --source-event-ref "MEM-EVT-SMOKE-001" \
  --tag "smoke" \
  --tag "orchestrator" >/dev/null

LIST_OUTPUT="$("$PYTHON_BIN" "$EXP_OPS" list --root "$TMP_ROOT" --tag smoke --format json)"
if ! printf '%s' "$LIST_OUTPUT" | grep -q '"count": 1'; then
  echo "error: list output missing expected count" >&2
  exit 1
fi

CARD_ID="$(printf '%s' "$LIST_OUTPUT" | "$PYTHON_BIN" -c 'import json,sys; data=json.loads(sys.stdin.read()); print(data["cards"][0]["id"])')"
"$PYTHON_BIN" "$EXP_OPS" link --root "$TMP_ROOT" --id "$CARD_ID" \
  --doc-ref docs/knowledge/experience-skill-alignment-record.md \
  --experience-ref EXP-20260301-0001 >/dev/null

echo "experience-capture smoke passed: $TMP_ROOT"
