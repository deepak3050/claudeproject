# Running DFS Claude with Podman

This guide explains how to run the DFS Claude project using Podman instead of Docker.

> **Note**: This project uses a **single container** architecture for simplicity and efficiency. All 7 services (Tree Visualizer, Graph Visualizer, Jupyter, and 4 HTTP servers) run in one container, saving resources and simplifying management.

## Prerequisites

1. **Install Podman** - Follow [PODMAN_INSTALLATION.md](./PODMAN_INSTALLATION.md) for installation instructions
2. **Start Podman Machine** (macOS only):
   ```bash
   podman machine start
   ```

## Quick Start (Single Container - Recommended)

This project now runs all 7 services in **ONE container** for simplicity and efficiency:

```bash
# Navigate to project directory
cd /Users/deepakdas/Github3050/claude/dfs_claude

# Build and start all services in ONE container
podman-compose -f podman-compose-single.yml up --build

# Or run in detached mode (background) - RECOMMENDED
podman-compose -f podman-compose-single.yml up -d --build
```

**What runs in the single container:**
- Tree Visualizer (port 5001)
- Graph Visualizer (port 5000)
- Jupyter Notebook (port 8888)
- HTML Game (port 8000)
- Cheatsheet Viewer (port 8001)
- Portfolio (port 8002)
- AZ-204 Study Guide (port 8003)

**Resource usage**: ~300-400MB RAM total

### Alternative: Multiple Containers (Advanced)

If you need service isolation (for debugging or production), use the multi-container setup:

```bash
# Build and start all services in separate containers
podman-compose -f podman-compose.yml up -d --build
```

**Resource usage**: ~425MB+ RAM (3 separate containers with overhead)

## Common Commands (Single Container)

```bash
# Start the container
podman-compose -f podman-compose-single.yml up -d

# Stop the container
podman-compose -f podman-compose-single.yml down

# View logs (all services)
podman logs -f dfs-claude-all-in-one

# Restart the container
podman restart dfs-claude-all-in-one

# Rebuild and restart
podman-compose -f podman-compose-single.yml up -d --build

# Check resource usage
podman stats

# Check running containers
podman ps
```

---

## Manual Podman Commands (Without Compose)

If you prefer to run containers manually or podman-compose isn't available:

### 1. Build the Image

```bash
# Build the image
podman build -t dfs-claude:latest .

# Verify the image
podman images
```

### 2. Single Container Deployment (Simplest)

Run everything in one container:

```bash
# Build image
podman build -t dfs-claude:latest .

# Run all services in one container
podman run -d \
  --name dfs-claude-all \
  -p 5000:5000 \
  -p 5001:5001 \
  -p 8888:8888 \
  -p 8000:8000 \
  -p 8001:8001 \
  -p 8002:8002 \
  -p 8003:8003 \
  -v .:/app:Z \
  dfs-claude:latest \
  /bin/bash /app/start-all.sh

# View logs
podman logs -f dfs-claude-all

# Stop container
podman stop dfs-claude-all

# Remove container
podman rm dfs-claude-all
```

### 3. Multiple Container Deployment (Advanced)

For better isolation, run each service separately:

#### Create Network

```bash
# Create network for containers to communicate
podman network create ds-network
```

#### Run Individual Containers

#### Tree Visualizer (Port 5001)

```bash
podman run -d \
  --name tree-visualizer \
  --network ds-network \
  -p 5001:5001 \
  -v ./apps/python_ds:/app/apps/python_ds:Z \
  -w /app/apps/python_ds \
  -e FLASK_ENV=development \
  -e PYTHONUNBUFFERED=1 \
  dfs-claude:latest \
  python tree_app.py
```

#### Graph Visualizer (Port 5000)

```bash
podman run -d \
  --name graph-visualizer \
  --network ds-network \
  -p 5000:5000 \
  -v ./apps/python_ds:/app/apps/python_ds:Z \
  -w /app/apps/python_ds \
  -e FLASK_ENV=development \
  -e PYTHONUNBUFFERED=1 \
  dfs-claude:latest \
  python app.py
```

#### Jupyter Notebook (Port 8888 + others)

