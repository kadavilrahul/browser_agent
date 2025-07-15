#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the main script
python3 unified.py || exit 1

# Deactivate the virtual environment
deactivate