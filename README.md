# FitHer - Women's Health Companion

A full-stack women's health application that combines menstrual cycle tracking with AI-powered health recommendations. Built as a WeChat Mini Program with a FastAPI backend.

## What it does

FitHer helps women track their menstrual cycles and get personalized health advice based on where they are in their cycle. Unlike basic period trackers, it includes:

- AI assistants that give advice tailored to your current cycle phase
- A community forum where users share experiences
- Health analytics that track cycle regularity and symptom trends
- Support for four life stages: period tracking, pregnancy prep, pregnancy, and parenting

## Tech Stack

**Frontend**
- uni-app (Vue 3 + TypeScript) - compiles to WeChat Mini Program and H5
- Custom UI components, no heavy framework dependencies

**Backend**
- FastAPI (Python) - async REST API
- SQLite for development, PostgreSQL for production
- JWT authentication + WeChat OAuth

**AI/ML**
- Qwen LLM via Alibaba DashScope API
- RAG with ChromaDB for grounding responses in verified health information
- Streaming responses via Server-Sent Events

**Deployment**
- Docker + Docker Compose
- Nginx reverse proxy with SSL
- Tencent Cloud Lighthouse

## Architecture

```
WeChat Mini Program / PWA
         |
    HTTPS/WebSocket
         |
    Nginx (SSL termination)
         |
    FastAPI Backend
         |
    +---------+---------+
    |         |         |
  SQLite   ChromaDB   DashScope
  (data)   (vectors)    (LLM)
```

The frontend communicates with the backend through REST endpoints. AI chat uses SSE for streaming. User data (periods, symptoms, daily logs) is stored in SQLite. Health articles and medical guidelines are embedded in ChromaDB for RAG retrieval.

## Key Features

**Cycle Tracking**
- Record period start/end dates
- Predict next cycle based on history
- Calendar view with period days highlighted
- Daily logging: flow, color, symptoms, temperature, weight, water intake

**AI Health Assistants**
Three specialized personas:
- Fitness coach - exercise recommendations based on cycle phase
- Nutritionist - diet advice tailored to current phase
- Health manager - overall wellness and symptom management

Each assistant uses RAG to ground responses in verified health information, reducing hallucination risk for medical advice.

**Health Analytics**
- Cycle regularity scoring (0-100)
- Symptom trend tracking over time
- Weight trends
- Personalized AI recommendations based on data

**Community Forum**
- Post creation with images
- Comments and likes
- Topic-based filtering (period, fitness, diet, skincare, mood)
- User profiles with follower system

**Four Life Modes**
The app adapts to different life stages:
1. Period mode - standard cycle tracking
2. Pregnancy prep - ovulation tracking, supplement reminders
3. Pregnancy - week-by-week development, checkup records, kick counting
4. Parenting - feeding logs, sleep tracking, growth milestones

## Technical Decisions

**Why uni-app instead of native?**
Single codebase for WeChat Mini Program and H5. The target users are in China where WeChat dominates, so Mini Program is essential. uni-app lets us compile to both platforms without maintaining separate codebases.

**Why FastAPI?**
Native async support for AI streaming, automatic OpenAPI docs, and Pydantic validation. It's also one of the fastest Python frameworks, which matters when handling concurrent AI requests.

**Why RAG instead of fine-tuning?**
Health information changes frequently. With RAG, we can update the knowledge base without retraining. It also provides transparency - we can show users which sources informed the AI's response. Most importantly, it reduces hallucination risk for medical advice.

**Why SQLite for development?**
Zero configuration, single file, easy to share and backup. For a solo developer project, it removes database setup friction. PostgreSQL is used in production for concurrent access and better performance.

## Data Flow Examples

**User records a period:**
1. User taps "Record period start" button
2. Frontend validates and sends POST to `/api/period/records`
3. Backend writes to SQLite
4. Backend calculates next prediction based on historical cycles
5. Frontend updates calendar and analytics dashboard

**AI chat interaction:**
1. User sends message in chat
2. Frontend loads last 10 messages for context
3. Frontend sends message + history to `/api/chat/stream`
4. Backend builds RAG query with user's cycle phase and message
5. ChromaDB retrieves relevant health articles
6. Backend constructs prompt with retrieved context
7. Qwen generates response, streamed back via SSE
8. Frontend displays tokens in real-time
9. Message saved to chat history

**Health score calculation:**
1. Load all period records from database
2. Calculate cycle lengths (days between period starts)
3. Compute variance of cycle lengths
4. Convert to regularity score (lower variance = higher score)
5. Calculate average period duration score
6. Weighted combination → final score (0-100)
7. Generate AI recommendations based on score and trends

