#!/bin/bash

set -u

SERVICE_NAME="playaural"
SERVICE_USER="playaural"
VOICE_SERVICE_NAME="playaural-livekit"
VOICE_SERVICE_USER="livekit"

SERVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SERVER_DIR/.." && pwd)"
CONFIG_DIR="/etc/playaural"
VOICE_ENV_FILE="$CONFIG_DIR/voice.env"
LIVEKIT_CONFIG_FILE="$CONFIG_DIR/livekit.yaml"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
VOICE_SERVICE_FILE="/etc/systemd/system/${VOICE_SERVICE_NAME}.service"
VENV_DIR="$SERVER_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SERVER_PACKAGES=(
  websockets
  argon2-cffi
  fluent-compiler
  mashumaro
  babel
  openskill
)

pause_screen() {
    read -rp "Press Enter to continue..." _
}

say_info() {
    echo -e "${CYAN}$1${NC}"
}

say_ok() {
    echo -e "${GREEN}$1${NC}"
}

say_warn() {
    echo -e "${YELLOW}$1${NC}"
}

say_error() {
    echo -e "${RED}$1${NC}"
}

check_root() {
    if [ "${EUID:-0}" -ne 0 ]; then
        say_error "Please run this management script as root (sudo ./sc.sh)."
        exit 1
    fi
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

detect_python_bin() {
    if command_exists python3.12; then
        echo "python3.12"
        return
    fi
    if command_exists python3.11; then
        echo "python3.11"
        return
    fi
    if command_exists python3; then
        echo "python3"
        return
    fi
    echo ""
}

ensure_config_dir() {
    install -d -m 0755 "$CONFIG_DIR"
}

setup_system_user() {
    if ! id "$SERVICE_USER" >/dev/null 2>&1; then
        say_info "Creating service user: $SERVICE_USER"
        useradd -r -s /sbin/nologin "$SERVICE_USER"
    fi
}

setup_voice_user() {
    if ! id "$VOICE_SERVICE_USER" >/dev/null 2>&1; then
        say_info "Creating voice service user: $VOICE_SERVICE_USER"
        useradd -r -s /sbin/nologin "$VOICE_SERVICE_USER"
    fi
}

fix_permissions() {
    chown -R "$SERVICE_USER:$SERVICE_USER" "$SERVER_DIR"
    find "$SERVER_DIR" -type d -exec chmod 755 {} +
}

random_token() {
    tr -dc 'A-Za-z0-9' </dev/urandom | head -c 24
}

extract_domain_from_url() {
    local raw="$1"
    raw="${raw#ws://}"
    raw="${raw#wss://}"
    raw="${raw#http://}"
    raw="${raw#https://}"
    raw="${raw%%/*}"
    raw="${raw%%\?*}"
    raw="${raw%%#*}"
    raw="${raw%%:*}"
    echo "$raw"
}

normalize_voice_url() {
    local raw="$1"
    raw="${raw%% }"
    raw="${raw## }"
    if [ -z "$raw" ]; then
        echo ""
        return
    fi
    if [[ "$raw" != ws://* && "$raw" != wss://* ]]; then
        raw="wss://$raw"
    fi
    raw="${raw%/}"
    echo "$raw"
}

load_voice_config() {
    PLAYAURAL_VOICE_ENABLED=""
    PLAYAURAL_VOICE_PROVIDER=""
    PLAYAURAL_VOICE_URL=""
    PLAYAURAL_VOICE_API_KEY=""
    PLAYAURAL_VOICE_API_SECRET=""
    PLAYAURAL_VOICE_ROOM_PREFIX=""
    PLAYAURAL_VOICE_TOKEN_TTL_SECONDS=""
    if [ -f "$VOICE_ENV_FILE" ]; then
        set -a
        # shellcheck disable=SC1090
        . "$VOICE_ENV_FILE"
        set +a
    fi
}

write_voice_env() {
    local public_url="$1"
    local api_key="$2"
    local api_secret="$3"
    local room_prefix="$4"
    local ttl="$5"

    cat >"$VOICE_ENV_FILE" <<EOF
PLAYAURAL_VOICE_ENABLED=1
PLAYAURAL_VOICE_PROVIDER=livekit
PLAYAURAL_VOICE_URL=$public_url
PLAYAURAL_VOICE_API_KEY=$api_key
PLAYAURAL_VOICE_API_SECRET=$api_secret
PLAYAURAL_VOICE_ROOM_PREFIX=$room_prefix
PLAYAURAL_VOICE_TOKEN_TTL_SECONDS=$ttl
EOF
    chmod 600 "$VOICE_ENV_FILE"
}

write_livekit_config() {
    local public_url="$1"
    local api_key="$2"
    local api_secret="$3"
    local domain

    domain="$(extract_domain_from_url "$public_url")"
    if [ -z "$domain" ]; then
        say_error "Could not extract a domain from: $public_url"
        return 1
    fi

    cat >"$LIVEKIT_CONFIG_FILE" <<EOF
port: 7880
bind_addresses:
  - ""
log_level: info

rtc:
  tcp_port: 7881
  port_range_start: 50000
  port_range_end: 50100
  use_external_ip: true

turn:
  enabled: true
  domain: $domain
  tls_port: 5349
  udp_port: 443

keys:
  $api_key: $api_secret
EOF
    chown "root:$VOICE_SERVICE_USER" "$LIVEKIT_CONFIG_FILE"
    chmod 640 "$LIVEKIT_CONFIG_FILE"
}

ensure_livekit_config_from_env() {
    load_voice_config
    if [ -z "${PLAYAURAL_VOICE_URL:-}" ] || [ -z "${PLAYAURAL_VOICE_API_KEY:-}" ] || [ -z "${PLAYAURAL_VOICE_API_SECRET:-}" ]; then
        say_error "Voice configuration is incomplete. Run the voice configuration step first."
        return 1
    fi
    write_livekit_config "$PLAYAURAL_VOICE_URL" "$PLAYAURAL_VOICE_API_KEY" "$PLAYAURAL_VOICE_API_SECRET"
}

install_base_packages() {
    say_info "Installing required system packages if needed..."
    dnf install -y epel-release >/dev/null 2>&1 || true
    dnf install -y curl tar gzip openssl >/dev/null 2>&1 || true

    if ! command_exists python3.12 && ! command_exists python3.11 && ! command_exists python3; then
        dnf install -y python3.12 python3.12-pip >/dev/null 2>&1 || \
        dnf install -y python3.11 python3.11-pip >/dev/null 2>&1 || \
        dnf install -y python3 python3-pip >/dev/null 2>&1 || true
    fi
}

install_environment() {
    local python_bin

    setup_system_user
    install_base_packages

    python_bin="$(detect_python_bin)"
    if [ -z "$python_bin" ]; then
        say_error "No supported Python interpreter was found. Install Python 3.11 or 3.12 and try again."
        pause_screen
        return 1
    fi

    say_info "Using Python interpreter: $python_bin"

    if [ ! -d "$VENV_DIR" ]; then
        say_info "Creating virtual environment in $VENV_DIR"
        "$python_bin" -m venv "$VENV_DIR"
    fi

    say_info "Installing server Python dependencies..."
    "$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel
    "$VENV_PYTHON" -m pip install --upgrade "${SERVER_PACKAGES[@]}"

    fix_permissions
    say_ok "Game server environment is ready."
}

setup_service() {
    setup_system_user
    ensure_config_dir

    cat >"$SERVICE_FILE" <<EOF
[Unit]
Description=PlayAural Game Server
After=network-online.target
Wants=network-online.target

[Service]
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$SERVER_DIR
EnvironmentFile=-$VOICE_ENV_FILE
ExecStart=$VENV_PYTHON $SERVER_DIR/main.py --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=full
ReadWritePaths=$SERVER_DIR

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME" >/dev/null 2>&1 || true
}

setup_voice_service() {
    setup_voice_user
    ensure_config_dir

    cat >"$VOICE_SERVICE_FILE" <<EOF
[Unit]
Description=PlayAural LiveKit Voice Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$VOICE_SERVICE_USER
Group=$VOICE_SERVICE_USER
ExecStart=/usr/local/bin/livekit-server --config $LIVEKIT_CONFIG_FILE
Restart=on-failure
RestartSec=5
LimitNOFILE=1048576
NoNewPrivileges=true
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable "$VOICE_SERVICE_NAME" >/dev/null 2>&1 || true
}

ensure_voice_firewall_rules() {
    if ! command_exists firewall-cmd; then
        say_warn "firewall-cmd is not installed. Open the LiveKit ports manually if your firewall is enabled."
        return
    fi

    if ! systemctl is-active --quiet firewalld; then
        say_warn "firewalld is not active. Skipping firewall changes."
        return
    fi

    say_info "Opening LiveKit media ports in firewalld..."
    firewall-cmd --permanent --add-port=7881/tcp >/dev/null 2>&1 || true
    firewall-cmd --permanent --add-port=5349/tcp >/dev/null 2>&1 || true
    firewall-cmd --permanent --add-port=443/udp >/dev/null 2>&1 || true
    firewall-cmd --permanent --add-port=50000-50100/udp >/dev/null 2>&1 || true
    firewall-cmd --reload >/dev/null 2>&1 || true
}

install_voice_server_binary() {
    setup_voice_user

    if [ -x /usr/local/bin/livekit-server ]; then
        say_ok "LiveKit server is already installed at /usr/local/bin/livekit-server"
        return 0
    fi

    if ! command_exists curl; then
        dnf install -y curl >/dev/null 2>&1 || true
    fi

    if ! command_exists curl; then
        say_error "curl is required to install LiveKit automatically."
        return 1
    fi

    say_info "Installing LiveKit server using the official installer..."
    if ! curl -sSL https://get.livekit.io | bash; then
        say_error "The LiveKit installer failed."
        return 1
    fi

    if [ ! -x /usr/local/bin/livekit-server ]; then
        say_error "LiveKit installation finished but /usr/local/bin/livekit-server was not found."
        return 1
    fi

    say_ok "LiveKit server installed successfully."
}

configure_voice_server() {
    local current_url current_key current_secret current_prefix current_ttl
    local input_url input_key input_secret input_prefix input_ttl
    local final_url final_domain

    setup_voice_user
    ensure_config_dir
    load_voice_config

    current_url="${PLAYAURAL_VOICE_URL:-wss://voice.example.com}"
    current_key="${PLAYAURAL_VOICE_API_KEY:-PLAYAURAL_VOICE_API_KEY}"
    current_secret="${PLAYAURAL_VOICE_API_SECRET:-$(random_token)}"
    current_prefix="${PLAYAURAL_VOICE_ROOM_PREFIX:-playaural}"
    current_ttl="${PLAYAURAL_VOICE_TOKEN_TTL_SECONDS:-900}"

    echo "--- Configure Voice Server ---"
    read -rp "Public Voice URL [$current_url]: " input_url
    read -rp "LiveKit API key [$current_key]: " input_key
    read -rp "LiveKit API secret [$current_secret]: " input_secret
    read -rp "Voice room prefix [$current_prefix]: " input_prefix
    read -rp "Token TTL seconds [$current_ttl]: " input_ttl

    final_url="$(normalize_voice_url "${input_url:-$current_url}")"
    input_key="${input_key:-$current_key}"
    input_secret="${input_secret:-$current_secret}"
    input_prefix="${input_prefix:-$current_prefix}"
    input_ttl="${input_ttl:-$current_ttl}"
    final_domain="$(extract_domain_from_url "$final_url")"

    if [ -z "$final_url" ] || [ -z "$final_domain" ]; then
        say_error "A valid public Voice URL is required."
        pause_screen
        return 1
    fi

    if ! [[ "$input_ttl" =~ ^[0-9]+$ ]]; then
        say_error "Token TTL must be a whole number of seconds."
        pause_screen
        return 1
    fi

    write_voice_env "$final_url" "$input_key" "$input_secret" "$input_prefix" "$input_ttl"
    write_livekit_config "$final_url" "$input_key" "$input_secret" || {
        pause_screen
        return 1
    }
    setup_voice_service
    setup_service
    ensure_voice_firewall_rules

    say_ok "Voice server configuration saved."
    echo "Public voice URL: $final_url"
    echo "TURN domain:      $final_domain"
    echo "Room prefix:      $input_prefix"
    echo "Token TTL:        $input_ttl seconds"
    echo
    echo "Reminder:"
    echo "- Point your public voice hostname at this VPS in DNS."
    echo "- In Cloudflare, use DNS-only mode for the voice hostname unless you have a product that supports the required media transport."
    echo "- In Webmin/Virtualmin, reverse proxy the voice hostname to http://127.0.0.1:7880 with WebSocket upgrade support."
}

change_voice_url() {
    local current_url current_key current_secret current_prefix current_ttl
    local input_url final_url final_domain

    if [ ! -f "$VOICE_ENV_FILE" ]; then
        say_warn "Voice configuration does not exist yet. Opening the full voice configuration wizard."
        configure_voice_server
        pause_screen
        return
    fi

    load_voice_config
    current_url="${PLAYAURAL_VOICE_URL:-wss://voice.example.com}"
    current_key="${PLAYAURAL_VOICE_API_KEY:-PLAYAURAL_VOICE_API_KEY}"
    current_secret="${PLAYAURAL_VOICE_API_SECRET:-PLAYAURAL_VOICE_API_SECRET}"
    current_prefix="${PLAYAURAL_VOICE_ROOM_PREFIX:-playaural}"
    current_ttl="${PLAYAURAL_VOICE_TOKEN_TTL_SECONDS:-900}"

    echo "--- Change Voice Server URL / Domain ---"
    read -rp "New public Voice URL [$current_url]: " input_url
    final_url="$(normalize_voice_url "${input_url:-$current_url}")"
    final_domain="$(extract_domain_from_url "$final_url")"

    if [ -z "$final_url" ] || [ -z "$final_domain" ]; then
        say_error "A valid public Voice URL is required."
        pause_screen
        return 1
    fi

    write_voice_env "$final_url" "$current_key" "$current_secret" "$current_prefix" "$current_ttl"
    write_livekit_config "$final_url" "$current_key" "$current_secret" || {
        pause_screen
        return 1
    }

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl restart "$SERVICE_NAME"
    fi
    if systemctl is-active --quiet "$VOICE_SERVICE_NAME"; then
        systemctl restart "$VOICE_SERVICE_NAME"
    fi

    say_ok "Voice URL updated to $final_url"
    echo "TURN domain updated to $final_domain"
}

show_voice_config() {
    local secret_mask="(not set)"

    load_voice_config

    if [ -n "${PLAYAURAL_VOICE_API_SECRET:-}" ]; then
        secret_mask="${PLAYAURAL_VOICE_API_SECRET:0:4}********"
    fi

    echo "--- Voice Configuration ---"
    echo "Enabled:      ${PLAYAURAL_VOICE_ENABLED:-0}"
    echo "Provider:     ${PLAYAURAL_VOICE_PROVIDER:-livekit}"
    echo "Public URL:   ${PLAYAURAL_VOICE_URL:-not configured}"
    echo "API key:      ${PLAYAURAL_VOICE_API_KEY:-not configured}"
    echo "API secret:   $secret_mask"
    echo "Room prefix:  ${PLAYAURAL_VOICE_ROOM_PREFIX:-playaural}"
    echo "Token TTL:    ${PLAYAURAL_VOICE_TOKEN_TTL_SECONDS:-900}"
    if [ -f "$LIVEKIT_CONFIG_FILE" ]; then
        echo "LiveKit YAML: $LIVEKIT_CONFIG_FILE"
        echo "TURN domain:  $(awk '/^[[:space:]]*domain:/ {print $2; exit}' "$LIVEKIT_CONFIG_FILE" 2>/dev/null)"
    else
        echo "LiveKit YAML: not configured"
    fi
}

check_status() {
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "Game Server:  ${GREEN}RUNNING${NC}"
    else
        echo -e "Game Server:  ${RED}STOPPED${NC}"
    fi

    if systemctl is-active --quiet "$VOICE_SERVICE_NAME"; then
        echo -e "Voice Server: ${GREEN}RUNNING${NC}"
    else
        echo -e "Voice Server: ${RED}STOPPED${NC}"
    fi

    load_voice_config
    echo "Voice URL:    ${PLAYAURAL_VOICE_URL:-not configured}"
}

start_server() {
    setup_system_user
    install_environment || return 1
    setup_service

    say_info "Starting game server..."
    systemctl start "$SERVICE_NAME"
    sleep 2
    check_status
    pause_screen
}

stop_server() {
    say_info "Stopping game server..."
    systemctl stop "$SERVICE_NAME" >/dev/null 2>&1 || true
    sleep 1
    check_status
    pause_screen
}

restart_server() {
    setup_system_user
    install_environment || return 1
    setup_service
    say_info "Restarting game server..."
    systemctl restart "$SERVICE_NAME"
    sleep 2
    check_status
    pause_screen
}

start_voice_server() {
    install_voice_server_binary || {
        pause_screen
        return 1
    }
    if [ ! -f "$VOICE_ENV_FILE" ]; then
        say_warn "Voice is not configured yet."
        configure_voice_server || return 1
    fi
    ensure_livekit_config_from_env || {
        pause_screen
        return 1
    }
    setup_voice_service
    say_info "Starting voice server..."
    systemctl start "$VOICE_SERVICE_NAME"
    sleep 2
    check_status
    pause_screen
}

stop_voice_server() {
    say_info "Stopping voice server..."
    systemctl stop "$VOICE_SERVICE_NAME" >/dev/null 2>&1 || true
    sleep 1
    check_status
    pause_screen
}

restart_voice_server() {
    install_voice_server_binary || {
        pause_screen
        return 1
    }
    if [ ! -f "$VOICE_ENV_FILE" ]; then
        say_warn "Voice is not configured yet."
        configure_voice_server || return 1
    fi
    ensure_livekit_config_from_env || {
        pause_screen
        return 1
    }
    setup_voice_service
    say_info "Restarting voice server..."
    systemctl restart "$VOICE_SERVICE_NAME"
    sleep 2
    check_status
    pause_screen
}

install_voice_stack() {
    install_voice_server_binary || {
        pause_screen
        return 1
    }
    if [ ! -f "$VOICE_ENV_FILE" ]; then
        configure_voice_server || {
            pause_screen
            return 1
        }
    else
        ensure_livekit_config_from_env || {
            pause_screen
            return 1
        }
        setup_voice_service
        setup_service
        ensure_voice_firewall_rules
    fi
    say_ok "Voice server installation workflow is complete."
    echo "Use the menu to start or restart the voice service whenever needed."
    pause_screen
}

view_logs() {
    echo "Showing game server logs (Ctrl+C to exit)..."
    journalctl -u "$SERVICE_NAME" -n 50 -f
}

view_voice_logs() {
    echo "Showing voice server logs (Ctrl+C to exit)..."
    journalctl -u "$VOICE_SERVICE_NAME" -n 50 -f
}

clear_logs() {
    say_info "Rotating and trimming systemd journal logs..."
    journalctl --rotate >/dev/null 2>&1 || true
    journalctl --vacuum-time=1s >/dev/null 2>&1 || true

    say_info "Cleaning Python cache directories..."
    find "$SERVER_DIR" -type d -name "__pycache__" -exec rm -rf {} +

    say_ok "Logs and cache directories were cleaned."
    pause_screen
}

create_user() {
    local u_name u_pass

    setup_system_user
    install_environment || return 1

    echo "--- Create New User ---"
    read -rp "Enter username: " u_name
    if [ -z "$u_name" ]; then
        say_error "Username cannot be empty."
        pause_screen
        return 1
    fi

    read -rsp "Enter password: " u_pass
    echo

    (cd "$SERVER_DIR" && runuser -u "$SERVICE_USER" -- env PLAYAURAL_CLI_PW="$u_pass" "$VENV_PYTHON" "$SERVER_DIR/cli.py" create-user "$u_name")
    pause_screen
}

reset_password() {
    local u_name u_pass

    setup_system_user
    install_environment || return 1

    echo "--- Reset Password ---"
    read -rp "Enter username: " u_name
    if [ -z "$u_name" ]; then
        say_error "Username cannot be empty."
        pause_screen
        return 1
    fi

    read -rsp "Enter new password: " u_pass
    echo

    (cd "$SERVER_DIR" && runuser -u "$SERVICE_USER" -- env PLAYAURAL_CLI_PW="$u_pass" "$VENV_PYTHON" "$SERVER_DIR/cli.py" reset-password "$u_name")
    pause_screen
}

uninstall_voice_service() {
    say_warn "Disabling the voice service. The binary and configuration files will be kept."
    systemctl stop "$VOICE_SERVICE_NAME" >/dev/null 2>&1 || true
    systemctl disable "$VOICE_SERVICE_NAME" >/dev/null 2>&1 || true
    rm -f "$VOICE_SERVICE_FILE"
    systemctl daemon-reload
    say_ok "Voice service removed from systemd."
    pause_screen
}

uninstall_service() {
    say_warn "Disabling the game server service. Repository files will be kept."
    systemctl stop "$SERVICE_NAME" >/dev/null 2>&1 || true
    systemctl disable "$SERVICE_NAME" >/dev/null 2>&1 || true
    rm -f "$SERVICE_FILE"
    systemctl daemon-reload
    say_ok "Game server service removed from systemd."
    pause_screen
}

show_menu() {
    clear
    echo "=================================================="
    echo " PlayAural Server and Voice Manager"
    echo " Repo:  $REPO_DIR"
    echo " Server: $SERVER_DIR"
    echo "=================================================="
    check_status
    echo "=================================================="
    echo " 1. Start Game Server"
    echo " 2. Stop Game Server"
    echo " 3. Restart Game Server"
    echo " 4. View Game Logs"
    echo " 5. Clear Logs and Python Cache"
    echo " 6. Create User"
    echo " 7. Reset User Password"
    echo " 8. Install or Repair Game Environment"
    echo " 9. Install or Update Voice Server"
    echo "10. Configure Voice Server"
    echo "11. Change Voice Server URL / Domain"
    echo "12. Start Voice Server"
    echo "13. Stop Voice Server"
    echo "14. Restart Voice Server"
    echo "15. View Voice Logs"
    echo "16. Show Voice Configuration"
    echo "17. Uninstall Voice Service"
    echo "18. Uninstall Game Service"
    echo " 0. Exit"
    echo "=================================================="
    read -rp "Choose an option: " choice
}

check_root
ensure_config_dir

while true; do
    show_menu
    case "${choice:-}" in
        1) start_server ;;
        2) stop_server ;;
        3) restart_server ;;
        4) view_logs ;;
        5) clear_logs ;;
        6) create_user ;;
        7) reset_password ;;
        8) install_environment; pause_screen ;;
        9) install_voice_stack ;;
        10) configure_voice_server; pause_screen ;;
        11) change_voice_url; pause_screen ;;
        12) start_voice_server ;;
        13) stop_voice_server ;;
        14) restart_voice_server ;;
        15) view_voice_logs ;;
        16) show_voice_config; pause_screen ;;
        17) uninstall_voice_service ;;
        18) uninstall_service ;;
        0) exit 0 ;;
        *) say_error "Invalid option."; pause_screen ;;
    esac
done
