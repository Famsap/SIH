#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────────────
# ingest_data.sh — (Re)build the ChromaDB vector index from data/processed/
#
# Usage:
#   ./scripts/ingest_data.sh           # index all processed documents
#   ./scripts/ingest_data.sh --reset   # wipe and re-index from scratch
# ────────────────────────────────────────────────────────────────────────
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT/backend"

# ── Activate venv ──────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
  echo "❌ No .venv found in backend/. Run ./scripts/setup_backend.sh first."
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# ── Accept flags ───────────────────────────────────────────────────────
ARGS=("$@")
if [[ $# -eq 0 ]]; then
  ARGS=("--input-dir" "../data/processed")
fi

echo "📦 Ingesting documents into ChromaDB..."
echo "   (backend/) $ python -m app.rag.ingest ${ARGS[*]}"

python -m app.rag.ingest "${ARGS[@]}"

echo ""
echo "✅ Done. Start the backend with ./scripts/run_backend.sh"
