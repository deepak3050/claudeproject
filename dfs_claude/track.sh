#!/bin/bash

# Device Access Tracking Script
# Monitors connections to ports 8000-8003 and 8080

LOG_FILE="device_access.log"
PORTS=(8000 8001 8002 8003 8080)
STATE_FILE=".device_state"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Device Access Tracker${NC}"
echo -e "${BLUE}Monitoring ports: ${PORTS[*]}${NC}"
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
    elif [[ $mac == *":"* ]]; then
        # Check MAC address OUI for Apple devices
        local mac_prefix=$(echo "$mac" | cut -d':' -f1-3 | tr '[:upper:]' '[:lower:]')
        # Common Apple MAC prefixes (partial list)
        if [[ $mac_prefix == "00:1e:c2" ]] || [[ $mac_prefix == "00:25:00" ]] || \
           [[ $mac_prefix == "00:26:bb" ]] || [[ $mac_prefix == "a4:c3:61" ]] || \
           [[ $mac_prefix == "f0:db:e2" ]] || [[ $mac_prefix == "ac:87:a3" ]]; then
            device_type="Apple Device (iPad/iPhone/Mac)"
        fi
    fi

    # Build full device info
    local full_info="$device_type"
    if [ "$hostname" != "?" ] && [ ! -z "$hostname" ]; then
        full_info="$full_info ($hostname)"
    fi

    echo "$full_info"
}

# Function to check active connections
check_connections() {
    echo -e "${YELLOW}Active Connections:${NC}"
    echo "----------------------------------------"

    # Current state
    current_state=""

    # Try to detect if we're running on host with Docker containers
    docker_container=$(docker ps --format '{{.Names}}' 2>/dev/null | head -n 1)

    for port in "${PORTS[@]}"; do
        connections=""

        # First try lsof (works when running inside container or on host without Docker)
        connections=$(lsof -iTCP:$port -sTCP:ESTABLISHED 2>/dev/null | tail -n +2)

        # If no connections found and Docker is running, check inside Docker container
        if [ -z "$connections" ] && [ ! -z "$docker_container" ]; then
            # Try to get connections from Docker container (include all connection states)
            # States: ESTABLISHED, TIME_WAIT, CLOSE_WAIT, FIN_WAIT1, FIN_WAIT2, LAST_ACK, SYN_SENT, SYN_RECV
            docker_connections=$(docker exec $docker_container sh -c "netstat -tn 2>/dev/null | grep ':$port' || ss -tn 2>/dev/null | grep ':$port'" 2>/dev/null)

            if [ ! -z "$docker_connections" ]; then
                connections="$docker_connections"
            fi
        fi

        if [ ! -z "$connections" ]; then
            echo -e "${GREEN}Port $port:${NC}"
            echo "$connections" | while read line; do
                # Extract IP address - handle both lsof and netstat/ss output
                if echo "$line" | grep -q -- "->"; then
                    # lsof format
                    ip=$(echo "$line" | awk '{print $9}' | cut -d'>' -f2 | cut -d':' -f1)
                else
                    # netstat/ss format: extract foreign address
                    ip=$(echo "$line" | awk '{print $5}' | cut -d':' -f1)
                fi

                if [ ! -z "$ip" ] && [ "$ip" != "localhost" ] && [ "$ip" != "127.0.0.1" ] && [ "$ip" != "0.0.0.0" ] && [ "$ip" != "*" ]; then
                    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

                    # Check if IP is from Docker's internal network (192.168.65.x, 172.17-31.x.x, 10.x.x.x)
                    is_docker_ip=false
                    if echo "$ip" | grep -qE "^192\.168\.65\.|^172\.(1[7-9]|2[0-9]|3[0-1])\.|^10\."; then
                        is_docker_ip=true
                    fi

                    # If IP is Docker gateway/internal, find the real client from recent ARP entries
                    actual_ip="$ip"
                    if [ "$is_docker_ip" = true ]; then
                        # This is Docker's internal network - look for iPad/iPhone devices in ARP table
                        recent_device=$(arp -a | grep -iE "(ipad|iphone)" | grep -v "incomplete" | head -1 | awk '{print $2}' | tr -d '()')
                        if [ -z "$recent_device" ]; then
                            # Fall back to any recent non-host, non-router device on home network
                            recent_device=$(arp -a | grep -E "192\.168\.[0-9]+\." | grep -v "192.168.1.12" | grep -v "192.168.1.1" | grep -v "192.168.65" | grep -v "incomplete" | head -1 | awk '{print $2}' | tr -d '()')
                        fi
                        if [ ! -z "$recent_device" ]; then
                            actual_ip="$recent_device"
                        fi
                    fi

                    device_name=$(get_device_info "$actual_ip")

                    echo -e "  ${BLUE}Device:${NC} $device_name"
                    echo -e "  ${BLUE}IP:${NC} $actual_ip"
                    if [ "$is_docker_ip" = true ]; then
                        echo -e "  ${BLUE}Via:${NC} Docker gateway ($ip)"
                    fi
                    echo -e "  ${BLUE}Time:${NC} $timestamp"

                    # Create unique connection identifier
                    conn_id="$port:$actual_ip"

                    # Check if this connection was already logged recently (within last 5 minutes)
                    already_logged=false
                    if [ -f "$STATE_FILE" ]; then
                        # Check if connection exists in state file and is recent (less than 5 min old)
                        if grep -q "^$conn_id:" "$STATE_FILE" 2>/dev/null; then
                            log_time=$(grep "^$conn_id:" "$STATE_FILE" | cut -d: -f3)
                            current_epoch=$(date +%s)
                            if [ ! -z "$log_time" ]; then
                                time_diff=$((current_epoch - log_time))
                                if [ $time_diff -lt 300 ]; then  # 300 seconds = 5 minutes
                                    already_logged=true
                                fi
                            fi
                        fi
                    fi

                    # Only log if this is a new connection or hasn't been logged recently
                    if [ "$already_logged" = false ]; then
                        echo "[$timestamp] NEW CONNECTION - $device_name - Port $port - IP: $actual_ip" >> "$LOG_FILE"
                        # Save to state file with current epoch time
                        echo "$conn_id:$(date +%s)" >> "$STATE_FILE"
                    fi
                fi
            done
            echo ""
        fi
    done
}

