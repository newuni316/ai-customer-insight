# AI Customer Insight Dashboard

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> AI-powered customer insight and decision platform — Full-stack + RFM user segmentation + AI hybrid decision engine

> AI 驱动的客户洞察与决策平台 — 全栈开发 + RFM 用户分层 + AI 混合决策引擎

## Screenshots

<!-- TODO: Add screenshots -->

| Dashboard | User Segmentation | AI Insights |
|-----------|-------------------|-------------|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Segmentation](docs/screenshots/segmentation.png) | ![Insights](docs/screenshots/insights.png) |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (Browser)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────────────┐
│                   Frontend (Next.js 14)                         │
│              Tailwind CSS + Recharts + Axios                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────────┐
│                   Backend (FastAPI)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │
│  │  Auth    │ │ Feedback │ │  Orders  │ │    Decisions      │  │
│  │ (JWT)    │ │ (CRUD)   │ │  (CRUD)  │ │ (AI + Rules)      │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Services Layer                              │   │
│  │  RFM Scoring → Profile Updater → Decision Engine        │   │
│  │              (Rules + LLM with Fallback)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ SQLAlchemy ORM
┌──────────────────────────▼──────────────────────────────────────┐
│                Database (PostgreSQL / SQLite)                    │
│     Users │ Feedbacks │ Orders │ Profiles │ Decisions           │
└─────────────────────────────────────────────────────────────────┘
```

**Data Pipeline:**
```
CSV/API/Webhook → Ingestion → RFM Scoring → User Profile → AI Decision Engine → Dashboard
                                              (Rules + LLM with fallback)
```

## Features

- **Multi-source Data Ingestion** — CSV upload, external API sync, real-time webhooks
- **RFM User Segmentation** — Recency, Frequency, Monetary scoring (111–555 scale)
- **AI-powered Decision Engine** — Hybrid approach: rule-based pre-classification + LLM refinement with automatic fallback
- **Interactive Dashboard** — Real-time charts for revenue trends, retention, churn risk, and user segmentation
- **JWT Authentication** — Secure httpOnly cookie-based auth with bcrypt password hashing
- **Background Task Processing** — Async decision generation with progress tracking
- **Health Monitoring** — Database connection checks and service health endpoints
- **Security Hardening** — Rate limiting, CORS, security headers, input validation
- **Database Migrations** — Alembic-managed schema versioning
- **Containerized Deployment** — Docker Compose for one-click production setup

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, Tailwind CSS, Recharts, Axios |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL (production) / SQLite (development) |
| AI | OpenAI-compatible API / Ollama local models |
| Auth | JWT (python-jose) + bcrypt |
| Testing | pytest, Jest, Playwright |
| Deployment | Docker, Docker Compose, GitHub Actions CI/CD |

## Quick Start

### Option 1: Docker One-Click (Recommended)

```bash
git clone https://github.com/your-username/ai-customer-insight.git
cd ai-customer-insight

# Copy and edit environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start all services
docker-compose up -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

### Option 2: Manual Backend + Frontend

**Prerequisites:** Python 3.12+, Node.js 18+, PostgreSQL (or use SQLite for development)

**Terminal 1 — Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL, SECRET_KEY, AI_API_KEY, etc.

# Initialize database
alembic upgrade head

# Start development server
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Open http://localhost:3000 in your browser.

### Option 3: Production Deployment

```bash
# Build and start with production profile
docker-compose -f docker-compose.yml up -d --build

# Or deploy backend separately
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Build frontend for production
cd frontend
npm run build
npm start
```

**Production checklist:**
- Set `ENVIRONMENT=production` in backend `.env`
- Use a strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- Set `DATABASE_URL` to a PostgreSQL instance
- Configure `CORS_ORIGINS` for your domain
- Set `AUTO_MIGRATE=true` for automatic schema updates

## API Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register a new user account |
| `POST` | `/api/auth/login` | Login and receive JWT token (httpOnly cookie) |
| `GET` | `/api/auth/me` | Get current authenticated user info |

