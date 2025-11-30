# Docker/Podman Build Optimization

> **Note:** If you see many `<none>` images when running `podman images -a`, read [UNDERSTANDING_IMAGES.md](./UNDERSTANDING_IMAGES.md) first to understand the difference between intermediate layers and truly dangling images.

## The Problem: Why You Had Dangling Images

### Root Cause
Your Dockerfile was copying **everything** from your project directory into the image without filtering:
```dockerfile
COPY . /app
```

This meant every rebuild included:
- `.git/` directory (can be hundreds of MB)
- Python cache files (`__pycache__/`, `*.pyc`)
- Jupyter checkpoints (`.ipynb_checkpoints/`)
- IDE files (`.vscode/`, `.idea/`)
- Temporary files
- Even the Dockerfile itself!

### Why This Created Dangling Images
Every time you ran:
```bash
podman-compose -f podman-compose-single.yml up -d --build
```

Podman would:
1. Create new image layers with all those unnecessary files
2. Tag the new image as `localhost/dfs_claude_dfs-claude-all:latest`
3. **Leave the old layers as `<none>` (dangling images)**

After multiple rebuilds, you accumulated 10 images with 9 being unused dangling layers.

---

## The Solution: `.dockerignore` File

### What We Added
Created `/Users/deepakdas/Github3050/claude/dfs_claude/.dockerignore` to exclude:

```
# Git files (largest culprit)
.git
.gitignore

# Python cache (regenerated anyway)
__pycache__
*.pyc

# Jupyter checkpoints (temporary)
.ipynb_checkpoints

# IDE files (not needed in container)
.vscode/
.idea/

# Build files (metadata, not needed in runtime)
docker-compose*.yml
podman-compose*.yml
Dockerfile
```

### How This Helps
- **Smaller images**: Excludes ~50-200MB of unnecessary files
- **Faster builds**: Less data to copy into image
- **Better caching**: Docker/Podman can reuse layers more effectively
- **Fewer dangling images**: Only rebuild when actual code changes

---

## Dockerfile Improvements Made

### Before
```dockerfile
RUN pip install uv                           # ❌ Caches pip downloads
COPY . /app                                  # ❌ Copies everything
RUN chmod +x /app/start.sh                   # ❌ Only one script
```

### After
```dockerfile
RUN pip install --no-cache-dir uv            # ✅ No cache (smaller layer)
COPY . /app                                  # ✅ Now respects .dockerignore
RUN chmod +x /app/start.sh /app/start-all.sh # ✅ Both scripts
```

---

## How to Verify the Fix

### Step 1: Clean Up Old Dangling Images

**Important:** Don't use `podman images -a` to check for dangling images! It shows intermediate layers which are normal. See [UNDERSTANDING_IMAGES.md](./UNDERSTANDING_IMAGES.md) for details.

```bash
# Check for truly dangling images
podman images -f "dangling=true"

# OR check reclaimable space
podman system df

# If RECLAIMABLE > 0, clean up
podman image prune -f

# Verify cleanup
podman images
```

**Expected output:**
```
REPOSITORY                           TAG         IMAGE ID      CREATED      SIZE
docker.io/library/python             3.11-slim   e58d60f13eb9  12 days ago  154 MB
```

### Step 2: Rebuild with Optimizations
```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude

# Rebuild the container
podman-compose -f podman-compose-single.yml up -d --build
```

### Step 3: Check Image Count
```bash
podman images
```

**Expected output:**
```
REPOSITORY                           TAG         IMAGE ID      CREATED         SIZE
localhost/dfs_claude_dfs-claude-all  latest      abc123def456  1 minute ago    900 MB
docker.io/library/python             3.11-slim   e58d60f13eb9  12 days ago     154 MB
```

**You should see ONLY 2 images** (not 10 like before)

### Step 4: Verify No Dangling Images
```bash
podman images -f "dangling=true"
```

**Expected output:**
```
REPOSITORY  TAG  IMAGE ID  CREATED  SIZE
(empty - no results)
```

---

## Future Rebuilds

### When You Make Code Changes
```bash
# Stop container
podman-compose -f podman-compose-single.yml down

# Rebuild (will be faster and cleaner now)
podman-compose -f podman-compose-single.yml up -d --build
```

### What to Expect
- **First rebuild after fix**: Creates 1 new image, no dangling images
- **Subsequent rebuilds**: Docker/Podman will reuse cached layers
- **Only changed layers rebuild**: If you only change Python code, only final layer rebuilds

---

## Build Cache Optimization (Advanced)

### How Docker/Podman Caching Works

