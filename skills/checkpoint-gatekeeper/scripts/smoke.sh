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
  "$SKILL_ROOT/references/artifact-contract.md"
  "$SKILL_ROOT/references/remediation-policy.md"
  "$SKILL_ROOT/references/output-contract.md"
  "$SKILL_ROOT/references/regression-cases.md"
  "$SKILL_ROOT/references/examples/README.md"
  "$SKILL_ROOT/references/examples/basic-pass.md"
  "$SKILL_ROOT/references/examples/auto-fix-pass.md"
  "$SKILL_ROOT/references/examples/acceptance-pass.md"
  "$SKILL_ROOT/references/examples/non-example.md"
  "$SKILL_ROOT/scripts/gate_ops.py"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "error: required file not found: $file" >&2
    exit 1
  fi
done

"$PYTHON_BIN" -m py_compile "$SKILL_ROOT/scripts/gate_ops.py"

if [[ -n "$TMP_ROOT" ]]; then
  mkdir -p "$TMP_ROOT"
  TMP_DIR="$(mktemp -d "$TMP_ROOT/checkpoint-gatekeeper-smoke.XXXXXX")"
else
  TMP_DIR="$(mktemp -d)"
fi
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$TMP_DIR/docs/plans"
cat > "$TMP_DIR/docs/plans/PLAN_INDEX.json" <<'EOF'
{
  "plans": [
    {
      "id": "PLAN-T-001",
      "title": "Checkpoint Gatekeeper Smoke",
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

"$PYTHON_BIN" "$SKILL_ROOT/scripts/gate_ops.py" --root "$TMP_DIR" init \
  --id PLAN-T-001 \
  --checkpoint CHK-A \
  --title "Checkpoint A" \
  --validation-command "true" >/dev/null

"$PYTHON_BIN" "$SKILL_ROOT/scripts/gate_ops.py" --root "$TMP_DIR" check \
  --id PLAN-T-001 \
  --checkpoint CHK-A >/dev/null

STATUS_OUTPUT="$("$PYTHON_BIN" "$SKILL_ROOT/scripts/gate_ops.py" --root "$TMP_DIR" status --id PLAN-T-001 --checkpoint CHK-A --json)"

if [[ "$STATUS_OUTPUT" != *'"verdict": "pass"'* ]]; then
  echo "error: smoke status did not report pass verdict" >&2
  exit 1
fi

if [[ ! -f "$TMP_DIR/docs/checkpoints/PLAN-T-001/CHK-A-checklist.md" ]]; then
  echo "error: checklist artifact missing" >&2
  exit 1
fi

if [[ ! -f "$TMP_DIR/docs/checkpoints/PLAN-T-001/CHK-A-gate.json" ]]; then
  echo "error: gate artifact missing" >&2
  exit 1
fi

"$PYTHON_BIN" "$SKILL_ROOT/scripts/gate_ops.py" --root "$TMP_DIR" init \
  --id PLAN-T-001 \
  --checkpoint CHK-B \
  --title "Checkpoint B" \
  --profile acceptance \
  --acceptance-target "semantic closure for sprint B" \
  --required-evidence "smoke passed" \
  --required-evidence "contract gaps empty" \
  --validation-command "true" >/dev/null

cat > "$TMP_DIR/docs/checkpoints/PLAN-T-001/CHK-B-evidence.json" <<'EOF'
{
  "plan_id": "PLAN-T-001",
  "checkpoint": "CHK-B",
  "acceptance_target": "semantic closure for sprint B",
  "contract_ref": "docs/contracts/CHK-B.json",
  "evidence_refs": [
    "results/CHK-B-smoke.txt"
  ],
  "changed_artifact_paths": [
    "skills/checkpoint-gatekeeper/scripts/gate_ops.py"
  ],
  "negative_cases": [
    "Do not create a second verdict owner."
  ],
  "declared_out_of_scope": [
    "No standalone verifier skill."
  ],
  "executor_summary": "Implemented checkpoint B scope and linked smoke evidence."
}
EOF

cat > "$TMP_DIR/docs/checkpoints/PLAN-T-001/CHK-B-acceptance-review.json" <<'EOF'
{
  "plan_id": "PLAN-T-001",
  "checkpoint": "CHK-B",
  "reviewer_kind": "peer_agent",
  "review_verdict": "accept",
  "contract_closure": "satisfied",
  "evidence_sufficiency": "sufficient",
  "gap_severity": "none",
  "gaps": [],
  "cited_evidence": [
    "results/CHK-B-smoke.txt"
  ],
  "summary": "Independent review accepted checkpoint B."
}
EOF

"$PYTHON_BIN" "$SKILL_ROOT/scripts/gate_ops.py" --root "$TMP_DIR" check \
  --id PLAN-T-001 \
  --checkpoint CHK-B >/dev/null

ACCEPTANCE_STATUS="$("$PYTHON_BIN" "$SKILL_ROOT/scripts/gate_ops.py" --root "$TMP_DIR" status --id PLAN-T-001 --checkpoint CHK-B --json)"

if [[ "$ACCEPTANCE_STATUS" != *'"profile": "acceptance"'* ]]; then
  echo "error: acceptance profile missing from gate JSON" >&2
  exit 1
fi

if [[ "$ACCEPTANCE_STATUS" != *'"acceptance_target": "semantic closure for sprint B"'* ]]; then
  echo "error: acceptance target missing from gate JSON" >&2
  exit 1
fi

if [[ "$ACCEPTANCE_STATUS" != *'"required_evidence": ['* ]]; then
  echo "error: required evidence missing from gate JSON" >&2
  exit 1
fi

if [[ "$ACCEPTANCE_STATUS" != *'"evidence_path": "docs/checkpoints/PLAN-T-001/CHK-B-evidence.json"'* ]]; then
  echo "error: evidence path missing from acceptance gate JSON" >&2
  exit 1
fi

if [[ "$ACCEPTANCE_STATUS" != *'"acceptance_review_path": "docs/checkpoints/PLAN-T-001/CHK-B-acceptance-review.json"'* ]]; then
  echo "error: acceptance review path missing from acceptance gate JSON" >&2
  exit 1
fi

if [[ "$ACCEPTANCE_STATUS" != *'"acceptance_gaps": []'* ]]; then
  echo "error: acceptance gaps should be empty for passing acceptance smoke" >&2
  exit 1
fi

if ! grep -q 'acceptance' "$SKILL_ROOT/SKILL.md" "$SKILL_ROOT/references/output-contract.md"; then
  echo "error: acceptance profile guidance missing" >&2
  exit 1
fi

echo "checkpoint-gatekeeper smoke passed: $SKILL_ROOT"
