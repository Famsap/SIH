# ManakSetu Backend

FastAPI and retrieval-augmented generation (RAG) backend for the AI-powered Indian Standards and BIS services assistant.

## Prerequisites

- Windows 10/11 with PowerShell
- Python 3.13 installed and available through the `py` launcher
- Optional: Ollama with the configured local model for offline fallback
- A populated local corpus and Chroma index for useful answers

## Windows PowerShell setup

Run all backend commands from the repository's `backend` directory.

```powershell
cd .\backend
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation for the current session, run this once and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Configuration

From the repository root, copy `.env.example` to `.env` and replace placeholder values. Do not commit `.env`.

```powershell
cd ..
Copy-Item .env.example .env
cd .\backend
```

`CHROMA_PERSIST_DIR` must point to the local Chroma directory. The default `../data/chroma` is suitable when running from `backend/`.

## Run the API

With the virtual environment active and the terminal in `backend/`, start the development server:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Open the API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). Health checks are available at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) and [http://127.0.0.1:8000/api/chat/health](http://127.0.0.1:8000/api/chat/health).

## Data and ingestion

Place approved source documents in `data/raw/`, extract them into `data/processed/`, and build the local Chroma index in `data/chroma/`. Follow [INTAKE_SOURCES.txt](INTAKE_SOURCES.txt) for approved sources and ingestion controls. Runtime source files and the vector database are deliberately not tracked by Git.

## Windows troubleshooting

### PowerShell cannot activate `Activate.ps1`

Use the process-scoped `Set-ExecutionPolicy` command in the setup section. It changes policy only for the current PowerShell window.

### `ModuleNotFoundError: No module named 'app'`

Run the server from `backend/`:

```powershell
cd .\backend
python -m uvicorn app.main:app --reload --port 8000
```

Avoid relying on a global `PYTHONPATH`; changing into `backend/` gives Python the intended import root. If a separate process genuinely requires it, set it only for that process: `$env:PYTHONPATH = (Get-Location).Path`.

### Uvicorn uses the wrong Python version

Do not run a globally installed `uvicorn` executable. Activate `venv` and always use `python -m uvicorn ...`. This prevents an unrelated installation, such as Python 3.14, from being selected instead of the Python 3.13 virtual environment.

### File handle locks or failed directory deletion

Stop Uvicorn and any ingestion process with `Ctrl+C`. Close File Explorer windows, Python shells, and editors that have files open under `data/chroma/`; Windows may retain handles such as `index.lock`. Wait briefly, then retry the operation. Do not delete an index while the API or an ingestion job is using it.

### Chroma index is empty or responses are gated

Confirm that approved documents were ingested, `CHROMA_PERSIST_DIR` points to the intended directory, and `CHROMA_COLLECTION` matches the collection used by ingestion. Rebuild the index only after stopping the API.
