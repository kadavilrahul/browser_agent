#!/bin/bash

# Function to display the menu
show_menu() {
    echo "==========================="
    echo "  Interactive Browser Agent"
    echo "==========================="
    echo "1. Setup (First time only)"
    echo "2. Run Agent (with browser window)"
    echo "3. Run Agent (headless/no window)"
    echo "4. Add/Update Credentials"
    echo "5. Exit"
    echo "---------------------------"
}

# Function to set up the environment
setup_agent() {
    echo "-> Setting up the environment..."
    python3 -m venv venv &&
    source venv/bin/activate &&
    pip install -r requirements.txt &&
    playwright install
    echo "-> Setup complete."
}

# Function to run the agent
run_agent() {
    echo "-> Running the agent with browser window..."
    source venv/bin/activate &&
    python3 interactive_controller.py --no-menu
}

# Function to run the agent in headless mode
run_agent_headless() {
    echo "-> Running the agent in headless mode (no browser window)..."
    source venv/bin/activate &&
    python3 interactive_controller.py --headless --no-menu
}
# Function to handle login
add_credentials() {
    echo "-> Adding/Updating credentials..."
    if [ ! -d "venv" ]; then
        echo "-> Virtual environment not found. Please run Setup (Option 1) first."
        return
    fi
    source venv/bin/activate
    python3 login_manager.py
}
# Main loop
handle_choice() {
    local choice=$1
    case $choice in
        1)
            setup_agent
            ;;
        2)
            run_agent
            ;;
        3)
            run_agent_headless
            ;;
        4)
            add_credentials
            ;;
        5)
            echo "-> Exiting."
            exit 0
            ;;
        *)
            echo "Invalid choice, please try again."
            ;;
    esac
}

if [ -z "$1" ]; then
    while true; do
        show_menu
        read -p "Enter your choice [1-5]: " choice
        handle_choice $choice
        echo
    done
else
    handle_choice "$1"
fi
