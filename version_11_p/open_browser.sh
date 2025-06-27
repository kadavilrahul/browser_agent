#!/bin/bash
# Script to open example.com using Playwright

# Check if Playwright is installed
if ! command -v npx &> /dev/null; then
    echo "Error: npx is not available. Please install Node.js first."
    exit 1
fi

# Check if Playwright is installed
if ! npx playwright --version &> /dev/null; then
    echo "Error: Playwright is not installed. Please run playwright_install.sh first."
    exit 1
fi

# Run Playwright script to open example.com
echo "Opening example.com in browser..."
npx playwright open https://github.com