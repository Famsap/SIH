# SIH26107 — Tech Stack & System Requirements

**Project:** AI-Powered Intelligent Assistant for Indian Standards and BIS Services
**Status:** Awaiting team confirmation before any code is scaffolded
**Last updated:** 2026-04-09

This document is Step 1 + Step 2 only. Once the team signs off, scaffolding (Step 3) starts from this file.

---

## 1. The stack (locked recommendation)

One process language for RAG (Python), one modern chat UI for judges (Next.js), everything that can run locally *does* run locally so a dead venue Wi‑Fi does not kill the demo.

| Layer | Choice | Why this, not the alternative |
|---|---|---|
| **Frontend** | Next.js 15 (App Router) + TypeScript + Tailwind CSS | Looks like a real product on stage. Streamlit is faster to write but reads as a prototype to SIH judges. A single HTML page is more reliable but looks weaker. |
| **Backend API** | Python 3.11+ FastAPI + Uvicorn | Native home of PDF parsing, embeddings, Chroma. FastAPI gives streaming SSE for token-by-token chat. |
| **Vector DB** | ChromaDB (persistent, local, embedded) | Zero cloud account, zero network, metadata filters (IS number, scheme, doc type). FAISS is more code for the same job. Pinecone/Weaviate Cloud die if Wi‑Fi dies. |
| **Embeddings** | `sentence-transformers` — `BAAI/bge-small-en-v1.5` | Fully local, no API key, ~130 MB, CPU-fine. Better retrieval quality than `all-MiniLM-L6-v2` at almost the same speed. OpenAI `text-embedding-3-small` is paid + online-only. |
| **LLM (primary, online)** | **Groq** — `llama-3.3-70b-versatile` | Free tier, ~300–500 tokens/sec, quality close to paid GPT-4o-mini for grounded RAG. Best live-demo latency. |
| **LLM (offline fallback)** | **Ollama** — `llama3.1:8b` (or `mistral:7b` on 8 GB RAM) | Same prompt, same citations, works with airplane mode. Slightly weaker answers; demo still runs. |
| **Orchestration** | Thin custom Python (no LangChain/LlamaIndex app layer) | Hackathon-debuggable. We *will* use `langchain-text-splitters` for chunking only. Full LangChain chains hide failures and are hard to explain to judges. |
| **PDF parsing** | PyMuPDF (`fitz`) | Fastest, most reliable Python PDF text extract. Unstructured.io is heavier; pypdf misses layout. |
| **HTML parsing** | BeautifulSoup4 + httpx | BIS pages are simple HTML. Scrapy is overkill. |
| **Chunking** | `RecursiveCharacterTextSplitter` (800 tokens / 120 overlap) + heading-aware split on IS clause numbers (`4.2.1`, etc.) | Clause-level citations are what judges will ask to see. |
| **Chat memory** | Last N turns sent in the prompt + optional summary | No extra DB for MVP. Redis later if needed. |
| **License lookup (stretch)** | httpx scraper / public BIS enquiry pages, cached locally | Only if the public pages stay scrape-able. Fail closed: "I cannot verify this license from retrieved BIS text." |
| **Config / secrets** | `.env` via `python-dotenv` (backend) + `.env.local` (frontend) | Keys never committed. `.env.example` shipped. |
| **Package mgmt** | `uv` or `pip` + `requirements.txt` (backend); `npm` (frontend) | `uv` is faster; pip is the fallback every lab machine has. |

### Why Groq over OpenAI / Anthropic / Gemini

| Provider | Cost | Speed | Offline | Verdict |
|---|---|---|---|---|
| **Groq (Llama 3.3 70B)** | Free tier | Fastest | No (use Ollama) | **Primary** |
| OpenAI GPT-4o-mini | Paid | Medium | No | Better prose, not worth the key + billing risk in 36 hours |
| Anthropic Claude | Paid | Medium | No | Same |
| Gemini Flash | Free tier | Fast | No | Quota is bursty; Groq is more predictable for a 5-min demo |
| Ollama local 8B | Free | Medium on CPU | **Yes** | **Fallback**, auto-switched when Groq is unreachable |

Paid APIs *do* improve long-form nuance. They do **not** improve groundedness if the RAG prompt is strict — and groundedness is the scoring criterion. Groq + tight prompt is the right tradeoff.

---

## 2. Hardware & software prerequisites

### Developer laptop (minimum)

