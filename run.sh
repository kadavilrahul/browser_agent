#!/bin/bash
set -e

# Function to setup virtual environment
setup_venv() {
    if [[ ! -d "venv" ]]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip
    
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
    
    echo "🌐 Installing Playwright browser binaries..."
    playwright install
    
    echo "✅ Virtual environment setup complete!"
}

# Function to activate existing venv and ensure dependencies
activate_venv() {
    if [[ -d "venv" ]]; then
        echo "🔧 Activating virtual environment..."
        source venv/bin/activate
        
        # Check if requirements are installed
        echo "🔍 Checking dependencies..."
        if ! pip show playwright > /dev/null 2>&1; then
            echo "📥 Installing missing dependencies..."
            pip install --upgrade pip
            pip install -r requirements.txt
            playwright install
        fi
    else
        echo "❌ Virtual environment not found. Creating..."
        setup_venv
    fi
}

# Check for special commands first
if [[ "$1" == "gmail-test" ]]; then
    echo "🧪 Setting up Gmail Automation Test..."
    echo "⚠️  WARNING: This will use REAL Gmail credentials!"
    
    # Setup virtual environment and dependencies
    activate_venv
    
    # Setup test environment
    if [[ ! -f ".env.test" ]]; then
        echo "❌ .env.test file not found!"
        echo "Please create .env.test with your Gmail credentials"
        echo "Use .env.sample as a template"
        exit 1
    fi
    
    # Copy test config to main .env
    cp .env.test .env
    echo "✅ Test environment configured"
    
    # Run Gmail test
    echo "🚀 Starting Gmail automation test..."
    python gmail_automation_test.py
    
elif [[ "$1" == "setup" ]]; then
    echo "🔧 Setting up Browser Agent version_12_p..."
    setup_venv
    echo "✅ Setup complete!"
    echo "💡 Virtual environment created in ./venv"
    echo "💡 To activate manually: source venv/bin/activate"
    
elif [[ "$1" == "install" ]]; then
    echo "📥 Installing/updating requirements..."
    activate_venv
    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
    echo "🌐 Installing Playwright browser binaries..."
    playwright install
    echo "✅ Requirements installation complete!"
    
elif [[ "$1" == "demo" ]]; then
    echo "🎭 Running in demo mode..."
    activate_venv > /dev/null 2>&1
    export DEMO_MODE=true
    export ALLOW_REAL_LOGIN=false
    python main.py "${@:2}"
    
elif [[ "$1" == "help" || "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Browser Agent v12_p - Usage Guide"
    echo "================================="
    echo ""
    echo "Basic Usage:"
    echo "  ./run.sh                    - Interactive mode"
    echo "  ./run.sh --url example.com  - Navigate and start interactive"
    echo ""
    echo "Special Commands:"
    echo "  ./run.sh gmail-test         - Run Gmail automation test (REAL credentials)"
    echo "  ./run.sh demo               - Force demo mode (safe testing)"
    echo "  ./run.sh setup              - Create venv and install dependencies"
    echo "  ./run.sh install            - Install/update requirements in existing venv"
    echo "  ./run.sh clean              - Remove venv and .env files"
    echo "  ./run.sh help               - Show this help"
    echo ""
    echo "Gmail Test Requirements:"
    echo "  - Create .env.test with GMAIL_EMAIL, GMAIL_PASSWORD, etc."
    echo "  - Use .env.sample as template"
    echo "  - Script includes safety confirmations"
    echo ""
    echo "Examples:"
    echo "  ./run.sh setup                         # First time setup"
    echo "  ./run.sh install                       # Update dependencies"
    echo "  ./run.sh gmail-test                    # Full Gmail automation"
    echo "  ./run.sh demo --url gmail.com          # Safe Gmail testing"
    echo "  ./run.sh --url google.com --screenshot # Take screenshot"
    echo ""
    
elif [[ "$1" == "clean" ]]; then
    echo "🧹 Cleaning up..."
    if [[ -d "venv" ]]; then
        echo "🗑️  Removing virtual environment..."
        rm -rf venv
    fi
    if [[ -f ".env" ]]; then
        echo "🗑️  Removing .env file..."
        rm .env
    fi
    echo "✅ Cleanup complete!"
    
else
    echo "Setting up Browser Agent version_12_p..."
    
    # Setup virtual environment and dependencies
    activate_venv
    
    echo "Installation complete! Starting browser agent..."
    python main.py "$@"
fi