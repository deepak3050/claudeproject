-- ============================================================================
-- Working with Real OpenAI Embeddings - SQL-Only Workflow
-- ============================================================================
--
-- This file shows you TWO approaches:
--
-- METHOD 1 (RECOMMENDED): Generate embeddings DIRECTLY in SQL queries
--   - Uses PostgreSQL's http extension
--   - No terminal/curl commands needed!
--   - Generate embeddings with: openai_embed('your text')
--   - List models with: SELECT * FROM openai_list_models()
--   - API key stored securely in database
--   → Jump to SECTION A below
--
-- METHOD 2 (LEGACY): Generate embeddings using curl in terminal
--   - Requires terminal commands
--   - Manual copy-paste workflow
--   → Jump to SECTION B below
--
-- Prerequisites:
-- - OpenAI API key (get from: https://platform.openai.com/api-keys)
-- - PostgreSQL running: docker-compose up -d
-- - For Method 1: http extension (we'll install it)
-- - For Method 2: curl installed (already on macOS)
--
-- Model: text-embedding-3-small (cheapest & best)
-- Cost: $0.02 per 1 million tokens (~$0.00001 per document)
-- Dimensions: 1536
-- ============================================================================


-- ╔════════════════════════════════════════════════════════════════════════╗
-- ║  SECTION A: DIRECT SQL INTEGRATION (RECOMMENDED)                       ║
-- ║  Generate embeddings right from SQL queries!                           ║
-- ╚════════════════════════════════════════════════════════════════════════╝


-- ----------------------------------------------------------------------------
-- A1: Install http extension (enables HTTP requests from SQL)
-- ----------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS http;

-- Verify installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'http';
-- Expected: http | 1.x


-- ----------------------------------------------------------------------------
-- A2: Store your OpenAI API key in database
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS openai_config CASCADE;

CREATE TABLE openai_config (
    id SERIAL PRIMARY KEY,
    api_key TEXT NOT NULL,
    model TEXT DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert your API key here (replace with your actual key)
-- IMPORTANT: Keep this secure! Don't commit to git!
INSERT INTO openai_config (api_key) VALUES ('sk-your-api-key-here');

-- Verify (shows preview of your key)
SELECT id,
       substring(api_key, 1, 10) || '...' as api_key_preview,
       model
FROM openai_config;


-- ----------------------------------------------------------------------------
-- A3: List available OpenAI embedding models
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION openai_list_models()
RETURNS TABLE(model_id TEXT, created_date TEXT, owned_by TEXT) AS $$
DECLARE
    api_key TEXT;
    response TEXT;
BEGIN
    -- Set HTTP timeout to 10 seconds for API calls
    PERFORM set_config('http.timeout_msec', '10000', true);

    -- Get API key from config
    SELECT openai_config.api_key INTO api_key FROM openai_config LIMIT 1;

    IF api_key IS NULL THEN
        RAISE EXCEPTION 'API key not configured. Run: INSERT INTO openai_config (api_key) VALUES (''sk-...'')';
    END IF;

    -- Make HTTP request to OpenAI
    SELECT content::TEXT INTO response
    FROM http((
        'GET',
        'https://api.openai.com/v1/models',
        ARRAY[http_header('Authorization', 'Bearer ' || api_key)],
        NULL,
        NULL
    )::http_request);

    -- Return only embedding models
    RETURN QUERY
    SELECT
        (model->>'id')::TEXT as model_id,
        to_timestamp((model->>'created')::BIGINT)::TEXT as created_date,
        (model->>'owned_by')::TEXT as owned_by
    FROM json_array_elements((response::JSON)->'data') AS model
    WHERE (model->>'id')::TEXT LIKE '%embedding%'
    ORDER BY (model->>'id')::TEXT;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to list models: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Usage: List all embedding models from OpenAI
SELECT * FROM openai_list_models();

-- Expected output:
-- model_id                    | created_date              | owned_by
-- text-embedding-3-small      | 2024-01-25 ...           | system
-- text-embedding-3-large      | 2024-01-25 ...           | system
-- text-embedding-ada-002      | 2022-12-16 ...           | openai-internal


-- ----------------------------------------------------------------------------
-- A4: Create function to generate embeddings directly from SQL
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION openai_embed(input_text TEXT)
RETURNS vector(1536) AS $$
DECLARE
    api_key TEXT;
    model TEXT;
    response TEXT;
    embedding_array TEXT;
    http_status INTEGER;
BEGIN
    -- Set HTTP timeout to 10 seconds for API calls (transaction-scoped)
    PERFORM set_config('http.timeout_msec', '10000', true);

    -- Get API configuration
    SELECT openai_config.api_key, openai_config.model
    INTO api_key, model
    FROM openai_config
    LIMIT 1;

    IF api_key IS NULL THEN
        RAISE EXCEPTION 'API key not configured. Run: INSERT INTO openai_config (api_key) VALUES (''sk-...'')';
    END IF;

    -- Make HTTP request to OpenAI embeddings API
    SELECT status, content::TEXT
    INTO http_status, response
    FROM http((
        'POST',
        'https://api.openai.com/v1/embeddings',
        ARRAY[
            http_header('Authorization', 'Bearer ' || api_key),
            http_header('Content-Type', 'application/json')
        ],
        'application/json',
        json_build_object(
            'input', input_text,
            'model', model
        )::TEXT
    )::http_request);

    -- Check for errors
    IF http_status != 200 THEN
        RAISE EXCEPTION 'OpenAI API error (status %): %', http_status, response;
    END IF;

    -- Extract embedding from response
    embedding_array := (response::JSON)->'data'->0->>'embedding';

    -- Return as vector
    RETURN embedding_array::vector(1536);

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to generate embedding: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Test: Generate a single embedding
SELECT openai_embed('Python is a programming language');
-- Returns: vector with 1536 dimensions


-- ----------------------------------------------------------------------------
-- A5: Create table with auto-embedding trigger
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS smart_docs CASCADE;

CREATE TABLE smart_docs (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Auto-generate embeddings on INSERT
CREATE OR REPLACE FUNCTION auto_generate_embedding()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.embedding IS NULL THEN
        NEW.embedding := openai_embed(NEW.content);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS smart_docs_auto_embed ON smart_docs;

CREATE TRIGGER smart_docs_auto_embed
    BEFORE INSERT OR UPDATE ON smart_docs
    FOR EACH ROW
    EXECUTE FUNCTION auto_generate_embedding();

-- Create index for fast searches
CREATE INDEX smart_docs_embedding_idx
ON smart_docs
USING hnsw (embedding vector_cosine_ops);


-- ----------------------------------------------------------------------------
-- A6: Insert documents - embeddings generated automatically!
-- ----------------------------------------------------------------------------

-- Just insert content - embedding is auto-generated!
INSERT INTO smart_docs (content) VALUES
    ('Python is a versatile programming language'),
    ('JavaScript runs in web browsers'),
    ('PostgreSQL is a powerful relational database'),
    ('Docker provides containerization for applications'),
    ('React is a JavaScript library for building user interfaces');

-- Verify
SELECT id, content,
       CASE
           WHEN embedding IS NO∂T NULL THEN '✓ Generated (' || vector_dims(embedding) || 'D)'
           ELSE '✗ Missing'
       END as embedding_status
FROM smart_docs;


-- ----------------------------------------------------------------------------
-- A7: Semantic search - embeddings generated on the fly!
-- ----------------------------------------------------------------------------

-- Search for documents similar to a query
SELECT
    id,
    content,
    embedding <=> openai_embed('programming languages') AS similarity_score
FROM smart_docs
ORDER BY similarity_score
LIMIT 5;

-- Find documents about databases
SELECT
    content,
    1 - (embedding <=> openai_embed('databases')) AS similarity_percentage
FROM smart_docs
ORDER BY similarity_percentage DESC
LIMIT 3;

-- Combined filtering and semantic search
SELECT
    content,
    embedding <=> openai_embed('web development') AS score
FROM smart_docs
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY score
LIMIT 5;


-- ----------------------------------------------------------------------------
-- A8: Update API key or model
-- ----------------------------------------------------------------------------

-- Update API key
UPDATE openai_config
SET api_key = 'sk-new-api-key-here'
WHERE id = 1;

-- Switch to larger model (more accurate, more expensive)
UPDATE openai_config
SET model = 'text-embedding-3-large'
WHERE id = 1;
-- Note: text-embedding-3-large uses 3072 dimensions!
-- You'll need to recreate tables with vector(3072)


-- ----------------------------------------------------------------------------
-- A9: Cost tracking and monitoring
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS embedding_usage CASCADE;

CREATE TABLE embedding_usage (
    id SERIAL PRIMARY KEY,
    text_length INTEGER,
    model TEXT,
    tokens_estimated INTEGER,
    cost_usd NUMERIC(10, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced function with usage tracking
CREATE OR REPLACE FUNCTION tracked_openai_embed(input_text TEXT)
RETURNS vector(1536) AS $$
DECLARE
    result vector(1536);
    text_len INTEGER;
    estimated_tokens INTEGER;
    estimated_cost NUMERIC(10, 8);
BEGIN
    -- Generate embedding (may fail with timeout or API errors)
    result := openai_embed(input_text);

    -- Track usage (only if embedding succeeded)
    text_len := length(input_text);
    estimated_tokens := text_len / 4;
    estimated_cost := (estimated_tokens::NUMERIC / 1000000.0) * 0.02;

    -- Use autonomous transaction for usage tracking (don't fail if this fails)
    BEGIN
        INSERT INTO embedding_usage (text_length, model, tokens_estimated, cost_usd)
        VALUES (text_len, 'text-embedding-3-small', estimated_tokens, estimated_cost);
    EXCEPTION
        WHEN OTHERS THEN
            -- Log error but don't fail the embedding generation
            RAISE WARNING 'Failed to track usage: %', SQLERRM;
    END;

    RETURN result;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to generate tracked embedding: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- View usage statistics
SELECT
    COUNT(*) as total_requests,
    SUM(tokens_estimated) as total_tokens,
    SUM(cost_usd) as total_cost_usd,
    AVG(text_length) as avg_text_length
FROM embedding_usage;


-- ============================================================================
-- QUICK REFERENCE: Method 1 (In-Database)
-- ============================================================================
--
-- Setup (one time):
--   1. CREATE EXTENSION http;
--   2. INSERT INTO openai_config (api_key) VALUES ('sk-...');
--
-- List models:
--   SELECT * FROM openai_list_models();
--
-- Insert with auto-embedding:
--   INSERT INTO smart_docs (content) VALUES ('your text');
--
-- Search:
--   SELECT content FROM smart_docs
--   ORDER BY embedding <=> openai_embed('search query')
--   LIMIT 10;
--
-- Update API key:
--   UPDATE openai_config SET api_key = 'sk-new-key' WHERE id = 1;
--
-- ============================================================================


-- ╔════════════════════════════════════════════════════════════════════════╗
-- ║  SECTION B: LEGACY METHOD (Terminal + curl)                           ║
-- ║  For reference or if http extension is not available                  ║
-- ╚════════════════════════════════════════════════════════════════════════╝

-- ----------------------------------------------------------------------------
-- STEP 1: Set your OpenAI API key
-- ----------------------------------------------------------------------------
--
-- In your terminal (macOS/Linux):
--
-- Temporary (current session only):
--   export OPENAI_API_KEY='sk-your-key-here'
--
-- Permanent (all sessions):
--   echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
--   source ~/.zshrc
--
-- Verify:
--   echo $OPENAI_API_KEY


-- ----------------------------------------------------------------------------
-- STEP 2: Create table for real embeddings
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS real_docs CASCADE;

CREATE TABLE real_docs (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),  -- text-embedding-3-small has 1536 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verify table
\d real_docs


-- ----------------------------------------------------------------------------
-- STEP 3: Generate an embedding using curl
-- ----------------------------------------------------------------------------
--
-- Copy this command to your terminal (replace 'sk-...' with your API key):
--
-- curl https://api.openai.com/v1/embeddings \
--   -H "Authorization: Bearer $OPENAI_API_KEY" \
--   -H "Content-Type: application/json" \
--   -d '{
--     "input": "Python is a high-level programming language",
--     "model": "text-embedding-3-small"
--   }' | jq -r '.data[0].embedding'
--
-- This will output something like:
-- [0.0123,-0.456,0.789, ... ,0.234]  (1536 numbers)
--
-- COPY THE OUTPUT (the entire array with brackets)


-- ----------------------------------------------------------------------------
-- STEP 4: Insert the embedding into PostgreSQL
-- ----------------------------------------------------------------------------
--
-- Method 1: Direct insert with embedding
--
-- Replace [...] with the actual embedding vector from curl output:

INSERT INTO real_docs (content, embedding) VALUES
    ('Python is a high-level programming language',
     '[0.0123,-0.456,0.789, ... ,0.234]'::vector);

-- For now, let's use a sample embedding (you'll replace this with real ones)
-- These are FAKE embeddings just for demonstration:

TRUNCATE real_docs;  -- Clear table

INSERT INTO real_docs (content, embedding) VALUES
    ('Python programming language',
     -- Generate this with curl command above!
     -- This is a PLACEHOLDER - replace with real embedding
     '[ ... paste embedding here ... ]'::vector
    );


-- ----------------------------------------------------------------------------
-- STEP 5: Quick Guide - How to get multiple embeddings
-- ----------------------------------------------------------------------------
--
-- Save this as get_embedding.sh and run it:
--
-- #!/bin/bash
-- curl https://api.openai.com/v1/embeddings \
--   -H "Authorization: Bearer $OPENAI_API_KEY" \
--   -H "Content-Type: application/json" \
--   -d "{
--     \"input\": \"$1\",
--     \"model\": \"text-embedding-3-small\"
--   }" | jq -r '.data[0].embedding'
--
-- Usage:
--   chmod +x get_embedding.sh
--   ./get_embedding.sh "Python is awesome"
--
-- Then copy the output and insert into SQL


-- ----------------------------------------------------------------------------
-- STEP 6: Example - Complete workflow for one document
-- ----------------------------------------------------------------------------
--
-- 1. In terminal, get embedding:
--
-- $ curl https://api.openai.com/v1/embeddings \
--   -H "Authorization: Bearer $OPENAI_API_KEY" \
--   -H "Content-Type: application/json" \
--   -d '{
--     "input": "Machine learning is a subset of AI",
--     "model": "text-embedding-3-small"
--   }' | jq -r '.data[0].embedding'
--
-- Output: [0.234, -0.567, 0.891, ... ]
--
-- 2. Copy the output
--
-- 3. Insert in SQL:
--
-- INSERT INTO real_docs (content, embedding) VALUES
--     ('Machine learning is a subset of AI',
--      '[0.234, -0.567, 0.891, ...]'::vector);


-- ----------------------------------------------------------------------------
-- STEP 7: Batch insert multiple documents (recommended)
-- ----------------------------------------------------------------------------
--
-- Instead of one-by-one, generate all embeddings first, then bulk insert.
--
-- 1. Create file: documents.txt
--    Python is a programming language
--    JavaScript runs in browsers
--    PostgreSQL is a database
--    Docker provides containers
--
-- 2. Generate embeddings for all (save as generate_all.sh):
--
-- #!/bin/bash
-- while IFS= read -r line; do
--   echo "Processing: $line"
--   embedding=$(curl -s https://api.openai.com/v1/embeddings \
--     -H "Authorization: Bearer $OPENAI_API_KEY" \
--     -H "Content-Type: application/json" \
--     -d "{\"input\": \"$line\", \"model\": \"text-embedding-3-small\"}" \
--     | jq -r '.data[0].embedding')
--   echo "('$line', '$embedding'::vector),"
-- done < documents.txt
--
-- 3. Run:
--    chmod +x generate_all.sh
--    ./generate_all.sh > inserts.sql
--
-- 4. Edit inserts.sql to add INSERT statement:
--    INSERT INTO real_docs (content, embedding) VALUES
--    <paste generated lines here, remove last comma>
--    ;


-- ----------------------------------------------------------------------------
-- STEP 8: Pre-populated example (for testing)
-- ----------------------------------------------------------------------------
--
-- Since you might not have curl/API set up yet, here's how to test
-- with simulated data that LOOKS like real embeddings:
--
-- WARNING: These are RANDOM vectors, not real embeddings!
-- They won't give good semantic search results.

TRUNCATE real_docs;

-- Simulated "real-looking" embeddings (384D for easier copy-paste)
-- In production, you'd use actual OpenAI embeddings (1536D)

-- First, let's create a test table with smaller dimensions
DROP TABLE IF EXISTS test_real_docs;

CREATE TABLE test_real_docs (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384)  -- Smaller for testing (real would be 1536)
);

-- Insert some test data with random embeddings (NOT production!)
-- Just for exploring SQL queries

INSERT INTO test_real_docs (content, embedding) VALUES
    ('Python programming language',
     -- Random vector - replace with real OpenAI embeddings!
     ('[' || array_to_string(ARRAY(SELECT random()::text FROM generate_series(1, 384)), ',') || ']')::vector
    );

-- Check if it worked
SELECT id, content, vector_dims(embedding) FROM test_real_docs;


-- ----------------------------------------------------------------------------
-- STEP 9: Semantic Search Queries (once you have real embeddings)
-- ----------------------------------------------------------------------------
--
-- After inserting real embeddings, use these queries:

-- Find similar documents to a query
-- (You need to generate query embedding first with curl)

SELECT
    content,
    embedding <=> '[... query embedding ...]'::vector AS distance
FROM real_docs
ORDER BY distance
LIMIT 5;


-- Find documents within a distance threshold

SELECT
    content,
    embedding <=> '[... query embedding ...]'::vector AS distance
FROM real_docs
WHERE embedding <=> '[... query embedding ...]'::vector < 0.3
ORDER BY distance;


-- Compare multiple queries side by side

SELECT
    content,
    embedding <=> '[... query1 ...]'::vector AS python_score,
    embedding <=> '[... query2 ...]'::vector AS js_score,
    embedding <=> '[... query3 ...]'::vector AS ai_score
FROM real_docs;


-- ----------------------------------------------------------------------------
-- STEP 10: Create index for performance
-- ----------------------------------------------------------------------------

-- IMPORTANT: Create index AFTER inserting all data

CREATE INDEX real_docs_embedding_hnsw_idx
ON real_docs
USING hnsw (embedding vector_cosine_ops);

-- Check index was created
\di

-- Test query performance
EXPLAIN ANALYZE
SELECT content, embedding <=> '[...]'::vector AS distance
FROM real_docs
ORDER BY distance
LIMIT 10;


-- ----------------------------------------------------------------------------
-- STEP 11: Complete Example Workflow
-- ----------------------------------------------------------------------------
--
-- Here's the complete workflow:
--
-- === TERMINAL (generate embeddings) ===
--
-- # Set API key
-- export OPENAI_API_KEY='sk-your-key-here'
--
-- # Get embedding for document 1
-- curl https://api.openai.com/v1/embeddings \
--   -H "Authorization: Bearer $OPENAI_API_KEY" \
--   -H "Content-Type: application/json" \
--   -d '{
--     "input": "Python is awesome",
--     "model": "text-embedding-3-small"
--   }' | jq -r '.data[0].embedding' > embed1.txt
--
-- # Get embedding for document 2
-- curl https://api.openai.com/v1/embeddings \
--   -H "Authorization: Bearer $OPENAI_API_KEY" \
--   -H "Content-Type: application/json" \
--   -d '{
--     "input": "JavaScript is great",
--     "model": "text-embedding-3-small"
--   }' | jq -r '.data[0].embedding' > embed2.txt
--
-- # Get embedding for query
-- curl https://api.openai.com/v1/embeddings \
--   -H "Authorization: Bearer $OPENAI_API_KEY" \
--   -H "Content-Type: application/json" \
--   -d '{
--     "input": "programming languages",
--     "model": "text-embedding-3-small"
--   }' | jq -r '.data[0].embedding' > query_embed.txt
--
-- === SQL (insert and query) ===
--
-- Insert documents:

