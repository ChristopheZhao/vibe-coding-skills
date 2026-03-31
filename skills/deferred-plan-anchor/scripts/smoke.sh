#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  smoke.sh [--repo-root PATH] [--skill-root PATH] [--python BIN] [--tmp-root PATH]
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TMP_ROOT="${TMP_ROOT:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    --skill-root)
      SKILL_ROOT="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --tmp-root)
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
if [[ "$REPO_ROOT" != /* ]]; then
  REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
fi

required_files=(
  "$SKILL_ROOT/SKILL.md"
  "$SKILL_ROOT/agents/openai.yaml"
  "$SKILL_ROOT/references/positioning-boundary.md"
  "$SKILL_ROOT/references/trigger-rules.md"
  "$SKILL_ROOT/references/process-protocol.md"
  "$SKILL_ROOT/references/artifact-contract.md"
  "$SKILL_ROOT/references/output-contract.md"
  "$SKILL_ROOT/references/regression-cases.md"
  "$SKILL_ROOT/references/examples/README.md"
  "$SKILL_ROOT/references/examples/activate-sot-only-guardrail.md"
  "$SKILL_ROOT/references/examples/resolve-for-planning-noop.md"
  "$SKILL_ROOT/references/examples/non-example-execution-plan.md"
  "$SKILL_ROOT/scripts/anchor_ops.py"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "error: required file not found: $file" >&2
    exit 1
  fi
done

"$PYTHON_BIN" -m py_compile "$SKILL_ROOT/scripts/anchor_ops.py"

if [[ -n "$TMP_ROOT" ]]; then
  mkdir -p "$TMP_ROOT"
  TMP_DIR="$(mktemp -d "$TMP_ROOT/deferred-plan-anchor-smoke.XXXXXX")"
else
  TMP_DIR="$(mktemp -d)"
fi
trap 'rm -rf "$TMP_DIR"' EXIT

OUTPUT="$("$PYTHON_BIN" "$SKILL_ROOT/scripts/anchor_ops.py" --root "$TMP_DIR" resolve-for-planning --json)"
if [[ "$OUTPUT" != *'"enabled": false'* ]]; then
  echo "error: resolve-for-planning should no-op before init" >&2
  exit 1
fi

"$PYTHON_BIN" "$SKILL_ROOT/scripts/anchor_ops.py" --root "$TMP_DIR" ensure >/dev/null
"$PYTHON_BIN" "$SKILL_ROOT/scripts/anchor_ops.py" --root "$TMP_DIR" create \
  --id DP-T-001 \
  --title "Smoke Deferred Plan" \
  --goal "Converge to a single authority surface" \
  --why-not-now "Current slice cannot absorb the migration cost" \
  --current-deviation "Temporary dual-write still exists" \
  --scope-tags backend,planning \
  --topic-tags sot,authority \
  --plan-kinds feature \
  --do-not "Do not add new authority semantics on B" \
  --allowed-now "Compatibility reads only" \
  --reopen-trigger "Create a dedicated migration plan before touching the boundary" \
  --activate >/dev/null

OUTPUT="$("$PYTHON_BIN" "$SKILL_ROOT/scripts/anchor_ops.py" --root "$TMP_DIR" resolve-for-planning --scope-tags backend --topic-tags authority --plan-kind feature --json)"
if [[ "$OUTPUT" != *'"applies": true'* ]]; then
  echo "error: resolve-for-planning should apply matching guardrails" >&2
  exit 1
fi

"$PYTHON_BIN" "$SKILL_ROOT/scripts/anchor_ops.py" --root "$TMP_DIR" doctor >/dev/null

echo "deferred-plan-anchor smoke passed: $SKILL_ROOT"
