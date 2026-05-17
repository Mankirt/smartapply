# SmartApply — AI Resume Fit Analyzer

> Upload your resume. Paste a job description. Get an instant fit score, gap analysis, and AI-tailored bullet point suggestions — section by section.

![Demo](docs/demo.gif)

---

## What it does

Most resume analyzers just return a keyword list. SmartApply goes deeper:

1. **Parses** your PDF resume into sections (Experience, Skills, Education, etc.)
2. **Embeds** each section as a vector using sentence-transformers
3. **Matches** your resume sections to the JD semantically — not just by keywords
4. **Scores** overall fit (0–100) and identifies gaps using Claude API
5. **Suggests** improved bullet points per section, tailored to the specific JD
6. **Lets you review** each suggestion — Accept, Edit, or Ignore
7. **Exports** your tailored suggestions as a text file

Review decisions persist — come back to an analysis anytime and your Accept/Edit/Ignore choices are saved.

---

## Screenshots

| Main page | Analysis results |
|-----------|-----------------|
| ![Main](docs/main.png) | ![Analysis](docs/analysis.png) |

---

## Architecture

```
React Frontend (Vite + Tailwind)
         ↓
FastAPI Backend (Python 3.12)
    ↓           ↓            ↓
Claude API   pgvector    PostgreSQL
(analysis +  (semantic   (resumes +
suggestions)  search)     analyses +
                          suggestions +
                          reviews)
```

### RAG Pipeline

```
UPLOAD
PDF → text → sections (chunked by section, not whole doc)
           → sentence-transformers embeddings
           → stored in pgvector

ANALYZE
JD text → embedding
        → pgvector cosine similarity → top 5 relevant sections
        → Claude API: fit score + gaps + bullet suggestions
        → suggestions persisted to DB with review state
```

**Why section-level chunking?**
A JD requirement for "Kubernetes experience" should match the Skills section specifically — not get diluted by Education or Summary content. Each section gets its own embedding for precise retrieval.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL 16 + pgvector |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2, runs locally) |
| AI | Claude API (claude-sonnet-4-6) |
| Frontend | React + Vite + Tailwind CSS |
| Infra | Docker Compose |

---

## Key Design Decisions

**Section-level chunking** — resume is split by section, each gets its own embedding. Gives precise similarity matching rather than blending all content into one vector.

**Structured output prompting** — Claude is instructed to return only valid JSON. Markdown code fences are stripped before parsing. Invalid responses trigger one retry with a stricter prompt.

**Suggestions persisted to DB** — every bullet suggestion is saved with its own id. Accept/Edit/Ignore decisions are stored per suggestion and reloaded when you revisit an analysis.

**Rate limiting** — the analyze endpoint is rate limited (10 req/min by default) to control Claude API costs.

**Structured logging** — every request logs method, path, status code, and latency for observability.

---

## Getting Started

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- Node.js 18+
- Anthropic API key ([get one here](https://console.anthropic.com))

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/smartapply
cd smartapply
```

Create your environment file:
```bash
cp .env.example .env
```

Open `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Start PostgreSQL

```bash
docker compose up
```

This starts PostgreSQL with pgvector and runs the schema automatically.

### 3. Start the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`
Auto-generated docs at `http://localhost:8000/docs`

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`

---

## Project Structure

```
smartapply/
├── docker-compose.yml
├── backend/
│   ├── init.sql                  ← DB schema
│   ├── requirements.txt
│   └── app/
│       ├── main.py               ← FastAPI app, CORS, request logging
│       ├── config/
│       │   ├── settings.py       ← Pydantic settings
│       │   └── database.py       ← async connection pool
│       ├── models/
│       │   └── schemas.py        ← Pydantic data contracts
│       ├── routes/
│       │   ├── resume.py         ← upload + fetch
│       │   ├── analyze.py        ← pipeline + rate limiting
│       │   └── history.py        ← list, fetch, review, delete
│       └── services/
│           ├── parser.py         ← PDF → sections
│           ├── embeddings.py     ← sentence-transformers
│           ├── similarity.py     ← pgvector cosine search
│           └── analyzer.py       ← Claude API integration
└── frontend/
    └── src/
        ├── api.js                ← centralized API client
        ├── App.jsx               ← main layout + state
        └── components/
            ├── ResumeUpload.jsx
            ├── JDInput.jsx
            ├── FitScore.jsx
            ├── GapAnalysis.jsx
            ├── SectionCard.jsx
            └── HistoryPanel.jsx
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/smartapply` | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | — | Required. Get from console.anthropic.com |
| `APP_ENV` | `development` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ANALYZE_RATE_LIMIT` | `10` | Max analyze requests per window |
| `ANALYZE_RATE_LIMIT_WINDOW` | `60` | Rate limit window in seconds |

---

## License

MIT
