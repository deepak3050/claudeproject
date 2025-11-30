#!/bin/bash

echo "Starting all DFS Claude applications..."

# Start Tree Visualizer (Flask) in background
echo "Starting Tree Visualizer on port 5001..."
cd /app/apps/python_ds && python tree_app.py &

# Start Graph Visualizer (Flask) in background
echo "Starting Graph Visualizer on port 5000..."
cd /app/apps/python_ds && python app.py &

# Start HTTP server for HTML game in background
echo "Starting HTML Game on port 8000..."
cd /app/apps/game && python -m http.server 8000 --bind 0.0.0.0 &

# Start HTTP server for cheatsheet in background
echo "Starting Cheatsheet Viewer on port 8001..."
cd /app/apps/cheatsheet && python -m http.server 8001 --bind 0.0.0.0 &

# Start HTTP server for portfolio in background
echo "Starting Portfolio on port 8002..."
cd /app/apps/portfolio && python -m http.server 8002 --bind 0.0.0.0 &

# Run AZ-204 content scraper if extracted content doesn't exist
if [ ! -f /app/apps/az204/extracted-content.json ]; then
    echo "Running AZ-204 content scraper (first time only)..."
    cd /app/apps/az204 && python scraper.py
fi

# Start HTTP server for AZ-204 study guide in background
echo "Starting AZ-204 Study Guide on port 8003..."
cd /app/apps/az204 && python -m http.server 8003 --bind 0.0.0.0 &

# Start Jupyter notebook in foreground (keeps container running)
echo "Starting Jupyter Notebook on port 8888..."
cd /app/notebooks && jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