```bash
podman run -d \
  --name jupyter-notebook \
  --network ds-network \
  -p 8888:8888 \
  -p 8000:8000 \
  -p 8001:8001 \
  -p 8002:8002 \
  -p 8003:8003 \
  -v .:/app:Z \
  -e PYTHONUNBUFFERED=1 \
  dfs-claude:latest \
  jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
```

---

## Accessing Services

Once the container is running, access all services at:

| Service | URL | Description |
|---------|-----|-------------|
| **Tree Visualizer** | http://localhost:5001 | Binary tree learning app |
| **Graph Visualizer** | http://localhost:5000 | Graph algorithms app |
| **Jupyter Notebook** | http://localhost:8888 | Development environment |
| **HTML Game** | http://localhost:8000 | Interactive game |
| **Markdown Viewer** | http://localhost:8001 | Cheatsheet viewer |
| **Portfolio** | http://localhost:8002 | Portfolio website |
| **AZ-204 Guide** | http://localhost:8003 | Study guide |

All services run in **one container** (`dfs-claude-all-in-one`).

---

## Container Management Commands

### Basic Operations

```bash
# List running containers
podman ps

# Stop the container
podman stop dfs-claude-all-in-one

# Start the container
podman start dfs-claude-all-in-one

# Restart the container
podman restart dfs-claude-all-in-one

# Remove the container
podman stop dfs-claude-all-in-one
podman rm dfs-claude-all-in-one

# Remove all stopped containers
podman container prune
```

### Logs and Debugging

```bash
# View all logs (all 7 services)
podman logs -f dfs-claude-all-in-one

# View last 100 lines
podman logs --tail 100 dfs-claude-all-in-one

# Execute commands inside container
podman exec -it dfs-claude-all-in-one bash

# Check which processes are running
podman exec dfs-claude-all-in-one ps aux

# Inspect container details
podman inspect dfs-claude-all-in-one
```

### Image Management

```bash
# List images
podman images

# Remove image
podman rmi dfs-claude:latest

# Remove unused images
podman image prune

# Pull an image
podman pull python:3.11-slim
```

### Network Management

```bash
# List networks
podman network ls

# Inspect network
podman network inspect ds-network

# Remove network
podman network rm ds-network
```

### Volume Management

```bash
# List volumes
podman volume ls

# Remove unused volumes
podman volume prune

# Inspect volume
podman volume inspect <volume-name>
```

---

## Podman Pods (Alternative to Compose)

Podman supports Kubernetes-style pods. Here's how to run all services in a single pod:

### Create and Run Pod

```bash
# Create pod with all port mappings
podman pod create \
  --name dfs-pod \
  -p 5000:5000 \
  -p 5001:5001 \
  -p 8888:8888 \
  -p 8000:8000 \
  -p 8001:8001 \
  -p 8002:8002 \
  -p 8003:8003

# Run containers in the pod
podman run -d \
  --pod dfs-pod \
  --name tree-visualizer \
  -v ./apps/python_ds:/app/apps/python_ds:Z \
  -w /app/apps/python_ds \
  dfs-claude:latest \
  python tree_app.py

podman run -d \
  --pod dfs-pod \
  --name graph-visualizer \
  -v ./apps/python_ds:/app/apps/python_ds:Z \
  -w /app/apps/python_ds \
  dfs-claude:latest \
  python app.py

podman run -d \
  --pod dfs-pod \
  --name jupyter \
  -v .:/app:Z \
  dfs-claude:latest \
  jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
```

### Pod Management

```bash
# List pods
podman pod ls

# Stop pod (stops all containers)
podman pod stop dfs-pod

# Start pod
podman pod start dfs-pod

# Remove pod
podman pod rm dfs-pod

# Generate Kubernetes YAML from pod
podman generate kube dfs-pod > dfs-pod.yaml
```

---

## Systemd Integration (Linux Only)

Podman integrates with systemd for automatic container startup:

### Generate Systemd Unit File

