#!/bin/bash
# Playwright installation script with comprehensive error handling

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Install Playwright package with fallback options
echo "Installing Playwright package..."
echo "Attempting global installation..."
if npm install -g playwright; then
    echo "Playwright package installed globally"
elif sudo npm install -g playwright; then
    echo "Playwright package installed globally with sudo"
elif npm install playwright; then
    echo "Playwright package installed locally"
else
    echo "Failed to install Playwright package"
    exit 1
fi

# Install browsers with retry logic
echo "Installing browser packages (chromium, firefox, webkit)..."
MAX_RETRIES=3
retry_count=0

while [ $retry_count -lt $MAX_RETRIES ]; do
    if npx playwright install chromium firefox webkit; then
        echo "Browser packages installed successfully"
        exit 0
    fi
    retry_count=$((retry_count+1))
    echo "Retrying browser installation (attempt $retry_count/$MAX_RETRIES)..."
    sleep 5
done

echo "Failed to install browser packages after $MAX_RETRIES attempts"
exit 1