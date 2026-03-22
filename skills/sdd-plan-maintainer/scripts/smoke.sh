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
  TMP_ROOT="$(mktemp -d /tmp/sdd-plan-smoke-XXXXXX)"
fi
mkdir -p "$TMP_ROOT"

export PYTHONPYCACHEPREFIX="$TMP_ROOT/.pycache"
PLAN_OPS="$SKILL_ROOT/scripts/plan_ops.py"

if [[ ! -f "$PLAN_OPS" ]]; then
  echo "error: plan ops script not found: $PLAN_OPS" >&2
  exit 1
fi

"$PYTHON_BIN" -m py_compile "$PLAN_OPS"
"$PYTHON_BIN" "$PLAN_OPS" --help >/dev/null

"$PYTHON_BIN" "$PLAN_OPS" ensure --root "$TMP_ROOT" >/dev/null
"$PYTHON_BIN" "$PLAN_OPS" create --root "$TMP_ROOT" \
  --id PLAN-SMOKE-001 --title "Smoke Validation" --kind feature --priority P1 >/dev/null
"$PYTHON_BIN" "$PLAN_OPS" status --root "$TMP_ROOT" \
  --id PLAN-SMOKE-001 --status in_progress --note "smoke start" >/dev/null
"$PYTHON_BIN" "$PLAN_OPS" status --root "$TMP_ROOT" \
  --id PLAN-SMOKE-001 --status superseded --note "Superseded by newer diagnosis during smoke" >/dev/null
"$PYTHON_BIN" "$PLAN_OPS" doctor --root "$TMP_ROOT" >/dev/null
"$PYTHON_BIN" "$PLAN_OPS" dashboard --root "$TMP_ROOT" >/dev/null

PLAN_FILE="$TMP_ROOT/docs/plans/active/PLAN-SMOKE-001.md"
sed -i 's/^- Status: superseded$/- Status: completed/' "$PLAN_FILE"

if "$PYTHON_BIN" "$PLAN_OPS" doctor --root "$TMP_ROOT" >/dev/null; then
  echo "error: expected doctor to fail on doc status drift" >&2
  exit 1
fi

"$PYTHON_BIN" "$PLAN_OPS" doctor --root "$TMP_ROOT" --fix >/dev/null
"$PYTHON_BIN" "$PLAN_OPS" doctor --root "$TMP_ROOT" >/dev/null

echo "sdd-plan-maintainer smoke passed: $TMP_ROOT"