### Feedback

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/feedback/upload-csv` | Upload CSV file with customer feedback data |
| `GET` | `/api/feedbacks` | List feedbacks with pagination (`?page=1&size=20`) |
| `POST` | `/api/feedbacks/{id}/analyze` | Trigger AI sentiment/topic analysis for a feedback |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/orders` | Create a new order (auto-updates user RFM profile) |
| `GET` | `/api/orders` | List orders with filters (`?user_id=&start_date=&end_date=`) |
| `GET` | `/api/orders/{id}` | Get order detail by ID |

### Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/metrics/overview` | Dashboard overview stats (users, orders, revenue, AOV) |
| `GET` | `/api/metrics/retention` | Monthly cohort retention rates |
| `GET` | `/api/metrics/revenue?period=daily\|weekly\|monthly` | Revenue trend data by period |
| `GET` | `/api/metrics/conversion` | Conversion rates by user level/segment |

### Decisions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/decisions/generate` | Generate AI decisions (single user or all) |
| `POST` | `/api/decisions/generate/async` | Async decision generation with task tracking |
| `GET` | `/api/decisions/generate/status/{task_id}` | Check async task progress and result |
| `GET` | `/api/decisions/insights` | Aggregate decision statistics and distributions |
| `GET` | `/api/decisions/{user_id}` | Get latest decision for a specific user |
| `GET` | `/api/decisions/` | List all decisions with filters |

### Data Sources

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/sources/csv/upload` | Upload CSV as a data source |
| `POST` | `/api/sources/api/sync` | Sync data from an external API source |
| `POST` | `/api/sources/webhook/{platform}` | Receive real-time webhook data |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Service health check (DB connection, uptime) |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./insight.db` |
| `SECRET_KEY` | JWT signing secret | Auto-generated (set in production!) |
| `AI_API_KEY` | OpenAI-compatible API key | — |
| `AI_API_BASE_URL` | AI API base URL | `https://api.openai.com/v1` |
| `AI_MODEL` | Model name | `gpt-4o-mini` |
| `USE_LOCAL_MODEL` | Use Ollama instead of cloud | `false` |
| `LOCAL_MODEL_BACKEND` | Local model backend | `ollama` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `AUTO_MIGRATE` | Auto-run migrations on start | `false` |
| `ENVIRONMENT` | `development` or `production` | `development` |

## Database Migrations

```bash
cd backend

# Generate a new migration after model changes
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View migration history
alembic history
```

## Local AI Model (Offline)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull qwen2.5:7b

# In backend/.env
USE_LOCAL_MODEL=true
LOCAL_MODEL_BACKEND=ollama
```

## Testing

```bash
# Backend unit & integration tests
cd backend && python -m pytest tests/ -v

# Frontend unit tests
cd frontend && npm test

