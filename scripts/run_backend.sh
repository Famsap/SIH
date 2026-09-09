#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# run_backend.sh — Start the FastAPI dev server from anywhere
# ──────────────────────────────────────────────────────────────
# Usage (from the repository root):
#   ./scripts/run_backend.sh
#
# This is the safe way to start the server. It always runs
# Uvicorn from the backend/ directory so that the `app` package
# is on the import path. Running `uvicorn app.main:app` from any
# other directory fails with "Could not import module app.main".
# ──────────────────────────────────────────────────────────────
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
VENV_DIR="$BACKEND_DIR/.venv"

# Activate the virtual environment if it exists.
if [ -f "$VENV_DIR/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
else
    echo "Virtual environment not found at $VENV_DIR."
    echo "Run ./scripts/setup_backend.sh first."
    exit 1
fi

# Ensure we're in the backend dir so `app` is importable.
cd "$BACKEND_DIR"

PORT="${1:-8000}"
echo "Starting ManakSetu backend on http://127.0.0.1:$PORT"
echo "(Press CTRL+C to stop)"
exec python -m uvicorn app.main:app --reload --port "$PORT"
