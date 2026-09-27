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
DATABASE_PATH="$SERVER_DIR/PlayAural.db"
DATABASE_BACKUP_DIR="$SERVER_DIR/backups"
SERVICE_RESTART_DELAY_SECONDS=10
SERVICE_START_LIMIT_INTERVAL_SECONDS=300
SERVICE_START_LIMIT_BURST=3

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

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
    local candidate

    for candidate in python3.12 python3.11 python3; do
        if command_exists "$candidate" && \
            "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' \
                >/dev/null 2>&1; then
            echo "$candidate"
            return
        fi
    done
    echo ""
}

load_server_dependencies() {
    "$VENV_PYTHON" - "$SERVER_DIR/pyproject.toml" <<'PY'
import sys
import tomllib

with open(sys.argv[1], "rb") as project_file:
    project = tomllib.load(project_file)

dependencies = project.get("project", {}).get("dependencies")
if (
    not isinstance(dependencies, list)
    or not dependencies
    or not all(isinstance(dependency, str) and dependency for dependency in dependencies)
):
    raise SystemExit("project.dependencies must be a non-empty list of strings")

print(*dependencies, sep="\n")
PY
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

prepare_database_storage() {
    local path

    if ! install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0700 "$DATABASE_BACKUP_DIR"; then
        say_error "Could not prepare the database backup directory: $DATABASE_BACKUP_DIR"
        return 1
    fi
    for path in \
        "$DATABASE_PATH" \
        "$DATABASE_PATH-wal" \
        "$DATABASE_PATH-shm" \
        "$DATABASE_PATH-journal" \
        "$SERVER_DIR/errors.log"; do
        if [ -e "$path" ]; then
            if ! chown "$SERVICE_USER:$SERVICE_USER" "$path"; then
                say_error "Could not assign database storage ownership: $path"
                return 1
            fi
            if ! chmod 600 "$path"; then
                say_error "Could not apply private database storage permissions: $path"
                return 1
            fi
        fi
    done
    if ! find "$DATABASE_BACKUP_DIR" -type f -exec chmod 600 {} +; then
        say_error "Could not apply private permissions to existing database backups."
        return 1
    fi
}

fix_permissions() {
    if ! chown -R "$SERVICE_USER:$SERVICE_USER" "$SERVER_DIR"; then
        say_error "Could not assign the game server files to $SERVICE_USER."
        return 1
    fi
    if ! find "$SERVER_DIR" -type d -exec chmod 755 {} +; then
        say_error "Could not normalize game server directory permissions."
        return 1
    fi
    prepare_database_storage || return 1
}

probe_service_directory() {
    local directory="$1"

    runuser -u "$SERVICE_USER" -- "$VENV_PYTHON" - "$directory" <<'PY'
import os
import sys
import tempfile

directory = os.path.abspath(sys.argv[1])
probe_path = None
try:
    descriptor, probe_path = tempfile.mkstemp(
        prefix=".playaural-write-probe-",
        dir=directory,
    )
    with os.fdopen(descriptor, "wb") as probe:
        probe.write(b"\0" * 4096)
        probe.flush()
        os.fsync(probe.fileno())
    os.unlink(probe_path)
    probe_path = None
    directory_descriptor = os.open(
        directory,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
    )
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)
finally:
    if probe_path is not None:
        try:
            os.unlink(probe_path)
        except FileNotFoundError:
            pass
PY
}

