-- ============================================================================
-- PostgreSQL Vector Database - Interactive Queries
-- ============================================================================
-- Use these queries in DBeaver or psql to explore vector operations
--
-- To run in psql:
--   docker exec -it pgvector-db psql -U postgres -d vectors_db
--   Then copy-paste queries from this file
--
-- To run in DBeaver:
--   Connect to localhost:5432, database: vectors_db
--   Open this file in SQL Editor and run queries
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. BASIC EXPLORATION
-- ----------------------------------------------------------------------------

-- View all tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

-- See current data in items table
SELECT id, name, embedding, category
FROM items
ORDER BY id;

-- See documents table
SELECT id, title,
       vector_dims(embedding) as dimension,
       created_at
FROM documents;

-- Count items per category
SELECT
    category,
    COUNT(*) as count
FROM items
WHERE category IS NOT NULL
GROUP BY category
ORDER BY count DESC;

-- ----------------------------------------------------------------------------
-- 2. SIMILARITY SEARCH - COSINE DISTANCE (Best for semantic search)
-- ----------------------------------------------------------------------------

-- Find items similar to "Python Programming"
-- Vector [1,0,0] represents "Python-like" content
SELECT
    name,
    category,
    embedding <=> '[1,0,0]'::vector AS similarity_score
FROM items
ORDER BY similarity_score
LIMIT 5;

-- Find items similar to "JavaScript"
-- Vector [0,1,0] represents "JavaScript-like" content
SELECT
    name,
    category,
    embedding <=> '[0,1,0]'::vector AS similarity_score
FROM items
ORDER BY similarity_score
LIMIT 5;

-- Find items similar to "AI/Machine Learning"
-- Vector [0,0,1] represents "AI-like" content
SELECT
    name,
    category,
    embedding <=> '[0,0,1]'::vector AS similarity_score
FROM items
ORDER BY similarity_score
LIMIT 5;

-- Find items similar to "Full-stack" (Python + JavaScript)
-- Vector [0.5,0.5,0] represents both Python and JavaScript
SELECT
    name,
    category,
    embedding <=> '[0.5,0.5,0]'::vector AS similarity_score
FROM items
ORDER BY similarity_score
LIMIT 5;

-- ----------------------------------------------------------------------------
-- 3. SIMILARITY SEARCH - L2 DISTANCE (Euclidean distance)
-- ----------------------------------------------------------------------------

-- Same query as above but using L2 distance
SELECT
    name,
    category,
    embedding <-> '[1,0,0]'::vector AS l2_distance
FROM items
ORDER BY l2_distance
LIMIT 5;

-- ----------------------------------------------------------------------------
-- 4. SIMILARITY SEARCH - INNER PRODUCT
-- ----------------------------------------------------------------------------

