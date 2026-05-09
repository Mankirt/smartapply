-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id          SERIAL PRIMARY KEY,
    filename    TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Resume sections — one row per section, each with its own embedding
CREATE TABLE IF NOT EXISTS resume_sections (
    id           SERIAL PRIMARY KEY,
    resume_id    INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    section_type TEXT NOT NULL,
    title        TEXT NOT NULL,
    content      TEXT NOT NULL,
    order_index  INTEGER NOT NULL,
    embedding    vector(384),
    created_at   TIMESTAMP DEFAULT NOW()
);

-- Index for fast cosine similarity search
CREATE INDEX IF NOT EXISTS resume_sections_embedding_idx
    ON resume_sections
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Analyses table
CREATE TABLE IF NOT EXISTS analyses (
    id               SERIAL PRIMARY KEY,
    resume_id        INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    jd_text          TEXT NOT NULL,
    fit_score        INTEGER CHECK (fit_score >= 0 AND fit_score <= 100),
    matching_skills  JSONB DEFAULT '[]',
    missing_keywords JSONB DEFAULT '[]',
    summary          TEXT,
    created_at       TIMESTAMP DEFAULT NOW()
);

-- Section reviews — Accept/Edit/Ignore decisions
CREATE TABLE IF NOT EXISTS section_reviews (
    id             SERIAL PRIMARY KEY,
    analysis_id    INTEGER REFERENCES analyses(id) ON DELETE CASCADE,
    section_type   TEXT NOT NULL,
    status         TEXT NOT NULL CHECK (status IN ('accepted', 'edited', 'ignored')),
    edited_content TEXT,
    created_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE (analysis_id, section_type)
);