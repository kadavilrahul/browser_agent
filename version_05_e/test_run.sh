#!/bin/bash

DEFAULT_URL="https://www.google.com"
TEST_USERNAME="testuser"
TEST_PASSWORD="testpassword"

if [ -z "$1" ]; then
    # No arguments provided, run both setup and agent with default URL
    echo "No arguments provided. Running setup and then the agent with default URL: $DEFAULT_URL..."
    ./run.sh 2 2 "$DEFAULT_URL" "exit" 4
elif [ "$1" == "setup" ]; then
    # Argument provided is 'setup'
    echo "Argument 'setup' provided. Running ./run.sh setup..."
    ./run.sh 1 4
elif [ "$1" == "run" ]; then
    # Argument provided is 'run', check for URL
    if [ -z "$2" ]; then
        echo "Error: URL argument is required for 'run' command in test_run.sh."
        echo "Usage: ./test_run.sh run <URL>"
        exit 1
    fi
    echo "Argument 'run' provided. Running ./run.sh run $2..."
    ./run.sh 2 2 "$2" "exit" 4
elif [ "$1" == "login" ]; then
    # Argument provided is 'login'
    echo "Argument 'login' provided. Running login test..."
    ./run.sh 3 github.com kadavilrahul Karimpadam4@
else
    # Invalid argument
    echo "Invalid argument: $1"
    echo "Usage: ./test_run.sh [setup|run <URL>|login]"
    exit 1
fi