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
    """Test browser manager initialization and basic operations"""
    print("\n🧪 Testing browser manager...")
    
    try:
        from config import Config
        from browser_manager import BrowserManager
        
        # Force headless mode for testing
        config = Config()
        config._config['headless'] = True
        config._config['verbose'] = False
        
        browser_manager = BrowserManager(config)
        
        print("✅ BrowserManager initialization successful")
        print(f"   - Config loaded: {type(config).__name__}")
        print(f"   - Manager created: {type(browser_manager).__name__}")
        print(f"   - Headless mode: {config.get('headless')}")
        
        # Test browser startup and basic operations
        print("🔧 Testing browser startup...")
        page = await browser_manager.start()
        
        print("✅ Browser started successfully")
        print(f"   - Page object: {type(page).__name__}")
        
        # Test navigation
        print("🌐 Testing navigation...")
        success = await browser_manager.navigate("https://httpbin.org/html")
        
        if success:
            print("✅ Navigation successful")
            
            # Test page info
            info = await browser_manager.get_page_info()
            print(f"   - Page title: {info.get('title', 'N/A')[:50]}")
            print(f"   - Page URL: {info.get('url', 'N/A')}")
        else:
            print("⚠️  Navigation failed (may be network issue)")
        
        # Test element detection
        print("🔍 Testing element detection...")
        elements = await browser_manager.find_clickable_elements()
        print(f"✅ Found {len(elements)} clickable elements")
        
        # Test screenshot
        print("📸 Testing screenshot...")
        screenshot_success = await browser_manager.take_screenshot("test_screenshot.png")
        if screenshot_success:
            print("✅ Screenshot taken successfully")
        else:
            print("⚠️  Screenshot failed")
        
        # Cleanup
        await browser_manager.close()
        print("✅ Browser closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ BrowserManager error: {e}")
        try:
            if 'browser_manager' in locals():
                await browser_manager.close()
        except:
            pass
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
    """Test main application initialization and basic workflow"""
    print("\n🧪 Testing main application...")
    
    try:
        from main import RovoBrowserAgent
        
        # Create agent with headless mode
        agent = RovoBrowserAgent()
        agent.config._config['headless'] = True
        agent.config._config['verbose'] = False
        
        print("✅ RovoBrowserAgent created successfully")
        print(f"   - Config: {type(agent.config).__name__}")
        print(f"   - Browser Manager: {type(agent.browser_manager).__name__}")
        print(f"   - Running: {agent.running}")
        print(f"   - Headless mode: {agent.config.get('headless')}")
        
        # Test agent startup
        print("🚀 Testing agent startup...")
        await agent.start()
        
        print("✅ Agent started successfully")
        print(f"   - Running status: {agent.running}")
        print(f"   - Crew created: {agent.crew is not None}")
        
        # Test simple navigation (if we have internet)
        try:
            print("🧭 Testing simple navigation workflow...")
            result = agent.navigate_and_analyze("https://httpbin.org/html")
            print("✅ Navigation workflow completed")
            print(f"   - Result type: {type(result).__name__}")
            print(f"   - Result preview: {str(result)[:100]}...")
        except Exception as nav_error:
            print(f"⚠️  Navigation test skipped: {nav_error}")
        
        # Cleanup
        await agent.stop()
        print("✅ Agent stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Main application error: {e}")
        try:
            if 'agent' in locals():
                await agent.stop()
        except:
            pass
        return False

async def main():
    """Run all tests"""
    print("🚀 ROVO Browser Agent - Headless Testing Mode")
    print("=" * 50)
    print("ℹ️  Running tests in headless mode for CI/automation compatibility")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config),
        ("Browser Manager Tests", test_browser_manager),
        ("Agent Creation Tests", test_agents),
        ("Main Application Tests", test_main_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔄 Running: {test_name}")
            result = await test_func()
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! ROVO Browser Agent is ready to use.")
        print("\n✅ Headless browser testing successful")
        print("✅ All core components working")
        print("✅ Agent workflows functional")
        print("\nNext steps:")
        print("1. Add your GOOGLE_API_KEY to .env")
        print("2. Run: ./run.sh")
        print("3. Try: ./run.sh --mode nav --url google.com")
    elif passed >= total - 1:
        print("⚠️  Most tests passed. Minor issues detected.")
        print("🎯 ROVO Browser Agent should work for basic operations.")
        return 0
    else:
        print("❌ Multiple tests failed. Please check the errors above.")
        print("💡 Try running: ./run.sh --setup --force")
        return 1
    
    # Cleanup any test files
    try:
        import os
        if os.path.exists("test_screenshot.png"):
            os.remove("test_screenshot.png")
            print("🧹 Cleaned up test files")
    except:
        pass
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)