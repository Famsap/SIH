#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# setup_backend.sh — Cross-platform (macOS / Linux) backend setup
# ──────────────────────────────────────────────────────────────
# Usage (from the repository root):
#   chmod +x scripts/setup_backend.sh
#   ./scripts/setup_backend.sh
#
# What it does:
#   1. Creates (or recreates) the Python virtual environment in backend/.venv
#   2. Activates it
#   3. Installs / upgrades pip
#   4. Installs every package listed in backend/requirements.txt
#   5. Copies .env.example → .env (if .env does not already exist)
#   6. Verifies that critical imports succeed
# ──────────────────────────────────────────────────────────────
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
VENV_DIR="$BACKEND_DIR/.venv"

# ── Colour helpers ───────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; NC='\033[0m'   # No Colour

info()  { printf "${CYAN}%s${NC}\n" "$*"; }
warn()  { printf "${YELLOW}%s${NC}\n" "$*"; }
ok()    { printf "${GREEN}%s${NC}\n" "$*"; }
fail()  { printf "${RED}ERROR: %s${NC}\n" "$*" >&2; exit 1; }

# ── Preflight checks ────────────────────────────────────────
# Prefer a Homebrew-installed Python 3.11+ over the system Python
PYTHON_CMD=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        _ver="$("$candidate" -c 'import sys; print(sys.version_info.minor)')"
        if [ "$_ver" -ge 11 ] 2>/dev/null; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    fail "Python 3.11+ not found. Install it first:  brew install python@3.13"
fi

PYTHON_VERSION="$("$PYTHON_CMD" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
ok "Found $PYTHON_CMD (Python $PYTHON_VERSION)"

[ -d "$BACKEND_DIR" ] || fail "Backend directory not found at $BACKEND_DIR"

# ── Create / recreate venv ──────────────────────────────────
if [ -d "$VENV_DIR" ]; then
    warn "Existing virtual environment found — removing and recreating…"
    rm -rf "$VENV_DIR"
fi

info "Creating virtual environment in $VENV_DIR …"
"$PYTHON_CMD" -m venv "$VENV_DIR"

# ── Activate ────────────────────────────────────────────────
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
ok "Activated $(python --version)"

# ── Upgrade pip ─────────────────────────────────────────────
info "Upgrading pip …"
python -m pip install --upgrade pip --quiet

# ── Install dependencies ────────────────────────────────────
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    info "Installing backend requirements …"
    python -m pip install -r "$BACKEND_DIR/requirements.txt"
else
    warn "requirements.txt not found — installing core packages only."
    python -m pip install fastapi 'uvicorn[standard]' chromadb sentence-transformers pydantic python-dotenv
fi
ok "Dependencies installed"

# ── .env setup ──────────────────────────────────────────────
ENV_FILE="$REPO_ROOT/.env"
ENV_EXAMPLE="$REPO_ROOT/.env.example"
if [ -f "$ENV_EXAMPLE" ] && [ ! -f "$ENV_FILE" ]; then
    info "Creating .env from .env.example …"
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    ok ".env created — edit it with your API keys before running the server."
elif [ -f "$ENV_FILE" ]; then
    warn ".env already exists — skipping copy."
fi

# ── Verify imports ──────────────────────────────────────────
info "Verifying critical imports …"
python -c "import fastapi, uvicorn, chromadb, sentence_transformers, pydantic; print('ALL_MODULES_OK')" \
    || fail "Import verification failed. Check the installation output above."
ok "All critical modules imported successfully"

# ── Build / refresh ChromaDB index ─────────────────────────
# This indexes all documents in data/processed/ into the bis_standards
# collection. Takes ~30-60 seconds on first run (downloads the embedding
# model). Safe to re-run; pass --reset to wipe and rebuild.
if [ -d "$REPO_ROOT/data/processed" ]; then
    info "Building ChromaDB index from data/processed/ (first run downloads ~130 MB model) …"
    cd "$BACKEND_DIR"
    python -m app.rag.ingest --input-dir "$REPO_ROOT/data/processed" \
        || warn "ChromaDB ingestion failed — you can retry later with: ./scripts/ingest_data.sh --reset"
    ok "ChromaDB index built"
else
    warn "data/processed/ not found — skipping ChromaDB ingestion. Add documents and run: ./scripts/ingest_data.sh"
fi

# ── Done ────────────────────────────────────────────────────
echo ""
ok "✅  Backend environment is ready!"
echo ""
echo "   To activate later:"
echo "     source $VENV_DIR/bin/activate"
echo ""
echo "   To run the dev server (from repo root):"
echo "     ./scripts/run_backend.sh"
echo ""
