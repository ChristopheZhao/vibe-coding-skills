#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  check-structure.sh [--repo-root PATH] [--skills-root PATH]

Options:
  --repo-root PATH   Repository root. Defaults to script parent.
  --skills-root PATH Skills root (absolute or repo-relative).
                     Default: skills
  -h, --help         Show this help message.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-$DEFAULT_REPO_ROOT}"
SKILLS_ROOT="${SKILLS_ROOT:-skills}"

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
    --skills-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --skills-root requires a value" >&2
        exit 1
      fi
      SKILLS_ROOT="$2"
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

REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
if [[ "$SKILLS_ROOT" = /* ]]; then
  SKILLS_DIR="$SKILLS_ROOT"
else
  SKILLS_DIR="$REPO_ROOT/$SKILLS_ROOT"
fi
SKILLS_DIR="$(cd "$SKILLS_DIR" && pwd)"

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "error: skills root not found: $SKILLS_DIR" >&2
  exit 1
fi

issues=0
checked=0

while IFS= read -r -d '' skill_dir; do
  checked=$((checked + 1))
  skill_name="$(basename "$skill_dir")"

  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "error: $skill_name missing SKILL.md" >&2
    issues=$((issues + 1))
  fi

  for required_dir in agents references scripts; do
    if [[ ! -d "$skill_dir/$required_dir" ]]; then
      echo "error: $skill_name missing required directory: $required_dir/" >&2
      issues=$((issues + 1))
    fi
  done

  while IFS= read -r -d '' entry; do
    base="$(basename "$entry")"
    case "$base" in
      SKILL.md|agents|references|scripts)
        ;;
      *)
        echo "error: $skill_name contains non-standard top-level entry: $base" >&2
        issues=$((issues + 1))
        ;;
    esac
  done < <(find "$skill_dir" -mindepth 1 -maxdepth 1 -print0)
done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

if [[ "$checked" -eq 0 ]]; then
  echo "error: no skill directories found under $SKILLS_DIR" >&2
  exit 1
fi

if [[ "$issues" -gt 0 ]]; then
  echo "structure-check: failed (skills=$checked, issues=$issues)" >&2
  exit 1
fi

echo "structure-check: ok (skills=$checked)"
