# Extend pgvector image with http extension
FROM pgvector/pgvector:pg17

# Switch to root to install packages
USER root

# Install http extension for making HTTP requests from PostgreSQL
RUN apt-get update && \
    apt-get install -y \
    postgresql-17-http \
    && rm -rf /var/lib/apt/lists/*

# Switch back to postgres user
USER postgres