-- Using inner product (negative for descending order)
SELECT
    name,
    category,
    (embedding <#> '[1,0,0]'::vector) * -1 AS similarity
FROM items
ORDER BY embedding <#> '[1,0,0]'::vector
LIMIT 5;

-- ----------------------------------------------------------------------------
-- 5. FILTERED SIMILARITY SEARCH
-- ----------------------------------------------------------------------------

-- Find similar items ONLY in 'programming' category
SELECT
    name,
    category,
    embedding <=> '[1,0,0]'::vector AS score
FROM items
WHERE category = 'programming'
ORDER BY score
LIMIT 5;

-- Find similar items ONLY in 'ai' category
SELECT
    name,
    category,
    embedding <=> '[0,0,1]'::vector AS score
FROM items
WHERE category = 'ai'
ORDER BY score
LIMIT 3;

-- Find items within distance threshold (< 0.5)
SELECT
    name,
    category,
    embedding <=> '[1,0,0]'::vector AS distance
FROM items
WHERE embedding <=> '[1,0,0]'::vector < 0.5
ORDER BY distance;

-- ----------------------------------------------------------------------------
-- 6. COMPARE SIMILARITIES ACROSS MULTIPLE TOPICS
-- ----------------------------------------------------------------------------

-- Show how each item relates to Python, JavaScript, and AI
SELECT
    name,
    category,
    ROUND((embedding <=> '[1,0,0]'::vector)::numeric, 4) AS python_score,
    ROUND((embedding <=> '[0,1,0]'::vector)::numeric, 4) AS js_score,
    ROUND((embedding <=> '[0,0,1]'::vector)::numeric, 4) AS ai_score
FROM items
ORDER BY id;

-- Find the "best match" for each item
SELECT
    name,
    category,
    CASE
        WHEN embedding <=> '[1,0,0]'::vector < embedding <=> '[0,1,0]'::vector
         AND embedding <=> '[1,0,0]'::vector < embedding <=> '[0,0,1]'::vector
        THEN 'Python'
        WHEN embedding <=> '[0,1,0]'::vector < embedding <=> '[0,0,1]'::vector
        THEN 'JavaScript'
        ELSE 'AI/ML'
    END AS best_match
FROM items;

-- ----------------------------------------------------------------------------
-- 7. ADVANCED SEMANTIC SEARCH WITH RELEVANCE LABELS
-- ----------------------------------------------------------------------------

-- Search with human-readable relevance labels
SELECT
    name,
    category,
    ROUND((embedding <=> '[1,0,0]'::vector)::numeric, 4) AS score,
    CASE
        WHEN embedding <=> '[1,0,0]'::vector < 0.01 THEN '🔥 Exact match'
        WHEN embedding <=> '[1,0,0]'::vector < 0.3 THEN '✅ Very similar'
        WHEN embedding <=> '[1,0,0]'::vector < 0.6 THEN '⚠️  Somewhat similar'
        ELSE '❌ Not similar'
    END AS relevance
FROM items
ORDER BY score;

-- ----------------------------------------------------------------------------
-- 8. DISTANCE BETWEEN TWO SPECIFIC ITEMS
-- ----------------------------------------------------------------------------

-- Calculate distances between "Python Programming" and "JavaScript Basics"
SELECT
    a.name AS item1,
    b.name AS item2,
    ROUND((a.embedding <=> b.embedding)::numeric, 4) AS cosine_distance,
    ROUND((a.embedding <-> b.embedding)::numeric, 4) AS l2_distance,
    ROUND(((a.embedding <#> b.embedding) * -1)::numeric, 4) AS inner_product
FROM items a, items b
WHERE a.name = 'Python Programming'
  AND b.name = 'JavaScript Basics';

-- Compare "Python Programming" with all other items
SELECT
    a.name AS reference,
    b.name AS compared_to,
    ROUND((a.embedding <=> b.embedding)::numeric, 4) AS distance
FROM items a
CROSS JOIN items b
WHERE a.name = 'Python Programming'
  AND a.id != b.id
ORDER BY distance;

-- ----------------------------------------------------------------------------
-- 9. VECTOR MATH OPERATIONS
-- ----------------------------------------------------------------------------

-- Vector addition
SELECT '[1,2,3]'::vector + '[4,5,6]'::vector AS addition_result;

-- Vector subtraction
SELECT '[5,6,7]'::vector - '[1,2,3]'::vector AS subtraction_result;

-- Get vector dimensions
SELECT vector_dims('[1,2,3,4,5]'::vector) AS dimensions;

-- Get vector magnitude (L2 norm)
SELECT vector_norm('[3,4]'::vector) AS magnitude;
-- Result should be 5.0 because sqrt(3² + 4²) = 5

-- Calculate distance between two vectors directly
SELECT
    '[1,0,0]'::vector <=> '[0,1,0]'::vector AS cosine_distance,
    '[1,0,0]'::vector <-> '[0,1,0]'::vector AS l2_distance;

-- ----------------------------------------------------------------------------
-- 10. AGGREGATE STATISTICS
-- ----------------------------------------------------------------------------

-- Count items per category with average vector magnitude
SELECT
    category,
    COUNT(*) as item_count,
    ROUND(AVG(vector_norm(embedding))::numeric, 4) as avg_magnitude
FROM items
WHERE category IS NOT NULL
GROUP BY category
ORDER BY item_count DESC;

-- Find the most "extreme" vectors (highest magnitude)
SELECT
    name,
    category,
    ROUND(vector_norm(embedding)::numeric, 4) as magnitude
FROM items
ORDER BY magnitude DESC
LIMIT 5;

-- ----------------------------------------------------------------------------
-- 11. INDEX INFORMATION
-- ----------------------------------------------------------------------------

-- View all indexes on vector columns
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexdef LIKE '%vector%'
ORDER BY tablename, indexname;

-- Check if indexes exist
SELECT
    indexname,
    tablename
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('items', 'documents');

-- ----------------------------------------------------------------------------
-- 12. RE-INSERT SAMPLE DATA
-- ----------------------------------------------------------------------------

-- Option A: Re-insert fruits (if you want to explore with fruit data)
DELETE FROM items;

INSERT INTO items (name, embedding) VALUES
    ('apple', '[1,0,0]'),
    ('strawberry', '[0.9,0.1,0]'),
    ('banana', '[0,1,0]'),
    ('lemon', '[0.1,0.9,0]'),
    ('blueberry', '[0,0,1]'),
    ('grape', '[0.5,0,0.5]');

-- Verify fruits are inserted
SELECT name, embedding FROM items;

-- Now try similarity search: "Find red fruits"
SELECT
    name,
    embedding <=> '[1,0,0]'::vector AS similarity_to_red
FROM items
ORDER BY similarity_to_red
LIMIT 3;

-- ----------------------------------------------------------------------------

-- Option B: Re-insert programming topics (default state after tutorial)
DELETE FROM items;

INSERT INTO items (name, embedding, category) VALUES
    ('Python Programming', '[1,0,0]', 'programming'),
    ('Python Web Development', '[0.9,0.1,0]', 'programming'),
    ('JavaScript Basics', '[0,1,0]', 'programming'),
    ('React Tutorial', '[0,0.9,0.1]', 'frontend'),
    ('Machine Learning', '[0,0,1]', 'ai'),
    ('Deep Learning', '[0.1,0,0.9]', 'ai');

-- Verify programming topics are inserted
SELECT name, embedding, category FROM items;

-- Now try semantic search: "Find Python resources"
SELECT
    name,
    category,
    embedding <=> '[1,0,0]'::vector AS relevance
FROM items
ORDER BY relevance
LIMIT 3;

-- ----------------------------------------------------------------------------
-- 13. PRACTICAL EXPERIMENTS
-- ----------------------------------------------------------------------------

-- Experiment 1: Find items that are similar to MULTIPLE topics
-- (e.g., both Python AND AI)
SELECT
    name,
    category,
    -- Average similarity to both Python and AI
    ROUND(((embedding <=> '[1,0,0]'::vector + embedding <=> '[0,0,1]'::vector) / 2)::numeric, 4) AS combined_score
FROM items
ORDER BY combined_score
LIMIT 5;

-- Experiment 2: Find items that are DIFFERENT from a topic
-- (highest cosine distance = most different)
SELECT
    name,
    category,
    embedding <=> '[1,0,0]'::vector AS distance_from_python
FROM items
ORDER BY distance_from_python DESC
LIMIT 3;

-- Experiment 3: Compare ALL pairwise distances
-- (See how similar/different each item is to every other item)
SELECT
    a.name AS item_a,
    b.name AS item_b,
    ROUND((a.embedding <=> b.embedding)::numeric, 4) AS similarity
FROM items a
CROSS JOIN items b
WHERE a.id < b.id  -- Avoid duplicates (a,b) and (b,a)
ORDER BY similarity;

-- ----------------------------------------------------------------------------
-- 14. UNDERSTANDING DISTANCE METRICS
-- ----------------------------------------------------------------------------

-- Compare all three distance metrics side-by-side
SELECT
    name,
    ROUND((embedding <=> '[1,0,0]'::vector)::numeric, 4) AS cosine,
    ROUND((embedding <-> '[1,0,0]'::vector)::numeric, 4) AS l2,
    ROUND(((embedding <#> '[1,0,0]'::vector) * -1)::numeric, 4) AS inner_product
FROM items
ORDER BY cosine;

-- Key insights:
-- - Cosine: 0 = identical direction, 2 = opposite direction
-- - L2: 0 = same point, larger = further apart
-- - Inner product: 1 = same direction (if normalized), 0 = perpendicular

-- ============================================================================
-- UNDERSTANDING EMBEDDINGS: Simulated vs Real
-- ============================================================================
--
-- WHAT ARE EMBEDDINGS?
-- Embeddings are numerical representations of text/images/data that capture
-- semantic meaning. Similar items have similar vectors.
--
-- SIMULATED EMBEDDINGS (what this tutorial uses):
-- - Example: [1.0, 0.0, 0.0] represents "Python-related"
-- - Manually crafted, each dimension = a concept
-- - Easy to understand but NOT how real systems work
-- - Good for learning vector operations
--
-- REAL EMBEDDINGS (production usage):
-- - Example: [0.234, -0.567, 0.891, ..., 0.123] (384-1536 dimensions)
-- - Generated by neural networks (OpenAI, sentence-transformers, BERT, etc.)
-- - Each dimension is learned from data, not manually assigned
-- - Captures semantic meaning automatically
-- - Similar text → similar vectors (even if you didn't train it!)
--
-- HOW REAL EMBEDDINGS WORK:
--
-- 1. Text Input:
--    "Python is a programming language"
--
-- 2. ML Model (e.g., sentence-transformers):
--    Processes text through neural network
--
-- 3. Output Vector:
--    [0.123, -0.456, 0.789, ..., 0.234]  (384 dimensions)
--
-- 4. Storage:
--    INSERT INTO documents (content, embedding) VALUES (..., vector)
--
-- 5. Search:
--    Query: "coding languages"
--    → Generate embedding → Find similar vectors in database
--
-- POPULAR EMBEDDING MODELS:
--
-- Model                      Dimensions  Cost        Quality    Use Case
-- ────────────────────────────────────────────────────────────────────────
-- text-embedding-3-small     1536        $0.02/1M    Excellent  Production
-- text-embedding-3-large     3072        $0.13/1M    Best       High quality
-- all-MiniLM-L6-v2          384         Free        Good       Learning/Dev
-- all-mpnet-base-v2         768         Free        Very Good  Local prod
--
-- ============================================================================
-- HOW TO GET REAL EMBEDDINGS
-- ============================================================================
--
-- OPTION 1: External API (OpenAI, Cohere, etc.)
-- ────────────────────────────────────────────────────────────────────────
-- 1. Call API from your application
-- 2. Get embedding vector
-- 3. Insert into PostgreSQL
--
-- Example flow:
--   Your App → OpenAI API → Get [0.123, ...] → INSERT INTO vectors_db
--
-- Pros: Best quality, handles any text
-- Cons: Costs money, requires internet
--
--
-- OPTION 2: Local Model in Docker Container
-- ────────────────────────────────────────────────────────────────────────
-- 1. Run embedding model in Docker container
-- 2. Your app calls the container's HTTP API
-- 3. Insert embeddings into PostgreSQL
--
-- Setup (see docker-compose.yml for embedding service):
--   docker-compose up -d embedding-service
--
-- Pros: Free, private, fast
-- Cons: Requires GPU for best performance, lower quality than OpenAI
--
--
-- OPTION 3: PostgreSQL Extension (pl/python)
-- ────────────────────────────────────────────────────────────────────────
-- Call Python embedding models directly from SQL (advanced)
--
-- CREATE FUNCTION get_embedding(text) RETURNS vector AS $$
--   # Python code to generate embedding
-- $$ LANGUAGE plpython3u;
--
-- Pros: Everything in database
-- Cons: Complex setup, not recommended for production
--
-- ============================================================================
-- DISTANCE METRICS EXPLAINED
-- ============================================================================
--
-- PostgreSQL pgvector supports 3 distance metrics:
--
-- 1. COSINE DISTANCE (<=>)
-- ────────────────────────────────────────────────────────────────────────
-- Measures angular similarity (direction, not magnitude)
--
-- Formula: 1 - (A · B) / (||A|| × ||B||)
--
-- Range: 0 to 2
--   0.0   = Identical direction (perfect match)
--   1.0   = Perpendicular (orthogonal, unrelated)
--   2.0   = Opposite direction (antonyms)
--
-- Use when: Text/semantic search (most common)
-- Why: Handles vectors of different magnitudes well
--
-- Example:
--   SELECT content FROM docs ORDER BY embedding <=> '[...]'::vector LIMIT 10;
--
--
-- 2. EUCLIDEAN DISTANCE (L2) (<->)
-- ────────────────────────────────────────────────────────────────────────
-- Measures geometric distance (straight-line distance in N-dimensional space)
--
-- Formula: sqrt(Σ(A[i] - B[i])²)
--
-- Range: 0 to ∞
--   0.0   = Identical vectors
--   Larger = Further apart
--
-- Use when: Vectors are normalized, or magnitude matters
-- Why: Intuitive geometric interpretation
--
-- Example:
--   SELECT content FROM docs ORDER BY embedding <-> '[...]'::vector LIMIT 10;
--
--
-- 3. INNER PRODUCT (<#>)
-- ────────────────────────────────────────────────────────────────────────
-- Measures dot product similarity
--
-- Formula: Σ(A[i] × B[i])
--
-- Range: -∞ to ∞
--   Higher = More similar
--   Note: pgvector returns NEGATIVE inner product, so use ORDER BY
--
-- Use when: Vectors are normalized (length = 1)
-- Why: Faster than cosine, equivalent for normalized vectors
--
-- Example:
--   SELECT content FROM docs ORDER BY embedding <#> '[...]'::vector LIMIT 10;
--
--
-- WHICH TO USE?
-- ────────────────────────────────────────────────────────────────────────
-- For semantic/text search:     Use COSINE (<=>)     ← Most common
-- For image search:              Use COSINE or L2
-- For normalized vectors:        Use INNER PRODUCT (fastest)
-- For geometric similarity:      Use L2
--
-- ============================================================================
-- REAL-WORLD EXAMPLE: Semantic Search Flow
-- ============================================================================
--
-- Scenario: User searches "how to learn Python programming"
--
-- Step 1: Generate embedding for user query
-- ────────────────────────────────────────────────────────────────────────
-- (Done in your application, e.g., call OpenAI API or local model)
--
-- query = "how to learn Python programming"
-- query_embedding = call_embedding_api(query)
-- → [0.234, -0.567, 0.891, ..., 0.123]  (1536 dimensions)
--
--
-- Step 2: Search database for similar documents
-- ────────────────────────────────────────────────────────────────────────
-- SELECT
--     id,
--     title,
--     content,
--     embedding <=> '[0.234,-0.567,...]'::vector AS relevance_score
-- FROM documents
-- ORDER BY relevance_score
-- LIMIT 10;
--
-- Results:
--   1. "Python Tutorial for Beginners"     (score: 0.12)
--   2. "Learn Python Programming"          (score: 0.15)
--   3. "Python Course Overview"            (score: 0.18)
--   ...
--
--
-- Step 3: Filter by metadata (optional)
-- ────────────────────────────────────────────────────────────────────────
-- SELECT
--     id,
--     title,
--     category,
--     embedding <=> '[...]'::vector AS score
-- FROM documents
-- WHERE category = 'tutorials'
--   AND language = 'en'
--   AND published_date > '2023-01-01'
-- ORDER BY score
-- LIMIT 10;
--
-- ============================================================================
-- PERFORMANCE TIPS
-- ============================================================================
--
-- 1. ALWAYS use indexes for large datasets (>10,000 vectors)
-- ────────────────────────────────────────────────────────────────────────
-- CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
--
-- Without index: O(n) - scans every row
-- With index:    O(log n) - much faster
--
--
-- 2. Choose the right index type
-- ────────────────────────────────────────────────────────────────────────
-- HNSW:    Better accuracy, slower build, <1M vectors
-- IVFFlat: Faster build, lower accuracy, >1M vectors
--
--
-- 3. Match index operator to query operator
-- ────────────────────────────────────────────────────────────────────────
-- Query uses <=>  → Create index with vector_cosine_ops
-- Query uses <->  → Create index with vector_l2_ops
-- Query uses <#>  → Create index with vector_ip_ops
--
--
-- 4. Batch insert for better performance
-- ────────────────────────────────────────────────────────────────────────
-- Use COPY or multi-row INSERT for bulk data
--
--
-- 5. Monitor query performance
-- ────────────────────────────────────────────────────────────────────────
-- EXPLAIN ANALYZE
-- SELECT * FROM docs ORDER BY embedding <=> '[...]'::vector LIMIT 10;
--
-- ============================================================================
-- TIPS FOR EXPLORATION:
-- ============================================================================
--
-- 1. Start with basic SELECT queries to understand the data
-- 2. Try different query vectors to see how results change
-- 3. Experiment with distance thresholds
-- 4. Compare the three distance metrics (cosine, L2, inner product)
-- 5. Add your own data with INSERT statements
-- 6. Use DBeaver to visualize results in table format
--
-- Remember:
-- - Lower distance = more similar (for <=> and <->)
-- - Higher inner product = more similar (for <#>)
-- - Cosine distance is best for semantic/text search
--
-- Next steps:
-- 1. Read the README.md for Docker setup with embedding service
-- 2. Try the tutorial: python vector_tutorial.py
-- 3. Explore with these queries in DBeaver
-- 4. Build your own semantic search application!
-- ============================================================================
