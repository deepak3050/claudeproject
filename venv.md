# Virtual Environment Management Guide

## Overview

This repository uses a **single shared UV virtual environment** managed by a consolidated `pyproject.toml` file. This approach provides automatic dependency management using `uv sync` and eliminates the need for manual package installations.

## Architecture

### Shared Virtual Environment Location
```
/Users/deepakdas/Github3050/claude/.venv/
```

**Size**: ~333MB
**Python Version**: 3.11.6
**Total Packages**: 138 packages
**Management**: Automated via `uv sync`

### Project Structure

```
/Users/deepakdas/Github3050/claude/
├── .venv/                     # ← Actual virtual environment (333MB)
├── pyproject.toml             # ← Single source of truth for dependencies
├── uv.lock                    # ← Lock file for reproducible builds
├── cli_project/
│   └── .venv → ../.venv       # Symlink to shared venv
├── dfs_claude/
│   └── .venv → ../.venv       # Symlink to shared venv
├── mathematics/
│   └── .venv → ../.venv       # Symlink to shared venv
└── venv.md                    # This file
```

### How It Works

1. **Single pyproject.toml**: All dependencies are defined in one file at the repository root
2. **Symlinks**: Each project has a `.venv` symlink pointing to the shared `../.venv`
3. **uv sync**: Automatically installs/updates all dependencies and creates `uv.lock`
4. **Lock file**: `uv.lock` ensures reproducible builds across machines

## Dependencies

All dependencies are consolidated in `/Users/deepakdas/Github3050/claude/pyproject.toml`:

```toml
[project]
dependencies = [
    # CLI Project dependencies
    "anthropic>=0.51.0",
    "mcp[cli]>=1.8.0",
    "prompt-toolkit>=3.0.51",
    "python-dotenv>=1.1.0",

    # DFS Claude dependencies
    "networkx",
    "matplotlib",
    "ipywidgets",
    "numpy",
    "jupyter",
    "plotext",
    "flask",
]
```

## Adding New Packages

### The Simple Way (Recommended)

**Step 1**: Edit the root `pyproject.toml`

```bash
cd /Users/deepakdas/Github3050/claude
# Edit pyproject.toml and add your package to dependencies
```

Example - adding `requests`:
```toml
[project]
dependencies = [
    "anthropic>=0.51.0",
    "mcp[cli]>=1.8.0",
    # ... other packages ...
    "requests>=2.31.0",  # ← Add this
]
```

**Step 2**: Run `uv sync`

```bash
uv sync
```

That's it! ✅ `uv sync` will:
- Install the new package
- Update `uv.lock` with the exact version
- Make it available to all projects

### Quick Add (Without Editing pyproject.toml First)

```bash
# Add package and automatically update pyproject.toml
uv add requests

# Or with version constraint
uv add "requests>=2.31.0"
```

This will:
1. Add the package to `pyproject.toml`
2. Install it
3. Update `uv.lock`

### Removing Packages

```bash
# Remove from pyproject.toml and uninstall
uv remove requests
```

## Activating the Environment

From **any** project directory:

```bash
# From repository root
cd /Users/deepakdas/Github3050/claude
source .venv/bin/activate

# Or from any subdirectory (via symlink)
cd cli_project && source .venv/bin/activate
cd dfs_claude && source .venv/bin/activate
cd mathematics && source .venv/bin/activate
```

All activate the **same environment** thanks to symlinks!

## Syncing Dependencies

### Initial Setup (New Machine/Clone)

```bash
cd /Users/deepakdas/Github3050/claude
uv sync
```

This reads `uv.lock` and installs the exact same package versions, ensuring consistency.

### After Pulling Changes

If someone else updated `pyproject.toml` or `uv.lock`:

```bash
git pull
uv sync
```

### Updating All Packages

```bash
# Update to latest compatible versions
uv sync --upgrade
```

This respects version constraints in `pyproject.toml` but upgrades to newest compatible versions.

## Checking Installed Packages

```bash
source .venv/bin/activate

# List all packages
uv pip list

# Check for dependency conflicts
uv pip check

# Show dependency tree
uv pip tree
```

## Understanding uv.lock

The `uv.lock` file:
- **Auto-generated** by `uv sync`
- **Should be committed** to git
- **Pins exact versions** for reproducibility
- **Cross-platform** - works on macOS, Linux, Windows

**Do NOT** edit `uv.lock` manually. It's managed by UV.

## Development Workflow

### Daily Work

```bash
# Activate environment
source .venv/bin/activate

# Work on your code
cd cli_project
python your_script.py

# No need to install packages manually!
```

### Adding Dependencies

```bash
# Option 1: Quick add
uv add pandas

# Option 2: Edit pyproject.toml then sync
# Edit pyproject.toml to add "pandas"
uv sync
```

### Updating Dependencies

```bash
# Update specific package
uv add --upgrade pandas

# Update all packages
uv sync --upgrade
```

## Best Practices

### ✅ Do:

1. **Always use `uv sync`** after:
   - Cloning the repository
   - Pulling changes
   - Editing `pyproject.toml`

2. **Commit both files** to git:
   ```bash
   git add pyproject.toml uv.lock
   git commit -m "Add pandas dependency"
   ```

