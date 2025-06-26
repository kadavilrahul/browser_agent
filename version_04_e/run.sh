#!/bin/bash

# Web Browsing Agent - Comprehensive Setup and Runner
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
INTERACTIVE_SCRIPT="$SCRIPT_DIR/interactive_controller.py"
BROWSER_CORE_SCRIPT="$SCRIPT_DIR/browser_core.py"
LOGIN_SCRIPT="$SCRIPT_DIR/login_manager.py"
ELEMENT_SCRIPT="$SCRIPT_DIR/element_analyzer.py"

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            echo "Python $PYTHON_VERSION found"
            return 0
        else
            echo "ERROR: Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        echo "ERROR: Python 3 not found"
        return 1
    fi
}

setup() {
    echo "=== SETUP ==="
    
    # Check Python
    if ! check_python; then
        echo "Please install Python 3.8 or higher"
        exit 1
    fi
    
    # Create virtual environment if needed
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install --upgrade pip >/dev/null 2>&1
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt >/dev/null 2>&1
    else
        pip install playwright python-dotenv requests >/dev/null 2>&1
    fi
    
    # Install Playwright browsers
    echo "Installing Playwright browsers..."
    playwright install chromium >/dev/null 2>&1
    
    # Setup environment file
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        if [ -f "$SCRIPT_DIR/sample.env" ]; then
            cp "$SCRIPT_DIR/sample.env" "$SCRIPT_DIR/.env"
            echo "Environment file created from template"
        else
            # Create basic .env file
            cat > "$SCRIPT_DIR/.env" << EOF
HEADLESS=true
BROWSER_TIMEOUT=30000
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=800
LOG_LEVEL=INFO
LOG_FILE=web_agent.log
WAIT_FOR_NETWORK=true
SCREENSHOT_QUALITY=90
DISABLE_AUTOMATION_DETECTION=true
EOF
            echo "Basic environment file created"
        fi
    fi
    
    echo "Setup completed successfully!"
}

# Check if setup is needed
needs_setup() {
    [ ! -d "$VENV_DIR" ] || [ ! -f "$SCRIPT_DIR/.env" ]
}

# Status check
status() {
    echo "=== STATUS CHECK ==="
    check_python
    
    if [ -d "$VENV_DIR" ]; then
        echo "Virtual environment: EXISTS"
    else
        echo "Virtual environment: MISSING"
    fi
    
    if [ -f "$SCRIPT_DIR/.env" ]; then
        echo "Environment file: EXISTS"
    else
        echo "Environment file: MISSING"
    fi
    
    if [ -f "$INTERACTIVE_SCRIPT" ]; then
        echo "Main script: EXISTS"
    else
        echo "Main script: MISSING"
    fi
}

# Run the application
run_app() {
    if needs_setup; then
        echo "Setup required. Running setup..."
        setup
    fi
    
    # Select version if not already selected
    if [ -z "$SELECTED_SCRIPT" ]; then
        select_version
    fi
    
    source "$VENV_DIR/bin/activate"
    
    case "$1" in
        "interactive")
            echo "Starting Interactive Browser Mode..."
            python "$SELECTED_SCRIPT" --mode interactive
            ;;
        "login")
            echo "Starting Login Mode..."
            python "$SELECTED_SCRIPT" --mode login
            ;;
        "scraper")
            echo "Starting Web Scraper Mode..."
            python "$SELECTED_SCRIPT" --mode scraper ${2:+--url "$2"}
            ;;
        "navigate")
            echo "Starting Navigation Mode..."
            python "$SELECTED_SCRIPT" --mode navigate ${2:+--url "$2"}
            ;;
        *)
            python "$SELECTED_SCRIPT" "$@"
            ;;
    esac
}

# Version selection - simplified to always use interactive controller
select_version() {
    SELECTED_SCRIPT="$INTERACTIVE_SCRIPT"
}


# Main menu
show_menu() {
    echo "=========================================="
    echo "         WEB BROWSING AGENT"
    echo "=========================================="
    echo "1. Browse Website"
    echo "2. Login to Website"
    echo "3. Exit"
    echo "=========================================="
}



# Main execution
case "${1:-menu}" in
    setup) 
        setup 
        ;;
    status) 
        status 
        ;;
    interactive|login|scraper|navigate) 
        run_app "$@" 
        ;;
    menu|"")
        while true; do
            show_menu
            read -p "Choose option (1-3): " choice
            
            case "$choice" in
                1) 
                    run_app interactive 
                    ;;
                2) 
                    run_app login
                    ;;
                3) 
                    echo "Goodbye!"
                    exit 0 
                    ;;
                *) 
                    echo "Invalid choice. Please try again." 
                    ;;
            esac
            echo
            read -p "Press Enter to continue..."
        done
        ;;
    *)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup              - Install dependencies"
        echo "  status             - Check system status"
        echo "  interactive        - Browse websites"
        echo "  login              - Login to websites"
        echo ""
        echo "Run without arguments for menu"
        ;;
esac