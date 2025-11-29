#!/bin/bash

# HTTP Access Log Tracker
# Monitors Docker container logs for HTTP access from devices

LOG_FILE="device_access.log"
CONTAINER_NAME="dfs_claude-sliding-window-1"
STATE_FILE=".http_access_state"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}HTTP Access Tracker${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to get device info from IP
get_device_info() {
    local ip=$1

    # Get hostname from ARP table
    local arp_line=$(arp -a | grep "$ip")
    local hostname=$(echo "$arp_line" | awk '{print $1}')
    local mac=$(echo "$arp_line" | awk '{print $4}')

    # Try to determine device type from hostname or MAC
    local device_type="Unknown Device"

    if [[ $hostname == *"ipad"* ]] || [[ $hostname == *"iPad"* ]]; then
        device_type="iPad"
    elif [[ $hostname == *"iphone"* ]] || [[ $hostname == *"iPhone"* ]]; then
        device_type="iPhone"
    elif [[ $hostname == *"macbook"* ]] || [[ $hostname == *"MacBook"* ]] || [[ $hostname == *"imac"* ]]; then
        device_type="Mac"
    elif [[ $hostname == *"android"* ]] || [[ $hostname == *"Android"* ]]; then
        device_type="Android"
    fi

    # Build full device info
    local full_info="$device_type"
    if [ "$hostname" != "?" ] && [ ! -z "$hostname" ]; then
        full_info="$full_info ($hostname)"
    fi

    echo "$full_info"
}

# Function to monitor HTTP access logs
monitor_http_access() {
    echo -e "${YELLOW}Monitoring HTTP Access Logs (Ctrl+C to stop)...${NC}\n"

    # Follow Docker logs and parse HTTP access lines
    docker logs -f --tail 0 $CONTAINER_NAME 2>&1 | while read line; do
        # Match Python HTTP server access log format: IP - - [timestamp] "GET /path HTTP/1.1" status
        if echo "$line" | grep -q "GET\|POST"; then
            # Extract IP address (first field)
            ip=$(echo "$line" | awk '{print $1}')

            # Skip Docker internal IPs
            if [ "$ip" = "192.168.65.1" ] || [ "$ip" = "127.0.0.1" ] || [ "$ip" = "::1" ]; then
                # This is the Docker gateway - the actual client is external
                # We need to find the real client IP from the host's network connections

                # Check ARP table for recent devices
                recent_devices=$(arp -a | grep -v "incomplete" | grep -E "192.168.1\." | awk '{print $2}' | tr -d '()')

                for device_ip in $recent_devices; do
                    if [ "$device_ip" != "192.168.1.12" ]; then  # Skip the host machine itself
                        ip=$device_ip
                        break
                    fi
                done
            fi

            # Extract request details
            request=$(echo "$line" | grep -oP '"[^"]*"' | head -1 | tr -d '"')
            timestamp=$(date '+%Y-%m-%d %H:%M:%S')

            # Determine which port was accessed (from the log line context)
            port="unknown"

            # Get device name
            device_name=$(get_device_info "$ip")

            echo -e "${GREEN}HTTP Request Detected:${NC}"
            echo -e "  ${BLUE}Device:${NC} $device_name"
            echo -e "  ${BLUE}IP:${NC} $ip"
            echo -e "  ${BLUE}Request:${NC} $request"
            echo -e "  ${BLUE}Time:${NC} $timestamp"
            echo ""

            # Log to file
            echo "[$timestamp] HTTP ACCESS - $device_name - IP: $ip - Request: $request" >> "$LOG_FILE"
        fi
    done
}

# Function to show recent access
show_recent_access() {
    echo -e "${YELLOW}Recent HTTP Access:${NC}"
    echo "----------------------------------------"
    if [ -f "$LOG_FILE" ]; then
        tail -n 20 "$LOG_FILE"
    else
        echo -e "${RED}No access log found${NC}"
    fi
}

# Main menu
case "${1}" in
    "live"|"-l")
        monitor_http_access
        ;;
    "log"|"-log")
        show_recent_access
        ;;
    "help"|"-h"|"")
        echo "Usage: ./track_http.sh [option]"
        echo ""
        echo "Options:"
        echo "  live, -l     Monitor HTTP access in real-time"
        echo "  log, -log    Show recent HTTP access log"
        echo "  help, -h     Show this help message"
        ;;
    *)
        echo "Unknown option: $1"
        echo "Run './track_http.sh help' for usage information"
        ;;
esac