| Item | Requirement |
|---|---|
| OS | macOS 13+, Ubuntu 22.04+, or Windows 11 + WSL2 |
| RAM | **16 GB recommended**, 8 GB absolute minimum (Ollama 7B will swap on 8 GB) |
| CPU | Any modern 4+ core. **No GPU required.** |
| Disk | ~3 GB total: Python deps ~500 MB, embedding model ~130 MB, Ollama 8B ~4.7 GB *if* you install the fallback, Chroma index for ~500 PDFs ~200–500 MB |
| Node | **20.x LTS** (Next.js 15) |
| Python | **3.11 or 3.12** (3.13 still has occasional wheel gaps for `sentence-transformers`) |
| GPU | Optional. A laptop GPU speeds Ollama; embeddings are fine on CPU. |

### Accounts / API keys to create *before* scaffolding

1. **Groq** — https://console.groq.com → API key. Free.
2. **Ollama** (optional but strongly recommended for the demo-safety net) — https://ollama.com → install app, then `ollama pull llama3.1:8b`.
3. No OpenAI / Pinecone / Hugging Face token required for MVP.
4. Hugging Face is used only to *download* `bge-small-en-v1.5` the first time (no key for this public model). If the venue has no net, pre-download the model on a home connection.

### Environment variables (will live in `.env.example`)

```
GROQ_API_KEY=           # required for online mode
LLM_PROVIDER=groq       # groq | ollama
GROQ_MODEL=llama-3.3-70b-versatile
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://127.0.0.1:11434
CHROMA_PATH=./data/chroma
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

---

## 3. Third-party services & free-tier limits (read this before demo day)

| Service | What we use it for | Free-tier reality (as of 2026) | Demo risk |
|---|---|---|---|
| **Groq API** | Chat completions | Free tier is rate-limited (typically ~30 RPM / ~6k–14k RPD depending on model). 70B models have tighter caps than 8B. | **Medium.** One judge session is fine. A queue of 10 parallel testers can 429. Mitigation: cache frequent answers, fall back to Ollama automatically, or switch to `llama-3.1-8b-instant` which has higher RPM. |
| **Ollama (local)** | Offline LLM | Unlimited, local. | **None**, if the model is pulled *before* you leave Wi‑Fi. First `ollama pull` is ~4.7 GB. |
| **Hugging Face Hub** | First-time download of `bge-small-en-v1.5` | Public, no key. Rate-limits anonymous downloads. | **Low.** Pre-cache `~/.cache/huggingface/`. |
| **bis.gov.in** | Source PDFs + HTML + (stretch) license enquiry | Public. No official API. Scraping should be polite (delay, cache, robots.txt). | **High for live scrape.** Never scrape live during a demo. Ingest + snapshot *before* the event. |
| **OpenAI / Anthropic** | Not used | — | — |
| **Chroma Cloud / Pinecone** | Not used | — | — |

### Offline fallback plan (stage Wi‑Fi dies)

```
User query
  → embeddings (local sentence-transformers)     always offline
  → Chroma retrieve (local disk)                 always offline
  → LLM: try Groq (2s timeout)
       ├─ success → stream answer
       └─ fail/timeout → Ollama llama3.1:8b      offline
  → citations from retrieved chunks              always offline
```

**Pre-demo checklist (print this):**
- [ ] `data/chroma/` already built (do **not** ingest on venue Wi‑Fi)
- [ ] Hugging Face model in `~/.cache/huggingface/`
- [ ] `ollama list` shows `llama3.1:8b`
- [ ] Groq key in `.env`, but app boots and answers even if Groq is unreachable
- [ ] Phone hotspot ready as last resort for Groq-only mode

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  INGESTION  (run once, offline, before demo)                            │
│                                                                         │
│  bis.gov.in PDFs / HTML  →  PyMuPDF / BS4  →  clean text                │
│       →  clause-aware chunker  →  bge-small-en embeddings               │
│       →  Chroma persistent dir (data/chroma/)                           │
│       metadata: {source, is_number, title, clause, url, doc_type}       │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────┐    POST /api/chat     ┌──────────────────────────────────┐
│  Next.js UI  │ ───────────────────▶  │  FastAPI                         │
│  chat + cite │  ◀── SSE token stream │   1. embed query (local)         │
│  cards       │                       │   2. Chroma similarity + filter  │
│              │                       │   3. drop chunks below score     │
│              │                       │   4. build grounded prompt       │
│              │                       │   5. Groq (or Ollama fallback)   │
└──────────────┘                       │   6. return answer + citations   │
                                       └──────────────────────────────────┘
```

