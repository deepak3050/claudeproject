# 🐳 Docker Setup for Data Structure Visualizers

This guide helps you run the Tree and Graph Visualizer applications using Docker.

## 📋 Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)

## 🚀 Quick Start

### Option 1: Run All Services (Recommended)

```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude

# Build and start all services
docker-compose up --build
```

This starts:
- **Tree Visualizer** on http://localhost:5001
- **Graph Visualizer** on http://localhost:5000
- **Jupyter Notebook** on http://localhost:8888

### Option 2: Run Individual Services

#### Tree Visualizer Only (Beginners)
```bash
docker-compose up tree-visualizer
```
Access at: http://localhost:5001

#### Graph Visualizer Only (Advanced)
```bash
docker-compose up graph-visualizer
```
Access at: http://localhost:5000

#### Jupyter Notebook Only
```bash
docker-compose up jupyter
```
Access at: http://localhost:8888

## 📦 Available Services

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Tree Visualizer | 5001 | http://localhost:5001 | Binary tree learning app (START HERE!) |
| Graph Visualizer | 5000 | http://localhost:5000 | Graph algorithms app (Advanced) |
| Jupyter Notebook | 8888 | http://localhost:8888 | Development environment |

## 🛠️ Docker Commands

### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start specific service
docker-compose up -d tree-visualizer

# Start with live logs
docker-compose up
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop tree-visualizer
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f tree-visualizer

# Last 100 lines
docker-compose logs --tail=100 tree-visualizer
```

### Rebuild After Code Changes
```bash
# Rebuild all services
docker-compose up --build

# Rebuild specific service
docker-compose up --build tree-visualizer
```

### Check Running Containers
```bash
docker-compose ps
```

### Access Container Shell
```bash
# Tree visualizer
docker exec -it tree-visualizer bash

# Graph visualizer
docker exec -it graph-visualizer bash

# Jupyter
docker exec -it jupyter-notebook bash
```

## 📁 Volume Mounts

The Docker containers mount local directories for live development:

```yaml
volumes:
  - ./apps/python_ds:/app/apps/python_ds  # Flask apps
  - .:/app                                 # Jupyter notebooks
```

**What this means:**
- ✅ Edit code locally, changes reflect immediately
- ✅ No need to rebuild for code changes
- ✅ Files persist after container stops

## 🔧 Configuration

### Change Ports

Edit `docker-compose.yaml`:

```yaml
services:
  tree-visualizer:
    ports:
      - "5001:5001"  # Change left number (host port)
```

Example: `"8001:5001"` → Access at http://localhost:8001

### Environment Variables

Current settings in `docker-compose.yaml`:

```yaml
environment:
  - FLASK_ENV=development
  - PYTHONUNBUFFERED=1
```

**FLASK_ENV=development:**
- Auto-reload on code changes
- Detailed error messages
- Debug mode enabled

**PYTHONUNBUFFERED=1:**
- Real-time log output
- No buffering of print statements

### Production Mode

For production, change:

```yaml
environment:
  - FLASK_ENV=production
```

And update Flask apps to set `debug=False`.

## 🏗️ Build Process

The Dockerfile does the following:

1. Uses `python:3.11-slim` base image
2. Installs system tools (`net-tools`, `procps`)
3. Installs `uv` for fast package management
4. Installs Python dependencies:
   - Flask (web framework)
   - NetworkX (graph library)
   - Matplotlib (visualization)
   - Jupyter (notebooks)
   - Plotext (terminal plotting)
5. Copies application code
6. Exposes ports 5000, 5001, 8888

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `Bind for 0.0.0.0:5001 failed: port is already allocated`

**Solution 1:** Stop the local Flask app
```bash
# Find process using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>
```

**Solution 2:** Change Docker port mapping
```yaml
ports:
  - "5002:5001"  # Use port 5002 on host
```

### Container Exits Immediately

Check logs:
```bash
docker-compose logs tree-visualizer
```

Common causes:
- Missing dependencies (rebuild: `docker-compose up --build`)
- Python syntax errors in code
- Port binding issues

### Code Changes Not Reflecting

1. **For Python code:** Flask auto-reloads in development mode
2. **For dependencies:** Rebuild container
   ```bash
   docker-compose up --build tree-visualizer
   ```
3. **For templates/static files:** Restart container
   ```bash
   docker-compose restart tree-visualizer
   ```

### Can't Access from Browser

1. Check container is running:
   ```bash
   docker-compose ps
   ```

2. Check logs for errors:
   ```bash
   docker-compose logs tree-visualizer
   ```

3. Verify port mapping:
   ```bash
   docker ps
   ```

4. Test from inside container:
   ```bash
   docker exec -it tree-visualizer curl localhost:5001
   ```

### Container Uses Old Code

Force rebuild without cache:
```bash
docker-compose build --no-cache
docker-compose up
```

## 🔄 Development Workflow

### Recommended Workflow:

1. **Start containers in background:**
   ```bash
   docker-compose up -d
   ```

2. **View logs in real-time:**
   ```bash
   docker-compose logs -f tree-visualizer
   ```

3. **Edit code locally** in your IDE
   - Changes auto-reload (Flask development mode)
   - Refresh browser to see updates

4. **Stop when done:**
   ```bash
   docker-compose down
   ```

### Full Reset (Clean Slate):

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker-compose down --rmi all

# Rebuild and start
docker-compose up --build
```

## 📊 Resource Usage

Check container resource usage:
```bash
docker stats
```

Output shows:
- CPU usage
- Memory usage
- Network I/O
- Block I/O

## 🌐 Network

All services run on a shared `ds-network` bridge network:

```yaml
networks:
  ds-network:
    driver: bridge
```

**Benefits:**
- Services can communicate with each other
- Isolated from host network
- Custom DNS resolution

**Example:** Access from Jupyter to Tree Visualizer:
```python
import requests
response = requests.get('http://tree-visualizer:5001/api/tree/info')
```

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start all | `docker-compose up -d` |
| Start one | `docker-compose up tree-visualizer` |
| Stop all | `docker-compose down` |
| Rebuild | `docker-compose up --build` |
| Logs | `docker-compose logs -f` |
| Shell access | `docker exec -it tree-visualizer bash` |
| Check status | `docker-compose ps` |

## 🆘 Getting Help

### View Container Details
```bash
docker inspect tree-visualizer
```

### Check Network
```bash
docker network inspect dfs_claude_ds-network
```

### Execute Python Commands
```bash
docker exec -it tree-visualizer python -c "import flask; print(flask.__version__)"
```

## 🚀 Next Steps

Once containers are running:

1. **Beginners:** Start with Tree Visualizer → http://localhost:5001
2. **Advanced:** Try Graph Visualizer → http://localhost:5000
3. **Development:** Use Jupyter → http://localhost:8888

## 📝 Additional Notes

- **Auto-restart:** Containers restart automatically if they crash (`restart: unless-stopped`)
- **Volumes:** Code changes persist and reflect immediately
- **Logs:** Unbuffered output for real-time debugging
- **Isolation:** Each service runs in its own container

---

**Need to customize?** Edit:
- `Dockerfile` - Change base image or dependencies
- `docker-compose.yaml` - Modify ports, volumes, or services
- Flask apps - Edit directly in `apps/python_ds/`
