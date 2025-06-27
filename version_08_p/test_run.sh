#!/bin/bash

# Test Runner for Web Browsing Agent
# This script runs automated tests without user input

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "=========================================="
echo "         WEB AGENT TEST RUNNER"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment not found. Please run ./run.sh first to set up."
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "ERROR: .env file not found. Please run ./run.sh first to set up."
    exit 1
fi

echo "Running automated tests..."

# Test 1: Basic navigation test
echo "Test 1: Basic navigation to test site..."
python3 -c "
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def test_navigation():
    from web_agent import UnifiedWebAgent
    async with UnifiedWebAgent() as agent:
        test_url = os.getenv('TEST_URL', 'https://httpbin.org/forms/post')
        await agent.navigate(test_url)
        await agent.take_screenshot('test_navigation.png')
        print('SUCCESS: Navigation test passed')

asyncio.run(test_navigation())
"

# Test 2: Element detection test
echo "Test 2: Element detection test..."
python3 -c "
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def test_elements():
    from web_agent import UnifiedWebAgent
    async with UnifiedWebAgent() as agent:
        test_url = os.getenv('TEST_URL', 'https://httpbin.org/forms/post')
        await agent.navigate(test_url)
        elements = await agent.find_clickable_elements()
        print(f'SUCCESS: Found {len(elements)} clickable elements')
        if len(elements) > 0:
            print('SUCCESS: Element detection test passed')
        else:
            print('WARNING: No elements found')

asyncio.run(test_elements())
"

# Test 3: AI integration test (if API key is provided)
echo "Test 3: AI integration test..."
python3 -c "
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def test_ai():
    api_key = os.getenv('GEMINI_API_KEY', '')
    if api_key and api_key != 'your_gemini_api_key_here':
        from web_agent import UnifiedWebAgent
        async with UnifiedWebAgent() as agent:
            test_url = os.getenv('TEST_URL', 'https://httpbin.org/forms/post')
            await agent.navigate(test_url)
            # Test AI element selection
            suggestion = await agent.get_ai_element_suggestion('find login form')
            print(f'SUCCESS: AI suggestion received: {suggestion[:100]}...')
            print('SUCCESS: AI integration test passed')
    else:
        print('WARNING: Skipping AI test - no API key configured')

asyncio.run(test_ai())
"

echo "=========================================="
echo "All tests completed!"
echo "Check test_navigation.png for screenshot"
echo "=========================================="