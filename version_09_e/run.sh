#!/bin/bash

# Set up virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
    . venv/bin/activate
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r requirements.txt --break-system-packages
else
    . venv/bin/activate
fi

# Set default values
URL=""
EXTRACT=false
SCREENSHOT=false
OUTPUT="json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --extract)
            EXTRACT=true
            shift
            ;;
        --screenshot)
            SCREENSHOT=true
            shift
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
                # Accept domains without protocol
                if [[ "$1" != http* ]]; then
                    URL="https://$1"
                else
                    URL="$1"
                fi
                shift
                ;;
    esac
done

# Validate URL
if [[ -z "$URL" ]]; then
    echo "Error: URL is required"
    exit 1
fi

# Build command arguments
ARGS="$URL"
if [[ "$EXTRACT" == true ]]; then
    ARGS="$ARGS --extract"
fi
if [[ "$SCREENSHOT" == true ]]; then
    ARGS="$ARGS --screenshot"
fi
if [[ -n "$OUTPUT" ]]; then
    ARGS="$ARGS --output $OUTPUT"
fi

# Execute the Python script
python3 main.py $ARGS