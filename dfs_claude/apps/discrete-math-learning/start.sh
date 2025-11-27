#!/bin/bash

echo "🚀 Discrete Mathematics Learning Platform"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker is not running. Please start Docker Desktop first."
    echo ""
    echo "Alternative: Start with a simple HTTP server"
    echo ""

    # Check for Python
    if command -v python3 &> /dev/null; then
        echo "Starting with Python HTTP server on port 8080..."
        cd src
        python3 -m http.server 8080
    elif command -v python &> /dev/null; then
        echo "Starting with Python HTTP server on port 8080..."
        cd src
        python -m http.server 8080
    else
        echo "Python not found. Please install Python or start Docker."
        exit 1
    fi
else
    echo "✅ Docker is running"
    echo ""
    echo "Building and starting the application..."

    # Build and run with docker-compose
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
        docker-compose up --build -d
        echo ""
        echo "✅ Application is running!"
        echo "🌐 Open http://localhost:8080 in your browser"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
    else
        # Fallback to docker commands
        docker build -t discrete-math-learning .
        docker run -d -p 8080:80 --name discrete-math discrete-math-learning
        echo ""
        echo "✅ Application is running!"
        echo "🌐 Open http://localhost:8080 in your browser"
        echo ""
        echo "To view logs: docker logs discrete-math"
        echo "To stop: docker stop discrete-math && docker rm discrete-math"
    fi
fi
