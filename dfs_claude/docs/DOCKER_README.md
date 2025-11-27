# Docker Setup for Sliding Window Learning Materials

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude

# Build and run
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Option 2: Using Docker directly

```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude

# Build the image
docker build -t sliding-window .

# Run the container
docker run -p 8888:8888 -p 8000:8000 -p 8001:8001 sliding-window
```

## Access the Applications

Once running, open your browser:

| Application | URL | Description |
|-------------|-----|-------------|
| **HTML Game** | http://localhost:8000 | Interactive Sliding Window Explorer |
| **Jupyter Notebook** | http://localhost:8888 | Notebooks with animations and pseudocode |
| **Cheatsheet** | http://localhost:8001 | Markdown cheatsheet rendered in GitHub style |
| **Portfolio** | http://localhost:8002 | Professional portfolio website |
| **AZ-204 Study Guide** | http://localhost:8003 | Azure exam preparation materials |

## Available Notebooks

In Jupyter (http://localhost:8888):

1. **sliding.ipynb** - Interactive visualizations with matplotlib animations
2. **sliding_pseudocode.ipynb** - Clean pseudocode examples for interview prep
3. **sliding_cheatsheet.md** - Quick reference cheatsheet

## Useful Commands

```bash
# Stop the container
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build

# Run in background
docker-compose up -d

# Enter container shell
docker exec -it dfs_claude-sliding-window-1 bash
```

## Port Configuration

If ports are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "9999:8888"  # Jupyter Notebook
  - "9000:8000"  # HTML Game
  - "9001:8001"  # Cheatsheet
  - "9002:8002"  # Portfolio
  - "9003:8003"  # AZ-204 Study Guide
```

Then access:
- Jupyter: http://localhost:9999
- Game: http://localhost:9000
- Cheatsheet: http://localhost:9001
- Portfolio: http://localhost:9002
- AZ-204 Study Guide: http://localhost:9003

## AZ-204 Study Guide

The AZ-204 Study Guide automatically extracts content from Microsoft Learn on first launch. This may take a few minutes.

To manually run the scraper:
```bash
docker exec -it dfs_claude-sliding-window-1 bash
cd /app/azure_204/appservice
python scraper.py
```

Features:
- Extracts all content from Azure App Service and Container modules
- Includes code examples, tables, and lists
- Dark/light mode toggle
- Search functionality

## Troubleshooting

### Port already in use
```bash
# Find what's using the port
lsof -i :8888
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Container won't start
```bash
# Check logs
docker-compose logs


# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d


# Rebuild docker
docker-compose up --build -d
```

### Changes not reflecting
If you mounted volumes and changes aren't showing:
```bash
# Restart the container
docker-compose restart
```
