import psycopg2
import time
import sys

# Retry connection up to 10 times with 5-second intervals
max_retries = 10
retry_count = 0

while retry_count < max_retries:
    try:
        print(f"🔄 Attempt {retry_count + 1}/{max_retries}: Connecting to PostgreSQL...")
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="vectors_db",
            user="postgres",
            password="postgres"
        )
        
        print("✅ Connected successfully!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        db_version = cursor.fetchone()
        print(f"📊 Database version: {db_version[0]}")
        
        # Check if pgvector extension is available
        cursor.execute("""
            SELECT 1 FROM pg_extension WHERE extname = 'vector'
        """)
        has_vector = cursor.fetchone()
        
        if has_vector:
            print("✅ pgvector extension is installed")
        else:
            print("⚠️  pgvector extension not found, installing...")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.commit()
            print("✅ pgvector extension installed")
        
        cursor.close()
        conn.close()
        sys.exit(0)  # Success
        
    except psycopg2.OperationalError as e:
        retry_count += 1
        print(f"❌ Connection failed: {e}")
        
        if retry_count < max_retries:
            print(f"⏳ Waiting 5 seconds before retry...")
            time.sleep(5)
        else:
            print(f"\n❌ Failed to connect after {max_retries} attempts")
            print("\n🔧 Troubleshooting steps:")
            print("1. Check if Docker is running: docker ps")
            print("2. Check container logs: docker logs pgvector-db")
            print("3. Verify port 5432 is available: netstat -an | grep 5432")
            print("4. Try stopping and restarting: docker-compose down && docker-compose up -d")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)