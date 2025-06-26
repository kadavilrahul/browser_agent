#!/bin/bash

# Function to display the menu
show_menu() {
    echo "==========================="
    echo "  Interactive Browser Agent"
    echo "==========================="
    echo "1. Setup (First time only)"
    echo "2. Run Agent"
    echo "3. Exit"
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
    echo "-> Starting the agent..."
    source venv/bin/activate &&
    python3 interactive_controller.py
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice [1-3]: " choice

    case $choice in
        1)
            setup_agent
            ;;
        2)
            run_agent
            ;;
        3)
            echo "Exiting."
            exit 0
            ;;
        *)
            echo "Invalid choice, please try again."
            ;;
    esac
    echo
done