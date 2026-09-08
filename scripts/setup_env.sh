#!/usr/bin/env bash
# setup_env.sh — idempotent musicom env setup + verification.
#
# Creates/reuses the musicom micromamba env from environment.yml, installs the
# repo editable, and verifies the ONE-ENV contract:
#   - MUSICOM_PYTHON resolves to a python that imports the engine (structures)
#   - MUSICOM_FLUIDSYNTH resolves to a fluidsynth binary
#   - bare `fluidsynth` works (env bin on PATH) — scripts never hardcode paths
#
# Usage:
#   bash scripts/setup_env.sh            # create + install + verify
#   bash scripts/setup_env.sh --check    # verify only (no mutation)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${MUSICOM_ENV_NAME:-musicom}"
ENV_DIR="${MUSICOM_ENV_DIR:-/opt/data/micromamba/envs/${ENV_NAME}}"
PYTHON_BIN="${ENV_DIR}/bin/python"
FLUID_BIN="${ENV_DIR}/bin/fluidsynth"

echo "== musicom env setup =="
echo "   repo: $REPO_ROOT"
echo "   env:  $ENV_DIR"

if [[ "${1:-}" == "--check" ]]; then
  echo "== verify-only =="
else
  if [[ ! -x "$PYTHON_BIN" ]]; then
    echo ">> env not found — creating from environment.yml"
    micromamba create -y -n "$ENV_NAME" -f "$REPO_ROOT/environment.yml" || \
      micromamba create -y -n "$ENV_NAME" -f "$REPO_ROOT/environment.yml" --channel conda-forge
  else
    echo ">> env exists — syncing deps"
    micromamba install -y -n "$ENV_NAME" -f "$REPO_ROOT/environment.yml" || true
  fi
  echo ">> editable install"
  (cd "$REPO_ROOT" && "$PYTHON_BIN" -m pip install -e ".[dev]")
fi

echo "== verify =="
fail=0
if "$PYTHON_BIN" -c "from structures import MusicEvent; from workflows.unitmatrix_composer import UnitMatrixComposer" 2>/dev/null; then
  echo "  [OK] engine imports ($PYTHON_BIN)"
else
  echo "  [FAIL] engine imports"; fail=1
fi
if [[ -x "$FLUID_BIN" ]]; then
  echo "  [OK] fluidsynth binary ($FLUID_BIN)"
else
  echo "  [FAIL] no fluidsynth in env"; fail=1
fi
if command -v fluidsynth >/dev/null 2>&1; then
  echo "  [OK] bare 'fluidsynth' on PATH"
else
  echo "  [WARN] bare 'fluidsynth' not on PATH (source ~/.bashrc or export MUSICOM_ENV_DIR/bin)"
fi
if command -v ffmpeg >/dev/null 2>&1; then
  echo "  [OK] ffmpeg on PATH"
else
  echo "  [FAIL] no ffmpeg"; fail=1
fi
echo "== done (fail=$fail) =="
exit $fail
