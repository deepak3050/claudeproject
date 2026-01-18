"""
PostgreSQL Vector Operations Tutorial

This script demonstrates how to work with vector embeddings in PostgreSQL
using the pgvector extension. Perfect for learning semantic search,
similarity matching, and RAG systems.

Topics covered:
1. Creating tables with vector columns
2. Inserting vector embeddings
3. Similarity search (cosine, L2, inner product)
4. Vector indexing for performance
5. Practical examples with sample data
"""

import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import numpy as np
from typing import List, Tuple


# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "vectors_db",
    "user": "postgres",
    "password": "postgres"
}


def connect_db():
    """Establish connection to PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise


def setup_vector_extension(conn):
    """Ensure pgvector extension is installed."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        print("✅ pgvector extension ready")


def adapt_list(lst):
    """Convert Python list to PostgreSQL vector format."""
    return AsIs(f"'[{','.join(map(str, lst))}]'::vector")


def numpy_to_vector(array):
    """Convert numpy array to PostgreSQL vector format."""
    return AsIs(f"'[{','.join(map(str, array))}]'::vector")


# Register adapters for psycopg2
register_adapter(np.ndarray, numpy_to_vector)
register_adapter(list, adapt_list)


# =============================================================================
# TUTORIAL 1: CREATE TABLES WITH VECTOR COLUMNS
# =============================================================================

def tutorial_1_create_tables(conn):
    """
    Create tables with vector columns.

    Vector columns can store embeddings of different dimensions:
    - vector(3): 3-dimensional vectors
    - vector(384): Common for sentence embeddings (sentence-transformers)
    - vector(1536): OpenAI text-embedding-ada-002
    - vector(768): BERT embeddings
    """
    print("\n" + "="*70)
    print("TUTORIAL 1: Creating Tables with Vector Columns")
    print("="*70)

    with conn.cursor() as cur:
        # Drop existing tables for clean start
        cur.execute("DROP TABLE IF EXISTS items CASCADE")
        cur.execute("DROP TABLE IF EXISTS documents CASCADE")

        # Create a simple items table with 3D vectors (for easy visualization)
        cur.execute("""
            CREATE TABLE items (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                embedding vector(3)  -- 3-dimensional vector
            )
        """)
        print("✅ Created 'items' table with 3D vectors")

        # Create a documents table with higher-dimensional vectors
        cur.execute("""
            CREATE TABLE documents (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                embedding vector(384),  -- 384-dimensional (common for sentence embeddings)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created 'documents' table with 384D vectors")

        conn.commit()

    print("\n📝 Key Points:")
    print("   - vector(N) creates a column that stores N-dimensional vectors")
    print("   - Choose dimension based on your embedding model")
    print("   - All vectors in a column must have the same dimension")


# =============================================================================
# TUTORIAL 2: INSERT VECTOR EMBEDDINGS
# =============================================================================

def tutorial_2_insert_embeddings(conn):
    """
    Insert sample embeddings into the database.

    In real applications, these embeddings would come from:
    - OpenAI API (text-embedding-ada-002)
    - sentence-transformers (all-MiniLM-L6-v2)
    - BERT models
    - Custom ML models
    """
    print("\n" + "="*70)
    print("TUTORIAL 2: Inserting Vector Embeddings")
    print("="*70)

    # Sample 3D embeddings (imagine these represent fruits in 3D space)
    # In reality, embeddings are semantic representations of text/images
    sample_items = [
        ("apple", [1.0, 0.0, 0.0]),      # Red fruit
        ("strawberry", [0.9, 0.1, 0.0]), # Also red, similar to apple
        ("banana", [0.0, 1.0, 0.0]),     # Yellow fruit
        ("lemon", [0.1, 0.9, 0.0]),      # Also yellow, similar to banana
        ("blueberry", [0.0, 0.0, 1.0]),  # Blue fruit
        ("grape", [0.5, 0.0, 0.5]),      # Purple (mix of red and blue)
    ]

    with conn.cursor() as cur:
        # Method 1: Insert using list literal
        for name, embedding in sample_items:
            cur.execute(
                "INSERT INTO items (name, embedding) VALUES (%s, %s)",
                (name, embedding)
            )

        print(f"✅ Inserted {len(sample_items)} items with embeddings")

        # Method 2: Insert using numpy array (more realistic)
        random_embedding = np.random.rand(384)  # Simulate a 384D embedding
        cur.execute(
            "INSERT INTO documents (title, content, embedding) VALUES (%s, %s, %s)",
            ("Sample Document", "This is a test document", random_embedding)
        )
        print("✅ Inserted document with 384D numpy array embedding")

        conn.commit()

    # Verify the data
    with conn.cursor() as cur:
        cur.execute("SELECT name, embedding FROM items")
        rows = cur.fetchall()
        print("\n📊 Inserted Items:")
        for name, embedding in rows:
            print(f"   {name:12} → {embedding}")

    print("\n📝 Key Points:")
    print("   - Embeddings can be inserted as Python lists or numpy arrays")
    print("   - pgvector automatically validates dimension matches")
    print("   - In production, embeddings come from ML models (OpenAI, etc.)")


# =============================================================================
# TUTORIAL 3: SIMILARITY SEARCH
# =============================================================================

def tutorial_3_similarity_search(conn):
    """
    Perform similarity searches using different distance metrics.

    Distance Metrics:
    - <-> : L2 distance (Euclidean) - geometric distance
    - <#> : Inner product (negative) - dot product similarity
    - <=> : Cosine distance - angular similarity (most common for text)
    """
    print("\n" + "="*70)
    print("TUTORIAL 3: Similarity Search with Different Metrics")
    print("="*70)

    # Query: Find fruits similar to a "red fruit"
    query_vector = [1.0, 0.0, 0.0]  # Red fruit profile

    print(f"\n🔍 Query Vector: {query_vector} (searching for red fruits)")

    # Method 1: L2 Distance (Euclidean distance)
    print("\n1️⃣  L2 Distance (Euclidean) - <->")
    print("   Measures geometric distance between vectors")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, embedding, embedding <-> %s AS distance
            FROM items
            ORDER BY distance
            LIMIT 3
        """, (query_vector,))

        print("   Top 3 similar items:")
        for name, embedding, distance in cur.fetchall():
            print(f"      {name:12} (distance: {distance:.4f}) {embedding}")

    # Method 2: Cosine Distance (most common for semantic search)
    print("\n2️⃣  Cosine Distance - <=>")
    print("   Measures angular similarity (best for text embeddings)")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, embedding, embedding <=> %s AS distance
            FROM items
            ORDER BY distance
            LIMIT 3
        """, (query_vector,))

        print("   Top 3 similar items:")
        for name, embedding, distance in cur.fetchall():
            print(f"      {name:12} (distance: {distance:.4f}) {embedding}")

    # Method 3: Inner Product (useful for certain ML models)
    print("\n3️⃣  Inner Product (Negative) - <#>")
    print("   Measures dot product similarity")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, embedding, (embedding <#> %s) * -1 AS similarity
            FROM items
            ORDER BY embedding <#> %s
            LIMIT 3
        """, (query_vector, query_vector))

        print("   Top 3 similar items:")
        for name, embedding, similarity in cur.fetchall():
            print(f"      {name:12} (similarity: {similarity:.4f}) {embedding}")

    print("\n📝 Key Points:")
    print("   - <=> Cosine distance: Best for text/semantic search (0=identical, 2=opposite)")
    print("   - <-> L2 distance: Best for geometric similarity")
    print("   - <#> Inner product: Best when vectors are normalized")
    print("   - Always use ORDER BY distance LIMIT N for top-N search")


