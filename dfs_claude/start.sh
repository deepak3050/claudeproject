#!/bin/bash

# Start HTTP server for HTML game in background
cd /app/sliding_window_game && python -m http.server 8000 &

# Start Jupyter notebook
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""
