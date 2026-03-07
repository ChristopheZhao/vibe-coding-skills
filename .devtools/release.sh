#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  release.sh [--repo-root PATH] [--skill-dir PATH] [--skill-name NAME] [--tool codex|claude|cursor|gemini|copilot] [--runtime-root PATH] [--dry-run] [--no-delete]

Options:
  --repo-root PATH      Repository root. Defaults to script parent.
  --skill-dir PATH      Skill source directory (absolute or repo-relative).
                        Default: skills/sdd-plan-maintainer
  --skill-name NAME     Skill folder name in runtime target. Default: basename(skill-dir)
  --tool NAME           Target tool profile. One of: codex, claude, cursor, gemini, copilot.
                        Default: codex.
  --runtime-root PATH   Target runtime skill directory.
  --dry-run             Show rsync changes without writing.
  --no-delete           Do not delete extra files at target.
  -h, --help            Show this help message.

Environment:
  REPO_ROOT, SKILL_DIR, SKILL_NAME, TOOL, RUNTIME_ROOT
  CODEX_HOME            Used to infer runtime root when RUNTIME_ROOT is not set.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-$DEFAULT_REPO_ROOT}"
SKILL_DIR="${SKILL_DIR:-skills/sdd-plan-maintainer}"
SKILL_NAME="${SKILL_NAME:-}"
TOOL="${TOOL:-codex}"
RUNTIME_ROOT="${RUNTIME_ROOT:-}"

DRY_RUN=0
DELETE_FLAG="--delete"

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
    --skill-name)
      if [[ $# -lt 2 ]]; then
        echo "error: --skill-name requires a value" >&2
        exit 1
      fi
      SKILL_NAME="$2"
      shift 2
      ;;
    --tool)
      if [[ $# -lt 2 ]]; then
        echo "error: --tool requires a value" >&2
        exit 1
      fi
      TOOL="$2"
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

REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
TOOL="$(printf '%s' "$TOOL" | tr '[:upper:]' '[:lower:]')"
case "$TOOL" in
  codex|claude|cursor|gemini|copilot) ;;
  *)
    echo "error: unsupported --tool value: $TOOL (expected codex|claude|cursor|gemini|copilot)" >&2
    exit 1
    ;;
esac
if [[ "$SKILL_DIR" = /* ]]; then
  SKILL_ROOT="$SKILL_DIR"
else
  SKILL_ROOT="$REPO_ROOT/$SKILL_DIR"
fi
SKILL_ROOT="$(cd "$SKILL_ROOT" && pwd)"
if [[ -z "$SKILL_NAME" ]]; then
  SKILL_NAME="$(basename "$SKILL_ROOT")"
fi

if [[ -z "$RUNTIME_ROOT" ]]; then
  case "$TOOL" in
    codex)
      if [[ -n "${CODEX_HOME:-}" ]]; then
        RUNTIME_ROOT="$CODEX_HOME/skills/$SKILL_NAME"
      elif [[ -n "${HOME:-}" ]]; then
        RUNTIME_ROOT="$HOME/.codex/skills/$SKILL_NAME"
      fi
      ;;
    claude)
      if [[ -n "${CLAUDE_HOME:-}" ]]; then
        RUNTIME_ROOT="$CLAUDE_HOME/skills/$SKILL_NAME"
      elif [[ -n "${HOME:-}" ]]; then
        RUNTIME_ROOT="$HOME/.claude/skills/$SKILL_NAME"
      fi
      ;;
    cursor)
      if [[ -n "${CURSOR_HOME:-}" ]]; then
        RUNTIME_ROOT="$CURSOR_HOME/skills/$SKILL_NAME"
      elif [[ -n "${HOME:-}" ]]; then
        RUNTIME_ROOT="$HOME/.cursor/skills/$SKILL_NAME"
      fi
      ;;
    gemini)
      if [[ -n "${GEMINI_HOME:-}" ]]; then
        RUNTIME_ROOT="$GEMINI_HOME/skills/$SKILL_NAME"
      elif [[ -n "${HOME:-}" ]]; then
        RUNTIME_ROOT="$HOME/.gemini/skills/$SKILL_NAME"
      fi
      ;;
    copilot)
      if [[ -n "${COPILOT_HOME:-}" ]]; then
        RUNTIME_ROOT="$COPILOT_HOME/skills/$SKILL_NAME"
      elif [[ -n "${HOME:-}" ]]; then
        RUNTIME_ROOT="$HOME/.copilot/skills/$SKILL_NAME"
      fi
      ;;
  esac
fi

if [[ ! -f "$SKILL_ROOT/SKILL.md" ]]; then
  echo "error: SKILL.md not found under skill root: $SKILL_ROOT" >&2
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
  RSYNC_ARGS+=(--delete-excluded)
fi

rsync "${RSYNC_ARGS[@]}" \
  --include='/SKILL.md' \
  --include='/agents/' \
  --include='/agents/***' \
  --include='/references/' \
  --include='/references/***' \
  --include='/scripts/' \
  --include='/scripts/***' \
  --include='/assets/' \
  --include='/assets/***' \
  --exclude='*' \
  "$SKILL_ROOT/" "$RUNTIME_ROOT/"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run release ($TOOL): $SKILL_ROOT -> $RUNTIME_ROOT"
else
  echo "released ($TOOL): $SKILL_ROOT -> $RUNTIME_ROOT"
fi
