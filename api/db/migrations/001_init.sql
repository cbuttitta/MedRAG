-- Step 1: Enable the pgvector extension
-- This adds the 'vector' data type and similarity search operators to PostgreSQL.
-- Must be run before creating any column with type vector().
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Main document storage table
-- Each row is one chunk of text from a medical source document.
CREATE TABLE IF NOT EXISTS documents (
    id          SERIAL PRIMARY KEY,
    source      TEXT NOT NULL,
    section     TEXT,
    content     TEXT NOT NULL,
    embedding   vector(1536),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Step 3: API request audit log
-- Stores a record of every call made to /api/recommend.
CREATE TABLE IF NOT EXISTS requests (
    id             SERIAL PRIMARY KEY,
    input_preview  TEXT,
    conditions     TEXT[],
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Step 4: Vector similarity index
-- IVFFlat is an approximate nearest-neighbor index.
-- Makes similarity searches fast even with thousands of document chunks.
-- 'lists' controls how many clusters the index creates.
-- Rule of thumb: set lists to sqrt(number_of_rows). Start with 10.
CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