# Function to show ARP table (devices on local network)
show_network_devices() {
    echo -e "\n${YELLOW}Devices on Local Network (ARP Table):${NC}"
    echo "----------------------------------------"
    arp -a | grep -v "incomplete" | while read line; do
        hostname=$(echo "$line" | awk '{print $1}')
        ip=$(echo "$line" | awk '{print $2}' | tr -d '()')
        mac=$(echo "$line" | awk '{print $4}')

        # Highlight Apple devices (iPad, iPhone, Mac)
        if [[ $mac == *"a:"* ]] || [[ $mac == *"b:"* ]] || [[ $mac == *"c:"* ]]; then
            echo -e "${GREEN}$hostname - $ip - $mac (Possible Apple Device)${NC}"
        else
            echo "$hostname - $ip - $mac"
        fi
    done
}

# Function for continuous monitoring
continuous_monitor() {
    echo -e "\n${YELLOW}Starting continuous monitoring (Ctrl+C to stop)...${NC}\n"

    while true; do
        clear
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}Device Access Tracker - Live Monitor${NC}"
        echo -e "${BLUE}$(date)${NC}"
        echo -e "${BLUE}========================================${NC}\n"

        check_connections
        show_network_devices

        sleep 5
    done
}

# Main menu
case "${1}" in
    "live"|"-l")
        continuous_monitor
        ;;
    "arp"|"-a")
        show_network_devices
        ;;
    "log"|"-log")
        if [ -f "$LOG_FILE" ]; then
            echo -e "${YELLOW}Recent Access Log:${NC}"
            echo "----------------------------------------"
            tail -n 20 "$LOG_FILE"
        else
            echo -e "${RED}No log file found${NC}"
        fi
        ;;
    "help"|"-h"|"")
        echo "Usage: ./track.sh [option]"
        echo ""
        echo "Options:"
        echo "  live, -l     Continuous monitoring (refreshes every 5s)"
        echo "  arp, -a      Show devices on local network"
        echo "  log, -log    Show recent access log"
        echo "  help, -h     Show this help message"
        echo ""
        echo "Default (no option): Single connection check"
        ;;
    *)
        check_connections
        show_network_devices
        ;;
esac