-- INSERT INTO real_docs (content, embedding) VALUES
--     ('Python is awesome', (SELECT content FROM embed1.txt)::vector),
--     ('JavaScript is great', (SELECT content FROM embed2.txt)::vector);

-- Search:

-- SELECT content, embedding <=> (SELECT content FROM query_embed.txt)::vector AS score
-- FROM real_docs
-- ORDER BY score;


-- ----------------------------------------------------------------------------
-- STEP 12: Helper script (optional)
-- ----------------------------------------------------------------------------
--
-- Create a file: embed.sh
--
-- #!/bin/bash
-- # Usage: ./embed.sh "your text here"
--
-- if [ -z "$OPENAI_API_KEY" ]; then
--     echo "Error: OPENAI_API_KEY not set!"
--     echo "Run: export OPENAI_API_KEY='sk-...'"
--     exit 1
-- fi
--
-- TEXT="$1"
--
-- if [ -z "$TEXT" ]; then
--     echo "Usage: $0 \"text to embed\""
--     exit 1
-- fi
--
-- echo "Generating embedding for: $TEXT"
--
-- EMBEDDING=$(curl -s https://api.openai.com/v1/embeddings \
--   -H "Authorization: Bearer $OPENAI_API_KEY" \
--   -H "Content-Type: application/json" \
--   -d "{
--     \"input\": \"$TEXT\",
--     \"model\": \"text-embedding-3-small\"
--   }" | jq -r '.data[0].embedding')
--
-- if [ -z "$EMBEDDING" ]; then
--     echo "Error: Failed to generate embedding"
--     exit 1
-- fi
--
-- echo "Embedding (copy this):"
-- echo "'$EMBEDDING'::vector"
--
-- Usage:
--   chmod +x embed.sh
--   ./embed.sh "Python programming"
--
-- Output:
--   '[0.123, -0.456, ...]'::vector
--
-- Then paste directly into SQL:
--   INSERT INTO real_docs (content, embedding)
--   VALUES ('Python programming', '[0.123, -0.456, ...]'::vector);


