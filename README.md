# ManakSetu Backend

FastAPI and retrieval-augmented generation (RAG) backend for the AI-powered Indian Standards and BIS services assistant.

## Prerequisites

- **Python 3.11+** (3.13 recommended)
- **Node.js 18+** (for the frontend)
- **LLM provider** (at least one required for answer generation):
  - [Groq API key](https://console.groq.com) (free tier, fast) — set `GROQ_API_KEY` in `.env`
  - OR [Ollama](https://ollama.com) with the configured local model for offline fallback
- A populated local corpus and Chroma index for useful answers (see *Data ingestion* below)

---

## Quick setup (macOS / Linux)

From the repository root, run the one-command setup script:

```bash
cd /path/to/SIH
chmod +x scripts/setup_backend.sh
./scripts/setup_backend.sh
```

This will:

1. Create a Python virtual environment in `backend/.venv`
2. Install all dependencies from `backend/requirements.txt`
3. Copy `.env.example` → `.env` (if `.env` does not already exist)
4. Verify that critical imports succeed

After the script finishes:

```bash
# Option A — easiest (works from repo root, runs in correct dir)
./scripts/run_backend.sh

# Option B — manual
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

> ⚠️ **Important:** You must run `uvicorn app.main:app` from the `backend/`
> directory. If you run it from anywhere else (e.g. the repository root or
> `frontend/`), Python cannot find the `app` package and you'll see:
> `ERROR: Could not import module "app.main"`. The `run_backend.sh` script
> handles this for you automatically.

### Manual setup (macOS / Linux)

If you prefer to run each step yourself:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Quick setup (Windows PowerShell)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup_backend_windows.ps1
```

### Manual setup (Windows PowerShell)

```powershell
cd .\backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run this once and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

---

## Configuration

From the repository root, copy `.env.example` to `.env` and replace placeholder values. Do not commit `.env`.

```bash
# macOS / Linux
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

`CHROMA_PERSIST_DIR` must point to the local Chroma directory. Paths in `.env` are relative to the **repository root** (e.g. `data/chroma`). Legacy values like `../data/chroma` (relative to `backend/` CWD) are also supported.

## Data ingestion

Build the ChromaDB vector index from the processed documents:

```bash
# Index all documents in data/processed/
./scripts/ingest_data.sh

# Wipe and re-index from scratch
./scripts/ingest_data.sh --reset
```

This creates/updates the `bis_standards` collection in `data/chroma/` with ~6,000+ clause-aware chunks.
The embedding model (`BAAI/bge-small-en-v1.5`) is cached locally after the first run (~130 MB download).

Windows PowerShell equivalent:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\ingest_data.ps1 -Reset   # -Reset wipes and rebuilds
```

## Run the API

The easiest way to start the backend server (from the repository root):

```bash
./scripts/run_backend.sh
```

Or manually — with the virtual environment active and the terminal **in `backend/`**:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

Open the API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). Health checks are available at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) and [http://127.0.0.1:8000/api/chat/health](http://127.0.0.1:8000/api/chat/health).

## Data and ingestion

Place approved source documents in `data/raw/`, extract them into `data/processed/`, and build the local Chroma index in `data/chroma/`. Follow [INTAKE_SOURCES.txt](INTAKE_SOURCES.txt) for approved sources and ingestion controls. Runtime source files and the vector database are deliberately not tracked by Git.

## Troubleshooting

### `python` command not found (macOS)

macOS ships Python 3 via `python3`. Always use `python3` or activate the virtual environment first, which provides the `python` command.

### PowerShell cannot activate `Activate.ps1`

Use the process-scoped `Set-ExecutionPolicy` command in the setup section. It changes policy only for the current PowerShell window.

### `ModuleNotFoundError: No module named 'app'`

Run the server from `backend/`:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Avoid relying on a global `PYTHONPATH`; changing into `backend/` gives Python the intended import root.

### Uvicorn uses the wrong Python version

Do not run a globally installed `uvicorn` executable. Activate the virtual environment and always use `python -m uvicorn ...`.

### Chroma index is empty or responses are gated

Confirm that approved documents were ingested, `CHROMA_PERSIST_DIR` points to the intended directory, and `CHROMA_COLLECTION` matches the collection used by ingestion. Rebuild the index only after stopping the API.

```bash
# Check index status from backend/
source .venv/bin/activate
python -c "import chromadb; c=chromadb.PersistentClient(path='../data/chroma'); print([(x.name,x.count()) for x in c.list_collections()])"
```

If the collection shows 0 vectors or uses a different name than `bis_standards`, rebuild it:

```bash
./scripts/ingest_data.sh --reset
```

### "Generation service is unavailable"

Both Groq and Ollama failed. Set at least one LLM provider:

```bash
# Option A — Groq (free, fast, requires internet)
# Sign up at https://console.groq.com, create a key, add to .env:
GROQ_API_KEY=gsk_your_actual_key_here

# Option B — Ollama (offline, local)
# Install: brew install ollama (macOS)
# Pull model: ollama pull llama3.1:8b
# Start: ollama serve
```