verify_database_storage() {
    local path

    for path in \
        "$DATABASE_PATH" \
        "$DATABASE_PATH-wal" \
        "$DATABASE_PATH-shm" \
        "$DATABASE_PATH-journal"; do
        if [ -e "$path" ]; then
            if ! runuser -u "$SERVICE_USER" -- test -r "$path" || \
                ! runuser -u "$SERVICE_USER" -- test -w "$path"; then
                say_error "The service user cannot read and write $path"
                return 1
            fi
        fi
    done

    if ! probe_service_directory "$SERVER_DIR"; then
        say_error "The service user could not durably write in $SERVER_DIR"
        return 1
    fi
    if ! probe_service_directory "$DATABASE_BACKUP_DIR"; then
        say_error "The service user could not durably write in $DATABASE_BACKUP_DIR"
        return 1
    fi

    say_ok "Database storage permissions and durable-write probes passed."
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

VOICE_TLS_CERT_FILE=""
VOICE_TLS_KEY_FILE=""

cert_matches_domain() {
    local cert_file="$1"
    local domain="$2"
    local san_output subject_output wildcard_domain

    if [ ! -f "$cert_file" ]; then
        return 1
    fi

    wildcard_domain=""
    if [[ "$domain" == *.* ]]; then
        wildcard_domain="*.${domain#*.}"
    fi

    san_output="$(openssl x509 -in "$cert_file" -noout -ext subjectAltName 2>/dev/null || true)"
    if printf '%s\n' "$san_output" | grep -Fqi "DNS:$domain"; then
        return 0
    fi
    if [ -n "$wildcard_domain" ] && printf '%s\n' "$san_output" | grep -Fqi "DNS:$wildcard_domain"; then
        return 0
    fi

    subject_output="$(openssl x509 -in "$cert_file" -noout -subject 2>/dev/null || true)"
    if printf '%s\n' "$subject_output" | grep -Eq "CN[[:space:]]*=[[:space:]]*$domain([,/]|\$)"; then
        return 0
    fi
    if [ -n "$wildcard_domain" ] && printf '%s\n' "$subject_output" | grep -Eq "CN[[:space:]]*=[[:space:]]*\\$wildcard_domain([,/]|\$)"; then
        return 0
    fi

    return 1
}

find_existing_tls_pair() {
    local cert_file="$1"
    local key_file="$2"
    local domain="$3"

    if [ -f "$cert_file" ] && [ -f "$key_file" ] && cert_matches_domain "$cert_file" "$domain"; then
        VOICE_TLS_CERT_FILE="$cert_file"
        VOICE_TLS_KEY_FILE="$key_file"
        return 0
    fi

    return 1
}

find_voice_tls_files() {
    local domain="$1"
    local entry cert_file key_file

    VOICE_TLS_CERT_FILE=""
    VOICE_TLS_KEY_FILE=""

    for entry in \
        "/etc/letsencrypt/live/$domain/fullchain.pem|/etc/letsencrypt/live/$domain/privkey.pem" \
        "/etc/letsencrypt/live/$domain/cert.pem|/etc/letsencrypt/live/$domain/privkey.pem" \
        "/home/$domain/ssl.combined|/home/$domain/ssl.key" \
        "/home/$domain/ssl.cert|/home/$domain/ssl.key" \
        "/home/$domain/ssl.certfile|/home/$domain/ssl.keyfile"; do
        cert_file="${entry%%|*}"
        key_file="${entry#*|}"
        if find_existing_tls_pair "$cert_file" "$key_file" "$domain"; then
            return 0
        fi
    done

    for cert_file in /etc/letsencrypt/live/*/fullchain.pem /etc/letsencrypt/live/*/cert.pem; do
        if [ ! -f "$cert_file" ] || ! cert_matches_domain "$cert_file" "$domain"; then
            continue
        fi
        key_file="$(dirname "$cert_file")/privkey.pem"
        if find_existing_tls_pair "$cert_file" "$key_file" "$domain"; then
            return 0
        fi
    done

    for cert_file in /home/*/ssl.combined /home/*/ssl.cert /home/*/ssl.certfile; do
        if [ ! -f "$cert_file" ] || ! cert_matches_domain "$cert_file" "$domain"; then
            continue
        fi
        for key_file in \
            "$(dirname "$cert_file")/ssl.key" \
            "$(dirname "$cert_file")/ssl.keyfile" \
            "$(dirname "$cert_file")/privkey.pem"; do
            if find_existing_tls_pair "$cert_file" "$key_file" "$domain"; then
                return 0
            fi
        done
    done

    return 1
}

copy_voice_tls_files_for_livekit() {
    local domain="$1"
    local source_cert="$2"
    local source_key="$3"
    local safe_domain dest_cert dest_key

    safe_domain="$(printf '%s' "$domain" | tr -c 'A-Za-z0-9_.-' '_')"
    dest_cert="$CONFIG_DIR/livekit-turn-${safe_domain}.fullchain.pem"
    dest_key="$CONFIG_DIR/livekit-turn-${safe_domain}.privkey.pem"

    setup_voice_user
    ensure_config_dir

    if ! cp -f "$source_cert" "$dest_cert"; then
        say_warn "Could not copy TURN certificate from $source_cert"
        return 1
    fi

    if ! cp -f "$source_key" "$dest_key"; then
        say_warn "Could not copy TURN private key from $source_key"
        rm -f "$dest_cert"
        return 1
    fi

    chown "root:$VOICE_SERVICE_USER" "$dest_cert" "$dest_key"
    chmod 640 "$dest_cert" "$dest_key"

    VOICE_TLS_CERT_FILE="$dest_cert"
    VOICE_TLS_KEY_FILE="$dest_key"
    return 0
}

write_livekit_config() {
    local public_url="$1"
    local api_key="$2"
    local api_secret="$3"
    local domain turn_enabled turn_cert turn_key

    domain="$(extract_domain_from_url "$public_url")"
    if [ -z "$domain" ]; then
        say_error "Could not extract a domain from: $public_url"
        return 1
    fi

    turn_enabled="false"
    turn_cert=""
    turn_key=""
    if find_voice_tls_files "$domain"; then
        if copy_voice_tls_files_for_livekit "$domain" "$VOICE_TLS_CERT_FILE" "$VOICE_TLS_KEY_FILE"; then
            turn_enabled="true"
            turn_cert="$VOICE_TLS_CERT_FILE"
            turn_key="$VOICE_TLS_KEY_FILE"
            say_ok "Using copied TLS certificate for TURN: $turn_cert"
        else
            say_warn "A certificate was found for $domain, but it could not be copied for the LiveKit service user. TURN will be disabled."
        fi
    else
        say_warn "No TLS certificate was found for $domain. TURN will be disabled so LiveKit can start safely."
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
  enabled: $turn_enabled
EOF

    if [ "$turn_enabled" = "true" ]; then
        cat >>"$LIVEKIT_CONFIG_FILE" <<EOF
  domain: $domain
  tls_port: 5349
  udp_port: 443
  cert_file: $turn_cert
  key_file: $turn_key
EOF
    fi

    cat >>"$LIVEKIT_CONFIG_FILE" <<EOF

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

    if [ -z "$(detect_python_bin)" ]; then
        dnf install -y python3.12 python3.12-pip >/dev/null 2>&1 || \
        dnf install -y python3.11 python3.11-pip >/dev/null 2>&1 || \
        dnf install -y python3 python3-pip >/dev/null 2>&1 || true
    fi
}

install_environment() {
    local dependencies_output python_bin
    local -a server_packages=()

    setup_system_user || return 1
    install_base_packages

    python_bin="$(detect_python_bin)"
    if [ -z "$python_bin" ]; then
        say_error "No supported Python interpreter was found. Install Python 3.11 or 3.12 and try again."
        pause_screen
        return 1
    fi

    say_info "Using Python interpreter: $python_bin"

    if [ ! -x "$VENV_PYTHON" ] || \
        ! "$VENV_PYTHON" -c \
            'import sys; raise SystemExit(sys.version_info < (3, 11))' \
            >/dev/null 2>&1; then
        say_info "Creating or repairing the virtual environment in $VENV_DIR"
        if ! "$python_bin" -m venv "$VENV_DIR"; then
            say_error "Could not create or repair the virtual environment: $VENV_DIR"
            return 1
        fi
    fi

    say_info "Installing server Python dependencies..."
    if ! "$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel; then
        say_error "Could not update the Python packaging tools."
        return 1
    fi
    if ! dependencies_output="$(load_server_dependencies)"; then
        say_error "Could not read server dependencies from $SERVER_DIR/pyproject.toml"
        return 1
    fi
    if [ -z "$dependencies_output" ]; then
        say_error "No server dependencies were declared in $SERVER_DIR/pyproject.toml"
        return 1
    fi
    mapfile -t server_packages <<<"$dependencies_output"
    if ! "$VENV_PYTHON" -m pip install --upgrade "${server_packages[@]}"; then
        say_error "Could not install the game server dependencies."
        return 1
    fi

    fix_permissions || return 1
    say_ok "Game server environment is ready."
}

ensure_cli_environment() {
    setup_system_user || return 1
    if [ ! -x "$VENV_PYTHON" ]; then
        install_environment
        return $?
    fi
    fix_permissions || return 1
}

run_account_cli() {
    local command_name="$1"
    local username="$2"
    local password="$3"
    shift 3

    (cd "$SERVER_DIR" && runuser -u "$SERVICE_USER" -- env PLAYAURAL_CLI_PW="$password" "$VENV_PYTHON" "$SERVER_DIR/cli.py" "$command_name" "$username" "$@")
}

run_role_cli() {
    local username="$1"
    local role_name="$2"

    (cd "$SERVER_DIR" && runuser -u "$SERVICE_USER" -- \
        "$VENV_PYTHON" "$SERVER_DIR/cli.py" set-user-role \
        "$username" "$role_name" \
        --database "$DATABASE_PATH" \
        --database-backup-dir "$DATABASE_BACKUP_DIR" \
        --confirm-server-stopped)
}

setup_service() {
    setup_system_user || return 1
    ensure_config_dir || return 1

    if ! cat >"$SERVICE_FILE" <<EOF
[Unit]
Description=PlayAural Game Server
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=$SERVICE_START_LIMIT_INTERVAL_SECONDS
StartLimitBurst=$SERVICE_START_LIMIT_BURST

[Service]
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$SERVER_DIR
EnvironmentFile=-$VOICE_ENV_FILE
ExecStart=$VENV_PYTHON $SERVER_DIR/main.py --host 127.0.0.1 --port 8000 --database-backup-dir $DATABASE_BACKUP_DIR
Restart=on-failure
RestartSec=$SERVICE_RESTART_DELAY_SECONDS
UMask=0077
LimitFSIZE=infinity
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=full
ReadWritePaths=$SERVER_DIR

[Install]
WantedBy=multi-user.target
EOF
    then
        say_error "Could not write the systemd service file: $SERVICE_FILE"
        return 1
    fi

    if ! systemctl daemon-reload; then
        say_error "systemd could not reload the game service definition."
        return 1
    fi
    if ! systemctl enable "$SERVICE_NAME" >/dev/null 2>&1; then
        say_error "systemd could not enable the game service."
        return 1
    fi
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
    setup_service || {
        pause_screen
        return 1
    }
    ensure_voice_firewall_rules

    say_ok "Voice server configuration saved."
    echo "Public voice URL: $final_url"
    echo "TURN domain:      $final_domain"
    echo "TURN enabled:     $(awk '/^[[:space:]]*enabled:/ {print $2; exit}' "$LIVEKIT_CONFIG_FILE" 2>/dev/null)"
    if grep -q '^[[:space:]]*cert_file:' "$LIVEKIT_CONFIG_FILE" 2>/dev/null; then
        echo "TURN cert:        $(awk '/^[[:space:]]*cert_file:/ {print $2; exit}' "$LIVEKIT_CONFIG_FILE" 2>/dev/null)"
    else
        echo "TURN cert:        not found; TURN disabled"
    fi
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
        echo "TURN enabled: $(awk '/^[[:space:]]*enabled:/ {print $2; exit}' "$LIVEKIT_CONFIG_FILE" 2>/dev/null)"
        echo "TURN domain:  $(awk '/^[[:space:]]*domain:/ {print $2; exit}' "$LIVEKIT_CONFIG_FILE" 2>/dev/null)"
        echo "TURN cert:    $(awk '/^[[:space:]]*cert_file:/ {print $2; exit}' "$LIVEKIT_CONFIG_FILE" 2>/dev/null)"
        echo "TURN key:     $(awk '/^[[:space:]]*key_file:/ {print $2; exit}' "$LIVEKIT_CONFIG_FILE" 2>/dev/null)"
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

stop_game_service_for_environment_change() {
    if [ ! -e "$SERVICE_FILE" ]; then
        if ! systemctl cat "$SERVICE_NAME" >/dev/null 2>&1; then
            return 0
        fi
    fi

    say_info "Stopping the game server before changing its environment..."
    if ! systemctl stop "$SERVICE_NAME"; then
        say_error "The game server could not be stopped; its environment was not changed."
        return 1
    fi
}

stop_game_service_for_role_change() {
    if [ ! -e "$SERVICE_FILE" ] && \
        ! systemctl cat "$SERVICE_NAME" >/dev/null 2>&1; then
        say_error "The managed game service is not installed, so sc.sh cannot verify that the server is offline."
        say_error "Install the service or stop every manually launched server process before managing roles."
        return 1
    fi

    say_info "Stopping the game server before changing persistent authorization..."
    if ! systemctl stop "$SERVICE_NAME"; then
        say_error "The game server could not be stopped; no role change was attempted."
        return 1
    fi
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        say_error "The game server still reports as active; no role change was attempted."
        return 1
    fi
    say_ok "The game server is stopped. Active sessions cannot retain stale permissions."
}

start_game_service() {
    if ! systemctl reset-failed "$SERVICE_NAME"; then
        say_error "systemd could not reset the game service failure state."
        return 1
    fi
    if ! systemctl start "$SERVICE_NAME"; then
        say_error "systemd could not start the game service."
        return 1
    fi
}

restore_game_service_after_role_operation() {
    if ! start_game_service; then
        return 1
    fi
    sleep 2
    if ! systemctl is-active --quiet "$SERVICE_NAME"; then
        say_error "The game service did not remain active after startup. Review its logs before retrying."
        return 1
    fi
}

start_server() {
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        say_warn "The game server is already running. Performing a controlled restart instead."
        restart_server
        return $?
    fi

    if ! stop_game_service_for_environment_change; then
        pause_screen
        return 1
    fi
    if ! install_environment; then
        say_error "Environment installation failed; the game server remains stopped."
        pause_screen
        return 1
    fi
    if ! setup_service; then
        pause_screen
        return 1
    fi
    verify_database_storage || {
        pause_screen
        return 1
    }

    say_info "Starting game server..."
    if ! start_game_service; then
        pause_screen
        return 1
    fi
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
    if ! stop_game_service_for_environment_change; then
        pause_screen
        return 1
    fi
    if ! install_environment; then
        say_error "Environment installation failed; the game server remains stopped."
        pause_screen
        return 1
    fi
    if ! setup_service; then
        pause_screen
        return 1
    fi
    verify_database_storage || {
        pause_screen
        return 1
    }
    say_info "Restarting game server..."
    if ! start_game_service; then
        pause_screen
        return 1
    fi
    sleep 2
    check_status
    pause_screen
}

repair_game_environment() {
    local was_active=0

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        was_active=1
    fi
    if ! stop_game_service_for_environment_change; then
        return 1
    fi

    if ! install_environment; then
        say_error "Environment repair failed; the game server remains stopped."
        return 1
    fi
    setup_service || return 1
    if ! verify_database_storage; then
        say_error "Storage preflight failed; the game server remains stopped."
        return 1
    fi

    if [ "$was_active" -eq 1 ]; then
        say_info "Starting the game server after environment repair..."
        start_game_service || return 1
    fi
    say_ok "Game server environment repair completed."
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
        setup_service || {
            pause_screen
            return 1
        }
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
    local u_name u_pass result

    ensure_cli_environment || return 1

    echo "--- Create New User ---"
    read -rp "Enter username: " u_name
    if [ -z "$u_name" ]; then
        say_error "Username cannot be empty."
        pause_screen
        return 1
    fi

    read -rsp "Enter password: " u_pass
    echo
    if [ -z "$u_pass" ]; then
        say_error "Password cannot be empty."
        pause_screen
        return 1
    fi

    if run_account_cli create-user "$u_name" "$u_pass"; then
        say_ok "Create user command completed."
        result=0
    else
        say_error "Create user command failed."
        result=1
    fi
    pause_screen
    return "$result"
}

reset_password() {
    local u_name u_pass result

    ensure_cli_environment || return 1

    echo "--- Reset Password ---"
    read -rp "Enter username: " u_name
    if [ -z "$u_name" ]; then
        say_error "Username cannot be empty."
        pause_screen
        return 1
    fi

    read -rsp "Enter new password: " u_pass
    echo
    if [ -z "$u_pass" ]; then
        say_error "Password cannot be empty."
        pause_screen
        return 1
    fi

    if run_account_cli reset-password "$u_name" "$u_pass"; then
        say_ok "Password reset command completed."
        result=0
    else
        say_error "Password reset command failed."
        result=1
    fi
    pause_screen
    return "$result"
}

apply_user_role_change() {
    local username="$1"
    local role_name="$2"
    local was_active=0
    local result=0

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        was_active=1
    fi
    if ! stop_game_service_for_role_change; then
        return 1
    fi
    if ! ensure_cli_environment; then
        say_error "The role-management environment could not be prepared. The game server remains stopped."
        return 1
    fi
    if ! verify_database_storage; then
        say_error "Database storage verification failed. The game server remains stopped and no role change was attempted."
        return 1
    fi

    if run_role_cli "$username" "$role_name"; then
        result=0
    else
        result=$?
    fi
    if [ "$result" -ne 0 ]; then
        if [ "$result" -eq 2 ]; then
            say_warn "The requested role change was rejected without changing the account."
            if [ "$was_active" -eq 1 ]; then
                say_info "Restoring the previously running game service..."
                restore_game_service_after_role_operation || return 1
            fi
        else
            say_error "Role management encountered a database or storage failure."
            say_error "For safety, the game server remains stopped. Review the error and verified backups before starting it."
        fi
        return 1
    fi

    if ! verify_database_storage; then
        say_error "Post-change storage verification failed. The role change may have committed, so the game server remains stopped."
        return 1
    fi
    if [ "$was_active" -eq 1 ]; then
        say_info "Starting the game server after the verified role change..."
        if ! restore_game_service_after_role_operation; then
            say_error "The role change completed, but the game server could not be restarted."
            return 1
        fi
        say_ok "The game server returned to its previous running state."
    else
        say_info "The game server was already stopped and has been left stopped."
    fi
    return 0
}

manage_user_role() {
    local username role_choice role_name confirmation result

    echo "--- User Role Management ---"
    say_warn "This changes production authorization and requires the game server to be offline."
    echo "sc.sh will stop the managed game service, create a verified database backup,"
    echo "apply and verify one atomic role change, and restart the service only if it"
    echo "was previously running and every safety check succeeds."
    echo "The last approved developer cannot be demoted; promote a replacement first."
    say_warn "Ask active users to save and log out before continuing."
    echo
    echo "Roles:"
    echo " 1. User       - normal account access"
    echo " 2. Admin      - moderation and account administration"
    echo " 3. Developer  - full server, database, SMTP, and moderation control"
    echo " 0. Cancel"
    echo

    read -rp "Enter the exact username: " username
    if [ -z "$username" ]; then
        say_error "Username cannot be empty."
        pause_screen
        return 1
    fi
    read -rp "Choose the target role: " role_choice
    case "$role_choice" in
        1) role_name="user" ;;
        2) role_name="admin" ;;
        3) role_name="developer" ;;
        0)
            say_info "Role management cancelled."
            pause_screen
            return 0
            ;;
        *)
            say_error "Invalid role selection."
            pause_screen
            return 1
            ;;
    esac

    echo
    echo "Requested account: $username"
    echo "Requested role:    $role_name"
    read -rp "Type YES to stop the game server and continue: " confirmation
    if [ "$confirmation" != "YES" ]; then
        say_info "Role management cancelled; the game server was not stopped."
        pause_screen
        return 0
    fi

    if apply_user_role_change "$username" "$role_name"; then
        say_ok "User role management completed."
        result=0
    else
        say_error "User role management did not complete successfully."
        result=1
    fi
    pause_screen
    return "$result"
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
    echo "19. Manage User Role (stops game server; verified backup)"
    echo " 0. Exit"
    echo "=================================================="
    read -rp "Choose an option: " choice
}

check_root
if ! ensure_config_dir; then
    say_error "Could not prepare the configuration directory: $CONFIG_DIR"
    exit 1
fi

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
        8) repair_game_environment; pause_screen ;;
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
        19) manage_user_role ;;
        0) exit 0 ;;
        *) say_error "Invalid option."; pause_screen ;;
    esac
done
