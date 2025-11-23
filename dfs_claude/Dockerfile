FROM python:3.11-slim

WORKDIR /app

# Install uv for faster package management
RUN pip install uv

# Install dependencies using uv (much faster than pip)
RUN uv pip install --system --no-cache \
    jupyter \
    notebook \
    matplotlib \
    numpy \
    ipywidgets \
    grip \
    beautifulsoup4 \
    requests

# Expose ports: 8888 for Jupyter, 8000 for HTML game, 8001 for Markdown viewer, 8002 for Portfolio, 8003 for AZ-204 Study Guide
EXPOSE 8888 8000 8001 8002 8003

# Copy all files
COPY . /app

# Make start script executable
RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]
