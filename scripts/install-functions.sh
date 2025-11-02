#!/bin/bash

# HacknoverNGFW Installation Functions
# This file contains all the functions used by install.sh

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo -e "\n${CYAN}=== $1 ===${NC}" | tee -a "$LOG_FILE"
}

# System requirement checks
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        export OS_NAME="$NAME"
        export OS_ID="$ID"
        export OS_VERSION="$VERSION_ID"
        export OS_ID_LIKE="$ID_LIKE"
        log_info "Detected OS: $OS_NAME $OS_VERSION"
        log_info "OS ID: $OS_ID, Based on: $OS_ID_LIKE"
        
        # Determine OS family for package management
        if [[ "$ID" == "kali" ]] || [[ "$ID_LIKE" =~ .*debian.* ]]; then
            export OS_FAMILY="debian"
            log_info "Detected Debian-based system"
        elif [[ "$ID" =~ (ubuntu|debian|linuxmint|pop) ]]; then
            export OS_FAMILY="debian"
            log_info "Detected Debian-based system"
        elif [[ "$ID" =~ (centos|rhel|fedora|rocky|almalinux) ]] || [[ "$ID_LIKE" =~ .*rhel.*|.*fedora.* ]]; then
            export OS_FAMILY="redhat"
            log_info "Detected Red Hat-based system"
        elif [[ "$ID" =~ (arch|manjaro) ]] || [[ "$ID_LIKE" =~ .*arch.* ]]; then
            export OS_FAMILY="arch"
            log_info "Detected Arch-based system"
        else
            export OS_FAMILY="unknown"
            log_warning "Unknown OS family, will attempt package manager detection"
        fi
    else
        log_error "Cannot detect operating system - /etc/os-release not found"
        return 1
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        log_info "Python version: $PYTHON_VERSION"
        
        # Check Python version compatibility
        if [[ "$(printf '%s\n' "3.7" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.7" ]]; then
            log_warning "Python version < 3.7 may have compatibility issues"
        fi
    else
        log_error "Python3 is not installed"
        return 1
    fi
    
    # Check available disk space
    if command -v df &> /dev/null; then
        local available_kb
        available_kb=$(df . 2>/dev/null | awk 'NR==2 {print $4}' || df / 2>/dev/null | awk 'NR==2 {print $4}')
        if [[ -n "$available_kb" && "$available_kb" -lt 1048576 ]]; then  # Less than 1GB
            log_warning "Low disk space. Recommended: at least 1GB free"
        fi
    else
        log_warning "Cannot check disk space (df command not available)"
    fi
    
    # Check memory
    if command -v free &> /dev/null; then
        local total_mem
        total_mem=$(free -m 2>/dev/null | awk 'NR==2 {print $2}' || echo "0")
        if [[ "$total_mem" -lt 512 ]]; then  # Less than 512MB
            log_warning "Low memory. Recommended: at least 512MB RAM"
        fi
    else
        log_warning "Cannot check memory (free command not available)"
    fi
    
    # Check essential commands
    local missing_commands=()
    for cmd in grep awk sed; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [[ ${#missing_commands[@]} -gt 0 ]]; then
        log_warning "Missing basic commands: ${missing_commands[*]} - these will be installed with dependencies"
    fi
    
    log_success "System requirements check passed"
    return 0
}

# Detect and install packages based on available package manager
detect_and_install_packages() {
    log_info "Attempting to detect package manager and install dependencies..."
    
    if command -v apt-get &> /dev/null; then
        log_info "Detected apt-get, using Debian/Ubuntu/Kali package list"
        if ! apt-get update; then
            log_error "Failed to update package lists"
            return 1
        fi
        if ! apt-get install -y \
            python3-pip \
            python3-venv \
            net-tools \
            iptables \
            tcpdump \
            build-essential \
            libssl-dev \
            libffi-dev \
            python3-dev \
            libxml2-dev \
            libxslt1-dev \
            zlib1g-dev \
            grep \
            sed \
            awk; then
            log_error "Failed to install packages with apt-get"
            return 1
        fi
        
    elif command -v dnf &> /dev/null; then
        log_info "Detected dnf, using Fedora/RHEL package list"
        if ! dnf update -y; then
            log_error "Failed to update package lists"
            return 1
        fi
        if ! dnf install -y \
            python3-pip \
            python3-devel \
            net-tools \
            iptables \
            tcpdump \
            gcc \
            openssl-devel \
            libffi-devel \
            libxml2-devel \
            libxslt-devel \
            gcc-c++ \
            grep \
            sed \
            awk; then
            log_error "Failed to install packages with dnf"
            return 1
        fi
        
    elif command -v yum &> /dev/null; then
        log_info "Detected yum, using CentOS/RHEL package list"
        if ! yum update -y; then
            log_error "Failed to update package lists"
            return 1
        fi
        if ! yum install -y \
            python3-pip \
            python3-devel \
            net-tools \
            iptables \
            tcpdump \
            gcc \
            openssl-devel \
            libffi-devel \
            libxml2-devel \
            libxslt-devel \
            gcc-c++ \
            grep \
            sed \
            awk; then
            log_error "Failed to install packages with yum"
            return 1
        fi
        
    elif command -v pacman &> /dev/null; then
        log_info "Detected pacman, using Arch/Manjaro package list"
        if ! pacman -Syu --noconfirm; then
            log_error "Failed to update package lists"
            return 1
        fi
        if ! pacman -S --noconfirm \
            python-pip \
            python-virtualenv \
            net-tools \
            iptables \
            tcpdump \
            gcc \
            openssl \
            libffi \
            pkgconf \
            grep \
            sed \
            awk; then
            log_error "Failed to install packages with pacman"
            return 1
        fi
        
    else
        log_error "Cannot detect supported package manager (apt-get, dnf, yum, or pacman)"
        return 1
    fi
    
    return 0
}

# Install system dependencies
install_system_dependencies() {
    log_info "Installing system dependencies for $OS_NAME..."
    
    # Use OS family for package management
    case "$OS_FAMILY" in
        debian)
            if command -v apt-get &> /dev/null; then
                log_info "Using apt-get for Debian/Ubuntu/Kali Linux"
                if ! apt-get update; then
                    log_error "Failed to update package lists"
                    return 1
                fi
                if ! apt-get install -y \
                    python3-pip \
                    python3-venv \
                    net-tools \
                    iptables \
                    tcpdump \
                    build-essential \
                    libssl-dev \
                    libffi-dev \
                    python3-dev \
                    libxml2-dev \
                    libxslt1-dev \
                    zlib1g-dev \
                    grep \
                    sed \
                    awk; then
                    log_error "Failed to install packages with apt-get"
                    return 1
                fi
            else
                log_error "apt-get not found on Debian-based system"
                return 1
            fi
            ;;
        redhat)
            if command -v dnf &> /dev/null; then
                log_info "Using dnf for Fedora/RHEL/CentOS"
                if ! dnf update -y; then
                    log_error "Failed to update package lists"
                    return 1
                fi
                if ! dnf install -y \
                    python3-pip \
                    python3-devel \
                    net-tools \
                    iptables \
                    tcpdump \
                    gcc \
                    openssl-devel \
                    libffi-devel \
                    libxml2-devel \
                    libxslt-devel \
                    gcc-c++ \
                    grep \
                    sed \
                    awk; then
                    log_error "Failed to install packages with dnf"
                    return 1
                fi
            elif command -v yum &> /dev/null; then
                log_info "Using yum for CentOS/RHEL"
                if ! yum update -y; then
                    log_error "Failed to update package lists"
                    return 1
                fi
                if ! yum install -y \
                    python3-pip \
                    python3-devel \
                    net-tools \
                    iptables \
                    tcpdump \
                    gcc \
                    openssl-devel \
                    libffi-devel \
                    libxml2-devel \
                    libxslt-devel \
                    gcc-c++ \
                    grep \
                    sed \
                    awk; then
                    log_error "Failed to install packages with yum"
                    return 1
                fi
            else
                log_error "Neither dnf nor yum found on Red Hat-based system"
                return 1
            fi
            ;;
        arch)
            if command -v pacman &> /dev/null; then
                log_info "Using pacman for Arch/Manjaro"
                if ! pacman -Syu --noconfirm; then
                    log_error "Failed to update package lists"
                    return 1
                fi
                if ! pacman -S --noconfirm \
                    python-pip \
                    python-virtualenv \
                    net-tools \
                    iptables \
                    tcpdump \
                    gcc \
                    openssl \
                    libffi \
                    pkgconf \
                    grep \
                    sed \
                    awk; then
                    log_error "Failed to install packages with pacman"
                    return 1
                fi
            else
                log_error "pacman not found on Arch-based system"
                return 1
            fi
            ;;
        *)
            log_warning "Unknown OS family '$OS_FAMILY', attempting automatic package manager detection..."
            if ! detect_and_install_packages; then
                log_error "Failed to install dependencies using automatic detection"
                return 1
            fi
            ;;
    esac
    
    # Verify critical dependencies were installed
    log_info "Verifying critical dependencies..."
    local missing_deps=()
    for dep in python3 pip3 iptables; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing critical dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    log_success "System dependencies installed successfully"
    return 0
}