## Project Structure

```
fitness-rag/
├── api/                    # FastAPI backend
│   ├── main.py            # App entry point
│   ├── routers/           # API endpoints
│   │   ├── users.py       # Auth + user management
│   │   ├── chat.py        # AI chat streaming
│   │   ├── period.py      # Period tracking
│   │   └── posts.py       # Forum posts
│   ├── models/            # SQLAlchemy models + Pydantic schemas
│   └── services/          # Business logic (AI, RAG)
│
├── fitness-mini/          # uni-app frontend
│   ├── src/
│   │   ├── pages/         # Vue components
│   │   │   ├── index/     # Forum home
│   │   │   ├── period/    # Cycle tracking
│   │   │   ├── chat/      # AI assistants
│   │   │   ├── analysis/  # Health analytics
│   │   │   └── message/   # Notifications
│   │   ├── utils/         # API client, helpers
│   │   └── static/        # Icons, images
│   └── dist/              # Compiled output
│
├── data/                  # SQLite database, ChromaDB
├── docs/                  # Documentation, screenshots
└── docker/                # Docker configs
```

## Setup Instructions

### Backend

```bash
cd fitness-rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your DashScope API key to .env

# Run migrations (creates SQLite database)
python -m alembic upgrade head

# Start server
uvicorn api.main:app --reload --port 8000
```

API docs available at http://localhost:8000/docs

### Frontend (Mini Program)

```bash
cd fitness-mini
npm install
npm run build:mp-weixin
```

Import `dist/build/mp-weixin` into WeChat Developer Tools.

### Frontend (PWA - browser testing)

```bash
cd fitness-rag
# Make sure backend is running on port 8000
# Open frontend/index.html in browser
```

## Current Status

**Working:**
- User authentication (WeChat + username/password)
- Period tracking with calendar view
- AI chat with three personas (streaming responses)
- Health analytics and scoring
- Forum posts (create, comment, like)
- Daily logging (flow, color, symptoms, temperature, weight, water)
- Four life modes with mode-specific features

**In Progress:**
- Push notifications (period reminders)
- Image upload to cloud storage
- Real-time chat between users
- Data export (PDF reports)

**Planned:**
- Wearable device integration (Apple Watch, Fitbit)
- Partner sharing mode
- Multi-language support (English, Spanish)
- Telehealth integration

## Lessons Learned

**Data persistence matters early**
Started with localStorage for everything. Had to migrate to backend storage when users switched devices and lost data. Lesson: plan for multi-device from the start.

**AI streaming is harder than expected**
SSE works in browsers but WeChat Mini Program has limitations. Had to implement chunked responses and handle partial JSON parsing.

**Cycle prediction is tricky**
Simple "average cycle length" doesn't work well. Users have irregular cycles. Currently using weighted average with recency bias, but need to explore time series models.

**Health advice needs guardrails**
AI can give dangerous medical advice if not constrained. RAG helps, but also need explicit disclaimers and escalation to "see a doctor" for serious symptoms.

**WeChat Mini Program审核 is painful**
Health category requires additional documentation. First submission rejected. Had to add privacy policy, user agreement, and medical disclaimer before approval.

## Future Work

**Short term (1-2 months)**
- Deploy to production server with SSL
- Get 10-20 beta testers
- Collect feedback and iterate
- Submit to WeChat Mini Program review

**Medium term (3-6 months)**
- Add push notifications
- Implement data export for doctor visits
- Build admin dashboard for user analytics
- Explore partnerships with health organizations

**Long term (6-12 months)**
- Native iOS/Android apps
- Wearable device integration
- Telehealth features
- Expansion to other regions (US, Europe)

## Why I Built This

I noticed most period tracking apps on the market are just digital calendars - they record data but don't help you understand what it means. I wanted to build something that actually uses that data to give personalized advice.

This started as a side project to learn full-stack development and AI integration. It grew into something more substantial as I realized the gap between "tracking data" and "getting actionable insights" is real.

The project also gave me hands-on experience with RAG, streaming responses, cross-platform development, and the realities of deploying to WeChat's ecosystem.

## Contact

**Developer**: Linxuan Li  
**Email**: 779182617@qq.com  
**GitHub**: github.com/LinxuanLi-DS

## License

MIT - see LICENSE file

---

Built as a personal project to learn full-stack development, AI integration, and product development. Not intended as medical advice - always consult healthcare professionals for medical decisions.