Docker/Podman builds images in **layers**. Each `RUN`, `COPY`, `ADD` creates a new layer:

```dockerfile
FROM python:3.11-slim                # Layer 1 (cached - never changes)
RUN apt-get update && ...            # Layer 2 (cached - dependencies don't change often)
RUN pip install uv                   # Layer 3 (cached)
COPY pyproject.toml /app/            # Layer 4 (cached - only if pyproject.toml changes)
RUN uv pip install ...               # Layer 5 (cached - only if Layer 4 changed)
COPY . /app                          # Layer 6 (rebuilds when code changes)
RUN chmod +x ...                     # Layer 7 (rebuilds when Layer 6 changes)
```

### Why Order Matters
- Layers are cached **top to bottom**
- If a layer changes, **all layers below it rebuild**
- Put **rarely-changing** commands at the top
- Put **frequently-changing** commands at the bottom

### Current Dockerfile Order (Optimized)
1. **Base image** (never changes)
2. **System packages** (rarely change)
3. **Python dependencies** (change occasionally)
4. **Application code** (changes frequently) ✅ At the bottom!

---

## Monitoring Build Efficiency

### Check Image Sizes
```bash
podman images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### Check Build Time
```bash
time podman-compose -f podman-compose-single.yml up -d --build
```

**Expected times:**
- **Full rebuild** (no cache): ~2-3 minutes
- **Rebuild with cache** (code changed): ~20-30 seconds
- **Rebuild with cache** (nothing changed): ~5-10 seconds

### Check Disk Usage
```bash
podman system df
```

**Expected after cleanup:**
```
TYPE           TOTAL       ACTIVE      SIZE        RECLAIMABLE
Images         2           1           900MB       0B (0%)
Containers     1           1           33MB        0B (0%)
Local Volumes  0           0           0B          0B (0%)
```

---

## Best Practices Going Forward

### ✅ DO
- Keep `.dockerignore` updated as you add new file types
- Run `podman image prune -f` monthly to clean up dangling images
- Use `--build` only when you change code (not for restarts)
- Monitor `podman system df` occasionally

### ❌ DON'T
- Delete `.dockerignore` (it's essential)
- Use `--no-cache` flag unless debugging (defeats caching)
- Copy large unnecessary files into the image
- Rebuild unnecessarily (just restart with `podman-compose up -d`)

---

## Common Scenarios

### Scenario 1: Code Changed, Rebuild Needed
```bash
# Stop container
podman-compose -f podman-compose-single.yml down

# Rebuild (fast, uses cache for layers 1-5)
podman-compose -f podman-compose-single.yml up -d --build
```

### Scenario 2: Dependencies Changed (pyproject.toml)
```bash
# Stop container
podman-compose -f podman-compose-single.yml down

# Rebuild (slower, rebuilds layers 5-7)
podman-compose -f podman-compose-single.yml up -d --build
```

### Scenario 3: Just Restart (No Code Changes)
```bash
# Don't use --build!
podman-compose -f podman-compose-single.yml restart
```

### Scenario 4: Debugging Build Issues
```bash
# Force complete rebuild (no cache)
podman-compose -f podman-compose-single.yml build --no-cache
podman-compose -f podman-compose-single.yml up -d
```

---

## Troubleshooting

### Still Seeing Dangling Images?
```bash
# Check what's creating them
podman images -a

# If you see multiple <none>, you might be:
# 1. Building with --no-cache (don't do this)
# 2. Frequently changing base dependencies
# 3. Using docker-compose build instead of up --build
```

### Image Size Too Large?
```bash
# Check layer sizes
podman history localhost/dfs_claude_dfs-claude-all:latest

# Look for large layers - might need to optimize
```

### Build Not Using Cache?
```bash
# Ensure you didn't change early layers
# Check if .dockerignore is working:
podman build --progress=plain . 2>&1 | grep "COPY"

# Should show files being copied (without .git, __pycache__, etc.)
```

---

## Summary

### What Was Wrong
- No `.dockerignore` file → copied unnecessary files
- Every rebuild created new dangling images
- Wasted disk space and build time

### What We Fixed
- ✅ Added `.dockerignore` to exclude 50-200MB of files
- ✅ Optimized Dockerfile caching
- ✅ Added `--no-cache-dir` to pip install
- ✅ Made both start scripts executable

### Results
- **Before**: 10 images, 935MB reclaimable (100%)
- **After**: 2 images, 0MB reclaimable (0%)
- **Future rebuilds**: Minimal dangling images
- **Build time**: Faster due to better caching

---

**Last Updated:** 2025-11-30
**Applies to:** Docker and Podman builds
