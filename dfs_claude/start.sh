#!/bin/bash

# Start HTTP server for HTML game in background
cd /app/sliding_window_game && python -m http.server 8000 &

# Start grip for markdown viewer in background
cd /app && grip sliding_cheatsheet.md 0.0.0.0:8001 &

# Start HTTP server for portfolio in background
cd /app/portfolio && python -m http.server 8002 &

# Run AZ-204 content scraper if extracted content doesn't exist
if [ ! -f /app/azure_204/appservice/extracted-content.json ]; then
    echo "Running AZ-204 content scraper (first time only)..."
    cd /app/azure_204/appservice && python scraper.py
fi

# Start HTTP server for AZ-204 study guide in background
cd /app/azure_204/appservice && python -m http.server 8003 &

# Start Jupyter notebook
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""