# Frontend E2E tests (requires Playwright browsers)
cd frontend && npx playwright install && npm run test:e2e
```

## Project Structure

```
ai-customer-insight/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD
├── docker-compose.yml                # One-click deployment
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/                      # Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 001_initial.py
│   │       ├── 002_orders_profiles.py
│   │       └── 003_decisions.py
│   │
│   ├── main.py                       # FastAPI application entry
│   ├── config.py                     # Settings management
│   ├── database.py                   # SQLAlchemy engine & session
│   ├── models.py                     # ORM models (User, Order, Decision...)
│   ├── schemas.py                    # Pydantic request/response schemas
│   ├── auth.py                       # JWT authentication
│   ├── dependencies.py               # Shared FastAPI dependencies
│   ├── exceptions.py                 # Global exception handlers
│   ├── health.py                     # Health check endpoint
│   ├── middleware.py                  # Rate limiting, request logging
│   ├── logging_config.py             # Structured logging setup
│   │
│   ├── routers/                      # API route handlers
│   │   ├── auth.py                   # Register, login, me
│   │   ├── feedback.py               # Feedback CRUD + CSV upload
│   │   ├── analytics.py              # Dashboard analytics
│   │   ├── orders.py                 # Order management
│   │   ├── metrics.py                # KPI metrics (overview, retention, revenue)
│   │   ├── decisions.py              # AI decision generation & insights
│   │   └── data_sources.py           # Multi-source data ingestion
│   │
│   ├── services/                     # Business logic
│   │   ├── ai_analyzer.py            # AI feedback analysis (cloud + local)
│   │   ├── decision_engine.py        # Hybrid rules + LLM decision engine
│   │   ├── rfm.py                    # RFM scoring algorithm
│   │   ├── profile_updater.py        # User profile recalculation
│   │   ├── csv_parser.py             # CSV parsing utilities
│   │   ├── local_model.py            # Ollama local model integration
│   │   ├── task_queue.py             # Background task queue
│   │   └── data_sources/             # Data source abstraction
│   │       ├── base.py
│   │       ├── csv_source.py
│   │       ├── api_source.py
│   │       └── webhook_source.py
│   │
│   └── tests/                        # pytest test suite
│       ├── conftest.py               # Shared fixtures (test DB, client, auth)
│       ├── test_auth.py
│       ├── test_feedback.py
│       ├── test_rfm.py               # RFM scoring logic
│       ├── test_decision_engine.py   # Decision engine (rules + mocked AI)
│       ├── test_metrics.py           # Metrics API endpoints
│       ├── test_orders.py            # Orders API endpoints
│       ├── test_decisions.py         # Decisions API endpoints
│       ├── test_analytics.py
│       ├── test_csv_parser.py
│       ├── test_data_sources.py
│       ├── test_edge_cases.py
│       └── test_security.py
│
└── frontend/
    ├── Dockerfile
    ├── .env.example
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── jest.config.js
    ├── jest.setup.js
    ├── playwright.config.ts
    │
    ├── e2e/                          # Playwright E2E tests
    │   ├── auth.spec.ts
    │   └── dashboard.spec.ts
    │
    └── src/
        ├── app/                      # Next.js App Router
        │   ├── layout.tsx
        │   ├── page.tsx
        │   ├── globals.css
        │   ├── login/
        │   │   └── page.tsx
        │   ├── register/
        │   │   └── page.tsx
        │   ├── dashboard/
        │   │   └── page.tsx
        │   └── api/
        │       └── auth/
        │           └── token/
        │               └── route.ts
        │
        ├── components/               # React components
        │   ├── AIInsightPanel.tsx     # AI-powered insight cards
        │   ├── ChurnChart.tsx         # Churn risk visualization
        │   ├── DashboardSkeleton.tsx  # Loading skeleton
        │   ├── DataCard.tsx           # Metric card
        │   ├── FeedbackTable.tsx      # Feedback list table
        │   ├── FileUpload.tsx         # CSV drag-and-drop upload
        │   ├── FilterBar.tsx          # Dashboard filter controls
        │   ├── Navbar.tsx             # Navigation bar
        │   ├── OrdersTable.tsx        # Orders list
        │   ├── RetentionChart.tsx     # Retention curve
        │   ├── RevenueChart.tsx       # Revenue trend line chart
        │   ├── SentimentChart.tsx     # Sentiment area chart
        │   ├── TopicChart.tsx         # Topic distribution
        │   └── UserSegmentationChart.tsx  # User level pie chart
        │
        ├── lib/
        │   └── api.ts                # Axios API client
        │
        └── __tests__/                # Jest unit tests
            ├── AIInsightPanel.test.tsx
            ├── DataCard.test.tsx
            ├── FeedbackTable.test.tsx
            ├── FileUpload.test.tsx
            ├── FilterBar.test.tsx
            ├── Navbar.test.tsx
            ├── RevenueChart.test.tsx
            ├── SentimentChart.test.tsx
            ├── TopicChart.test.tsx
            └── api.test.ts
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Conventions:**
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages (`feat:`, `fix:`, `docs:`, `chore:`)
- Run tests before submitting (`pytest` for backend, `npm test` for frontend)
- Keep PRs focused — one feature or fix per PR

## License

MIT
