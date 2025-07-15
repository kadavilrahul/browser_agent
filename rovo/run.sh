#!/bin/bash

# ROVO Browser Agent - Unified Setup & Runner Script

# Function to show help
show_help() {
    echo "ROVO Browser Agent - Unified Setup & Runner"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Setup Options:"
    echo "  --setup            Run initial setup (install dependencies)"
    echo "  --force-setup      Force reinstall all dependencies"
    echo ""
    echo "Execution Options:"
    echo "  --mode MODE        Execution mode: interactive, nav, goal, auto"
    echo "  --url URL          Target URL"
    echo "  --goal GOAL        Browsing goal"
    echo "  --element ELEMENT  Element to interact with"
    echo "  --headless BOOL    Run in headless mode (true/false)"
    echo "  --test             Run basic tests"
    echo "  --help             Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --setup                               # Initial setup"
    echo "  $0                                       # Interactive mode"
    echo "  $0 --mode nav --url google.com          # Navigate and analyze"
    echo "  $0 --mode goal --url google.com --goal \"search for python\""
    echo "  $0 --headless false                     # Run with visible browser"
    echo "  $0 --test                               # Run tests"
}

# Function to check Python version
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    major=$(echo $python_version | cut -d. -f1)
    minor=$(echo $python_version | cut -d. -f2)
    
    if [[ $major -lt 3 ]] || [[ $major -eq 3 && $minor -lt 8 ]]; then
        echo "❌ Python 3.8+ required. Current version: $python_version"
        exit 1
    fi
    
    echo "✅ Python version: $python_version"
}

# Function to run setup
run_setup() {
    echo "🚀 Setting up ROVO Browser Agent..."
    
    # Check Python version
    check_python
    
    # Create virtual environment
    if [ ! -d "venv" ] || [ "$1" = "force" ]; then
        echo "📦 Creating virtual environment..."
        rm -rf venv 2>/dev/null
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    echo "⬆️ Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    
    # Install Playwright browsers
    echo "🌐 Installing Playwright browsers..."
    playwright install chromium
    
    # Copy environment file
    if [ ! -f .env ]; then
        echo "📝 Creating .env file..."
        cp .env.sample .env
        echo "⚠️  Please edit .env file with your API keys"
    else
        echo "✅ .env file already exists"
    fi
    
    # Make scripts executable
    chmod +x run.sh main.py
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys:"
    echo "   - GOOGLE_API_KEY (required for AI features)"
    echo "   - AGENTOPS_API_KEY (optional for monitoring)"
    echo ""
    echo "2. Run the agent:"
    echo "   ./run.sh"
    echo ""
    echo "3. Or run tests:"
    echo "   ./run.sh --test"
    echo ""
}

# Function to check if setup is needed
check_setup() {
    if [ ! -d "venv" ]; then
        echo "🔧 First time setup required..."
        run_setup
        return 1
    fi
    
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file from sample..."
        cp .env.sample .env
        echo "⚠️  Please edit .env file with your API keys"
        return 1
    fi
    
    return 0
}

# Function to run tests
run_tests() {
    echo "🧪 Running ROVO Browser Agent tests in headless mode..."
    
    # Check setup first
    if ! check_setup; then
        echo "⚠️  Setup required before testing. Run: ./run.sh --setup"
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Set headless mode for testing
    export HEADLESS=true
    export VERBOSE=false
    
    # Run tests
    echo "🤖 Starting headless browser tests..."
    python3 test_basic.py
    
    test_result=$?
    
    if [ $test_result -eq 0 ]; then
        echo ""
        echo "✅ All tests completed successfully!"
        echo "🎯 ROVO Browser Agent is ready for production use."
    else
        echo ""
        echo "⚠️  Some tests had issues. Check output above."
        echo "💡 Try: ./run.sh --force-setup"
    fi
    
    return $test_result
}

# Function to start the agent
start_agent() {
    echo "🤖 Starting ROVO Browser Agent..."
    
    # Check setup
    if ! check_setup; then
        echo "⚠️  Setup completed. Please configure .env file and run again."
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check for required API key
    if grep -q "GOOGLE_API_KEY=your_google_api_key_here" .env; then
        echo "⚠️  Please set your GOOGLE_API_KEY in .env file"
        echo "   Get your API key from: https://makersuite.google.com/app/apikey"
        echo "   Then run: ./run.sh"
        exit 1
    fi
    
    echo "✅ Configuration ready"
    
    # Build command
    CMD="python main.py --mode $MODE"
    
    if [ ! -z "$URL" ]; then
        CMD="$CMD --url \"$URL\""
    fi
    
    if [ ! -z "$GOAL" ]; then
        CMD="$CMD --goal \"$GOAL\""
    fi
    
    if [ ! -z "$ELEMENT" ]; then
        CMD="$CMD --element \"$ELEMENT\""
    fi
    
    if [ ! -z "$HEADLESS" ]; then
        CMD="$CMD --headless $HEADLESS"
    fi
    
    # Show startup info
    echo ""
    echo "🎯 Mode: $MODE"
    if [ ! -z "$URL" ]; then echo "🌐 URL: $URL"; fi
    if [ ! -z "$GOAL" ]; then echo "🎯 Goal: $GOAL"; fi
    echo ""
    
    # Run the agent
    eval $CMD
}

# Parse command line arguments
MODE="interactive"
URL=""
GOAL=""
ELEMENT=""
HEADLESS=""
SETUP_MODE=""
RUN_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --setup)
            SETUP_MODE="normal"
            shift
            ;;
        --force-setup)
            SETUP_MODE="force"
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --url)
            URL="$2"
            shift 2
            ;;
        --goal)
            GOAL="$2"
            shift 2
            ;;
        --element)
            ELEMENT="$2"
            shift 2
            ;;
        --headless)
            HEADLESS="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Execute based on mode
if [ ! -z "$SETUP_MODE" ]; then
    run_setup $SETUP_MODE
elif [ "$RUN_TESTS" = true ]; then
    run_tests
else
    start_agent
fi