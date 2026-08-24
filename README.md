# FitHer — Full-Stack RAG AI Health Assistant

> A production-style AI application that combines personalized health tracking with retrieval-augmented generation (RAG), LLM streaming, authentication, and full-stack product development.

**Tech:** Python · FastAPI · Vue 3 · TypeScript · PostgreSQL/SQLite · ChromaDB · RAG · Qwen LLM · REST APIs · SSE · JWT · Docker · Nginx

## Why this project matters

FitHer is more than a chatbot demo. It is an end-to-end AI application that connects user data, retrieval, LLM reasoning, backend APIs, authentication, analytics, and a cross-platform frontend.

The system was designed around a practical product question: **how can an AI assistant use both domain knowledge and personal context to generate more useful, grounded recommendations?**

## Core architecture

```text
User
  ↓
Vue 3 / TypeScript Client
  ↓ REST + SSE
FastAPI Backend
  ├── Authentication & User Context
  ├── Health / Cycle Data
  ├── RAG Pipeline
  │     └── ChromaDB Vector Retrieval
  └── LLM Service (Qwen)
          ↓
Grounded Streaming Response
```

## Key AI engineering features

### Retrieval-Augmented Generation
- Retrieves relevant health articles and guidance from a ChromaDB knowledge base.
- Combines retrieved context with user-specific information before calling the LLM.
- Grounds answers in domain knowledge rather than relying on model memory alone.
- Designed to reduce hallucination risk in a sensitive health-related setting.

### Context-aware AI assistants
Three specialized assistants generate recommendations based on the user's current context:
- **Fitness Coach** — exercise guidance
- **Nutritionist** — nutrition recommendations
- **Health Manager** — general wellness and symptom guidance

### Streaming LLM responses
- FastAPI serves AI responses through Server-Sent Events (SSE).
- The frontend renders model output incrementally for a lower-latency chat experience.
- Handles partial streaming responses and cross-platform client limitations.

### Full-stack integration
- FastAPI async REST backend
- Vue 3 + TypeScript frontend through uni-app
- JWT authentication and WeChat OAuth support
- SQLite for development and PostgreSQL-ready production persistence
- Docker / Docker Compose deployment workflow
- Nginx reverse proxy with SSL support

## Example AI request flow

```text
1. User sends a question
2. Backend loads recent conversation context
3. System identifies current user/cycle context
4. RAG query is constructed
5. ChromaDB retrieves relevant knowledge
6. Retrieved context + user context are assembled into the prompt
7. LLM generates a grounded answer
8. Response streams to the frontend through SSE
9. Conversation is persisted for future context
```

## Product features

### Health & cycle tracking
- Period start/end tracking
- Cycle prediction based on historical records
- Daily symptom, temperature, weight, flow, and hydration logging
- Health analytics and trend visualization

### Personalized AI
- Three role-specific AI assistants
- User-context-aware recommendations
- Retrieval-grounded answers
- Streaming chat experience

### Community & account system
- User profiles
- Posts, comments, and likes
- Topic-based filtering
- Authentication and account management

### Multi-stage experience
The product supports four configurable modes:
1. Period tracking
2. Pregnancy preparation
3. Pregnancy
4. Parenting

## Tech stack

| Layer | Technologies |
|---|---|
| Frontend | Vue 3, TypeScript, uni-app |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| AI | Qwen LLM, RAG, ChromaDB |
| Data | SQLite, PostgreSQL-ready architecture |
| Auth | JWT, WeChat OAuth |
| APIs | REST, Server-Sent Events |
| Deployment | Docker, Docker Compose, Nginx |

## Repository structure

```text
fitness-rag/
├── api/                  # FastAPI backend
│   ├── routers/          # API endpoints
│   ├── models/           # DB models and schemas
│   └── services/         # AI / RAG business logic
├── fitness-mini/         # Vue 3 + TypeScript client
├── frontend/             # Browser-facing frontend assets
├── data/                 # Local development data / vector store config
├── scripts/              # Utility scripts
├── src/                  # Supporting application modules
├── test_api.py           # API tests
├── requirements.txt
├── .env.example
└── README.md
```

## Local setup

### Backend

```bash
git clone https://github.com/LinxuanLi-DS/fitness-rag.git
cd fitness-rag

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add your model/API credentials to .env

uvicorn api.main:app --reload --port 8000
```

FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd fitness-mini
npm install
npm run build:mp-weixin
```

## Engineering decisions

### Why RAG instead of only prompting the LLM?
A general-purpose LLM can generate plausible but unsupported health information. RAG provides external context at inference time, allowing knowledge to be updated independently from the model while improving grounding.

### Why FastAPI?
FastAPI provides async request handling, Pydantic validation, automatic OpenAPI documentation, and a clean path for streaming AI responses.

### Why separate user context from retrieved knowledge?
Personalization and factual grounding solve different problems. User data provides **personal context**, while retrieval provides **domain context**. The prompt assembly layer combines both before generation.

### Why SSE for AI chat?
LLM responses can take several seconds to complete. Streaming improves perceived latency and gives the application a more responsive conversational experience.

## What I learned

Building FitHer highlighted several real-world AI engineering challenges:

- **RAG quality depends on context assembly, not just vector search.** Retrieval results need to be filtered and combined with the right user context.
- **AI output needs guardrails in sensitive domains.** Grounding, disclaimers, and escalation paths matter as much as prompt quality.
- **Streaming adds systems complexity.** Browser and Mini Program clients behave differently, so partial-response handling must be robust.
- **Persistence should be designed early.** Moving from local-only state to backend storage changed the architecture significantly.
- **AI products are end-to-end systems.** Model calls are only one piece; APIs, databases, UX, authentication, deployment, and evaluation all matter.

## Current status

**Implemented**
- Authentication
- Health / cycle tracking
- AI chat with specialized assistants
- RAG retrieval
- Streaming responses
- Health analytics
- Community features
- Daily logging

**Planned / in progress**
- Push notifications
- Cloud image storage
- Data export
- Additional evaluation and safety guardrails
- Wearable-device integration

## Portfolio relevance

This project demonstrates hands-on experience with:

- LLM application development
- RAG system design
- AI workflow orchestration
- REST API and backend engineering
- Structured user data + AI integration
- Streaming model responses
- Full-stack product development
- Responsible AI considerations
- Deployment-oriented architecture

## Author

**Linxuan Li**  
MS in Data Science, Northeastern University — Silicon Valley  
GitHub: [LinxuanLi-DS](https://github.com/LinxuanLi-DS)

---

*FitHer is an educational and portfolio project and is not intended to provide medical diagnosis or replace professional medical advice.*