```bash
# For a single container
podman generate systemd --new --name tree-visualizer > ~/.config/systemd/user/tree-visualizer.service

# Enable and start service
systemctl --user enable tree-visualizer.service
systemctl --user start tree-visualizer.service

# For a pod
podman generate systemd --new --name dfs-pod > ~/.config/systemd/user/dfs-pod.service
systemctl --user enable dfs-pod.service
systemctl --user start dfs-pod.service
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :5001

# Check if container is already running
podman ps

# Stop the container
podman stop dfs-claude-all-in-one
```

### Volume Permission Issues

The `:Z` flag in volume mounts handles SELinux labeling. If you encounter permission issues:

```bash
# On Linux: Check SELinux status
getenforce

# Temporarily disable (not recommended for production)
sudo setenforce 0

# Or use :Z flag in volume mounts (already configured)
-v ./apps:/app:Z
```

### Container Won't Start

```bash
# Check logs
podman logs dfs-claude-all-in-one

# Check if image exists
podman images

# Rebuild image
podman-compose -f podman-compose-single.yml build

# Restart container
podman restart dfs-claude-all-in-one

# Check Podman events
podman events --since 5m
```

### macOS: Machine Not Running

```bash
# Check machine status
podman machine list

# Start machine
podman machine start

# If issues persist, recreate machine
podman machine stop
podman machine rm
podman machine init
podman machine start
```

### Network Issues

```bash
# Recreate network
podman network rm ds-network
podman network create ds-network

# Or use host network (less isolation)
podman run --network host ...
```

---

## Performance Tips

### macOS Performance

1. **Allocate more resources to Podman machine:**
   ```bash
   podman machine stop
   podman machine rm
   podman machine init --cpus 4 --memory 8192 --disk-size 100
   podman machine start
   ```

2. **Use native filesystem (avoid volume mounts when possible)**

3. **Enable VM acceleration:**
   - Ensure Apple Hypervisor is available
   - Use latest Podman version

### Linux Performance

1. **Use rootless mode** (default) - better performance than Docker
2. **Use cgroups v2** for better resource control
3. **Configure storage driver:**
   ```bash
   # Edit /etc/containers/storage.conf
   [storage]
   driver = "overlay"
   ```

---

## Migrating from Docker

### Using Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias docker=podman
alias docker-compose=podman-compose
```

### Key Differences

- **Daemonless**: No background daemon required
- **Rootless**: Containers run as your user by default
- **SELinux**: Volume mounts need `:Z` or `:z` flag on SELinux systems
- **Networking**: Slightly different network stack, but compatible
- **Compose**: Use `podman-compose` instead of `docker-compose`

### Side-by-Side Comparison

```bash
# Docker
docker-compose up -d
docker ps
docker logs -f container-name

# Podman
podman-compose -f podman-compose.yml up -d
podman ps
podman logs -f container-name
```

---

## Cleanup

### Remove Container and Image

```bash
# Using compose (recommended)
podman-compose -f podman-compose-single.yml down

# Manual cleanup
podman stop dfs-claude-all-in-one
podman rm dfs-claude-all-in-one
podman rmi localhost/dfs_claude_dfs-claude-all:latest

# Clean up unused resources
podman volume prune
podman image prune -a
```

### Complete System Reset (macOS)

```bash
# Stop and remove machine
podman machine stop
podman machine rm

# This removes all containers, images, and volumes
```

---

## Additional Resources

- **Podman Documentation**: https://docs.podman.io/
- **Podman Compose**: https://github.com/containers/podman-compose
- **Docker to Podman Guide**: https://podman.io/getting-started/migration
- **Installation Guide**: [PODMAN_INSTALLATION.md](./PODMAN_INSTALLATION.md)
- **Original Docker Guide**: [DOCKER_README.md](./DOCKER_README.md)

---

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. View logs: `podman logs -f dfs-claude-all-in-one`
3. Check container status: `podman ps`
4. Check Podman machine status (macOS): `podman machine list`
5. Visit: https://github.com/containers/podman/discussions

## Quick Reference

```bash
# Start everything
podman-compose -f podman-compose-single.yml up -d

# Stop everything
podman-compose -f podman-compose-single.yml down

# View logs
podman logs -f dfs-claude-all-in-one

# Check status
podman ps
podman stats

# Restart
podman restart dfs-claude-all-in-one
```
