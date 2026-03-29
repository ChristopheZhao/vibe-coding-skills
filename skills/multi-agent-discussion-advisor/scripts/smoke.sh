#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  smoke.sh [--repo-root PATH] [--skill-root PATH] [--python BIN] [--tmp-root PATH]

Options:
  --repo-root PATH  Repository root (optional; not required by this smoke flow).
  --skill-root PATH Skill root. Defaults to script parent.
  --python BIN      Python executable (accepted for interface compatibility).
  --tmp-root PATH   Temporary root (accepted for interface compatibility).
  -h, --help        Show this help message.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_ROOT="$DEFAULT_SKILL_ROOT"

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
      shift 2
      ;;
    --tmp-root)
      if [[ $# -lt 2 ]]; then
        echo "error: --tmp-root requires a value" >&2
        exit 1
      fi
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
  "$SKILL_ROOT/references/principles.md"
  "$SKILL_ROOT/references/trigger-signals.md"
  "$SKILL_ROOT/references/process-protocol.md"
  "$SKILL_ROOT/references/collaboration-patterns.md"
  "$SKILL_ROOT/references/subagent-protocol.md"
  "$SKILL_ROOT/references/role-selection.md"
  "$SKILL_ROOT/references/output-contract.md"
  "$SKILL_ROOT/references/platform-adapters.md"
  "$SKILL_ROOT/references/regression-cases.md"
  "$SKILL_ROOT/references/examples/README.md"
  "$SKILL_ROOT/references/examples/ex-preflight-plan-review.md"
  "$SKILL_ROOT/references/examples/ex-real-multi-agent-review.md"
)

for path in "${required_files[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "error: required file missing: $path" >&2
    exit 1
  fi
done

if [[ -f "$SKILL_ROOT/agents/openai.yaml" ]]; then
  if ! rg -q "^interface:" "$SKILL_ROOT/agents/openai.yaml"; then
    echo "error: optional openai adapter missing interface block" >&2
    exit 1
  fi
fi

if ! grep -q "^name: multi-agent-discussion-advisor$" "$SKILL_ROOT/SKILL.md"; then
  echo "error: SKILL.md frontmatter name mismatch" >&2
  exit 1
fi

if ! grep -q "^description:" "$SKILL_ROOT/SKILL.md"; then
  echo "error: SKILL.md missing description frontmatter" >&2
  exit 1
fi

if ! rg -q "## Activation Cues" "$SKILL_ROOT/SKILL.md"; then
  echo "error: SKILL.md missing 'Activation Cues' section" >&2
  exit 1
fi

if ! rg -q "Advisory only" "$SKILL_ROOT/SKILL.md"; then
  echo "error: SKILL.md missing advisory-only hard rule" >&2
  exit 1
fi

if ! rg -q "single-role-ok|multi-role-recommended|inconclusive" "$SKILL_ROOT/references/output-contract.md"; then
  echo "error: output-contract missing verdict enum" >&2
  exit 1
fi

if ! rg -q "preflight-review|preflight_review|approve|revise|block" "$SKILL_ROOT/SKILL.md" "$SKILL_ROOT/references/output-contract.md"; then
  echo "error: preflight review guidance missing" >&2
  exit 1
fi

if ! rg -q "real sub-agent|multi-agent review|spawn_agent" "$SKILL_ROOT/SKILL.md" "$SKILL_ROOT/references/subagent-protocol.md"; then
  echo "error: subagent delegation guidance missing" >&2
  exit 1
fi

echo "multi-agent-discussion-advisor smoke passed: $SKILL_ROOT"
