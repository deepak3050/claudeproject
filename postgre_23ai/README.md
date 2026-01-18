# PostgreSQL Vector Database with pgvector

Learn vector embeddings, semantic search, and AI-powered database queries using PostgreSQL + pgvector.

---

## 📦 What's In This Folder

```
postgre_23ai/
├── README.md                    ← You are here
├── Dockerfile                   ← Custom image with pgvector + http extension
├── docker-compose.yml           ← PostgreSQL + pgvector + pgAdmin containers
├── vector_conn.py               ← Test database connection
├── vector_tutorial.py           ← Learn vector operations (7 tutorials)
├── vector_queries.sql           ← SQL queries for exploring vectors
└── openai_embeddings.sql        ← How to use real OpenAI embeddings (SQL-only)
```

---

## 🚀 Quick Start

```bash
# 1. Build and start PostgreSQL with pgvector + http extension
docker-compose up -d --build

# 2. Verify connection
uv run python vector_conn.py

# 3. Run tutorial (learn vector operations)
uv run python vector_tutorial.py

# 4. Explore in DBeaver or psql
# Connect: localhost:5432, database: vectors_db, user: postgres, pass: postgres

# 5. Verify http extension is available (in DBeaver or psql)
# Run: CREATE EXTENSION IF NOT EXISTS http;
```

---

## 🎯 Two Paths to Explore

### Path 1: SQL-Only Exploration (No Coding)

**For:** Learning vectors, testing queries, exploring semantic search
**Tools:** DBeaver or psql + curl commands

#### Step 1: Open SQL file in DBeaver

1. Connect DBeaver to `localhost:5432`, database: `vectors_db`
2. Open `vector_queries.sql` in SQL Editor
3. Run queries one-by-one to learn vector operations

**What you'll learn:**
- Create tables with vector columns
- Insert embeddings
- Similarity search (3 distance metrics: cosine, L2, inner product)
- Filter + search combinations
- Vector math operations
- Create indexes for performance

#### Step 2: Explore with Simulated Data (Easy)

The tutorial uses simple 3D vectors for learning:
```sql
-- "Python-like" content = [1.0, 0.0, 0.0]
-- "JavaScript-like" = [0.0, 1.0, 0.0]
-- "AI-like" = [0.0, 0.0, 1.0]

-- Find similar items
SELECT name, embedding <=> '[1,0,0]'::vector AS distance
FROM items
ORDER BY distance
LIMIT 5;
```

Run `vector_tutorial.py` first to populate the database with sample data.

#### Step 3: Use Real Embeddings with OpenAI (Production)

**Prerequisites:**
- OpenAI API key: https://platform.openai.com/api-keys

**Two Methods Available:**

**Method 1: In-Database (RECOMMENDED) - No Terminal Needed!**

Generate embeddings directly from SQL queries using PostgreSQL's `http` extension:

```sql
-- 1. Setup (one time in DBeaver)
CREATE EXTENSION IF NOT EXISTS http;
INSERT INTO openai_config (api_key) VALUES ('sk-your-api-key-here');

-- 2. List available models
SELECT * FROM openai_list_models();

-- 3. Insert with auto-embedding
INSERT INTO smart_docs (content) VALUES
    ('Python is a programming language');
-- Embedding is generated automatically!

-- 4. Search (embedding generated on the fly)
SELECT content
FROM smart_docs
ORDER BY embedding <=> openai_embed('programming languages')
LIMIT 10;
```

**Benefits:**
- ✅ Everything in SQL - no terminal commands
- ✅ Auto-generate embeddings on INSERT
- ✅ List models directly from SQL
- ✅ API key stored securely in database
- ✅ Cost tracking built-in
- ✅ **Automatic 10-second timeout** (fixes "Resolving timed out" errors)
- ✅ **Enhanced error handling** for better debugging

**Method 2: Terminal + curl (Legacy)**

Traditional workflow if http extension is not available:

```bash
# 1. Generate embedding (terminal)
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Python is a programming language",
    "model": "text-embedding-3-small"
  }' | jq -r '.data[0].embedding'

# 2. Insert in SQL (DBeaver) - copy-paste embedding
INSERT INTO real_docs (content, embedding) VALUES
    ('Python is a programming language',
     '[0.123, -0.456, 0.789, ..., 0.234]'::vector);
```

**Full guide:** See `openai_embeddings.sql` for detailed examples of both methods

**Cost:** $0.02 per 1M tokens (~$0.00001 per document, very cheap!)

---

### Path 2: Python Scripts (Automation)

**For:** Building applications, batch processing, automation
**Tools:** Python + OpenAI API + psycopg2

When you're ready to automate, use Python to:
- Generate embeddings in batch
- Insert thousands of documents automatically
- Build semantic search APIs
- Implement RAG (Retrieval Augmented Generation)

#### Option A: OpenAI Embeddings (Best Quality)

