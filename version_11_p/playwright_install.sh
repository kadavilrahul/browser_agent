#!/bin/bash
echo "Installing Playwright locally..."
if npm install playwright; then
    echo "Local installation successful"
    echo "Note: You'll need to use 'npx playwright' for commands"
else
    echo "Local installation failed" >&2
    exit 1
fi