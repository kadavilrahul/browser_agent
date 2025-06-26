#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Function to display the menu
show_menu() {
    echo ""
    echo "1. Run browse.py"
    echo "2. Run login.py"
    echo "3. Exit"
}

# Function to check if setup is needed
check_setup() {
    if [ ! -d "venv" ]; then
        echo "First time setup required..."
        setup_agent
    fi
}

# Function to set up the environment
setup_agent() {
    echo "Setting up..."
    python3 -m venv venv && \
    source venv/bin/activate && \
    pip install -r requirements.txt && \
    playwright install
    echo "Done."
}

# Function to run browse.py
run_browse() {
    check_setup
    source venv/bin/activate
    pip install -r requirements.txt
    # Reload .env to ensure latest environment variables are used
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    if [ "$HEADLESS_MODE" = "true" ]; then
        python3 browse.py --headless --no-menu
    else
        python3 browse.py --no-menu
    fi
}



run_login() {
    check_setup
    source venv/bin/activate
    pip install -r requirements.txt
    # Reload .env to ensure latest environment variables are used
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    python3 login.py "$@"
}

# Main loop
handle_choice() {
    local choice=$1
    shift # Remove the choice from arguments, pass the rest to the function
    case $choice in
        1)
            run_browse "$@"
            ;;
        2)
            run_login "$@"
            ;;
        3)
            exit 0
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
}

if [ -z "$1" ]; then
    while true; do
        show_menu
        read -p "> " choice
        handle_choice $choice
    done
else
    handle_choice "$@"
fi