# DFS Claude - Sliding Window Learning Suite

A Docker-based learning environment for mastering the sliding window algorithm pattern.

## Quick Start

```bash
docker-compose build && docker-compose up
```

## Services

| Port | Service | Description |
|------|---------|-------------|
| 8000 | [Game](http://localhost:8000) | Interactive Sliding Window Explorer |
| 8001 | [Cheatsheet](http://localhost:8001) | Visual algorithm cheatsheet |
| 8002 | [Portfolio](http://localhost:8002) | Portfolio website |
| 8003 | [AZ-204](http://localhost:8003) | Azure study guide |
| 8888 | [Jupyter](http://localhost:8888) | Notebook environment |

## Project Structure

```
dfs_claude/
├── apps/
│   ├── game/          # Interactive sliding window game (port 8000)
│   ├── cheatsheet/    # HTML cheatsheet (port 8001)
│   ├── portfolio/     # Portfolio website (port 8002)
│   └── az204/         # Azure AZ-204 study guide (port 8003)
├── notebooks/         # Jupyter notebooks
├── docs/              # Documentation
├── resume/            # Resume files
├── Dockerfile
├── docker-compose.yml
└── start.sh
```

## Features

- **Interactive Game**: Step through sliding window algorithms with visual feedback
- **Cheatsheet**: Quick reference with code templates for all patterns
- **Jupyter Notebooks**: Deep-dive tutorials and practice problems