```python
from openai import OpenAI
import psycopg2
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Generate embedding
response = client.embeddings.create(
    input="Your text here",
    model="text-embedding-3-small"  # $0.02 per 1M tokens
)
embedding = response.data[0].embedding  # 1536 dimensions

# Insert into PostgreSQL
conn = psycopg2.connect(
    host="localhost", port=5432,
    database="vectors_db", user="postgres", password="postgres"
)
cur = conn.cursor()
cur.execute(
    "INSERT INTO docs (content, embedding) VALUES (%s, %s::vector)",
    ("Your text here", str(embedding))
)
conn.commit()
```

#### Option B: Sentence Transformers (Free, Local)

```python
from sentence_transformers import SentenceTransformer
import psycopg2

# Load model (runs locally, no API key needed!)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embedding
embedding = model.encode(["Your text here"])[0]  # 384 dimensions

# Insert into PostgreSQL (same as above)
```

#### Install Dependencies

```bash
# For OpenAI
uv pip install openai

# For Sentence Transformers (local, free)
uv pip install sentence-transformers

# Database
uv pip install psycopg2-binary
```

---

## 🗂️ Database Tables

After running `vector_tutorial.py`, you'll have these tables:

| Table | Dimensions | Purpose |
|-------|-----------|---------|
| `items` | 3 | Learning examples (Python/JS/AI topics) |
| `documents` | 384 | Tutorial examples |
| `real_docs` | 1536 | For your real OpenAI embeddings |

**View in DBeaver:**
```sql
-- See all tables
\dt

-- Current data
SELECT * FROM items;
SELECT * FROM documents;
SELECT * FROM real_docs;
```

---

## 🔍 Key Concepts

### What are Embeddings?

**Simulated** (tutorial) vs **Real** (production):

```
SIMULATED (learning):
"Python" = [1.0, 0.0, 0.0]  ← Manually crafted
"JavaScript" = [0.0, 1.0, 0.0]
Easy to understand, but not real!

REAL (production):
"Python" = [0.123, -0.456, 0.789, ..., 0.234]  ← From ML model
"JavaScript" = [0.145, -0.423, 0.801, ..., 0.256]
Generated by OpenAI/sentence-transformers
Captures semantic meaning automatically
```

### Distance Metrics

| Operator | Name | Best For | Range |
|----------|------|----------|-------|
| `<=>` | Cosine | Text/semantic search | 0-2 (0=identical) |
| `<->` | L2 (Euclidean) | Geometric similarity | 0-∞ (0=identical) |
| `<#>` | Inner Product | Normalized vectors | -∞ to ∞ (higher=similar) |

**Use cosine (`<=>`) for semantic search - it's the most common!**

---

## 💡 Common Operations

### Connect to Database

```bash
# DBeaver (GUI)
Host: localhost
Port: 5432
Database: vectors_db
Username: postgres
Password: postgres

# psql (command line)
docker exec -it pgvector-db psql -U postgres -d vectors_db
```

### Set OpenAI API Key

**Method 1: In-Database (Recommended for DBeaver)**

Store API key directly in PostgreSQL:

```sql
-- In DBeaver SQL Editor, run:
CREATE EXTENSION IF NOT EXISTS http;
INSERT INTO openai_config (api_key) VALUES ('sk-your-key-here');

-- Verify
SELECT substring(api_key, 1, 10) || '...' as key_preview FROM openai_config;

-- Update if needed
UPDATE openai_config SET api_key = 'sk-new-key-here' WHERE id = 1;
```

**Method 2: Environment Variable (For Terminal/Python)**

```bash
# Temporary (current session)
export OPENAI_API_KEY='sk-your-key-here'

# Permanent (all sessions)
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc

# Verify
echo $OPENAI_API_KEY
```

### Docker Commands

```bash
# Start (first time or after Dockerfile changes)
docker-compose up -d --build

# Start (normal)
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f postgres

# Check status
docker ps

# Rebuild after updating Dockerfile
docker-compose down && docker-compose up -d --build

# Restart fresh (deletes all data!)
docker-compose down -v && docker-compose up -d --build
```

---

## 📚 Learning Resources

### Files to Explore

1. **`vector_tutorial.py`** - Run this first! 7 interactive tutorials
2. **`vector_queries.sql`** - Open in DBeaver, run queries, learn by doing
3. **`openai_embeddings.sql`** - How to use real OpenAI embeddings (SQL-only workflow)

### External Links

