#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  release.sh [--dev-root PATH] [--runtime-root PATH] [--dry-run] [--no-delete]

Options:
  --dev-root PATH       Skill development root. Defaults to script parent.
  --runtime-root PATH   Target runtime skill directory.
  --dry-run             Show rsync changes without writing.
  --no-delete           Do not delete extra files at target.
  -h, --help            Show this help message.

Environment:
  DEV_ROOT, RUNTIME_ROOT
  CODEX_HOME            Used to infer runtime root when RUNTIME_ROOT is not set.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_DEV_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEV_ROOT="${DEV_ROOT:-$DEFAULT_DEV_ROOT}"
RUNTIME_ROOT="${RUNTIME_ROOT:-}"

DRY_RUN=0
DELETE_FLAG="--delete"

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
    --runtime-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --runtime-root requires a value" >&2
        exit 1
      fi
      RUNTIME_ROOT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-delete)
      DELETE_FLAG=""
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
if [[ -z "$RUNTIME_ROOT" ]]; then
  SKILL_NAME="$(basename "$DEV_ROOT")"
  if [[ -n "${CODEX_HOME:-}" ]]; then
    RUNTIME_ROOT="$CODEX_HOME/skills/$SKILL_NAME"
  elif [[ -n "${HOME:-}" ]]; then
    RUNTIME_ROOT="$HOME/.codex/skills/$SKILL_NAME"
  fi
fi

if [[ ! -f "$DEV_ROOT/SKILL.md" ]]; then
  echo "error: SKILL.md not found under dev root: $DEV_ROOT" >&2
  exit 1
fi

if [[ -z "$RUNTIME_ROOT" ]]; then
  echo "error: runtime root is empty; set --runtime-root or RUNTIME_ROOT" >&2
  exit 1
fi

mkdir -p "$RUNTIME_ROOT"

RSYNC_ARGS=(-av)
if [[ "$DRY_RUN" -eq 1 ]]; then
  RSYNC_ARGS+=(--dry-run)
fi
if [[ -n "$DELETE_FLAG" ]]; then
  RSYNC_ARGS+=("$DELETE_FLAG")
fi

rsync "${RSYNC_ARGS[@]}" \
  --exclude '.git' \
  --exclude '.gitignore' \
  --exclude '__pycache__' \
  --exclude '.devtools/' \
  "$DEV_ROOT/" "$RUNTIME_ROOT/"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run release: $DEV_ROOT -> $RUNTIME_ROOT"
else
  echo "released: $DEV_ROOT -> $RUNTIME_ROOT"
fi
