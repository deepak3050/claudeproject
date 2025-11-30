# Podman Disk Space Cleanup Guide

This guide helps you understand and reclaim disk space used by Podman on macOS.

## Understanding the Problem

### Why Podman Uses More Disk Than Expected

On macOS, Podman runs in a lightweight Linux VM using a **RAW disk file**:

```
Your Mac Storage:
├── ~/.local/share/containers/podman/machine/
│   └── applehv/
│       └── podman-machine-default-arm64.raw  (e.g., 15GB on disk)
│
└── Inside the VM:
    └── Actually used: ~5GB (containers + images)
    └── Wasted space: ~10GB (freed but not released to macOS)
```

**The Issue:**
- RAW disk format **grows automatically** when you add data
- RAW disk format **DOES NOT shrink** when you delete data
- When you delete containers/images, space is freed *inside* the VM
- But the disk file on your Mac stays the same size

### Check Your Current Usage

```bash
# Check disk file size on macOS (what you see in Finder)
du -sh ~/.local/share/containers/podman/machine/

# Check actual usage inside the VM
podman machine ssh podman-machine-default "df -h /"

# Check Podman resources
podman system df
```

**Example output:**
```
macOS disk usage:     15GB  (the .raw file)
Inside VM usage:      5GB   (actual data)
Wasted space:         10GB  (can be reclaimed)
```

---

## Solution 1: Check and Prune (First Try This)

Before resetting the machine, try aggressive cleanup:

### Step 1: Check Current State

```bash
# Check what's using space
podman system df

# List all images
podman images

# List all containers
podman ps -a
```

### Step 2: Aggressive Cleanup

```bash
# Remove all unused images (keeps only running container's image)
podman image prune -a -f

# Remove stopped containers
podman container prune -f

# Remove unused volumes
podman volume prune -f

# Remove unused networks
podman network prune -f

# Check space reclaimed
podman system df
```

### Step 3: Verify Results

```bash
# Check disk usage inside VM
podman machine ssh podman-machine-default "df -h /"

# Check macOS disk file size (won't change, but good to know)
du -sh ~/.local/share/containers/podman/machine/
```

**Expected Result:**
- Inside VM: Should show less usage
- macOS file: Will NOT shrink (this is the problem)

---

## Solution 2: Reset Podman Machine (Reclaim Disk Space)

This is the **ONLY way** to reclaim disk space on macOS with Podman.

### ⚠️ Warning