# =============================================================================
# TUTORIAL 4: PRACTICAL SEMANTIC SEARCH EXAMPLE
# =============================================================================

def tutorial_4_semantic_search_example(conn):
    """
    Practical example: Build a simple semantic search over text documents.

    This simulates a real-world scenario where you:
    1. Have documents with embeddings
    2. User submits a query
    3. Find most relevant documents
    """
    print("\n" + "="*70)
    print("TUTORIAL 4: Practical Semantic Search Example")
    print("="*70)

    # Simulate embeddings for different topics
    # (In reality, these would come from an embedding model)
    documents_data = [
        ("Python Programming", "Learn Python basics", [1.0, 0.0, 0.0]),
        ("Python Web Development", "Build web apps with Python", [0.9, 0.1, 0.0]),
        ("JavaScript Basics", "Introduction to JavaScript", [0.0, 1.0, 0.0]),
        ("React Tutorial", "Build UIs with React", [0.0, 0.9, 0.1]),
        ("Machine Learning", "AI and ML fundamentals", [0.0, 0.0, 1.0]),
        ("Deep Learning", "Neural networks and AI", [0.1, 0.0, 0.9]),
    ]

    # Clear and insert sample documents
    with conn.cursor() as cur:
        cur.execute("DELETE FROM items")
        for title, content, embedding in documents_data:
            cur.execute(
                "INSERT INTO items (name, embedding) VALUES (%s, %s)",
                (title, embedding)
            )
        conn.commit()
        print(f"✅ Loaded {len(documents_data)} sample documents")

    # Simulate user queries
    queries = [
        ("Python coding", [1.0, 0.0, 0.0]),        # Should match Python docs
        ("Frontend development", [0.0, 1.0, 0.0]), # Should match JS/React
        ("Artificial Intelligence", [0.0, 0.0, 1.0]), # Should match ML/DL
    ]

    for query_text, query_vector in queries:
        print(f"\n🔍 Query: '{query_text}'")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, embedding <=> %s AS relevance_score
                FROM items
                ORDER BY embedding <=> %s
                LIMIT 3
            """, (query_vector, query_vector))

            print("   📄 Top 3 relevant documents:")
            for doc_name, score in cur.fetchall():
                print(f"      {doc_name:30} (score: {score:.4f})")

    print("\n📝 Key Points:")
    print("   - Lower cosine distance = higher relevance")
    print("   - This is the foundation of semantic search engines")
    print("   - In production, use real embeddings from OpenAI/sentence-transformers")


# =============================================================================
# TUTORIAL 5: VECTOR INDEXING FOR PERFORMANCE
# =============================================================================

def tutorial_5_vector_indexing(conn):
    """
    Create indexes on vector columns for fast similarity search.

    Index Types:
    - IVFFlat: Inverted file index (faster, less accurate)
    - HNSW: Hierarchical Navigable Small World (slower build, very accurate)

    Without indexes, searches are O(n) - scan every row.
    With indexes, searches are O(log n) - much faster for large datasets.
    """
    print("\n" + "="*70)
    print("TUTORIAL 5: Vector Indexing for Performance")
    print("="*70)

    with conn.cursor() as cur:
        # Create HNSW index (recommended for most use cases)
        print("\n🚀 Creating HNSW index on items.embedding...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS items_embedding_hnsw_idx
            ON items
            USING hnsw (embedding vector_cosine_ops)
        """)
        print("✅ HNSW index created (using cosine distance)")

        # Alternative: Create IVFFlat index
        # Requires specifying 'lists' parameter (rule of thumb: rows/1000)
        print("\n🚀 Creating IVFFlat index on documents.embedding...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_embedding_ivfflat_idx
            ON documents
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
        print("✅ IVFFlat index created (100 lists)")

        conn.commit()

    print("\n📝 Index Types Comparison:")
    print("\n   HNSW (Hierarchical Navigable Small World):")
    print("      ✓ Better recall (more accurate)")
    print("      ✓ Good for small to medium datasets (<1M vectors)")
    print("      ✗ Slower index build time")
    print("      ✗ More memory usage")

    print("\n   IVFFlat (Inverted File Flat):")
    print("      ✓ Faster index build")
    print("      ✓ Less memory usage")
    print("      ✓ Good for very large datasets (>1M vectors)")
    print("      ✗ Lower recall (less accurate)")
    print("      ✗ Requires tuning 'lists' parameter")

    print("\n📝 Distance Operators for Indexes:")
    print("   - vector_cosine_ops  → Use with <=> (cosine distance)")
    print("   - vector_l2_ops      → Use with <-> (L2 distance)")
    print("   - vector_ip_ops      → Use with <#> (inner product)")

    print("\n📝 When to Use Indexes:")
    print("   ✓ Dataset > 10,000 vectors")
    print("   ✓ Frequent similarity searches")
    print("   ✗ Skip if data changes frequently (index rebuild is expensive)")


# =============================================================================
# TUTORIAL 6: ADVANCED QUERIES
# =============================================================================

def tutorial_6_advanced_queries(conn):
    """
    Advanced vector queries combining filters and similarity search.
    """
    print("\n" + "="*70)
    print("TUTORIAL 6: Advanced Queries (Filters + Similarity)")
    print("="*70)

    # Add some metadata to items for filtering
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS category TEXT")
        cur.execute("UPDATE items SET category = 'programming' WHERE name LIKE '%Python%' OR name LIKE '%JavaScript%'")
        cur.execute("UPDATE items SET category = 'frontend' WHERE name LIKE '%React%'")
        cur.execute("UPDATE items SET category = 'ai' WHERE name LIKE '%Learning%'")
        conn.commit()

    query_vector = [1.0, 0.0, 0.0]

    # Query 1: Similarity search with WHERE filter
    print("\n🔍 Query 1: Find similar items in 'programming' category")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, category, embedding <=> %s AS distance
            FROM items
            WHERE category = 'programming'
            ORDER BY embedding <=> %s
            LIMIT 3
        """, (query_vector, query_vector))

        for name, category, distance in cur.fetchall():
            print(f"   {name:30} [{category:12}] (distance: {distance:.4f})")

    # Query 2: Get count of similar items above threshold
    print("\n🔍 Query 2: Count items within distance threshold")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) as similar_items
            FROM items
            WHERE embedding <=> %s < 0.5
        """, (query_vector,))

        count = cur.fetchone()[0]
        print(f"   Found {count} items within 0.5 distance")

    # Query 3: Combine similarity with multiple conditions
    print("\n🔍 Query 3: Complex query with multiple conditions")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, category, embedding <=> %s AS distance
            FROM items
            WHERE category IN ('programming', 'ai')
              AND embedding <=> %s < 1.0
            ORDER BY distance
        """, (query_vector, query_vector))

        print("   Items in programming/ai with distance < 1.0:")
        for name, category, distance in cur.fetchall():
            print(f"      {name:30} [{category:12}] (distance: {distance:.4f})")

    print("\n📝 Key Points:")
    print("   - Combine vector similarity with traditional SQL WHERE clauses")
    print("   - Use distance thresholds to filter results")
    print("   - Indexes work with filtered queries too!")


# =============================================================================
# TUTORIAL 7: VECTOR OPERATIONS
# =============================================================================

def tutorial_7_vector_operations(conn):
    """
    Perform mathematical operations on vectors.
    """
    print("\n" + "="*70)
    print("TUTORIAL 7: Vector Operations and Math")
    print("="*70)

    with conn.cursor() as cur:
        # Vector addition
        print("\n➕ Vector Addition:")
        cur.execute("""
            SELECT
                '[1,2,3]'::vector + '[4,5,6]'::vector AS result
        """)
        result = cur.fetchone()[0]
        print(f"   [1,2,3] + [4,5,6] = {result}")

        # Vector subtraction
        print("\n➖ Vector Subtraction:")
        cur.execute("""
            SELECT
                '[5,6,7]'::vector - '[1,2,3]'::vector AS result
        """)
        result = cur.fetchone()[0]
        print(f"   [5,6,7] - [1,2,3] = {result}")

        # Vector dimensions
        print("\n📏 Get Vector Dimensions:")
        cur.execute("""
            SELECT
                vector_dims('[1,2,3,4,5]'::vector) AS dimensions
        """)
        dims = cur.fetchone()[0]
        print(f"   vector_dims([1,2,3,4,5]) = {dims}")

        # L2 norm (magnitude)
        print("\n📐 L2 Norm (Magnitude):")
        cur.execute("""
            SELECT
                vector_norm('[3,4]'::vector) AS norm
        """)
        norm = cur.fetchone()[0]
        print(f"   vector_norm([3,4]) = {norm} (should be 5.0)")

        # Calculate distance between two vectors directly
        print("\n📍 Distance Calculation:")
        cur.execute("""
            SELECT
                '[1,0,0]'::vector <=> '[0,1,0]'::vector AS cosine_distance,
                '[1,0,0]'::vector <-> '[0,1,0]'::vector AS l2_distance
        """)
        cos_dist, l2_dist = cur.fetchone()
        print(f"   Cosine distance between [1,0,0] and [0,1,0]: {cos_dist:.4f}")
        print(f"   L2 distance between [1,0,0] and [0,1,0]: {l2_dist:.4f}")

    print("\n📝 Key Points:")
    print("   - Vectors support + and - operations")
    print("   - Use vector_dims() to get dimension count")
    print("   - Use vector_norm() to get magnitude/length")
    print("   - Calculate distances directly between vector literals")
    print("   - Cast text to vector using ::vector")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run all tutorials in sequence."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║        PostgreSQL Vector Operations Tutorial                    ║
    ║        Using pgvector for Similarity Search                     ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Connect to database
        conn = connect_db()

        # Setup pgvector extension
        setup_vector_extension(conn)

        # Run tutorials
        #tutorial_1_create_tables(conn)
        #tutorial_2_insert_embeddings(conn)
        tutorial_3_similarity_search(conn)
        #tutorial_4_semantic_search_example(conn)
        #tutorial_5_vector_indexing(conn)
        #tutorial_6_advanced_queries(conn)
        #tutorial_7_vector_operations(conn)

        # Close connection
        conn.close()

        print("\n" + "="*70)
        print("✅ All tutorials completed successfully!")
        print("="*70)

        print("\n🎓 What You Learned:")
        print("   ✓ How to create tables with vector columns")
        print("   ✓ How to insert embeddings (lists and numpy arrays)")
        print("   ✓ How to perform similarity searches (3 distance metrics)")
        print("   ✓ How to build practical semantic search")
        print("   ✓ How to create indexes for performance")
        print("   ✓ How to combine filters with vector search")
        print("   ✓ How to perform vector math operations")

        print("\n🚀 Next Steps:")
        print("   1. Integrate with real embedding models (OpenAI, sentence-transformers)")
        print("   2. Build a semantic search API")
        print("   3. Implement RAG (Retrieval Augmented Generation)")
        print("   4. Experiment with different index types and parameters")
        print("   5. Load larger datasets and benchmark performance")

        print("\n💡 Resources:")
        print("   - pgvector docs: https://github.com/pgvector/pgvector")
        print("   - OpenAI embeddings: https://platform.openai.com/docs/guides/embeddings")
        print("   - Sentence Transformers: https://www.sbert.net/")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    main()