# Setup Python virtual environment
setup_python_environment() {
    log_info "Setting up Python virtual environment..."
    
    # Create virtual environment
    if [[ ! -d "hacknover-env" ]]; then
        if ! python3 -m venv hacknover-env; then
            log_error "Failed to create virtual environment"
            return 1
        fi
        log_success "Created virtual environment: hacknover-env"
    else
        log_warning "Virtual environment already exists, reusing it"
    fi
    
    # Activate virtual environment
    if ! source hacknover-env/bin/activate; then
        log_error "Failed to activate virtual environment"
        return 1
    fi
    
    # Upgrade pip
    log_info "Upgrading pip..."
    if ! pip install --upgrade pip; then
        log_error "Failed to upgrade pip"
        return 1
    fi
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing Python dependencies from requirements.txt..."
        if ! pip install -r requirements.txt; then
            log_error "Failed to install Python dependencies from requirements.txt"
            log_info "Attempting to install common dependencies individually..."
            
            # Fallback to common dependencies
            local common_packages=(
                "requests"
                "flask"
                "psutil"
                "netifaces"
                "pyyaml"
                "click"
            )
            
            for package in "${common_packages[@]}"; do
                if ! pip install "$package"; then
                    log_warning "Failed to install $package"
                fi
            done
        fi
    else
        log_warning "requirements.txt not found, installing basic dependencies..."
        local basic_packages=(
            "requests>=2.25.1"
            "flask>=2.0.0"
            "psutil>=5.8.0"
            "netifaces>=0.11.0"
            "pyyaml>=5.4.0"
            "click>=8.0.0"
        )
        
        for package in "${basic_packages[@]}"; do
            if ! pip install "$package"; then
                log_error "Failed to install basic dependency: $package"
                return 1
            fi
        done
    fi
    
    # Verify Python environment
    log_info "Verifying Python environment..."
    if ! python3 -c "import flask, requests, psutil" &> /dev/null; then
        log_error "Failed to verify Python environment - missing critical packages"
        return 1
    fi
    
    log_success "Python environment setup completed"
    return 0
}

