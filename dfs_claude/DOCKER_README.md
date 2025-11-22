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
docker run -p 8888:8888 -p 8000:8000 sliding-window
```

## Access the Applications

Once running, open your browser:

| Application | URL | Description |
|-------------|-----|-------------|
| **HTML Game** | http://localhost:8000 | Interactive Sliding Window Explorer |
| **Jupyter Notebook** | http://localhost:8888 | Notebooks with animations and pseudocode |

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

If ports 8888 or 8000 are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "9999:8888"  # Change 9999 to your preferred Jupyter port
  - "9000:8000"  # Change 9000 to your preferred game port
```

Then access:
- Jupyter: http://localhost:9999
- Game: http://localhost:9000

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
docker-compose up
```

### Changes not reflecting
If you mounted volumes and changes aren't showing:
```bash
# Restart the container
docker-compose restart
```
