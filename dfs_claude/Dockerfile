FROM python:3.11-slim

WORKDIR /app

# Install system tools for network monitoring
RUN apt-get update && apt-get install -y net-tools procps && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install --no-cache-dir uv

# Copy pyproject.toml first for dependency installation
COPY pyproject.toml /app/

# Install dependencies using uv (much faster than pip)
# --no-cache prevents caching package downloads
RUN uv pip install --system --no-cache \
    jupyter \
    notebook \
    matplotlib \
    numpy \
    ipywidgets \
    grip \
    beautifulsoup4 \
    requests \
    networkx \
    flask \
    plotext

# Expose ports:
# 8888 - Jupyter
# 8000 - HTML game
# 8001 - Markdown viewer
# 8002 - Portfolio
# 8003 - AZ-204 Study Guide
# 5000 - Graph Visualizer (Flask)
# 5001 - Tree Visualizer (Flask)
EXPOSE 8888 8000 8001 8002 8003 5000 5001

# Copy application files (respects .dockerignore)
COPY . /app

# Make start scripts executable
RUN chmod +x /app/start.sh /app/start-all.sh

CMD ["/bin/bash", "/app/start.sh"]
