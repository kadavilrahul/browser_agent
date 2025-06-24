#!/bin/bash

echo "Starting environment setup..."

# Check for python3
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found. Please install python3 to continue."
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null
then
    echo "pip3 could not be found. Attempting to install pip..."
    python3 -m ensurepip --default-pip
    if [ $? -ne 0 ]; then
        echo "Failed to install pip. Please install pip manually."
        exit 1
    fi
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Please check requirements.txt."
    deactivate
    exit 1
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install
if [ $? -ne 0 ]; then
    echo "Failed to install Playwright browsers."
    deactivate
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from sample.env..."
    cp sample.env .env
    if [ $? -ne 0 ]; then
        echo "Failed to create .env file."
        deactivate
        exit 1
    fi
fi

# Update API key
echo "Please enter your GEMINI_API_KEY:"
read -r API_KEY

# Use sed to update the API key in .env
# The 's' command is for substitute, '^GEMINI_API_KEY=.*$' matches the line starting with GEMINI_API_KEY=
# and replaces it with the new key. The 'g' flag is for global replacement on the line (though not strictly
# necessary here as there's only one match per line).
# The 'i' flag is for in-place editing.
sed -i "s|^GEMINI_API_KEY=.*$|GEMINI_API_KEY=$API_KEY|" .env

echo "GEMINI_API_KEY updated in .env"

# Ask user about headless mode
echo ""
echo "Do you want to run the browser in headless mode? (recommended for servers without display)"
echo "1. Yes - Headless mode (no visible browser window)"
echo "2. No - Visible browser mode (requires display/X server)"
read -p "Enter your choice (1 or 2): " headless_choice

if [ "$headless_choice" = "1" ]; then
    sed -i "s|^HEADLESS=.*$|HEADLESS=true|" .env
    echo "Browser set to headless mode"
elif [ "$headless_choice" = "2" ]; then
    sed -i "s|^HEADLESS=.*$|HEADLESS=false|" .env
    echo "Browser set to visible mode"
    echo "Note: If you're on a server without display, the browser may fail to start."
    echo "You can install xvfb with: sudo apt-get install xvfb"
else
    echo "Invalid choice. Keeping current setting."
fi
echo "Environment setup complete. You can now run the application using ./run.sh"

# Deactivate the virtual environment (optional, but good practice for setup scripts)
deactivate