This will:
- ✅ Reclaim all wasted disk space
- ❌ Delete all containers (you'll need to rebuild)
- ❌ Delete all images (you'll need to re-download)
- ❌ Delete all volumes (backup any important data first)

### Quick Reset Script

```bash
#!/bin/bash
# Save as reset-podman.sh

echo "=== Podman Machine Reset ==="
echo ""
echo "Current disk usage:"
du -sh ~/.local/share/containers/podman/machine/
echo ""

read -p "This will DELETE all containers and images. Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1/5: Stopping containers..."
podman stop $(podman ps -aq) 2>/dev/null || echo "No containers to stop"

echo "Step 2/5: Stopping Podman machine..."
podman machine stop

echo "Step 3/5: Removing Podman machine..."
podman machine rm -f podman-machine-default

echo "Step 4/5: Creating new Podman machine..."
# Adjust these values based on your Mac's resources
podman machine init --cpus 2 --memory 4096 --disk-size 50

echo "Step 5/5: Starting Podman machine..."
podman machine start

echo ""
echo "✅ Done! Disk space reclaimed."
echo ""
echo "New disk usage:"
du -sh ~/.local/share/containers/podman/machine/
echo ""
echo "Next steps:"
echo "1. Navigate to your project: cd /Users/deepakdas/Github3050/claude/dfs_claude"
echo "2. Rebuild container: podman-compose -f podman-compose-single.yml up -d --build"
```

### Manual Step-by-Step Reset

```bash
# 1. Check current disk usage
du -sh ~/.local/share/containers/podman/machine/

# 2. Stop running containers
podman stop dfs-claude-all-in-one

# 3. Stop Podman machine
podman machine stop

# 4. Remove Podman machine (this deletes the 15GB file)
podman machine rm -f podman-machine-default

# 5. Create new machine with smaller disk limit
# For your use case, 50GB is plenty (starts at ~2GB)
podman machine init --cpus 2 --memory 4096 --disk-size 50

# 6. Start the new machine
podman machine start

# 7. Verify new disk usage (should be ~1-2GB)
du -sh ~/.local/share/containers/podman/machine/

# 8. Rebuild your container
cd /Users/deepakdas/Github3050/claude/dfs_claude
podman-compose -f podman-compose-single.yml up -d --build

# 9. Check final disk usage (should be ~3-5GB total)
du -sh ~/.local/share/containers/podman/machine/
```

### Resource Configuration Options

Choose based on your Mac's specs:

```bash
# Minimal (saves most disk/RAM)
podman machine init --cpus 1 --memory 2048 --disk-size 30

# Recommended for most Macs (8GB RAM, 4+ cores)
podman machine init --cpus 2 --memory 4096 --disk-size 50

# Performance (16GB+ RAM, 8+ cores)
podman machine init --cpus 4 --memory 8192 --disk-size 100
```

---

## Solution 3: Prevent Future Bloat

### Best Practices

1. **Regular Cleanup**
   ```bash
   # Run weekly
   podman image prune -a -f
   podman container prune -f
   podman volume prune -f
   ```

2. **Use Smaller Disk Limit**
   ```bash
   # When creating machine, use smaller limit
   podman machine init --disk-size 50  # instead of 100
   ```

3. **Monitor Disk Usage**
   ```bash
   # Check regularly
   podman system df
   du -sh ~/.local/share/containers/podman/machine/
   ```

4. **Don't Build Multiple Large Images**
   - Use single container architecture (already done!)
   - Clean up old images immediately after testing
   - Use `--no-cache` only when necessary

### Automated Cleanup Script

```bash
#!/bin/bash
# Save as: cleanup-podman.sh
# Run weekly: chmod +x cleanup-podman.sh && ./cleanup-podman.sh

echo "=== Podman Cleanup ==="
echo ""

echo "Before cleanup:"
podman system df
echo ""

echo "Removing unused images..."
podman image prune -a -f

echo "Removing stopped containers..."
podman container prune -f

echo "Removing unused volumes..."
podman volume prune -f

echo "Removing unused networks..."
podman network prune -f

echo ""
echo "After cleanup:"
podman system df
echo ""

echo "macOS disk usage:"
du -sh ~/.local/share/containers/podman/machine/
echo ""

echo "Inside VM usage:"
podman machine ssh podman-machine-default "df -h /" | grep "/$"
```

---

## Understanding Disk Usage

### How to Read Disk Usage

```bash
# Command
podman system df

# Output
TYPE           TOTAL       ACTIVE      SIZE        RECLAIMABLE
Images         10          1           935.1MB     935.1MB (100%)
Containers     1           1           33.21MB     0B (0%)
Local Volumes  0           0           0B          0B (0%)
```

**Explanation:**
- **Images TOTAL**: Total number of images (10)
- **Images ACTIVE**: Images being used by running containers (1)
- **SIZE**: Total disk space used (935MB)
- **RECLAIMABLE**: Space you can free by pruning (935MB = unused images)

### What Takes Space

| Item | Typical Size | Notes |
|------|-------------|-------|
| **Base Python image** | ~150MB | python:3.11-slim |
| **Your built image** | ~900MB | Base + dependencies |
| **Running container** | ~30-50MB | Container overhead |
| **Stopped containers** | ~30MB each | Delete if not needed |
| **Old image layers** | Varies | Prune regularly |
| **VM overhead** | ~1-2GB | OS, cache, logs |

---

## Comparison: Before vs After Reset

### Before Reset (Bloated)
```
macOS disk file:     15GB
Inside VM (used):    5GB
Wasted space:        10GB
Images:              10 (9 unused)
Containers:          1 running + stopped containers
```

### After Reset (Clean)
```
macOS disk file:     3-5GB
Inside VM (used):    3-5GB
Wasted space:        0GB
Images:              2 (python base + your image)
Containers:          1 running
```

**Disk space saved:** ~10-12GB

---

## Troubleshooting

### Reset Failed - Machine Won't Delete

```bash
# Force stop
podman machine stop -f

# Force remove
podman machine rm -f podman-machine-default

# If still stuck, manually delete
rm -rf ~/.local/share/containers/podman/machine/applehv/podman-machine-default*
rm -rf ~/.config/containers/podman/machine/applehv/podman-machine-default*

# Then recreate
podman machine init
podman machine start
```

### After Reset, Container Won't Build

```bash
# Ensure machine is running
podman machine list

# Start if needed
podman machine start

# Clean rebuild
cd /Users/deepakdas/Github3050/claude/dfs_claude
podman-compose -f podman-compose-single.yml down
podman-compose -f podman-compose-single.yml up -d --build
```

### Check What's Using Space Inside VM

```bash
# SSH into VM
podman machine ssh podman-machine-default

# Check disk usage
df -h

# Find large directories
du -sh /var/lib/containers/* | sort -h

# Exit VM
exit
```

---

## Alternative: Switch to Docker Desktop

If Podman's disk management is too frustrating:

### Docker Desktop Advantages
- ✅ Built-in "Reclaim Space" button (GUI)
- ✅ Automatic disk compaction
- ✅ Better macOS integration
- ✅ Resource limits in GUI

### Install Docker Desktop
```bash
# Using Homebrew
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

### Migrate from Podman to Docker
```bash
# Stop Podman
podman-compose -f podman-compose-single.yml down
podman machine stop

# Use Docker instead (same commands, just replace 'podman' with 'docker')
docker-compose -f docker-compose-single.yml up -d --build
```

---

## FAQ

### Q: Why doesn't Podman auto-compact like Docker Desktop?
**A:** Podman uses RAW disk format on macOS for performance. Docker Desktop uses QCOW2 with compaction support. It's a trade-off: Podman is faster but doesn't compact.

### Q: Can I compact without resetting?
**A:** Not easily on macOS. The RAW format doesn't support compaction. You'd need to:
1. Export all data
2. Delete machine
3. Create new machine
4. Import data back

Resetting is simpler.

### Q: How often should I reset?
**A:** Only when disk usage becomes a problem. With single container architecture, you shouldn't need to reset often (maybe once every 6-12 months).

### Q: Will I lose my code/data?
**A:** No! Your code is in `/Users/deepakdas/Github3050/claude/dfs_claude/` on your Mac, not in the VM. Only containers/images are deleted.

### Q: What's the minimum disk size I should use?
**A:** For this project:
- **Minimal:** 30GB (tight but works)
- **Recommended:** 50GB (comfortable)
- **Safe:** 100GB (never worry)

---

## Quick Reference

```bash
# Check disk usage
du -sh ~/.local/share/containers/podman/machine/
podman system df

# Cleanup
podman image prune -a -f
podman container prune -f
podman volume prune -f

# Reset machine (reclaim space)
podman machine stop
podman machine rm -f podman-machine-default
podman machine init --cpus 2 --memory 4096 --disk-size 50
podman machine start

# Rebuild container
cd /Users/deepakdas/Github3050/claude/dfs_claude
podman-compose -f podman-compose-single.yml up -d --build
```

---

## Resources

- **Podman Machine Docs**: https://docs.podman.io/en/latest/markdown/podman-machine.1.html
- **Podman System Docs**: https://docs.podman.io/en/latest/markdown/podman-system.1.html
- **Issue Tracker**: https://github.com/containers/podman/issues
- **Alternative (Docker)**: https://www.docker.com/products/docker-desktop

---

**Last Updated:** 2025-11-30
**Applies to:** Podman 4.0+ on macOS (Apple Silicon & Intel)
