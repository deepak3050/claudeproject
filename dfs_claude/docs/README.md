# Documentation Guide

## 📚 Documentation Overview

### ⭐ Start Here (Essential)

**[QUICK_START.md](QUICK_START.md)** - The only doc you need for daily work
- Fresh start commands
- Rebuild after code changes
- Common operations
- Monthly cleanup

**Use this for:** Building, rebuilding, and running the project

---

## 📖 Reference Docs (Read When Needed)

### Setup & Installation

- **[PODMAN_README.md](PODMAN_README.md)** - Complete Podman usage guide
- **[PODMAN_INSTALLATION.md](PODMAN_INSTALLATION.md)** - Installing Podman
- **[DOCKER_README.md](DOCKER_README.md)** - Docker alternative

**Use these when:** Setting up for the first time or switching tools

---

### Troubleshooting

- **[UNDERSTANDING_IMAGES.md](UNDERSTANDING_IMAGES.md)** ⚠️ Read if you see many `<none>` images
  - Explains intermediate layers vs dangling images
  - Why `podman images -a` looks scary (but is normal)
  - How to identify real waste

- **[BUILD_OPTIMIZATION.md](BUILD_OPTIMIZATION.md)** - Why we created `.dockerignore`
  - Build performance improvements
  - Layer caching explained
  - Prevention strategies

- **[CLEANUP_PODMAN.md](CLEANUP_PODMAN.md)** - Disk space management on macOS
  - Podman VM disk behavior
  - Machine reset instructions
  - Reclaiming disk space

**Use these when:** You have problems or see unexpected behavior

---

### Other

- **[DEVICE_TRACKING.md](DEVICE_TRACKING.md)** - Device tracking implementation
- **[sliding_cheatsheet.md](sliding_cheatsheet.md)** - Algorithm cheatsheet

---

## 🎯 Quick Decision Tree

```
What do you want to do?

├─ Run the project
│  └─ Use: QUICK_START.md ✅
│
├─ See `<none>` images when running `podman images -a`
│  └─ Read: UNDERSTANDING_IMAGES.md
│
├─ Build is slow or creates dangling images
│  └─ Read: BUILD_OPTIMIZATION.md
│
├─ Running out of disk space
│  └─ Read: CLEANUP_PODMAN.md
│
└─ First time setup
   └─ Read: PODMAN_README.md or DOCKER_README.md
```

---

## 📝 Documentation Summary

| Doc | Lines | Purpose | When to Read |
|-----|-------|---------|--------------|
| **QUICK_START.md** | ~70 | Essential commands | **Always - start here!** |
| UNDERSTANDING_IMAGES.md | ~450 | Image layers explained | When confused about `<none>` images |
| BUILD_OPTIMIZATION.md | ~330 | Build improvements | When builds create dangling images |
| CLEANUP_PODMAN.md | ~490 | Disk management | When running low on disk space |
| PODMAN_README.md | ~590 | Complete Podman guide | First time setup |
| PODMAN_INSTALLATION.md | ~300 | Install instructions | Installing Podman |
| DOCKER_README.md | ~390 | Docker alternative | Using Docker instead |

---

## 💡 Pro Tips

1. **For daily work:** Only read `QUICK_START.md`
2. **Having issues?** Find the specific doc in the decision tree above
3. **Don't read everything!** These docs are for reference, not cover-to-cover reading
4. **Bookmark:** `QUICK_START.md` - you'll use it the most

---

**Most Important:** You don't need to read all docs! Just use `QUICK_START.md` for normal work, and reference others only when you hit a specific problem. ✅