# Interactive configuration setup
setup_configuration_interactive() {
    log_info "Starting interactive configuration..."
    
    # Check if config exists
    if [[ ! -f "config.json" ]]; then
        if [[ -f "config-template.json" ]]; then
            cp config-template.json config.json
            log_info "Created config.json from template"
        else
            log_warning "No config template found, creating basic config..."
            create_basic_config
        fi
    fi
    
    # Detect available network interfaces
    log_info "Detecting network interfaces..."
    local interfaces=()
    if command -v ip &> /dev/null; then
        interfaces=($(ip link show | grep -E '^[0-9]+:' | awk -F: '{print $2}' | grep -v lo | sed 's/ //g'))
    elif command -v ifconfig &> /dev/null; then
        interfaces=($(ifconfig -a | grep -E '^[a-zA-Z]' | awk '{print $1}' | grep -v lo))
    else
        interfaces=("eth0" "ens33" "wlan0")
    fi
    
    if [[ ${#interfaces[@]} -eq 0 ]]; then
        interfaces=("eth0" "ens33" "wlan0")
    fi
    
    echo "Available network interfaces: ${interfaces[*]}"
    
    # Get user input with validation
    while true; do
        read -p "Enter network interface to monitor [${interfaces[0]}]: " interface
        interface=${interface:-${interfaces[0]}}
        
        if [[ " ${interfaces[*]} " =~ " ${interface} " ]] || [[ "$interface" == "eth0" ]]; then
            break
        else
            log_warning "Interface '$interface' not found in detected interfaces. Using anyway..."
            break
        fi
    done
    
    while true; do
        read -p "Enter admin web interface port [8080]: " port
        port=${port:-8080}
        
        if [[ "$port" =~ ^[0-9]+$ ]] && [ "$port" -ge 1 ] && [ "$port" -le 65535 ]; then
            break
        else
            log_warning "Port must be a number between 1 and 65535"
        fi
    done
    
    while true; do
        read -p "Enter log level (INFO/DEBUG/WARNING/ERROR) [INFO]: " log_level
        log_level=${log_level:-INFO}
        log_level=${log_level^^}  # Convert to uppercase
        
        if [[ "$log_level" =~ ^(INFO|DEBUG|WARNING|ERROR)$ ]]; then
            break
        else
            log_warning "Log level must be INFO, DEBUG, WARNING, or ERROR"
        fi
    done
    
    # Update configuration
    update_configuration "$interface" "$port" "$log_level"
    
    log_success "Interactive configuration completed"
}

# Non-interactive configuration setup
setup_configuration_noninteractive() {
    log_info "Setting up non-interactive configuration..."
    
    if [[ ! -f "config.json" ]]; then
        if [[ -f "config-template.json" ]]; then
            cp config-template.json config.json
        else
            create_basic_config
        fi
    fi
    
    # Use default values
    update_configuration "eth0" "8080" "INFO"
    
    log_success "Non-interactive configuration completed"
}

# Create basic configuration file
create_basic_config() {
    cat > config.json << 'EOF'
{
    "network_interface": "eth0",
    "admin_port": 8080,
    "log_level": "INFO",
    "database_path": "./hacknover.db",
    "firewall": {
        "default_policy": "drop",
        "rules": []
    },
    "web_filter": {
        "enabled": true,
        "blocked_categories": [],
        "allowed_domains": [],
        "blocked_domains": []
    },
    "logging": {
        "enabled": true,
        "max_size_mb": 100,
        "backup_count": 5
    }
}
EOF
    log_info "Created basic config.json"
}

# Update configuration values
update_configuration() {
    local interface="$1"
    local port="$2"
    local log_level="$3"
    
    log_info "Updating configuration: interface=$interface, port=$port, log_level=$log_level"
    
    # Use Python for JSON manipulation (more reliable than sed)
    if ! python3 - << EOF 2>> "$LOG_FILE"; then
import json
import sys

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Update basic settings
    config['network_interface'] = '$interface'
    config['admin_port'] = $port
    config['log_level'] = '$log_level'
    
    # Ensure nested structures exist
    if 'firewall' not in config:
        config['firewall'] = {'default_policy': 'drop', 'rules': []}
    
    if 'web_filter' not in config:
        config['web_filter'] = {'enabled': True, 'blocked_categories': [], 'allowed_domains': [], 'blocked_domains': []}
    
    if 'logging' not in config:
        config['logging'] = {'enabled': True, 'max_size_mb': 100, 'backup_count': 5}
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("Configuration updated successfully")
except Exception as e:
    print(f"Config update failed: {e}")
    sys.exit(1)
EOF
        log_warning "Could not update config using Python, using fallback method"
        # Fallback: create new config file
        create_basic_config
    fi
}

# Setup firewall rules
setup_firewall_rules() {
    log_info "Setting up initial firewall rules..."
    
    # Create rules directory
    mkdir -p rules
    
    # Create sample firewall rules
    if [[ ! -f "rules/firewall-rules.json" ]]; then
        cat > rules/firewall-rules.json << 'EOF'
[
    {
        "rule_name": "allow_ssh",
        "protocol": "tcp",
        "port": 22,
        "action": "allow",
        "direction": "inbound",
        "enabled": true,
        "description": "Allow SSH connections"
    },
    {
        "rule_name": "allow_http",
        "protocol": "tcp",
        "port": 80,
        "action": "allow", 
        "direction": "inbound",
        "enabled": true,
        "description": "Allow HTTP traffic"
    },
    {
        "rule_name": "allow_https",
        "protocol": "tcp",
        "port": 443,
        "action": "allow",
        "direction": "inbound", 
        "enabled": true,
        "description": "Allow HTTPS traffic"
    },
    {
        "rule_name": "allow_dns",
        "protocol": "udp",
        "port": 53,
        "action": "allow",
        "direction": "outbound",
        "enabled": true,
        "description": "Allow DNS queries"
    },
    {
        "rule_name": "allow_loopback",
        "protocol": "all",
        "interface": "lo",
        "action": "allow",
        "direction": "both",
        "enabled": true,
        "description": "Allow loopback traffic"
    }
]
EOF
        log_success "Created sample firewall rules at rules/firewall-rules.json"
    else
        log_info "Firewall rules already exist at rules/firewall-rules.json"
    fi
    
    # Create web filter rules if they don't exist
    if [[ ! -f "rules/web-filter-rules.json" ]]; then
        cat > rules/web-filter-rules.json << 'EOF'
{
    "blocked_categories": [
        "malware",
        "phishing",
        "adult"
    ],
    "allowed_domains": [
        "github.com",
        "python.org",
        "stackoverflow.com"
    ],
    "blocked_domains": [
        "example-malware.com",
        "bad-site.org"
    ],
    "time_restrictions": []
}
EOF
        log_success "Created web filter rules at rules/web-filter-rules.json"
    fi
}

# Install system service
install_system_service() {
    log_info "Installing system service..."
    
    if [[ $EUID -ne 0 ]]; then
        log_warning "Not running as root, skipping service installation"
        return 0
    fi
    
    # Get the actual user who invoked sudo
    local real_user
    if [[ -n "$SUDO_USER" ]]; then
        real_user="$SUDO_USER"
    else
        real_user=$(whoami)
    fi
    
    # Create service file
    cat > /etc/systemd/system/hacknover-ngfw.service << EOF
[Unit]
Description=Hacknover Next Generation Firewall
After=network.target
Wants=network.target
Documentation=https://github.com/Kolawole-Ibrahim/HacknoverNGFW

[Service]
Type=simple
User=$real_user
Group=$real_user
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/hacknover-env/bin
ExecStart=$INSTALL_DIR/hacknover-env/bin/python3 main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable hacknover-ngfw.service
    
    log_success "System service installed and enabled"
    log_info "To start the service: sudo systemctl start hacknover-ngfw"
    log_info "To check status: sudo systemctl status hacknover-ngfw"
    log_info "To view logs: sudo journalctl -u hacknover-ngfw -f"
}

# Finalize installation
finalize_installation() {
    log_section "Installation Complete"
    
    log_success "HacknoverNGFW has been successfully installed!"
    
    # Display installation summary
    echo ""
    log_info "Installation Summary:"
    echo "  - Installation directory: $INSTALL_DIR"
    echo "  - Python virtual environment: $INSTALL_DIR/hacknover-env"
    echo "  - Configuration file: $INSTALL_DIR/config.json"
    echo "  - Firewall rules: $INSTALL_DIR/rules/firewall-rules.json"
    echo "  - Web filter rules: $INSTALL_DIR/rules/web-filter-rules.json"
    echo "  - Log file: $LOG_FILE"
    
    # Display next steps
    echo ""
    log_info "Next steps:"
    echo "  1. Review configuration: cat config.json"
    echo "  2. Customize firewall rules: nano rules/firewall-rules.json"
    echo "  3. Customize web filter rules: nano rules/web-filter-rules.json"
    
    if [[ "$SKIP_SERVICE" == false ]] && [[ $EUID -eq 0 ]]; then
        echo "  4. Start the service: sudo systemctl start hacknover-ngfw"
        echo "  5. Access web interface: http://localhost:8080"
        echo "  6. Check service status: sudo systemctl status hacknover-ngfw"
    else
        echo "  4. Manual start: source hacknover-env/bin/activate && python3 main.py"
        echo "  5. Access web interface: http://localhost:8080"
    fi
    
    echo ""
    log_info "For support, check the documentation or project README"
    echo "Project URL: https://github.com/Kolawole-Ibrahim/HacknoverNGFW"
    
    # Save installation info
    cat > "$INSTALL_DIR/installation-info.txt" << EOF
HacknoverNGFW Installation Details
==================================
Installation Date: $(date)
Installation Directory: $INSTALL_DIR
Python Virtual Environment: $INSTALL_DIR/hacknover-env
Configuration: $INSTALL_DIR/config.json
Firewall Rules: $INSTALL_DIR/rules/firewall-rules.json
Web Filter Rules: $INSTALL_DIR/rules/web-filter-rules.json
Log File: $LOG_FILE

Service Commands:
- Start: systemctl start hacknover-ngfw
- Stop: systemctl stop hacknover-ngfw
- Status: systemctl status hacknover-ngfw
- Logs: journalctl -u hacknover-ngfw -f

Manual Start:
cd $INSTALL_DIR && source hacknover-env/bin/activate && python3 main.py
EOF
    
    log_info "Installation details saved to: $INSTALL_DIR/installation-info.txt"
}