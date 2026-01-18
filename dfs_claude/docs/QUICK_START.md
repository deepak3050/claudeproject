# Quick Start - Essential Commands

> **TL;DR:** Just the commands you need. Read other docs only if you have problems.

---

## Fresh Start / First Time Setup

```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude

# Start Podman machine (macOS only)
podman machine start

# Build and run
podman-compose -f podman-compose-single.yml up -d --build
```

**Access your apps:**
- Graph Visualizer: http://localhost:5000
- Tree Visualizer: http://localhost:5001
- Jupyter Notebook: http://localhost:8888
- HTML Game: http://localhost:8000
- Cheatsheet: http://localhost:8001
- Portfolio: http://localhost:8002
- AZ-204 Study Guide: http://localhost:8003

---

## When You Change Code

```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude

# Rebuild and restart
podman-compose -f podman-compose-single.yml up -d --build
```

That's it! The `--build` flag rebuilds the image with your new code.

---

## Common Commands

```bash
# Stop everything
podman-compose -f podman-compose-single.yml down

# Restart (without rebuild)
podman-compose -f podman-compose-single.yml restart

# View logs
podman logs -f dfs-claude-all-in-one

# Check what's running
podman ps
```

---

## Monthly Cleanup (Optional)

```bash
# Check for wasted space
podman images -f "dangling=true"

# Clean up if you see old images
podman image prune -f
```

---

## That's All You Need!

**Other docs are for troubleshooting only:**
- Having issues? → Read `PODMAN_README.md`
- See weird `<none>` images? → Read `UNDERSTANDING_IMAGES.md`
- Disk space problems? → Read `CLEANUP_PODMAN.md`

**For daily work, just use the commands above!** ✅
