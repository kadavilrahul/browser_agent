#!/usr/bin/env python3
"""
Basic test for ROVO Browser Agent
"""
import asyncio
import sys
import os

async def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config import successful")
        
        from browser_manager import BrowserManager
        print("✅ BrowserManager import successful")
        
        from agent_tools import NavigationTool, ElementDetectionTool
        print("✅ Agent tools import successful")
        
        from agents import BrowserAgents, BrowserCrew
        print("✅ Agents import successful")
        
        from main import RovoBrowserAgent
        print("✅ Main application import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    try:
        config = Config()
        
        # Test basic config values
        assert config.get('headless') is not None
        assert config.get('browser_type') == 'chromium'
        assert config.get('viewport_width') == 1280
        
        print("✅ Configuration loading successful")
        print(f"   - Headless: {config.get('headless')}")
        print(f"   - Browser: {config.get('browser_type')}")
        print(f"   - Viewport: {config.get('viewport_width')}x{config.get('viewport_height')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_browser_manager():
    """Test browser manager initialization"""
    print("\n🧪 Testing browser manager...")
    
    try:
        from config import Config
        from browser_manager import BrowserManager
        
        config = Config()
        browser_manager = BrowserManager(config)
        
        print("✅ BrowserManager initialization successful")
        print(f"   - Config loaded: {type(config).__name__}")
        print(f"   - Manager created: {type(browser_manager).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ BrowserManager error: {e}")
        return False

async def test_agents():
    """Test agent creation"""
    print("\n🧪 Testing agent creation...")
    
    try:
        from config import Config
        from browser_manager import BrowserManager
        from agents import BrowserAgents, BrowserCrew
        
        config = Config()
        browser_manager = BrowserManager(config)
        
        # Test agent factory
        agents_factory = BrowserAgents(browser_manager, config)
        print("✅ BrowserAgents factory created")
        
        # Test crew creation
        crew = BrowserCrew(browser_manager, config)
        print("✅ BrowserCrew created")
        
        # Test agent creation
        navigator = agents_factory.create_navigation_agent()
        detector = agents_factory.create_element_detection_agent()
        
        print(f"✅ Agents created successfully")
        print(f"   - Navigator: {navigator.role}")
        print(f"   - Detector: {detector.role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agents error: {e}")
        return False

async def test_main_app():
    """Test main application initialization"""
    print("\n🧪 Testing main application...")
    
    try:
        from main import RovoBrowserAgent
        
        # Create agent (don't start browser)
        agent = RovoBrowserAgent()
        
        print("✅ RovoBrowserAgent created successfully")
        print(f"   - Config: {type(agent.config).__name__}")
        print(f"   - Browser Manager: {type(agent.browser_manager).__name__}")
        print(f"   - Running: {agent.running}")
        
        return True
        
    except Exception as e:
        print(f"❌ Main application error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 ROVO Browser Agent - Basic Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_browser_manager,
        test_agents,
        test_main_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! ROVO Browser Agent is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.sample to .env")
        print("2. Add your GOOGLE_API_KEY to .env")
        print("3. Run: ./setup.sh")
        print("4. Run: ./run.sh")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)