3. **Use `uv add`** to add packages (it updates both `pyproject.toml` and installs)

4. **Check for conflicts**:
   ```bash
   uv pip check
   ```

5. **Keep dependencies organized** in `pyproject.toml` with comments:
   ```toml
   dependencies = [
       # CLI tools
       "anthropic>=0.51.0",
       "mcp[cli]>=1.8.0",

       # Data science
       "numpy",
       "pandas",
   ]
   ```

### ❌ Don't:

1. **Don't use `pip install`** - use `uv add` or edit `pyproject.toml` + `uv sync`
2. **Don't edit `uv.lock`** manually
3. **Don't delete `.venv`** unless you know what you're doing
4. **Don't create separate venvs** in subdirectories (defeats the purpose)
5. **Don't install packages without updating `pyproject.toml`**

## Handling Version Conflicts

### If Conflicts Arise

**Symptom**: `uv sync` fails due to incompatible version requirements

**Example**:
```
One project needs pandas>=2.0
Another needs pandas<2.0
```

**Solutions**:

1. **Reconcile versions** (preferred):
   - Update code to work with a single version range
   - Choose: `"pandas>=1.5,<3.0"` if compatible

2. **Separate the conflicting project**:
   ```bash
   cd cli_project
   rm .venv  # Remove symlink
   uv venv .venv-local --python 3.11
   source .venv-local/bin/activate
   # Create a separate pyproject.toml for this project
   ```

### Checking for Conflicts

```bash
source .venv/bin/activate
uv pip check
```

Output should be:
```
No broken requirements found.
```

## Advanced: Development Dependencies

For packages only needed during development (linters, formatters, etc.):

```toml
[project]
dependencies = [
    # Production dependencies
    "anthropic>=0.51.0",
]

[dependency-groups]
dev = [
    "pytest",
    "black",
    "ruff",
]
```

Install dev dependencies:
```bash
uv sync --group dev
```

Or install without dev:
```bash
uv sync --no-dev
```

## Troubleshooting

### "Module not found" error

```bash
# Verify environment is activated
which python
# Should show: /Users/deepakdas/Github3050/claude/.venv/bin/python

# If not, activate it
source .venv/bin/activate

# Reinstall all dependencies
uv sync
```

### Symlink broken

```bash
cd <project-directory>
rm .venv
ln -s ../.venv .venv
```

### Clean rebuild

```bash
cd /Users/deepakdas/Github3050/claude

# Remove environment
rm -rf .venv

# Recreate from lock file
uv sync

# Recreate symlinks if needed
cd cli_project && ln -s ../.venv .venv
cd ../dfs_claude && ln -s ../.venv .venv
cd ../mathematics && ln -s ../.venv .venv
```

### Completely fresh start

```bash
cd /Users/deepakdas/Github3050/claude

# Remove everything
rm -rf .venv uv.lock

# Rebuild from pyproject.toml
uv sync

# This will create new uv.lock with latest compatible versions
```

## Migration History

### What Changed (Dec 25, 2024)

**Before**:
- 3 separate `pyproject.toml` files (one per project)
- Manual `uv pip install` commands
- `.venv-shared` directory name

**After**:
- 1 consolidated `pyproject.toml` at repository root
- Automated `uv sync` workflow
- Standard `.venv` directory name
- `uv.lock` for reproducible builds

**Files Removed**:
- `cli_project/pyproject.toml`
- `dfs_claude/pyproject.toml`
- `mathematics/pyproject.toml`
- All `uv.lock` files from subdirectories
- `.python-version` files

**Files Created**:
- `/Users/deepakdas/Github3050/claude/pyproject.toml`
- `/Users/deepakdas/Github3050/claude/uv.lock`

## Quick Reference

| Task | Command |
|------|---------|
| Install all dependencies | `uv sync` |
| Add new package | `uv add package-name` |
| Remove package | `uv remove package-name` |
| Update all packages | `uv sync --upgrade` |
| Activate environment | `source .venv/bin/activate` |
| List installed packages | `uv pip list` |
| Check for conflicts | `uv pip check` |
| Show dependency tree | `uv pip tree` |
| Deactivate | `deactivate` |

## Comparison: Old vs New Workflow

### Old Workflow (Manual)
```bash
# Add a package
source .venv-shared/bin/activate
uv pip install requests
# Manually edit pyproject.toml
# Hope you remembered the version
```

### New Workflow (Automated)
```bash
# Add a package - one command does everything
uv add requests
# ✅ Installs package
# ✅ Updates pyproject.toml
# ✅ Updates uv.lock
```

## Benefits

✅ **Single source of truth**: `pyproject.toml` defines all dependencies
✅ **Automatic updates**: `uv sync` handles everything
✅ **Reproducible**: `uv.lock` ensures same versions everywhere
✅ **Space efficient**: One venv for all projects (~333MB vs ~999MB)
✅ **Simple workflow**: `uv add` / `uv remove` / `uv sync`
✅ **Cross-platform**: Works on macOS, Linux, Windows
✅ **Git-friendly**: Small lock file, easy diffs

---

**Last Updated**: December 25, 2024
**Python Version**: 3.11.6
**UV Management**: Automated via `uv sync`
**Total Packages**: 138
