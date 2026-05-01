#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  release-all.sh [--repo-root PATH] [--skills-root PATH] [--tool codex|claude|cursor|gemini|copilot] [--runtime-skills-root PATH] [--dry-run] [--no-delete]

Options:
  --repo-root PATH          Repository root. Defaults to script parent.
  --skills-root PATH        Skills root (absolute or repo-relative). Default: skills
  --tool NAME               Target tool profile. Default: codex.
  --runtime-skills-root PATH
                            Optional base target; each skill publishes to PATH/<skill-name>.
  --dry-run                 Show release plan without writing files.
  --no-delete               Keep extra files in target directories.
  -h, --help                Show this help message.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-$DEFAULT_REPO_ROOT}"
SKILLS_ROOT="${SKILLS_ROOT:-skills}"
TOOL="${TOOL:-codex}"
RUNTIME_SKILLS_ROOT="${RUNTIME_SKILLS_ROOT:-}"
DRY_RUN=0
NO_DELETE=0

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
    --tool)
      if [[ $# -lt 2 ]]; then
        echo "error: --tool requires a value" >&2
        exit 1
      fi
      TOOL="$2"
      shift 2
      ;;
    --runtime-skills-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --runtime-skills-root requires a value" >&2
        exit 1
      fi
      RUNTIME_SKILLS_ROOT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-delete)
      NO_DELETE=1
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

if [[ -n "$RUNTIME_SKILLS_ROOT" ]]; then
  mkdir -p "$RUNTIME_SKILLS_ROOT"
fi

release_script="$SCRIPT_DIR/release.sh"
if [[ ! -x "$release_script" ]]; then
  echo "error: release script not executable: $release_script" >&2
  exit 1
fi

count=0
while IFS= read -r -d '' skill_dir; do
  skill_name="$(basename "$skill_dir")"
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "skip: $skill_name (missing SKILL.md)" >&2
    continue
  fi

  count=$((count + 1))
  cmd=("$release_script" "--repo-root" "$REPO_ROOT" "--skill-dir" "$skill_dir" "--skill-name" "$skill_name" "--tool" "$TOOL")
  if [[ "$DRY_RUN" -eq 1 ]]; then
    cmd+=("--dry-run")
  fi
  if [[ "$NO_DELETE" -eq 1 ]]; then
    cmd+=("--no-delete")
  fi
  if [[ -n "$RUNTIME_SKILLS_ROOT" ]]; then
    cmd+=("--runtime-root" "$RUNTIME_SKILLS_ROOT/$skill_name")
  fi

  echo "release-all: $skill_name"
  "${cmd[@]}"
done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

if [[ "$count" -eq 0 ]]; then
  echo "error: no valid skills found under $SKILLS_DIR" >&2
  exit 1
fi

echo "release-all: completed ($count skill(s))"
