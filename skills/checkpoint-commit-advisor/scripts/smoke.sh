#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  smoke.sh [--repo-root PATH] [--skill-root PATH] [--python BIN] [--tmp-root PATH]

Options:
  --repo-root PATH  Repository root. Defaults to script grandparent.
  --skill-root PATH  Skill root. Defaults to script parent.
  --python BIN       Python executable. Default: python3.
  --tmp-root PATH    Temporary root parent.
  -h, --help         Show this help message.
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
  "$SKILL_ROOT/references/output-contract.md"
  "$SKILL_ROOT/references/regression-cases.md"
  "$SKILL_ROOT/references/examples/README.md"
  "$SKILL_ROOT/references/examples/two-layer-checkpoint.md"
  "$SKILL_ROOT/references/examples/defer-small-change.md"
  "$SKILL_ROOT/references/examples/non-example.md"
  "$SKILL_ROOT/scripts/commit_advisor.py"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "error: required file not found: $file" >&2
    exit 1
  fi
done

"$PYTHON_BIN" -m py_compile "$SKILL_ROOT/scripts/commit_advisor.py"

if [[ -n "$TMP_ROOT" ]]; then
  mkdir -p "$TMP_ROOT"
  TMP_DIR="$(mktemp -d "$TMP_ROOT/checkpoint-commit-advisor-smoke.XXXXXX")"
else
  TMP_DIR="$(mktemp -d)"
fi
trap 'rm -rf "$TMP_DIR"' EXIT

git -C "$TMP_DIR" init >/dev/null
git -C "$TMP_DIR" config user.name "Smoke Test"
git -C "$TMP_DIR" config user.email "smoke@example.com"

mkdir -p "$TMP_DIR/docs/plans/active" "$TMP_DIR/src"
cat > "$TMP_DIR/docs/plans/PLAN_INDEX.json" <<'EOF'
{
  "plans": [
    {
      "id": "PLAN-T-001",
      "title": "Smoke Plan",
      "kind": "feature",
      "status": "in_progress",
      "priority": "P0",
      "owner": "codex",
      "file_path": "docs/plans/active/PLAN-T-001.md",
      "confirmed_by_user": false,
      "created_at": "2026-03-22T00:00:00Z",
      "updated_at": "2026-03-22T00:00:00Z",
      "archived_at": null,
      "notes": []
    }
  ]
}
EOF
cat > "$TMP_DIR/docs/plans/active/PLAN-T-001.md" <<'EOF'
# Plan: Smoke Plan
- Status: in_progress
EOF
cat > "$TMP_DIR/src/app.py" <<'EOF'
print("base")
EOF
git -C "$TMP_DIR" add .
git -C "$TMP_DIR" commit -m "base" >/dev/null

cat > "$TMP_DIR/docs/plans/active/PLAN-T-001.md" <<'EOF'
# Plan: Smoke Plan
- Status: testing
EOF
cat > "$TMP_DIR/src/app.py" <<'EOF'
print("changed")
EOF

OUTPUT="$("$PYTHON_BIN" "$SKILL_ROOT/scripts/commit_advisor.py" --root "$TMP_DIR" analyze --json --plan-id PLAN-T-001)"

if [[ "$OUTPUT" != *'"decision": "commit_now"'* ]]; then
  echo "error: smoke analyze did not recommend commit_now" >&2
  exit 1
fi

if [[ "$OUTPUT" != *'"strategy": "two-layer"'* ]]; then
  echo "error: smoke analyze did not recommend two-layer strategy" >&2
  exit 1
fi

echo "checkpoint-commit-advisor smoke passed: $SKILL_ROOT"
