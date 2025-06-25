#!/usr/bin/env python3
"""
Simple test script to verify the setup is working correctly.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import asyncio
        print("✓ asyncio")
    except ImportError as e:
        print(f"✗ asyncio: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False
    
    try:
        from playwright.async_api import async_playwright
        print("✓ playwright")
    except ImportError as e:
        print(f"✗ playwright: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\nTesting environment...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['HEADLESS', 'LOG_LEVEL', 'LOG_FILE']
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}={value}")
        else:
            print(f"✗ {var} not set")
            all_good = False
    
    return all_good

def main():
    """Main test function"""
    print("=" * 50)
    print("UNIFIED WEB AGENT SETUP TEST")
    print("=" * 50)
    
    imports_ok = test_imports()
    env_ok = test_environment()
    
    print("\n" + "=" * 50)
    if imports_ok and env_ok:
        print("✓ ALL TESTS PASSED - Setup is working correctly!")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Check the setup")
        if not imports_ok:
            print("  - Install missing dependencies: pip install -r requirements.txt")
        if not env_ok:
            print("  - Copy environment file: cp sample.env .env")
        return 1

if __name__ == "__main__":
    sys.exit(main())