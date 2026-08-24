# FitHer — Full-Stack RAG AI Health Assistant

> A production-style AI application that combines personalized health tracking with retrieval-augmented generation (RAG), LLM streaming, authentication, and full-stack product development.

**Tech:** Python · FastAPI · Vue 3 · TypeScript · SQLite/PostgreSQL · ChromaDB · sentence-transformers · Qwen · REST APIs · SSE · JWT

## Overview

FitHer is an end-to-end AI application that connects user data, retrieval, LLM generation, backend APIs, authentication, analytics, and a cross-platform frontend.

The core product question is simple: **how can an AI assistant combine domain knowledge with personal context to generate more useful and grounded recommendations?**

## Architecture

```text
User
  ↓
Vue 3 / TypeScript Client
  ↓ REST + SSE
FastAPI Backend
  ├── Authentication & User Context
  ├── Health / Cycle Data
  ├── RAG Pipeline
  │     ├── ChromaDB
  │     └── all-MiniLM-L6-v2 embeddings
  └── Qwen LLM via DashScope OpenAI-compatible API
          ↓
Grounded Streaming Response
```

## Key AI engineering features

### Retrieval-Augmented Generation
- Retrieves relevant food and exercise knowledge from ChromaDB.
- Uses sentence-transformer embeddings for semantic retrieval.
- Combines retrieved knowledge with user-specific context before generation.
- Separates domain grounding from personalization instead of relying on the LLM alone.

### Context-aware AI assistants
The application includes three specialized assistants:
- **Fitness Coach** — strength training and exercise guidance
- **Nutritionist** — nutrition and diet recommendations
- **Health Manager** — sleep, stress, lifestyle, and general wellness guidance

### Multi-turn context
- Recent conversation history is included in prompt construction.
- User profile information is merged with current request context.
- The system can adapt recommendations to fitness level, goals, dietary preferences, and cycle-related information.

### Streaming LLM responses
- FastAPI exposes an SSE streaming endpoint.
- Qwen responses are streamed incrementally to the client.
- The frontend handles partial model output for a more responsive chat experience.

### Full-stack integration
- FastAPI backend with Pydantic and SQLAlchemy
- Vue 3 + TypeScript frontend through uni-app
- JWT authentication and WeChat OAuth support
- SQLite for local development with PostgreSQL support
- REST APIs for user, period, daily log, survey, feedback, vision, and chat workflows

## AI request flow

```text
1. User sends a question
2. Backend resolves authenticated user context
3. Frontend and database profile information are merged
4. ChromaDB retrieves relevant knowledge
5. Retrieved context + user context + recent chat history are assembled
6. Qwen generates the response
7. Tokens stream back through SSE
```

## Product features

### Health & cycle tracking
- Period start/end tracking
- Cycle prediction based on historical records
- Daily symptom, temperature, weight, flow, and hydration logging
- Health analytics and trend visualization

### Personalized AI
- Three specialized AI assistants
- User-context-aware recommendations
- RAG-grounded generation
- Multi-turn conversation context
- Streaming chat experience

### User & product workflows
- Authentication and profile management
- WeChat login support
- Feedback and survey collection
- Community-facing product components
- Multiple health/life-stage modes

## User research

The product direction was informed by a small 13-response user survey. The strongest signals were persistent memory, cycle-aware recommendations, and proactive guidance. This helped prioritize the product around **personal context + retrieval + AI assistance**, rather than building a generic chatbot.

## Tech stack

| Layer | Technologies |
|---|---|
| Frontend | Vue 3, TypeScript, uni-app |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| LLM | Qwen via Alibaba Cloud DashScope OpenAI-compatible API |
| RAG | ChromaDB, sentence-transformers, all-MiniLM-L6-v2 |
| Data | SQLite, PostgreSQL |
| Auth | JWT, WeChat OAuth |
| APIs | REST, Server-Sent Events |

## Repository structure

```text
FitHer-RAG-AI-Assistant/
├── api/                  # FastAPI backend
│   ├── routers/          # User, chat, period, feedback, etc.
│   └── models/           # SQLAlchemy models + Pydantic schemas
├── fitness-mini/         # Vue 3 + TypeScript client
├── frontend/             # Browser-facing frontend assets
├── data/                 # Product research / local data assets
├── scripts/              # Data and utility scripts
├── src/                  # RAG pipeline and supporting modules
├── test_api.py           # API tests
├── requirements.txt
├── .env.example
└── README.md
```

## Local setup

```bash
git clone https://github.com/LinxuanLi-DS/FitHer-RAG-AI-Assistant.git
cd FitHer-RAG-AI-Assistant

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add your local credentials to .env

uvicorn api.main:app --reload --port 8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

Frontend:

```bash
cd fitness-mini
npm install
npm run build:mp-weixin
```

## Engineering decisions

### Why RAG?
RAG allows external knowledge to be retrieved at inference time and updated independently of the model. It also makes the generation pipeline easier to inspect than relying only on model memory.

### Why separate personal context from retrieved knowledge?
They solve different problems. User data provides **personal context**; retrieval provides **domain context**. Prompt assembly combines both before generation.

### Why FastAPI + SSE?
FastAPI provides typed request validation and a clean backend API layer, while SSE reduces perceived latency by streaming model output to the client as it is generated.

## What I learned

- **RAG quality depends on context assembly, not only vector search.**
- **Personalization and factual grounding should be treated as separate system components.**
- **Streaming adds real systems complexity across different clients.**
- **AI products are end-to-end systems:** model calls, APIs, databases, authentication, UX, and evaluation all matter.
- **Sensitive-domain AI needs guardrails and clear product boundaries.**

## Current status

**Implemented**
- Authentication
- User profile context
- Health / cycle tracking
- RAG retrieval
- Three specialized AI assistants
- Multi-turn context
- SSE streaming
- Analytics and daily logging
- Survey and feedback workflows

**Next improvements**
- Stronger automated evaluation for RAG quality
- Better safety / escalation guardrails
- Cloud deployment hardening
- Additional integrations and notifications

## Author

**Linxuan Li**  
MS in Data Science, Northeastern University — Silicon Valley  
GitHub: [LinxuanLi-DS](https://github.com/LinxuanLi-DS)

---

*FitHer is an educational and portfolio project. It is not intended to provide medical diagnosis or replace professional medical advice.*
