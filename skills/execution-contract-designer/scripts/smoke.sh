#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  smoke.sh [--repo-root PATH] [--skill-root PATH] [--python BIN] [--tmp-root PATH]

Options:
  --repo-root PATH  Repository root (optional; accepted for interface compatibility).
  --skill-root PATH Skill root. Defaults to script parent.
  --python BIN      Python executable (optional; accepted for interface compatibility).
  --tmp-root PATH   Temporary root (optional; accepted for interface compatibility).
  -h, --help        Show this help message.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      shift 2
      ;;
    --skill-root)
      SKILL_ROOT="$2"
      shift 2
      ;;
    --python)
      shift 2
      ;;
    --tmp-root)
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
  "$SKILL_ROOT/references/contract-fields.md"
  "$SKILL_ROOT/references/process-protocol.md"
  "$SKILL_ROOT/references/output-contract.md"
  "$SKILL_ROOT/references/regression-cases.md"
  "$SKILL_ROOT/references/examples/README.md"
  "$SKILL_ROOT/references/examples/feature-contract.md"
  "$SKILL_ROOT/references/examples/refactor-contract.md"
  "$SKILL_ROOT/references/examples/non-example.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "error: required file not found: $file" >&2
    exit 1
  fi
done

if ! grep -q 'what the sprint closes, why the boundary exists, done signals, evidence checklist, negative cases, and suggested checkpoints' "$SKILL_ROOT/SKILL.md"; then
  echo "error: SKILL.md missing contract-field summary" >&2
  exit 1
fi

if ! grep -q 'Every contract must include at least one task-specific negative case' "$SKILL_ROOT/SKILL.md"; then
  echo "error: SKILL.md missing negative-case quality bar" >&2
  exit 1
fi

if ! grep -q '`done_signals`' "$SKILL_ROOT/references/output-contract.md"; then
  echo "error: output contract missing done_signals field" >&2
  exit 1
fi

if ! grep -q 'Prefer one contract per sprint or semantic work slice' "$SKILL_ROOT/references/trigger-rules.md"; then
  echo "error: trigger rules missing slice-level guidance" >&2
  exit 1
fi

echo "execution-contract-designer smoke passed: $SKILL_ROOT"
