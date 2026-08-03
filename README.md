# Multimodal RAG

A production-ready Multimodal Retrieval-Augmented Generation system. It ingests
PDF documents — extracting plain text, scanned/OCR text, tables, embedded
images, charts/graphs, and equations — embeds everything into a single FAISS
vector index, and answers user questions over that content via a Groq-hosted
LLM, with specialized agents for translation, summarization, and
image/graph-specific queries.

## Architecture

```
PDF Upload → Ingestion Pipeline → Chunking → Embeddings → FAISS Index
                                                              │
User Query → Retriever (FAISS + DB) → Agent Router → LLM → Answer + Sources
                                          │
                     ┌───────────┬────────┴────────┬───────────────┐
                     ▼           ▼                 ▼               ▼
               Multimodal   Summarization     Translation      Fallback
                 Agent         Agent            Agent           Agent
```

**Ingestion pipeline** (`app/ingestion/pipeline.py`) per PDF page:
1. Extract plain text (PyMuPDF). If a page is text-sparse (likely scanned),
   render it to an image and run Tesseract OCR as a fallback.
2. Extract tables (`pdfplumber`) and serialize them to markdown so structure
   survives chunking/embedding.
3. Extract embedded raster images; OCR each one, and if it looks like a
   chart/graph, additionally caption it with a vision LLM call.
4. Detect equation-like lines heuristically and reconstruct them with the LLM.
5. Chunk all text content (sentence-aware, overlapping), embed with
   `sentence-transformers`, and store vectors in FAISS + metadata rows in the DB.

**RAG pipeline** (`app/rag/pipeline.py`) per query:
1. Embed the query and retrieve top-k similar chunks from FAISS (optionally
   filtered to specific document IDs).
2. Route to a specialized agent based on the query and retrieved chunk types:
   - No relevant chunks → **fallback agent** (cautious, no hallucination).
   - Query mentions a chart/image and a matching image chunk was retrieved →
     **multimodal agent** (re-runs vision inference directly on that image).
   - Query asks for a summary → **summarization agent**.
   - Otherwise → default **RAG generation** with numbered source citations.
3. If a target language was requested, the final answer is passed through the
   **translation agent**.

Both the REST (`/api/chat`) and WebSocket (`/ws/chat/{session_id}`) endpoints
share this exact pipeline, so streaming and non-streaming responses are
always consistent.

## Tech stack

| Layer          | Choice                                  | Why |
|----------------|------------------------------------------|-----|
| API framework  | FastAPI + Uvicorn                        | Async-first, native WebSocket support |
| Database       | SQLAlchemy (async) + SQLite (swap-in Postgres via `DATABASE_URL`) | Lightweight default, production-swappable |
| PDF parsing    | PyMuPDF (`fitz`)                         | Fast, reliable text + image extraction |
| Table parsing  | `pdfplumber`                             | Good structural table extraction without native deps |
| OCR            | Tesseract via `pytesseract`              | Mature, free, works offline |
| Embeddings     | `sentence-transformers` (MiniLM-L6-v2)   | Small, fast, strong general-purpose retrieval quality |
| Vector store   | FAISS (`IndexFlatIP` over normalized vectors = cosine similarity) | Simple, exact, fast enough for single-node deployments |
| LLM            | Groq API (Llama 3.3 70B + vision model)  | Very low latency inference, supports streaming and vision |
| Frontend       | React + TypeScript + Vite                | Minimal, fast dev loop |

## Getting started

### 1. Configure environment

```bash
cp .env.example .env
# then edit .env and set GROQ_API_KEY
```

### 2. Run with Docker Compose (recommended)

```bash
docker compose up --build
```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173

### 3. Run locally without Docker

Backend:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_models.py     # pre-download the embedding model
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 4. Run tests

```bash
pytest tests/ -v
```

## Rebuilding the FAISS index

FAISS doesn't support cheap in-place deletion, so deleting documents leaves
unreachable vectors behind. Periodically reclaim space with:

```bash
python scripts/build_index.py
```

This rebuilds the index from scratch using the chunks currently in the
database and reassigns `faiss_index` positions accordingly.

## Key API endpoints

| Method | Path                              | Description |
|--------|------------------------------------|--------------|
| POST   | `/api/upload`                      | Upload a PDF; ingestion runs as a background task |
| GET    | `/api/documents`                   | List all documents and their status |
| GET    | `/api/documents/{id}`              | Get a single document's status |
| DELETE | `/api/documents/{id}`              | Delete a document and its chunks |
| POST   | `/api/chat`                        | Ask a question (non-streaming) |
| GET    | `/api/chat/sessions`                | List chat sessions |
| GET    | `/api/chat/sessions/{id}/messages` | Get chat history for a session |
| WS     | `/ws/chat/{session_id}`            | Streaming chat (token-by-token) |
| GET    | `/api/health`                      | Health check |

## Project layout

See the folder tree in this repository — `app/` is organized by concern
(api, database, ingestion, processing, embeddings, rag, agents, llm,
websocket, utils, schemas), `frontend/` is a standalone Vite app, `storage/`
holds uploaded files, extracted images, and the FAISS index, `models/` is
reserved for any locally-cached model weights, and `scripts/` contains
maintenance utilities.

## Notes & production considerations

- **Database**: SQLite is the default for zero-setup local development. Swap
  `DATABASE_URL` to a Postgres DSN (e.g. `postgresql+asyncpg://...`) for
  production; no code changes are required.
- **FAISS**: `IndexFlatIP` is exact (no approximation) and fine up to roughly
  a few million vectors on a single node. For larger scale, swap in
  `IndexIVFFlat` or `IndexHNSWFlat` inside `app/embeddings/faiss_store.py`.
- **Secrets**: never commit a real `.env`; `.env.example` is the template.
- **Concurrency**: the FAISS store uses a threading lock around add/search
  since `faiss-cpu` indices are not thread-safe for concurrent writes.
