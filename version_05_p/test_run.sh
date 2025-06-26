#!/bin/bash

DEFAULT_URL="https://www.google.com"

if [ -z "$1" ]; then
    # No arguments provided, run both setup and agent with default URL
    echo "No arguments provided. Running setup and then the agent with default URL: $DEFAULT_URL..."
    (echo 1; echo 2; echo "$DEFAULT_URL"; echo "exit"; echo 3) | ./run.sh
elif [ "$1" == "setup" ]; then
    # Argument provided is 'setup'
    echo "Argument 'setup' provided. Running ./run.sh setup..."
    (echo 1; echo 3) | ./run.sh
elif [ "$1" == "run" ]; then
    # Argument provided is 'run', check for URL
    if [ -z "$2" ]; then
        echo "Error: URL argument is required for 'run' command in test_run.sh."
        echo "Usage: ./test_run.sh run <URL>"
        exit 1
    fi
    echo "Argument 'run' provided. Running ./run.sh run $2..."
    (echo 2; echo "$2"; echo "exit"; echo 3) | ./run.sh
else
    # Invalid argument
    echo "Invalid argument: $1"
    echo "Usage: ./test_run.sh [setup|run <URL>]"
    exit 1
fi