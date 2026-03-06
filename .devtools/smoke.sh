#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  smoke.sh [--repo-root PATH] [--skill-dir PATH] [--python BIN] [--tmp-root PATH] [--keep-tmp]

Options:
  --repo-root PATH  Repository root. Defaults to script parent.
  --skill-dir PATH  Skill source directory (absolute or repo-relative).
                    Default: skills/sdd-plan-maintainer
  --python BIN      Python executable to run checks. Default: python3.
  --tmp-root PATH   Test repository root. If omitted, uses mktemp.
  --keep-tmp        Keep tmp root after completion.
  -h, --help        Show this help message.

Environment:
  REPO_ROOT, SKILL_DIR, PYTHON_BIN, TMP_ROOT
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-$DEFAULT_REPO_ROOT}"
SKILL_DIR="${SKILL_DIR:-skills/sdd-plan-maintainer}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TMP_ROOT="${TMP_ROOT:-}"
KEEP_TMP=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --repo-root requires a value" >&2
        exit 1
      fi
      REPO_ROOT="$2"
      shift 2
      ;;
    --skill-dir)
      if [[ $# -lt 2 ]]; then
        echo "error: --skill-dir requires a value" >&2
        exit 1
      fi
      SKILL_DIR="$2"
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

REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
if [[ "$SKILL_DIR" = /* ]]; then
  SKILL_ROOT="$SKILL_DIR"
else
  SKILL_ROOT="$REPO_ROOT/$SKILL_DIR"
fi
SKILL_ROOT="$(cd "$SKILL_ROOT" && pwd)"

if [[ ! -f "$SKILL_ROOT/SKILL.md" ]]; then
  echo "error: SKILL.md not found under skill root: $SKILL_ROOT" >&2
  exit 1
fi

SMOKE_SH="$SKILL_ROOT/scripts/smoke.sh"
SMOKE_PY="$SKILL_ROOT/scripts/smoke.py"
SMOKE_CMD=()
if [[ -f "$SMOKE_SH" ]]; then
  SMOKE_CMD=("bash" "$SMOKE_SH")
elif [[ -f "$SMOKE_PY" ]]; then
  SMOKE_CMD=("$PYTHON_BIN" "$SMOKE_PY")
else
  echo "error: no smoke entry found for skill: $SKILL_ROOT (expected scripts/smoke.sh or scripts/smoke.py)" >&2
  exit 1
fi

if [[ -z "$TMP_ROOT" ]]; then
  TMP_ROOT="$(mktemp -d "/tmp/$(basename "$SKILL_ROOT")-smoke-XXXXXX")"
else
  mkdir -p "$TMP_ROOT"
fi

cleanup() {
  if [[ "$KEEP_TMP" -eq 0 ]]; then
    rm -rf "$TMP_ROOT"
  fi
}
trap cleanup EXIT

"${SMOKE_CMD[@]}" \
  --repo-root "$REPO_ROOT" \
  --skill-root "$SKILL_ROOT" \
  --python "$PYTHON_BIN" \
  --tmp-root "$TMP_ROOT"

echo "smoke passed: skill=$(basename "$SKILL_ROOT") tmp=$TMP_ROOT"
