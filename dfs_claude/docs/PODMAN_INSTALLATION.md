# Podman Installation Guide

## What is Podman?

Podman is a daemonless container engine for developing, managing, and running OCI Containers on your Linux system. Unlike Docker, Podman doesn't require a daemon running in the background and runs containers with your user privileges (rootless by default).

**Key advantages of Podman:**
- ✅ Daemonless architecture (no background daemon required)
- ✅ Rootless containers (better security)
- ✅ Docker-compatible CLI (drop-in replacement)
- ✅ Native systemd integration
- ✅ Pod support (Kubernetes-style)
- ✅ No vendor lock-in (OCI compliant)

---

## Installation Instructions

### macOS Installation

On macOS, Podman runs containers inside a lightweight Linux VM (similar to Docker Desktop).

#### Option 1: Using Homebrew (Recommended)

```bash
# Install Podman
brew install podman

# Install podman-compose (Python-based docker-compose alternative)
brew install podman-compose

# Verify installation
podman --version
podman-compose --version
```

#### Option 2: Using Podman Desktop (GUI)

Download and install Podman Desktop from: https://podman-desktop.io/

```bash
# Or install via Homebrew
brew install --cask podman-desktop
```

#### Initialize Podman Machine

After installation, you need to create and start a Podman machine (Linux VM):

```bash
# Create a new Podman machine
podman machine init

# Start the machine
podman machine start

# Verify the machine is running
podman machine list

# Check Podman info
podman info
```

**Optional: Configure machine resources**
```bash
# Create with custom resources (4 CPUs, 8GB RAM, 100GB disk)
podman machine init --cpus 4 --memory 8192 --disk-size 100
```

---

### Linux Installation

#### Ubuntu/Debian

```bash
# Update package list
sudo apt-get update

# Install Podman
sudo apt-get -y install podman

# Install podman-compose
sudo apt-get -y install podman-compose

# OR install via pip
pip install podman-compose
```

#### Fedora/RHEL/CentOS

```bash
# Podman comes pre-installed on Fedora 35+
# For older versions or RHEL/CentOS:
sudo dnf install -y podman

# Install podman-compose
sudo dnf install -y podman-compose

# OR via pip
pip install podman-compose
```

#### Arch Linux

```bash
# Install Podman
sudo pacman -S podman

# Install podman-compose
sudo pacman -S podman-compose

# OR via AUR
yay -S podman-compose
```

---

### Windows Installation

#### Option 1: WSL2 (Recommended)

1. Install WSL2 with Ubuntu
2. Follow Linux installation steps above

#### Option 2: Podman Desktop

Download from: https://podman-desktop.io/

```powershell
# Or install via winget
winget install -e --id RedHat.Podman-Desktop
```

---

## Post-Installation Configuration

### macOS: Set Resource Limits

```bash
# Stop the machine
podman machine stop

# Remove existing machine
podman machine rm

# Create new machine with custom settings
podman machine init \
  --cpus 4 \
  --memory 8192 \
  --disk-size 100 \
  --rootful

# Start machine
podman machine start
```

### Enable Rootless Mode (Linux)

```bash
# Configure subuid and subgid (if not already set)
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER

# Enable user lingering (allows containers to run without active session)
loginctl enable-linger $USER

# Verify configuration
podman system info | grep -A 4 "graphRoot"
```

### Configure Registry Settings

```bash
# Edit registries.conf
sudo nano /etc/containers/registries.conf

# Add Docker Hub as unqualified search registry
[registries.search]
registries = ['docker.io']
```

---

## Verify Installation

Run these commands to verify everything is working:

```bash
# Check Podman version
podman --version

# Check podman-compose version
podman-compose --version

# Run a test container
podman run --rm hello-world

# Check running containers
podman ps

# Check system info
podman info

# For macOS: Check machine status
podman machine list
podman machine info
```

---

## Troubleshooting

### macOS: Machine won't start

```bash
# Remove and recreate machine
podman machine stop
podman machine rm
podman machine init
podman machine start
```

### Permission Denied Errors

```bash
# On Linux: Add user to subuid/subgid
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER

# Restart your session or reboot
```

### SELinux Issues (Linux)

```bash
# If you encounter SELinux issues, add :Z to volume mounts
# This is already configured in podman-compose.yml
volumes:
  - ./apps:/app:Z  # The :Z flag handles SELinux labeling
```

### podman-compose Not Found

```bash
# Install via pip
pip3 install podman-compose

# Or use Python module directly
python3 -m pip install podman-compose

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

---

## Docker to Podman Migration

### Create Alias (Optional)

You can create aliases to use Podman as a drop-in Docker replacement:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias docker=podman
alias docker-compose=podman-compose

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

### Key Differences

| Feature | Docker | Podman |
|---------|--------|--------|
| Daemon | Required | Daemonless |
| Root Access | Required (default) | Rootless by default |
| CLI Syntax | `docker` | `podman` (compatible) |
| Compose | `docker-compose` | `podman-compose` |
| Swarm | Yes | No (use Kubernetes) |
| Desktop GUI | Docker Desktop | Podman Desktop |

---

## Next Steps

After installation, proceed to [PODMAN_README.md](./PODMAN_README.md) for usage instructions specific to this project.

---

## Additional Resources

- **Official Documentation**: https://docs.podman.io/
- **Podman Desktop**: https://podman-desktop.io/
- **GitHub Repository**: https://github.com/containers/podman
- **Tutorials**: https://github.com/containers/podman/tree/main/docs/tutorials
- **Migration Guide**: https://podman.io/getting-started/migration