### End-to-end data flow for one user query

1. User types *"What IS standard applies to packaged drinking water?"* in the Next.js chat box. Previous turns (if any) sit in React state and are sent along.
2. Browser `POST /api/chat` with `{ question, history[] }`.
3. FastAPI embeds the question with the same local `bge-small-en-v1.5` model used at ingest time (critical: query and docs must share one embedding space).
4. Chroma returns top-k=6 chunks, each with metadata (`source`, `is_number`, `clause`, `url`) and a distance score.
5. **Anti-hallucination gate:** if the best chunk is below a similarity threshold (e.g. cosine distance > 0.55, tuned on a small eval set), skip the LLM and return a canned "I don't have information on this in the indexed BIS documents."
6. Otherwise assemble a strict system prompt (see §6) + retrieved context + last 6 turns of history.
7. Call Groq with `temperature=0.1`. If Groq errors/times out in 2 s, retry once on Ollama.
8. Stream tokens to the UI. After the stream, attach a `citations[]` array so the UI can render source cards (IS number + clause + snippet + link).
9. Frontend appends the assistant message. Next follow-up ("What documents do I need for that?") is sent with history so the LLM resolves "that" against the prior IS number, then retrieves fresh chunks for the new intent.

---

## 5. Proposed repo layout (will be created after confirmation)

```
SIH/
├── TECH_STACK.md                 ← this file
├── README.md
├── .env.example
├── data/
│   ├── raw/                      ← original BIS PDFs/HTML (gitignored)
│   ├── processed/                ← cleaned .txt / .jsonl
│   └── chroma/                   ← persistent vector index (gitignored)
├── backend/
│   ├── app/
│   │   ├── main.py               ← FastAPI app, CORS, routers
│   │   ├── config.py
│   │   ├── rag/
│   │   │   ├── ingest.py         ← PDF/HTML → chunks → Chroma
│   │   │   ├── retrieve.py       ← similarity search + threshold
│   │   │   ├── generate.py       ← prompt + Groq/Ollama
│   │   │   └── prompts.py        ← anti-hallucination system prompt
│   │   ├── api/
│   │   │   └── chat.py           ← POST /api/chat (SSE)
│   │   └── stretch/
│   │       └── license_lookup.py ← TODO: BIS public licence enquiry
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── app/                      ← Next.js App Router
│   ├── components/               ← ChatWindow, Message, CitationCard
│   ├── lib/api.ts
│   └── package.json
└── scripts/
    └── ingest_sample.py          ← one-command ingest for the demo corpus
```

---

## 6. Anti-hallucination safeguards (will be encoded in `prompts.py`)

These are requirements, not suggestions. The generator will refuse to answer if retrieval is empty or low-score.

1. **System prompt contract**
   - Answer *only* from the provided CONTEXT block.
   - Every factual sentence must end with a citation like `[IS 14543:2024, cl. 4.2]`.
   - If CONTEXT is empty or irrelevant: reply exactly with a refusal sentence, no extra advice.
   - Never invent IS numbers, fees, timelines, or licence statuses.
   - If the user asks for a licence check and stretch lookup is disabled/failed: say so, do not guess.

2. **Retrieval gate** — no context, no generation.

3. **Low temperature** (`0.1`) + capped `max_tokens`.

4. **Citations as structured data**, not just prose — UI shows source cards the judge can click.

5. **Prompt injection defence** — retrieved text is wrapped in delimiters; the model is told to treat CONTEXT as untrusted data, not instructions.

---

## 7. What is *not* in MVP (on purpose)

- User accounts / auth
- Fine-tuned LLM
- Live scrape of bis.gov.in during a query
- Multilingual UI (backend can still retrieve English IS text; Hindi queries via the LLM are a stretch)
- Payment / application filing (out of scope of a public assistant)

---

## 8. How to confirm

Team: read this file, then reply with one of:

1. **"Confirmed — scaffold as written"**
2. **"Confirmed, with changes:"** (list them — e.g. Streamlit instead of Next.js, OpenAI instead of Groq, FAISS instead of Chroma)
3. **"Hold"** if the problem statement or timeline changed

No application code will be written until that reply.




