#!/usr/bin/env python3
"""
Browser Agent v12_p - Main Entry Point
Minimalistic browser automation with essential functions
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from config import Config
from controller import InteractiveController

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Browser Agent v12_p - Minimalistic browser automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Interactive mode
  python main.py --url google.com          # Navigate and enter interactive mode
  python main.py --url google.com --find   # Navigate and find elements
  python main.py --url google.com --screenshot  # Navigate and take screenshot
  python main.py --headless false          # Run in non-headless mode
        """
    )
    
    # Main options
    parser.add_argument(
        '--url', '-u',
        help='URL to navigate to'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        default=True,
        help='Start in interactive mode (default)'
    )
    
    # Actions
    parser.add_argument(
        '--find', '--elements', '-f',
        action='store_true',
        help='Find clickable elements and exit'
    )
    
    parser.add_argument(
        '--screenshot', '-s',
        action='store_true',
        help='Take screenshot and exit'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show page info and exit'
    )
    
    # Browser options
    parser.add_argument(
        '--headless',
        type=str,
        choices=['true', 'false'],
        help='Run browser in headless mode (true/false)'
    )
    
    parser.add_argument(
        '--browser',
        choices=['chromium', 'firefox', 'webkit'],
        help='Browser type to use'
    )
    
    # Configuration
    parser.add_argument(
        '--config', '-c',
        help='Path to .env config file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for screenshots and exports'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Browser Agent v12_p'
    )
    
    return parser.parse_args()

def apply_cli_overrides(config: Config, args) -> None:
    """Apply command line argument overrides to config"""
    if args.headless is not None:
        config.set('headless', args.headless.lower() == 'true')
    
    if args.browser:
        config.set('browser_type', args.browser)
    
    if args.verbose:
        config.set('verbose', True)
    
    if args.output_dir:
        config.set('output_dir', args.output_dir)
        config.set('screenshot_dir', args.output_dir)

def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════╗
║         Browser Agent v12_p           ║
║    Minimalistic Browser Automation    ║
╚═══════════════════════════════════════╝
    """
    print(banner)

def validate_environment():
    """Validate required environment and dependencies"""
    try:
        import playwright
        return True
    except ImportError:
        print("❌ Error: Playwright not installed")
        print("Run: pip install playwright && playwright install")
        return False

async def main():
    """Main application entry point"""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        # Show banner for interactive mode (will be replaced by menu)
        if args.interactive and not any([args.find, args.screenshot, args.info]):
            pass  # Banner now shown in menu system
        
        # Initialize configuration
        config = Config(args.config)
        apply_cli_overrides(config, args)
        
        if args.verbose or config.get('verbose'):
            print(f"🔧 Configuration: {config}")
        
        # Initialize controller
        controller = InteractiveController(config)
        
        # Determine mode of operation
        if args.find or args.screenshot or args.info:
            # Single command mode
            await run_single_command(controller, args)
        else:
            # Interactive mode
            await run_interactive_mode(controller, args)
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)

async def run_single_command(controller: InteractiveController, args):
    """Run in single command mode"""
    if args.find:
        success = await controller.run_single_command('find', args.url)
    elif args.screenshot:
        success = await controller.run_single_command('screenshot', args.url)
    elif args.info:
        success = await controller.run_single_command('info', args.url)
    else:
        success = True
    
    sys.exit(0 if success else 1)

async def run_interactive_mode(controller: InteractiveController, args):
    """Run in interactive mode"""
    # Navigate to URL if provided
    if args.url:
        print(f"🌐 Starting browser and navigating to: {args.url}")
        await controller.browser.start()
        controller.elements = controller.elements or ElementManager(
            controller.config, controller.browser.page
        )
        
        success = await controller.browser.navigate(args.url)
        if not success:
            print(f"❌ Failed to navigate to: {args.url}")
            print("Continuing in interactive mode...")
        
        await controller.browser.stop()
    
    # Start interactive session
    await controller.start_interactive()

def create_sample_env():
    """Create sample .env file if it doesn't exist"""
    env_file = Path('.env')
    if env_file.exists():
        return
    
    sample_content = """# Browser Agent v12_p Configuration
# Browser settings
HEADLESS=true
BROWSER_TYPE=chromium
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=720

# Timeout settings (milliseconds)
PAGE_TIMEOUT=30000
ELEMENT_TIMEOUT=5000
NAVIGATION_TIMEOUT=30000

# Screenshot settings
SCREENSHOT_DIR=screenshots
SCREENSHOT_QUALITY=90
AUTO_SCREENSHOT=true

# Output settings
OUTPUT_DIR=output
ELEMENTS_FILE=elements.json
VERBOSE=false

# Default URL
DEFAULT_URL=https://www.google.com
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(sample_content)
        print(f"📝 Created sample .env file: {env_file}")
    except Exception as e:
        print(f"Warning: Could not create .env file: {e}")

if __name__ == "__main__":
    # Ensure we're using the right event loop policy on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Create sample .env if needed
    create_sample_env()
    
    # Fix import for interactive mode
    from elements import ElementManager
    
    # Run main application
    asyncio.run(main())