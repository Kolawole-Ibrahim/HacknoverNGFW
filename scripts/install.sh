#!/bin/bash
set -e

# HacknoverNGFW Main Installer Script
# This is the main orchestrator that calls functions from install-functions.sh

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source the functions
if [[ -f "$SCRIPT_DIR/install-functions.sh" ]]; then
    source "$SCRIPT_DIR/install-functions.sh"
else
    echo "ERROR: install-functions.sh not found in $SCRIPT_DIR"
    exit 1
fi

# Default values
INTERACTIVE=true
SKIP_SERVICE=false
INSTALL_DIR="$PROJECT_ROOT"
LOG_FILE="$PROJECT_ROOT/install.log"

# Installation info
INSTALL_START_TIME=$(date)

# Usage information
show_usage() {
    echo "HacknoverNGFW Installation Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -y, --non-interactive  Run non-interactively with defaults"
    echo "  -s, --skip-service  Skip system service installation"
    echo "  -d, --dir PATH      Installation directory (default: current dir)"
    echo "  -l, --log FILE      Log file path (default: install.log)"
    echo ""
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -y|--non-interactive)
                INTERACTIVE=false
                ;;
            -s|--skip-service)
                SKIP_SERVICE=true
                ;;
            -d|--dir)
                INSTALL_DIR="$2"
                shift
                ;;
            -l|--log)
                LOG_FILE="$2"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
        shift
    done
}

# Pre-flight checks
pre_flight_checks() {
    log_info "Running pre-flight checks..."
    
    # Check if we're in a git repository
    if [[ -d ".git" ]]; then
        log_info "Git repository detected"
    fi
    
    # Check basic system info
    log_info "System: $(uname -s) $(uname -r) $(uname -m)"
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_info "Running with root privileges"
    else
        log_warning "Running without root privileges - some features may be limited"
    fi
    
    # Check for essential commands without bc
    local missing_commands=()
    for cmd in python3 grep awk sed; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [[ ${#missing_commands[@]} -gt 0 ]]; then
        log_warning "Missing commands that will be installed: ${missing_commands[*]}"
    fi
    
    # Create log file directory if it doesn't exist
    local log_dir=$(dirname "$LOG_FILE")
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir"
    fi
    
    # Test write access to log file
    if ! touch "$LOG_FILE" 2>/dev/null; then
        log_error "Cannot write to log file: $LOG_FILE"
        return 1
    fi
}

# Initialize installation
init_installation() {
    log_info "Installation started at: $(date)"
    log_info "Log file: $LOG_FILE"
    log_info "Installation directory: $INSTALL_DIR"
    log_info "Interactive mode: $INTERACTIVE"
    
    # Validate installation directory
    if [[ ! -d "$INSTALL_DIR" ]]; then
        log_error "Installation directory does not exist: $INSTALL_DIR"
        exit 1
    fi
    
    cd "$INSTALL_DIR"
    log_info "Working directory: $(pwd)"
    
    # Run pre-flight checks
    if ! pre_flight_checks; then
        log_error "Pre-flight checks failed"
        exit 1
    fi
}

# Check if installation can proceed after system checks
can_proceed_with_installation() {
    local check_result=$?
    if [[ $check_result -ne 0 ]]; then
        log_error "System requirements check failed. Cannot proceed with installation."
        return $check_result
    fi
    return 0
}

# Check if installation can proceed after dependency installation
can_proceed_after_dependencies() {
    local deps_result=$?
    if [[ $deps_result -ne 0 ]]; then
        log_error "Dependency installation failed. Cannot proceed with installation."
        return $deps_result
    fi
    return 0
}

# Main installation sequence
main_installation() {
    log_info "Starting installation sequence..."
    
    # Step 1: System checks
    log_section "System Requirements Check"
    if ! check_system_requirements; then
        log_error "System requirements check failed"
        return 1
    fi
    
    # Check if we can proceed
    if ! can_proceed_with_installation; then
        return 1
    fi
    
    # Step 2: Dependencies
    log_section "Installing Dependencies"
    if ! install_system_dependencies; then
        log_error "Dependency installation failed"
        return 1
    fi
    
    # Check if we can proceed
    if ! can_proceed_after_dependencies; then
        return 1
    fi
    
    # Step 3: Python environment
    log_section "Python Environment Setup"
    if ! setup_python_environment; then
        log_error "Python environment setup failed"
        return 1
    fi
    
    # Step 4: Configuration
    log_section "Configuration Setup"
    if [[ "$INTERACTIVE" == true ]]; then
        setup_configuration_interactive
    else
        setup_configuration_noninteractive
    fi
    
    # Step 5: Firewall rules
    log_section "Firewall Rules Setup"
    setup_firewall_rules
    
    # Step 6: Service setup (optional)
    if [[ "$SKIP_SERVICE" == false ]]; then
        log_section "Service Installation"
        install_system_service
    else
        log_info "Skipping service installation as requested"
    fi
    
    # Step 7: Finalize
    log_section "Finalizing Installation"
    finalize_installation
    
    return 0
}

# Cleanup on failure
cleanup_on_failure() {
    log_error "Installation failed or was interrupted"
    log_info "Check the log file for details: $LOG_FILE"
    log_info "You may need to manually clean up before retrying installation"
}

# Main function
main() {
    local installation_successful=false
    
    # Set trap for cleanup on failure
    trap cleanup_on_failure EXIT
    
    parse_arguments "$@"
    init_installation
    
    if main_installation; then
        installation_successful=true
        trap - EXIT  # Remove trap on success
    else
        installation_successful=false
    fi
    
    if [[ "$installation_successful" == true ]]; then
        log_info "Installation finished at: $(date)"
        exit 0
    else
        log_info "Installation finished at: $(date)"
        exit 1
    fi
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi