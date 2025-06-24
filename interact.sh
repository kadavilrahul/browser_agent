#!/bin/bash

echo "🎮 INTERACTIVE BROWSER LAUNCHER"
echo "==============================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo "❌ .env file not found. Please run ./setup.sh first."
    deactivate
    exit 1
fi

echo "🌐 Browser Mode: $(if [ "$HEADLESS" = "true" ]; then echo "Headless (screenshots only)"; else echo "Visible (window will appear)"; fi)"
echo ""

# Run interactive browser
python3 interactive_browser.py

# Deactivate virtual environment
deactivate

echo ""
echo "✅ Interactive browser session ended."