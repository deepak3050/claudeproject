# Device Access Tracking

Monitor which devices (like your iPad) are accessing your localhost services on ports 8000-8003 and 8080.

## Quick Start

```bash
cd /Users/deepakdas/Github3050/claude/dfs_claude

# Single check
./track.sh

# Live monitoring (refreshes every 5 seconds)
./track.sh live

# Show network devices only
./track.sh arp

# View access log
./track.sh log
```

## Usage

The `track.sh` script provides multiple ways to monitor device access:

### Commands

| Command | Description |
|---------|-------------|
| `./track.sh` | Single connection check (default) |
| `./track.sh live` or `./track.sh -l` | Continuous monitoring with auto-refresh |
| `./track.sh arp` or `./track.sh -a` | Show devices on local network (ARP table) |
| `./track.sh log` or `./track.sh -log` | Display recent access log entries |
| `./track.sh help` or `./track.sh -h` | Show help message |

### Examples

**Monitor in real-time while testing on iPad:**
```bash
./track.sh live
```
This will continuously update every 5 seconds, showing active connections and network devices.

**Quick check who's connected:**
```bash
./track.sh
```

**View historical access:**
```bash
./track.sh log
```

## What It Shows

### Active Connections
- **IP Address** - The device's local network IP (e.g., 192.168.1.100)
- **Port** - Which service port is being accessed (8000-8003 or 8080)
- **Timestamp** - When the connection was detected

### Network Devices (ARP Table)
- **Hostname** - Device name on the network
- **IP Address** - Local network IP
- **MAC Address** - Hardware address
- **Device Type** - Highlights Apple devices (iPad, iPhone, Mac) in green

## Identifying Your iPad

Your iPad will appear with:
- **IP Address** starting with `192.168.x.x` or `10.0.x.x`
- **MAC Address** typically starting with Apple's OUI prefixes
- **Green highlight** indicating it's an Apple device
- Will show which specific port it's accessing

## Access Logging

All connections are automatically logged to `device_access.log` in the format:
```
[2025-11-28 15:04:32] Port 8000 - IP: 192.168.1.100
[2025-11-28 15:04:45] Port 8080 - IP: 192.168.1.100
```

## Tips

1. **Run in live mode** while actively testing to see connections appear in real-time
2. **Check ARP table** to see all devices on your network and identify your iPad's IP
3. **Review logs** to see historical access patterns
4. **Stop live monitoring** with `Ctrl+C`

## Monitored Ports

The script monitors these ports by default:
- **8000** - Typically used for development servers
- **8001** - Secondary dev server
- **8002** - Additional service
- **8003** - Additional service
- **8080** - Common HTTP alternative port

## Troubleshooting

**No connections showing:**
- Ensure your services are running on the monitored ports
- Verify your iPad is accessing `http://<your-local-ip>:PORT`
- Check that your firewall allows local network connections

**Can't see device names in ARP table:**
- Some devices don't broadcast hostnames
- Use IP address to identify devices instead

**Script won't run:**
```bash
chmod +x track.sh
```

## Technical Details

The script uses:
- `lsof` - To check active TCP connections on specified ports
- `arp -a` - To list devices on the local network with MAC addresses
- Color-coded terminal output for easy reading
- Automatic logging to track access history

## Integration

You can run this script alongside your development workflow:

```bash
# Terminal 1: Run your services
./start.sh

# Terminal 2: Monitor device access
./track.sh live
```

This way you can see exactly when your iPad (or any device) connects to your local services.
