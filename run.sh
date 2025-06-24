#!/bin/bash

echo "Starting the application..."

# Activate the virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Load environment variables from .env
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo ".env file not found. Please run ./setup.sh first."
    deactivate
    exit 1
fi

# Check if interactive mode is requested
if [ "$1" = "interactive" ] || [ "$1" = "interact" ]; then
    python3 interactive_browser.py
else
    # Run the main Python script with any passed arguments
    python3 web_browsing_agent.py "$@"
fi

# Deactivate the virtual environment
deactivate

echo "Application finished."