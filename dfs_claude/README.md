# DFS Claude - Data Structures & Algorithms Learning Suite

A containerized learning environment featuring tree/graph visualizers, Jupyter notebooks, and multiple web applications.

## Quick Start

### Using Docker (Traditional)
```bash
docker-compose -f docker-compose-single.yml up -d
```

### Using Podman (Recommended - Lightweight & Rootless)
```bash
podman-compose -f podman-compose-single.yml up -d
```

See [docs/DOCKER_README.md](docs/DOCKER_README.md) or [docs/PODMAN_README.md](docs/PODMAN_README.md) for detailed instructions.

## Services

All services run in a **single container** for efficiency:

| Port | Service | Description |
|------|---------|-------------|
| 5000 | [Graph Visualizer](http://localhost:5000) | Advanced graph algorithms explorer |
| 5001 | [Tree Visualizer](http://localhost:5001) | Binary tree learning app |
| 8000 | [HTML Game](http://localhost:8000) | Interactive game |
| 8001 | [Cheatsheet](http://localhost:8001) | Algorithm cheatsheet viewer |
| 8002 | [Portfolio](http://localhost:8002) | Portfolio website |
| 8003 | [AZ-204](http://localhost:8003) | Azure study guide |
| 8888 | [Jupyter](http://localhost:8888) | Notebook environment |

## Project Structure

```
dfs_claude/
├── apps/
│   ├── python_ds/       # Flask apps (tree & graph visualizers)
│   ├── game/            # Interactive game (port 8000)
│   ├── cheatsheet/      # Algorithm cheatsheet (port 8001)
│   ├── portfolio/       # Portfolio website (port 8002)
│   └── az204/           # Azure AZ-204 study guide (port 8003)
├── notebooks/           # Jupyter notebooks
├── docs/                # Documentation
│   ├── PODMAN_INSTALLATION.md
│   ├── PODMAN_README.md
│   └── DOCKER_README.md
├── Dockerfile
├── docker-compose-single.yml  # Single container (recommended)
├── podman-compose-single.yml  # Single container (Podman)
├── docker-compose.yml          # Multi-container (optional)
├── podman-compose.yml          # Multi-container (Podman)
└── start.sh                    # Startup script for all services
```

## Features

- **Tree Visualizer**: Interactive binary tree learning with step-by-step traversals
- **Graph Visualizer**: Advanced graph algorithms (DFS, BFS, Dijkstra, etc.)
- **Jupyter Notebooks**: Deep-dive tutorials and practice problems
- **Single Container**: Efficient resource usage (~300-400MB RAM)
- **Podman Support**: Daemonless, rootless container runtime