- [pgvector Docs](https://github.com/pgvector/pgvector) - Vector extension documentation
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings) - Best quality embeddings
- [Sentence Transformers](https://www.sbert.net/) - Free local embeddings
- [What are Vector Embeddings?](https://www.pinecone.io/learn/vector-embeddings/)

---

## 🔧 Troubleshooting

### Can't connect to database

```bash
# Check Docker is running
docker ps

# Should see: pgvector-db (port 5432)

# If not:
docker-compose up -d

# Wait 10 seconds, try again
```

### Port 5432 already in use

```bash
# Check what's using it
lsof -i :5432

# If Homebrew PostgreSQL:
brew services stop postgresql

# Or stop other container:
docker stop <container_id>
```

### http extension not found

If you get "extension http does not exist":

**Solution: Rebuild the Docker container**

The Dockerfile includes the http extension, but you need to rebuild:

```bash
# Stop current container
docker-compose down

# Rebuild with http extension
docker-compose up -d --build

# Verify in DBeaver
CREATE EXTENSION IF NOT EXISTS http;
SELECT extname FROM pg_extension WHERE extname = 'http';
```

**If still not working:**

Check that Dockerfile exists in the postgre_23ai folder and contains:
```dockerfile
FROM pgvector/pgvector:pg17
USER root
RUN apt-get update && apt-get install -y postgresql-17-http
USER postgres
```

**Alternative: Use legacy curl method**

See SECTION B in `openai_embeddings.sql` for terminal-based workflow (no http extension needed).

### OpenAI API errors

**In-Database Method:**
```sql
-- Check if API key is configured
SELECT substring(api_key, 1, 10) || '...' FROM openai_config;

-- If empty or wrong, update:
UPDATE openai_config SET api_key = 'sk-your-correct-key' WHERE id = 1;

-- Test the connection
SELECT * FROM openai_list_models();
```

**Terminal Method:**
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Should output: sk-...

# If empty, set it:
export OPENAI_API_KEY='sk-your-key-here'
```

**Common API Error Codes:**
- `401 Unauthorized`: Invalid API key - update it
- `429 Too Many Requests`: Rate limit - wait and retry
- `500 Server Error`: OpenAI issue - try again later

### Timeout errors ("Resolving timed out")

If you see: `ERROR: Failed to generate embedding: Resolving timed out after 1004 milliseconds`

**Root Cause:** The `http` extension has a default 1-second timeout, which is too short for OpenAI API calls.

**✅ Solution (ALREADY FIXED in openai_embeddings.sql):**

The functions `openai_embed()` and `openai_list_models()` now include automatic 10-second timeout handling. If you created these functions before this fix:

```sql
-- Option 1: Drop and recreate functions (recommended)
-- Open openai_embeddings.sql in DBeaver and re-run sections A3 and A4

-- Option 2: Manual session-level fix
SET http.timeout_msec = 10000;  -- 10 seconds
SELECT openai_embed('test');

-- Option 3: Database-level permanent fix
ALTER DATABASE vectors_db SET http.timeout_msec = 10000;
```

**To verify the fix is working:**
```sql
-- This should complete in 1-3 seconds (not timeout)
SELECT openai_embed('Python is a programming language');
```

**If you have NULL embeddings in smart_docs:**
```sql
-- Update existing rows with NULL embeddings
UPDATE smart_docs
SET embedding = openai_embed(content)
WHERE embedding IS NULL;
```

### Missing embeddings in smart_docs table

If `SELECT * FROM smart_docs` shows embeddings as `✗ Missing`:

**Cause:** The trigger failed (likely due to timeout before the fix was applied).

**Solution:**
```sql
-- Option 1: Reset everything and start fresh
-- Run this complete reset script in DBeaver:

DROP TABLE IF EXISTS smart_docs CASCADE;
DROP FUNCTION IF EXISTS auto_generate_embedding() CASCADE;

-- Then re-run sections A4, A5, A6 from openai_embeddings.sql

-- Option 2: Update existing rows
UPDATE smart_docs
SET embedding = openai_embed(content)
WHERE embedding IS NULL;

-- Verify
SELECT id, content,
       CASE
           WHEN embedding IS NOT NULL THEN '✓ Generated (' || vector_dims(embedding) || 'D)'
           ELSE '✗ Missing'
       END as embedding_status
FROM smart_docs;
```

---

## 🎓 What You've Built

- ✅ PostgreSQL 17 with pgvector running in Docker
- ✅ Sample data with simulated embeddings (for learning)
- ✅ SQL queries for semantic search
- ✅ Ready for real OpenAI embeddings
- ✅ Tools: DBeaver, psql, Python scripts

**Next:** Choose your path (SQL-only or Python) and start exploring!

---

## 📝 Quick Reference

### Database Setup
```bash
# Start database
docker-compose up -d

# Run tutorial
uv run python vector_tutorial.py

# Connect with psql
docker exec -it pgvector-db psql -U postgres -d vectors_db
```

### In-Database Embeddings (Recommended for DBeaver)
```sql
-- One-time setup
CREATE EXTENSION IF NOT EXISTS http;
INSERT INTO openai_config (api_key) VALUES ('sk-your-api-key');

-- List available models
SELECT * FROM openai_list_models();

-- Insert with auto-embedding
INSERT INTO smart_docs (content) VALUES ('your text');

-- Search
SELECT content FROM smart_docs
ORDER BY embedding <=> openai_embed('search query')
LIMIT 10;

-- Update API key
UPDATE openai_config SET api_key = 'sk-new-key' WHERE id = 1;
```

### Terminal Method (Legacy)
```bash
# Set API key
export OPENAI_API_KEY='sk-your-key'

# Generate embedding
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "your text", "model": "text-embedding-3-small"}' \
  | jq -r '.data[0].embedding'
```

**Questions?** Read `vector_queries.sql` or `openai_embeddings.sql` for detailed examples.
