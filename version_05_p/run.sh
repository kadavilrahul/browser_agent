#!/bin/bash

# Function to display the menu
show_menu() {
    echo ""
    echo "1. Run (with browser)"
    echo "2. Run (headless)"
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
    python3 -m venv venv &&
    source venv/bin/activate &&
    pip install -r requirements.txt &&
    playwright install
    echo "Done."
}

# Function to run the agent
run_agent() {
    check_setup
    source venv/bin/activate &&
    python3 browse.py --no-menu
}

# Function to run the agent in headless mode
run_agent_headless() {
    check_setup
    source venv/bin/activate &&
    python3 browse.py --headless --no-menu
}

# Main loop
handle_choice() {
    local choice=$1
    case $choice in
        1)
            run_agent
            ;;
        2)
            run_agent_headless
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
    handle_choice "$1"
fi