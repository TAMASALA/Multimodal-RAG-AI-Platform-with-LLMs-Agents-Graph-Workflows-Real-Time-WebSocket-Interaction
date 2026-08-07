# 📚 Multimodal RAG

<div align="center">

### **🚀 Production-Ready Multimodal Retrieval-Augmented Generation System**

*Built with RAG • Computer Vision • OCR • Semantic Search • Vision LLMs • Streaming AI*

<p>

<img src="https://img.shields.io/badge/RAG-Multimodal-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi"/>
<img src="https://img.shields.io/badge/React-TypeScript-61DAFB?style=for-the-badge&logo=react"/>
<img src="https://img.shields.io/badge/Groq-LLM-orange?style=for-the-badge"/>
<img src="https://img.shields.io/badge/FAISS-Vector%20Database-purple?style=for-the-badge"/>
<img src="https://img.shields.io/badge/PDF-AI-red?style=for-the-badge"/>
<img src="https://img.shields.io/badge/OCR-Tesseract-success?style=for-the-badge"/>
<img src="https://img.shields.io/badge/PyMuPDF-Document%20Parsing-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Sentence%20Transformers-Embeddings-yellow?style=for-the-badge"/>

</p>

---

### ⭐ An Enterprise-Ready Multimodal RAG system that understands **PDFs, Tables, Images, Charts, Graphs, OCR Text, and Equations**, retrieves the most relevant knowledge using semantic search, and generates grounded AI responses with source citations.

</div>

---

# ✨ Why This Project Stands Out

Most RAG projects only retrieve plain text.

**Multimodal RAG** goes much further by extracting and understanding every meaningful component inside a PDF—including scanned pages, embedded images, tables, charts, graphs, and mathematical equations—and combining them into a unified semantic knowledge base.

Instead of treating a document as plain text, this system understands the complete document context.

## 🎯 Highlights

✅ Production-Ready Multimodal RAG

✅ Intelligent PDF Ingestion Pipeline

✅ OCR for Scanned Documents

✅ Table Extraction

✅ Image Extraction

✅ Chart & Graph Understanding

✅ Equation Recognition

✅ Vision LLM Integration

✅ FAISS Semantic Search

✅ Source-Cited Answers

✅ Specialized AI Agents

✅ Translation Support

✅ AI Summarization

✅ Streaming Responses

✅ CPU Friendly

---

# 🧠 System Architecture

```text
                     PDF Upload

                          │

                Intelligent Ingestion

                          │

        ┌─────────┬─────────┬─────────┬─────────┐

        ▼         ▼         ▼         ▼

     Text      Tables     Images   Equations

        │         │         │         │

        └─────────┴─────────┴─────────┘

                    Chunking Engine

                          │

                 Sentence Embeddings

                          │

                    FAISS Vector Store

                          │

────────────────────────────────────────────────────

                     User Question

                          │

                     Query Embedding

                          │

                 Semantic Retrieval

                          │

                     Agent Router

                          │

      ┌────────────┬────────────┬────────────┬────────────┐

      ▼            ▼            ▼            ▼

Multimodal   Summarization   Translation   Fallback

    Agent        Agent          Agent       Agent

                          │

                          ▼

                 Grounded AI Response

                + Source References
```

---

# 🤖 Specialized AI Agents

| Agent                  | Responsibility                                                 |
| ---------------------- | -------------------------------------------------------------- |
| 🧠 Multimodal Agent    | Understands images, charts, graphs, and visual content         |
| 📄 Summarization Agent | Generates concise document and section summaries               |
| 🌍 Translation Agent   | Translates final responses into the requested language         |
| 🛡 Fallback Agent      | Prevents hallucinations when relevant knowledge is unavailable |

---

# 🚀 Intelligent PDF Processing Pipeline

Every uploaded PDF is processed through an advanced ingestion workflow.

---

## 📄 Text Extraction

* PyMuPDF
* Native PDF parsing
* Fast text extraction
* Layout preservation

---

## 🔍 OCR Pipeline

Automatically detects scanned pages.

Uses

* Tesseract OCR
* Image rendering
* Text reconstruction

---

## 📊 Table Extraction

Tables are extracted using **pdfplumber** and converted into structured Markdown, ensuring that rows, columns, and relationships remain searchable after chunking.

---

## 🖼 Image Understanding

The system extracts embedded images and performs:

* OCR on images
* Caption generation
* Visual understanding
* Metadata extraction

---

## 📈 Chart & Graph Intelligence

Automatically identifies charts and graphs.

Then

* Generates captions
* Understands visual trends
* Extracts semantic meaning
* Enables graph-specific question answering

---

## ➗ Equation Processing

Equation-like content is detected heuristically.

The LLM reconstructs mathematical expressions into readable forms so they become searchable.

---

# ⚡ Retrieval Pipeline

```text
User Question

↓

Embedding Generation

↓

Semantic Search

↓

Top-K Retrieval

↓

Agent Routing

↓

Specialized Processing

↓

Grounded LLM Generation

↓

Source Citations

↓

Translation (Optional)

↓

Final Response
```

