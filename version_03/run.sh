#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_SCRIPT="$SCRIPT_DIR/unified_web_agent.py"

setup() {
    echo "Setting up..."
    python3 -m venv "$VENV_DIR" >/dev/null 2>&1
    source "$VENV_DIR/bin/activate"
    pip install playwright python-dotenv requests >/dev/null 2>&1
    playwright install chromium >/dev/null 2>&1
    
    # Ask for browser mode
    echo "Browser mode:"
    echo "1. Headless (invisible, faster)"
    echo "2. Headed (visible window)"
    read -p "Choice: " mode_choice
    
    if [ "$mode_choice" = "2" ]; then
        HEADLESS_MODE="false"
    else
        HEADLESS_MODE="true"
    fi
    
    # Create .env file
    cat > "$SCRIPT_DIR/.env" << EOF
HEADLESS=$HEADLESS_MODE
BROWSER_TIMEOUT=30000
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=800
LOG_LEVEL=INFO
LOG_FILE=web_agent.log
WAIT_FOR_NETWORK=true
SCREENSHOT_QUALITY=90
DISABLE_AUTOMATION_DETECTION=true
EOF
    echo "Done"
}

check_env() {
    if [ -f "$SCRIPT_DIR/.env" ]; then
        echo "Current configuration:"
        cat "$SCRIPT_DIR/.env"
        echo ""
        echo "1. Continue with current settings"
        echo "2. Reconfigure"
        read -p "Choice: " env_choice
        
        if [ "$env_choice" = "2" ]; then
            echo "Browser mode:"
            echo "1. Headless (invisible, faster)"
            echo "2. Headed (visible window)"
            read -p "Choice: " mode_choice
            
            if [ "$mode_choice" = "2" ]; then
                HEADLESS_MODE="false"
            else
                HEADLESS_MODE="true"
            fi
            
            # Update .env file
            sed -i "s/HEADLESS=.*/HEADLESS=$HEADLESS_MODE/" "$SCRIPT_DIR/.env"
            echo "Configuration updated"
        fi
    fi
}

run_app() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Run setup first"
        return 1
    fi
    source "$VENV_DIR/bin/activate"
    python "$PYTHON_SCRIPT" --mode "$1" ${2:+--url "$2"}
}

case "${1:-menu}" in
    setup) setup ;;
    interactive) 
        [ ! -d "$VENV_DIR" ] && setup
        check_env
        run_app interactive ;;
    login) 
        [ ! -d "$VENV_DIR" ] && setup
        check_env
        run_app login ;;
    scraper) 
        [ ! -d "$VENV_DIR" ] && setup
        check_env
        run_app scraper "$2" ;;
    navigate) 
        [ ! -d "$VENV_DIR" ] && setup
        check_env
        run_app navigate "$2" ;;
    menu)
        echo "WEB BROWSING AGENT"
        echo "1. Interactive"
        echo "2. Login"
        echo "3. Scraper"
        echo "4. Navigate"
        echo "5. Exit"
        read -p "Choice: " choice
        case "$choice" in
            1) 
                [ ! -d "$VENV_DIR" ] && setup
                check_env
                run_app interactive ;;
            2) 
                [ ! -d "$VENV_DIR" ] && setup
                check_env
                run_app login ;;
            3) 
                [ ! -d "$VENV_DIR" ] && setup
                check_env
                read -p "URL: " url; run_app scraper "$url" ;;
            4) 
                [ ! -d "$VENV_DIR" ] && setup
                check_env
                read -p "URL: " url; run_app navigate "$url" ;;
            5) exit 0 ;;
        esac
        ;;
esac