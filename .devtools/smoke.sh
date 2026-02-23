#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  smoke.sh [--dev-root PATH] [--python BIN] [--tmp-root PATH] [--keep-tmp]

Options:
  --dev-root PATH   Skill development root. Defaults to script parent.
  --python BIN      Python executable to run checks. Default: python3.
  --tmp-root PATH   Test repository root. If omitted, uses mktemp.
  --keep-tmp        Keep tmp root after completion.
  -h, --help        Show this help message.

Environment:
  DEV_ROOT, PYTHON_BIN, TMP_ROOT
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_DEV_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEV_ROOT="${DEV_ROOT:-$DEFAULT_DEV_ROOT}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TMP_ROOT="${TMP_ROOT:-}"
KEEP_TMP=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --dev-root requires a value" >&2
        exit 1
      fi
      DEV_ROOT="$2"
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
    --keep-tmp)
      KEEP_TMP=1
      shift
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

DEV_ROOT="$(cd "$DEV_ROOT" && pwd)"
if [[ -z "$TMP_ROOT" ]]; then
  TMP_ROOT="$(mktemp -d /tmp/sdd-plan-smoke-XXXXXX)"
else
  mkdir -p "$TMP_ROOT"
fi

cleanup() {
  if [[ "$KEEP_TMP" -eq 0 ]]; then
    rm -rf "$TMP_ROOT"
  fi
}
trap cleanup EXIT

# Redirect pycache writes to tmp so readonly/mounted paths do not fail smoke.
export PYTHONPYCACHEPREFIX="$TMP_ROOT/.pycache"

"$PYTHON_BIN" -m py_compile "$DEV_ROOT/scripts/plan_ops.py"
"$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" --help >/dev/null

"$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" ensure --root "$TMP_ROOT" >/dev/null
"$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" create --root "$TMP_ROOT" \
  --id PLAN-SMOKE-001 --title "Smoke Validation" --kind feature --priority P1 >/dev/null
"$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" status --root "$TMP_ROOT" \
  --id PLAN-SMOKE-001 --status in_progress --note "smoke start" >/dev/null
"$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" doctor --root "$TMP_ROOT" >/dev/null
"$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" dashboard --root "$TMP_ROOT" >/dev/null

PLAN_FILE="$TMP_ROOT/docs/plans/active/PLAN-SMOKE-001.md"
sed -i 's/^- Status: in_progress$/- Status: completed/' "$PLAN_FILE"

if "$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" doctor --root "$TMP_ROOT" >/dev/null; then
  echo "error: expected doctor to fail on doc status drift" >&2
  exit 1
fi

"$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" doctor --root "$TMP_ROOT" --fix >/dev/null
"$PYTHON_BIN" "$DEV_ROOT/scripts/plan_ops.py" doctor --root "$TMP_ROOT" >/dev/null

echo "smoke passed: $TMP_ROOT"