---

# 🚀 Technology Stack

| Layer            | Technology                |
| ---------------- | ------------------------- |
| Backend          | FastAPI                   |
| Frontend         | React + TypeScript + Vite |
| Database         | SQLite / PostgreSQL       |
| ORM              | SQLAlchemy                |
| PDF Parsing      | PyMuPDF                   |
| Table Extraction | pdfplumber                |
| OCR              | Tesseract                 |
| Embeddings       | Sentence Transformers     |
| Vector Database  | FAISS                     |
| Vision AI        | Groq Vision               |
| LLM              | Groq Llama 3.3            |
| WebSocket        | FastAPI WebSockets        |
| Testing          | PyTest                    |

---

# 🧩 Core Features

### 📄 Document Intelligence

* PDF Parsing
* OCR
* Image Extraction
* Table Extraction
* Chart Detection
* Equation Recognition

---

### 🔍 Semantic Search

* Sentence Embeddings
* FAISS Vector Store
* Metadata Filtering
* Context Retrieval
* Source Grounding

---

### 🤖 AI Intelligence

* Multimodal RAG
* Vision LLM
* Translation
* Summarization
* Context-Aware Answers
* Hallucination Reduction

---

### ⚡ Real-Time Experience

* Streaming Responses
* WebSocket Support
* Session History
* Background Processing
* Live Document Status

---

# 📂 Project Structure

```text
Multimodal-RAG/

├── app
│
├── api
├── ingestion
├── processing
├── rag
├── embeddings
├── agents
├── llm
├── websocket
├── database
├── schemas
├── utils
│
├── frontend
│
├── storage
│
├── models
│
├── scripts
│
└── tests
```

---

# 📊 Processing Workflow

```text
PDF Upload

↓

Text Extraction

↓

OCR (If Needed)

↓

Table Extraction

↓

Image Extraction

↓

Chart Detection

↓

Equation Detection

↓

Chunking

↓

Embedding Generation

↓

FAISS Indexing

↓

Metadata Storage

↓

Ready for Retrieval
```

---

# 🌟 System Capabilities

✔ Native PDF Understanding

✔ OCR Support

✔ Table Understanding

✔ Image Reasoning

✔ Chart Analysis

✔ Graph Understanding

✔ Mathematical Equation Parsing

✔ Semantic Search

✔ Source Attribution

✔ Translation

✔ Summarization

✔ Vision AI

✔ Streaming Chat

✔ Background Processing

✔ Enterprise Architecture

---

# 📡 REST & WebSocket APIs

| Endpoint                               | Purpose                 |
| -------------------------------------- | ----------------------- |
| POST `/api/upload`                     | Upload PDF              |
| GET `/api/documents`                   | List uploaded documents |
| GET `/api/documents/{id}`              | Document details        |
| DELETE `/api/documents/{id}`           | Delete document         |
| POST `/api/chat`                       | Ask questions           |
| GET `/api/chat/sessions`               | Chat sessions           |
| GET `/api/chat/sessions/{id}/messages` | Chat history            |
| WS `/ws/chat/{session_id}`             | Streaming AI responses  |
| GET `/api/health`                      | System health           |

---

# 🧪 Testing

```bash
pytest tests -v
```

Includes

* Ingestion Tests
* Retrieval Tests
* Embedding Tests
* Agent Tests
* API Tests
* WebSocket Tests

---

# 🚀 Getting Started

## Configure Environment

```bash
cp .env.example .env
```

Add your

* GROQ_API_KEY

---

## Run with Docker

```bash
docker compose up --build
```

Backend

```
http://localhost:8000
```

Frontend

```
http://localhost:5173
```

---

## Local Development

### Backend

```bash
python -m venv .venv

pip install -r requirements.txt

python scripts/download_models.py

uvicorn app.main:app --reload
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🔄 Rebuilding the FAISS Index

```bash
python scripts/build_index.py
```

Rebuilds the complete vector index using all currently available document chunks while reclaiming unused vector space.

---

# 💡 Design Philosophy

This project demonstrates how enterprise-grade Retrieval-Augmented Generation systems should be built:

* Multimodal document understanding
* Grounded AI responses
* Source attribution
* Specialized AI agents
* Modular architecture
* Efficient semantic retrieval
* Streaming-first design
* Production-ready scalability

---

# 📈 Recruiter Highlights

✔ Multimodal RAG

✔ FastAPI

✔ React + TypeScript

✔ FAISS

✔ Sentence Transformers

✔ OCR

✔ Computer Vision

✔ Vision LLM

✔ Semantic Search

✔ PDF Intelligence

✔ WebSockets

✔ SQLAlchemy

✔ Async Python

✔ Enterprise Architecture

✔ Source-Grounded AI

✔ Streaming Responses

✔ AI Agents

✔ Production Deployment

---

<div align="center">

## ⭐ If you found this project interesting, consider giving it a Star!

### Designed to showcase production-grade AI engineering, multimodal retrieval, and enterprise-ready document intelligence.

**Building AI systems that understand documents the way humans do—across text, images, tables, charts, and equations.**

</div>
