#!/bin/bash

# PlayAural Server Management Script (Auto-Setup Version)
# Supported OS: AlmaLinux 8 / EL8
# Features: 
# - Auto-detects running directory
# - Auto-installs Python 3.9 + Dependencies if missing

SERVICE_NAME="playaural"

# Auto-detect the directory where this script is located
# We assume the script is placed inside the 'server' folder alongside main.py
SERVER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON="python3.12"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper Functions
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}Error: Please run as root (sudo ./server_control.sh)${NC}"
        exit 1
    fi
}

install_environment() {
    echo -e "${CYAN}Checking environment...${NC}"
    
    # 1. Check/Install Python 3.12
    if ! command -v $PYTHON &> /dev/null; then
        echo -e "${YELLOW}Python 3.12 not found. Installing...${NC}"
        # Ensure EPEL is available just in case, though 3.12 might be in appstream
        dnf install epel-release -y
        # Try installing python3.12 directly
        dnf install python3.12 python3.12-pip -y
        
        if [ $? -ne 0 ]; then
             echo -e "${RED}Failed to install Python 3.12.${NC}"
             echo -e "${YELLOW}Attempting to enable module stream...${NC}"
             # Fallback: sometimes it's hidden behind modules? (Less likely for 3.12 on EL8, but good measure)
             # Actually, simpler to just fail and ask user to check repos if standard install fails.
             echo -e "${RED}Could not install python3.12 automatically. Please install it manually.${NC}"
             read -p "Press Enter to return..."
             return
        fi
        echo -e "${GREEN}Python 3.12 installed.${NC}"
    else
        echo -e "${GREEN}Python 3.12 is present.${NC}"
    fi

    # 2. Check/Install Python Libraries
    echo "Checking required libraries..."
    # We run installation every time to ensure deps are there. It's fast if already installed.
    $PYTHON -m pip install --upgrade pip
    $PYTHON -m pip install websockets argon2-cffi fluent-compiler mashumaro babel openskill
    
    echo -e "${GREEN}Environment ready.${NC}"
    echo "-----------------------------------"
}

check_status() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "Server Status: ${GREEN}RUNNING${NC}"
        # Show only port 8000
        echo -n "Port 8000 Usage: "
        ss -tuln | grep ":8000 " && echo "" || echo "Not detecting listener on port 8000"
    else
        echo -e "Server Status: ${RED}STOPPED${NC}"
    fi
}

show_menu() {
    clear
    echo "==================================="
    echo "   PlayAural Server Manager"
    echo "   Dir: $SERVER_DIR"
    echo "==================================="
    check_status
    echo "==================================="
    echo "1. Start Server"
    echo "2. Stop Server"
    echo "3. Restart Server"
    echo "4. View Logs (Tail)"
    echo "5. Clear Logs"
    echo "6. Create User"
    echo "7. Reset User Password"
    echo "8. Re-install Environment (Fix missing libs)"
    echo "0. Exit"
    echo "==================================="
    read -p "Choose an option: " choice
}

start_server() {
    # Auto-generate service file if missing or path changed
    setup_service
    
    echo "Starting server..."
    systemctl start $SERVICE_NAME
    sleep 2
    check_status
    read -p "Press Enter to continue..."
}

stop_server() {
    echo "Stopping server..."
    systemctl stop $SERVICE_NAME
    sleep 2
    check_status
    read -p "Press Enter to continue..."
}

restart_server() {
    setup_service
    echo "Restarting server..."
    systemctl restart $SERVICE_NAME
    sleep 2
    check_status
    read -p "Press Enter to continue..."
}

view_logs() {
    echo "Showing last 50 lines of log (Ctrl+C to exit)..."
    journalctl -u $SERVICE_NAME -n 50 -f
}

clear_logs() {
    echo "Clearing systemd journal logs..."
    journalctl --rotate
    journalctl --vacuum-time=1s
    echo "Logs cleared."
    read -p "Press Enter to continue..."
}

create_user() {
    install_environment # Ensure env is ready before running python code
    
    echo "--- Create New User ---"
    read -p "Enter Username: " u_name
    
    if [ -z "$u_name" ]; then
        echo "Username cannot be empty."
        read -p "Press Enter..."
        return
    fi
    
    read -s -p "Enter Password: " u_pass
    echo ""
    
    cd "$SERVER_DIR"
    echo "Running CLI..."
    $PYTHON -m server.cli create-user "$u_name" "$u_pass"
    
    read -p "Press Enter to continue..."
}

reset_password() {
    install_environment
    
    echo "--- Reset Password ---"
    read -p "Enter Username: " u_name
    read -s -p "Enter New Password: " u_pass
    echo ""
    
    cd "$SERVER_DIR"
    $PYTHON -m server.cli reset-password "$u_name" "$u_pass"
    
    read -p "Press Enter to continue..."
}

setup_service() {
    # Dynamically creates/updates systemd service file based on current path
    echo "Verifying systemd service configuration..."
    
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    
    # Check if we need to update the service file (e.g. if path changed)
    # Ideally checking content, but simpler to just overwrite if valid
    
    # We construct the file content
    cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=PlayAural Game Server
After=network.target

[Service]
User=root
WorkingDirectory=$SERVER_DIR
ExecStart=/usr/bin/$PYTHON main.py --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Reload daemon
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME --now > /dev/null 2>&1
}

# Main Execution

check_root

# First run check: Try to setup environment immediately if python missing
if ! command -v $PYTHON &> /dev/null; then
    install_environment
fi

while true; do
    show_menu
    case $choice in
        1) start_server ;;
        2) stop_server ;;
        3) restart_server ;;
        4) view_logs ;;
        5) clear_logs ;;
        6) create_user ;;
        7) reset_password ;;
        8) install_environment; read -p "Done. Press Enter..." ;;
        0) exit 0 ;;
        *) echo "Invalid option." ;;
    esac
done
