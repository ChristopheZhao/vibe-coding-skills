#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  test.sh [--repo-root PATH] [--skill-dir PATH] [--python BIN] [--pattern GLOB] [--all]

Options:
  --repo-root PATH  Repository root. Defaults to script parent.
  --skill-dir PATH  Skill source directory (absolute or repo-relative).
                    Default: skills/sdd-plan-maintainer
  --python BIN      Python executable to run tests. Default: python3.
  --pattern GLOB    unittest discovery pattern. Default: test_*.py
  --all             Run tests for every skill that provides a test entry or scripts/tests.
  -h, --help        Show this help message.

Environment:
  REPO_ROOT, SKILL_DIR, PYTHON_BIN, TEST_PATTERN
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-$DEFAULT_REPO_ROOT}"
SKILL_DIR="${SKILL_DIR:-skills/sdd-plan-maintainer}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TEST_PATTERN="${TEST_PATTERN:-test_*.py}"
RUN_ALL=0

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
    --python)
      if [[ $# -lt 2 ]]; then
        echo "error: --python requires a value" >&2
        exit 1
      fi
      PYTHON_BIN="$2"
      shift 2
      ;;
    --pattern)
      if [[ $# -lt 2 ]]; then
        echo "error: --pattern requires a value" >&2
        exit 1
      fi
      TEST_PATTERN="$2"
      shift 2
      ;;
    --all)
      RUN_ALL=1
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

resolve_skill_root() {
  local skill_dir="$1"
  local skill_root
  if [[ "$skill_dir" = /* ]]; then
    skill_root="$skill_dir"
  else
    skill_root="$REPO_ROOT/$skill_dir"
  fi
  if [[ ! -d "$skill_root" ]]; then
    echo "error: skill directory not found: $skill_root" >&2
    return 1
  fi
  (cd "$skill_root" && pwd)
}

has_tests() {
  local skill_root="$1"
  [[ -f "$skill_root/scripts/test.sh" || -f "$skill_root/scripts/test.py" || -d "$skill_root/scripts/tests" ]]
}

run_skill_tests() {
  local skill_root="$1"
  local test_sh="$skill_root/scripts/test.sh"
  local test_py="$skill_root/scripts/test.py"
  local tests_dir="$skill_root/scripts/tests"

  echo "==> tests: $(basename "$skill_root")"
  if [[ -f "$test_sh" ]]; then
    bash "$test_sh" --repo-root "$REPO_ROOT" --skill-root "$skill_root" --python "$PYTHON_BIN"
  elif [[ -f "$test_py" ]]; then
    "$PYTHON_BIN" "$test_py" --repo-root "$REPO_ROOT" --skill-root "$skill_root"
  elif [[ -d "$tests_dir" ]]; then
    "$PYTHON_BIN" -m unittest discover -s "$tests_dir" -p "$TEST_PATTERN" -v
  else
    echo "error: no tests found for skill: $skill_root" >&2
    return 1
  fi
}

if [[ "$RUN_ALL" -eq 1 ]]; then
  ran=0
  while IFS= read -r -d '' skill_root; do
    if has_tests "$skill_root"; then
      run_skill_tests "$skill_root"
      ran=$((ran + 1))
    fi
  done < <(find "$REPO_ROOT/skills" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

  if [[ "$ran" -eq 0 ]]; then
    echo "error: no skill tests found under $REPO_ROOT/skills" >&2
    exit 1
  fi

  echo "test passed: skills=$ran"
  exit 0
fi

SKILL_ROOT="$(resolve_skill_root "$SKILL_DIR")"
run_skill_tests "$SKILL_ROOT"
echo "test passed: skill=$(basename "$SKILL_ROOT")"
