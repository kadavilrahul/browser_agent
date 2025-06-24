#!/bin/bash

# =============================================================================
# UNIFIED WEB BROWSING AGENT LAUNCHER
# =============================================================================
# This script combines setup, environment management, and application launching
# into a single convenient shell script.
#
# Usage:
#   ./unified_web_agent.sh                    # Interactive menu
#   ./unified_web_agent.sh setup              # Setup environment only
#   ./unified_web_agent.sh interactive        # Interactive browser mode
#   ./unified_web_agent.sh login              # Login mode
#   ./unified_web_agent.sh scraper <url>      # Web scraper mode
#   ./unified_web_agent.sh navigate <url>     # Navigation mode
# =============================================================================

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
ENV_FILE="$SCRIPT_DIR/.env"
SAMPLE_ENV_FILE="$SCRIPT_DIR/sample.env"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
PYTHON_SCRIPT="$SCRIPT_DIR/unified_web_agent.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to print banner
print_banner() {
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "                    UNIFIED WEB BROWSING AGENT"
    echo "============================================================================="
    echo "  Automated login to websites"
    echo "  Web scraping and element identification"
    echo "  Interactive browser control"
    echo "  Real-time navigation and interaction"
    echo "============================================================================="
    echo -e "${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    log_info "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python 3 found: $PYTHON_VERSION"
        return 0
    else
        log_error "Python 3 not found. Please install Python 3.7 or higher."
        echo "Installation instructions:"
        echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
        echo "  macOS:         brew install python3"
        return 1
    fi
}

# Function to create virtual environment
create_venv() {
    log_info "Creating virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        log_warning "Virtual environment already exists at $VENV_DIR"
        return 0
    fi
    
    if python3 -m venv "$VENV_DIR"; then
        log_success "Virtual environment created successfully"
        return 0
    else
        log_error "Failed to create virtual environment"
        return 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        log_info "Virtual environment activated"
        return 0
    else
        log_error "Virtual environment not found at $VENV_DIR"
        return 1
    fi
}

# Function to deactivate virtual environment
deactivate_venv() {
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
        log_info "Virtual environment deactivated"
    fi
}

# Function to install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_warning "requirements.txt not found. Creating basic requirements..."
        cat > "$REQUIREMENTS_FILE" << 'EOF'
# Core dependencies
playwright==1.41.1
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2

# Web automation essentials
html5lib==1.1
aiohttp==3.9.1
urllib3==2.1.0
EOF
    fi
    
    if pip install -r "$REQUIREMENTS_FILE"; then
        log_success "Python dependencies installed successfully"
    else
        log_error "Failed to install Python dependencies"
        return 1
    fi
    
    # Install Playwright browsers
    log_info "Installing Playwright browsers..."
    if playwright install; then
        log_success "Playwright browsers installed successfully"
    else
        log_error "Failed to install Playwright browsers"
        return 1
    fi
}

# Main setup function
setup_environment() {
    log_header "SETTING UP UNIFIED WEB BROWSING AGENT ENVIRONMENT"
    echo ""
    
    # Check Python
    if ! check_python; then
        return 1
    fi
    
    # Create virtual environment
    if ! create_venv; then
        return 1
    fi
    
    # Activate virtual environment
    if ! activate_venv; then
        return 1
    fi
    
    # Install dependencies
    if ! install_dependencies; then
        deactivate_venv
        return 1
    fi
    
    echo ""
    log_success "Environment setup completed successfully!"
    log_info "You can now run the application with:"
    echo "  ./unified_web_agent.sh interactive"
    echo "  ./unified_web_agent.sh login"
    echo "  ./unified_web_agent.sh scraper <url>"
    echo "  ./unified_web_agent.sh navigate <url>"
    echo ""
    
    deactivate_venv
    return 0
}

# Function to check if environment is ready
check_environment() {
    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment not found. Please run setup first:"
        echo "  ./unified_web_agent.sh setup"
        return 1
    fi
    
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        log_error "Python script not found: $PYTHON_SCRIPT"
        return 1
    fi
    
    return 0
}

# Function to load environment variables
load_env() {
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
        return 0
    else
        log_error ".env file not found. Please run setup first:"
        echo "  ./unified_web_agent.sh setup"
        return 1
    fi
}

# Function to run Python script with proper environment
run_python_script() {
    local mode="$1"
    shift
    local args="$@"
    
    # Check environment
    if ! check_environment; then
        return 1
    fi
    
    # Load environment variables
    if ! load_env; then
        return 1
    fi
    
    # Activate virtual environment
    if ! activate_venv; then
        return 1
    fi
    
    # Show current configuration
    log_info "Current configuration:"
    echo "  Browser Mode: $(if [ "$HEADLESS" = "true" ]; then echo "Headless"; else echo "Visible"; fi)"
    echo "  Mode: $mode"
    if [ -n "$args" ]; then
        echo "  Arguments: $args"
    fi
    echo ""
    
    # Run the Python script
    if [ "$mode" = "menu" ]; then
        python3 "$PYTHON_SCRIPT"
    else
        python3 "$PYTHON_SCRIPT" --mode "$mode" $args
    fi
    
    local exit_code=$?
    
    # Deactivate virtual environment
    deactivate_venv
    
    return $exit_code
}

# Function to show usage help
show_help() {
    print_banner
    echo "USAGE:"
    echo "  $0                          # Interactive menu mode"
    echo "  $0 setup                    # Setup environment and dependencies"
    echo "  $0 interactive              # Interactive browser mode"
    echo "  $0 login                    # Login mode"
    echo "  $0 scraper <url>            # Web scraper mode"
    echo "  $0 navigate <url>           # Navigation mode"
    echo "  $0 help                     # Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 setup                                    # First time setup"
    echo "  $0 interactive                              # Start interactive browser"
    echo "  $0 scraper https://example.com              # Analyze webpage elements"
    echo "  $0 navigate https://google.com              # Navigate to Google"
    echo ""
    echo "MODES:"
    echo "  setup       - Install dependencies and configure environment"
    echo "  interactive - Real-time browser control with commands"
    echo "  login       - Automated website login assistant"
    echo "  scraper     - Analyze and extract clickable elements from webpages"
    echo "  navigate    - Simple webpage navigation with screenshot"
    echo ""
}

# Main script logic
main() {
    # Make script executable
    chmod +x "$0" 2>/dev/null || true
    
    # Parse command line arguments
    case "${1:-}" in
        "setup")
            print_banner
            setup_environment
            ;;
        "interactive")
            print_banner
            log_info "Starting Interactive Browser Mode..."
            run_python_script "interactive"
            ;;
        "login")
            print_banner
            log_info "Starting Login Mode..."
            run_python_script "login"
            ;;
        "scraper")
            if [ -z "${2:-}" ]; then
                log_error "URL required for scraper mode"
                echo "Usage: $0 scraper <url>"
                exit 1
            fi
            print_banner
            log_info "Starting Web Scraper Mode..."
            run_python_script "scraper" "--url" "$2"
            ;;
        "navigate")
            if [ -z "${2:-}" ]; then
                log_error "URL required for navigate mode"
                echo "Usage: $0 navigate <url>"
                exit 1
            fi
            print_banner
            log_info "Starting Navigation Mode..."
            run_python_script "navigate" "--url" "$2"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        "")
            # No arguments - show interactive menu
            print_banner
            log_info "Starting Interactive Menu Mode..."
            run_python_script "menu"
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Trap to ensure cleanup on exit
trap 'deactivate_venv 2>/dev/null || true' EXIT

# Run main function
main "$@"