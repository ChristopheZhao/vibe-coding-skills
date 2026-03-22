#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  smoke.sh [--repo-root PATH] [--skill-root PATH] [--python BIN] [--tmp-root PATH]

Options:
  --repo-root PATH  Repository root (optional; not required by this smoke flow).
  --skill-root PATH  Skill root. Defaults to script parent.
  --python BIN       Python executable (optional; accepted for interface compatibility).
  --tmp-root PATH    Temporary root (optional; accepted for interface compatibility).
  -h, --help         Show this help message.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
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

required_files=(
  "$SKILL_ROOT/SKILL.md"
  "$SKILL_ROOT/agents/openai.yaml"
  "$SKILL_ROOT/references/positioning-boundary.md"
  "$SKILL_ROOT/references/trigger-rules.md"
  "$SKILL_ROOT/references/canonical-surfaces.md"
  "$SKILL_ROOT/references/process-protocol.md"
  "$SKILL_ROOT/references/output-contract.md"
  "$SKILL_ROOT/references/regression-cases.md"
  "$SKILL_ROOT/references/examples/README.md"
  "$SKILL_ROOT/references/examples/multi-subtask-session.md"
  "$SKILL_ROOT/references/examples/superseded-plan-session.md"
  "$SKILL_ROOT/references/examples/non-example.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "error: required file not found: $file" >&2
    exit 1
  fi
done

if ! grep -q 'docs/session-handoff/SHO-YYYYMMDD-NNNN.md' "$SKILL_ROOT/SKILL.md"; then
  echo "error: SKILL.md missing handoff output path contract" >&2
  exit 1
fi

if ! grep -q 'canonical artifact surfaces' "$SKILL_ROOT/SKILL.md"; then
  echo "error: SKILL.md missing artifact-surface boundary" >&2
  exit 1
fi

if ! grep -q 'Avoid Repeat' "$SKILL_ROOT/references/output-contract.md"; then
  echo "error: output contract missing Avoid Repeat section" >&2
  exit 1
fi

if ! grep -q 'Explicit trigger only' "$SKILL_ROOT/references/trigger-rules.md"; then
  echo "error: trigger rules missing MVP explicit-trigger policy" >&2
  exit 1
fi

echo "session-handoff smoke passed: $SKILL_ROOT"