-- ============================================================================
-- SUMMARY: SQL-Only Workflow
-- ============================================================================
--
-- 1. Generate embedding in terminal:
--    $ ./embed.sh "your text"
--    Output: '[0.123, -0.456, ...]'::vector
--
-- 2. Insert in DBeaver/psql:
--    INSERT INTO real_docs (content, embedding)
--    VALUES ('your text', '[...]'::vector);
--
-- 3. Query in DBeaver/psql:
--    SELECT content FROM real_docs
--    ORDER BY embedding <=> '[query embedding]'::vector
--    LIMIT 5;
--
-- 4. Repeat for all documents!
--
-- ============================================================================
-- TIPS:
-- ============================================================================
--
-- 1. Use jq for JSON parsing (install: brew install jq)
-- 2. Generate all embeddings first, then bulk INSERT
-- 3. Create index AFTER inserting all data (faster)
-- 4. Test with small datasets first
-- 5. Monitor costs at: https://platform.openai.com/usage
--
-- ============================================================================
-- COST ESTIMATION:
-- ============================================================================
--
-- text-embedding-3-small pricing: $0.02 per 1M tokens
--
-- Examples:
-- - 100 documents (100 words each):  ~$0.0002  (< 1 cent)
-- - 1,000 documents:                 ~$0.002   (< 1 cent)
-- - 10,000 documents:                ~$0.02    (2 cents)
-- - 100,000 documents:               ~$0.20    (20 cents)
--
-- Queries are FREE (once embeddings are generated)!
--
-- ============================================================================
