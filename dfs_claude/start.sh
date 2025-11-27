#!/bin/bash

# Start HTTP server for HTML game in background
cd /app/apps/game && python -m http.server 8000 &

# Start HTTP server for cheatsheet in background
cd /app/apps/cheatsheet && python -m http.server 8001 &

# Start HTTP server for portfolio in background
cd /app/apps/portfolio && python -m http.server 8002 &

# Run AZ-204 content scraper if extracted content doesn't exist
if [ ! -f /app/apps/az204/extracted-content.json ]; then
    echo "Running AZ-204 content scraper (first time only)..."
    cd /app/apps/az204 && python scraper.py
fi

# Start HTTP server for AZ-204 study guide in background
cd /app/apps/az204 && python -m http.server 8003 &

# Start Jupyter notebook (serves notebooks folder)
cd /app/notebooks && jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""
