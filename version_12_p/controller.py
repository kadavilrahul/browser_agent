"""
Interactive controller for Browser Agent v12_p
Handles user interface, commands, and interactive control
"""

import asyncio
import sys
from typing import List, Optional, Dict, Any
from browser import BrowserManager
from elements import ElementManager
from login_manager import LoginManager
from config import Config

class InteractiveController:
    """Manages interactive user interface and command processing"""
    
    def __init__(self, config: Config):
        """Initialize controller with configuration"""
        self.config = config
        self.browser = BrowserManager(config)
        self.elements: Optional[ElementManager] = None
        self.login_manager: Optional[LoginManager] = None
        self.running = True
        
        # Command mappings
        self.commands = {
            'help': self._show_help,
            'h': self._show_help,
            'navigate': self._navigate,
            'n': self._navigate,
            'go': self._navigate,
            'elements': self._find_elements,
            'e': self._find_elements,
            'find': self._find_elements,
            'click': self._click_element,
            'c': self._click_element,
            'screenshot': self._take_screenshot,
            's': self._take_screenshot,
            'info': self._show_info,
            'i': self._show_info,
            'export': self._export_elements,
            'list': self._list_elements,
            'l': self._list_elements,
            'login': self._login,
            'signin': self._login,
            'auth': self._login,
            'status': self._login_status,
            'session': self._session_info,
            'save_session': self._save_session,
            'quit': self._quit,
            'q': self._quit,
            'exit': self._quit,
        }
    
    async def start_interactive(self) -> None:
        """Start interactive mode with menu"""
        try:
            await self.browser.start()
            self.elements = ElementManager(self.config, self.browser.page)
            self.login_manager = LoginManager(self.config, self.browser)
            
            while self.running:
                try:
                    await self._show_interactive_menu()
                    
                except KeyboardInterrupt:
                    print("\n\n🛑 Use option 'q' to exit properly")
                    await asyncio.sleep(1)
                except EOFError:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    await asyncio.sleep(2)
        
        finally:
            await self.browser.stop()
    
    async def _show_interactive_menu(self) -> None:
        """Show interactive menu and handle user selection"""
        # Clear screen and show header
        print("\033[2J\033[H")  # Clear screen and move cursor to top
        print("╔═══════════════════════════════════════╗")
        print("║         Browser Agent v12_p           ║")
        print("║    Interactive Menu System            ║")
        print("╚═══════════════════════════════════════╝")
        print()
        
        # Show current status
        current_url = self.browser.get_current_url()
        login_status = "🔓 Not logged in"
        if self.login_manager and self.login_manager.is_logged_in():
            login_status = "🔒 Logged in"
        
        print(f"📍 Current Page: {current_url or 'No page loaded'}")
        print(f"🔐 Status: {login_status}")
        
        if self.elements and self.elements.get_element_count() > 0:
            print(f"🔍 Elements Found: {self.elements.get_element_count()}")
        
        print()
        print("═" * 50)
        print("           MAIN MENU OPTIONS")
        print("═" * 50)
        
        # Main menu options
        menu_options = [
            ("1", "🌐 Navigate to Website", "navigate"),
            ("2", "🔍 Find Elements on Page", "find"),
            ("3", "🔐 Login to Website", "login"),
            ("4", "📸 Take Screenshot", "screenshot"),
            ("5", "📊 Show Page Info", "info"),
            ("", "", ""),  # Separator
            ("e", "🎯 Element Actions Menu", "elements_menu"),
            ("s", "🔧 Session Menu", "session_menu"),
            ("", "", ""),  # Separator
            ("h", "❓ Help", "help"),
            ("q", "👋 Quit", "quit"),
        ]
        
        for key, description, _ in menu_options:
            if key and description:
                print(f"  {key:2} │ {description}")
            elif not key:
                print("     │")
        
        print("═" * 50)
        print()
        
        # Get user choice
        choice = await self._get_input("Select option: ")
        choice = choice.strip().lower()
        
        # Process menu choice
        await self._process_menu_choice(choice)
    
    async def _process_menu_choice(self, choice: str) -> None:
        """Process user menu choice"""
        if choice == "1":
            await self._menu_navigate()
        elif choice == "2":
            await self._menu_find_elements()
        elif choice == "3":
            await self._menu_login()
        elif choice == "4":
            await self._menu_screenshot()
        elif choice == "5":
            await self._menu_page_info()
        elif choice == "e":
            await self._menu_elements_actions()
        elif choice == "s":
            await self._menu_session()
        elif choice == "h":
            await self._menu_help()
        elif choice == "q":
            await self._quit([])
        else:
            print(f"❌ Invalid option: {choice}")
            await self._press_enter_to_continue()
    
    async def _menu_navigate(self) -> None:
        """Navigation menu"""
        print("\n🌐 NAVIGATE TO WEBSITE")
        print("-" * 30)
        
        # Show quick options
        print("Quick options:")
        print("  1. Gmail")
        print("  2. Google")
        print("  3. Custom URL")
        print()
        
        choice = await self._get_input("Select (1-3) or enter URL directly: ")
        
        if choice == "1":
            url = "gmail.com"
        elif choice == "2":
            url = "google.com"
        elif choice == "3" or not choice.isdigit():
            if choice.isdigit():
                url = await self._get_input("Enter URL: ")
            else:
                url = choice
        else:
            print("❌ Invalid choice")
            await self._press_enter_to_continue()
            return
        
        if url:
            print(f"\n🚀 Navigating to: {url}")
            await self._navigate([url])
        
        await self._press_enter_to_continue()
    
    async def _menu_find_elements(self) -> None:
        """Find elements menu"""
        print("\n🔍 FIND ELEMENTS ON PAGE")
        print("-" * 30)
        
        if not self.browser.is_ready():
            print("❌ No page loaded. Navigate to a website first.")
        else:
            await self._find_elements([])
        
        await self._press_enter_to_continue()
    
    async def _menu_login(self) -> None:
        """Login menu"""
        print("\n🔐 LOGIN TO WEBSITE")
        print("-" * 30)
        
        if not self.browser.is_ready():
            print("❌ No page loaded. Navigate to a website first.")
            await self._press_enter_to_continue()
            return
        
        print("Login options:")
        print("  1. Interactive login (enter credentials)")
        print("  2. Demo login (safe testing)")
        print("  3. Show login status")
        print()
        
        choice = await self._get_input("Select option (1-3): ")
        
        if choice == "1":
            await self._login([])
        elif choice == "2":
            print("🎭 Demo mode enabled for this login")
            original_demo = self.config.get('demo_mode')
            self.config.set('demo_mode', True)
            await self._login([])
            self.config.set('demo_mode', original_demo)
        elif choice == "3":
            await self._login_status([])
        else:
            print("❌ Invalid choice")
        
        await self._press_enter_to_continue()
    
    async def _menu_screenshot(self) -> None:
        """Screenshot menu"""
        print("\n📸 TAKE SCREENSHOT")
        print("-" * 30)
        
        if not self.browser.is_ready():
            print("❌ No page loaded. Navigate to a website first.")
        else:
            await self._take_screenshot([])
        
        await self._press_enter_to_continue()
    
    async def _menu_page_info(self) -> None:
        """Page info menu"""
        print("\n📊 PAGE INFORMATION")
        print("-" * 30)
        
        await self._show_info([])
        await self._press_enter_to_continue()
    
    async def _menu_elements_actions(self) -> None:
        """Elements actions submenu"""
        if not self.elements or self.elements.get_element_count() == 0:
            print("\n❌ No elements found. Use 'Find Elements' first.")
            await self._press_enter_to_continue()
            return
        
        while True:
            print("\033[2J\033[H")  # Clear screen
            print("╔═══════════════════════════════════════╗")
            print("║         ELEMENT ACTIONS MENU          ║")
            print("╚═══════════════════════════════════════╝")
            print()
            
            print(f"📊 Found {self.elements.get_element_count()} elements")
            print()
            
            # Show first few elements
            summary = self.elements.get_element_summary()
            display_count = min(10, len(summary))
            
            print("Recent Elements:")
            for i in range(display_count):
                print(f"  {i:2} │ {summary[i]}")
            
            if len(summary) > display_count:
                print(f"     │ ... and {len(summary) - display_count} more")
            
            print()
            print("Options:")
            print("  [number] │ Click element by number")
            print("  l        │ List all elements")
            print("  r        │ Refresh/find elements again")
            print("  e        │ Export elements to JSON")
            print("  b        │ Back to main menu")
            print()
            
            choice = await self._get_input("Select option: ")
            choice = choice.strip()
            
            if choice.isdigit():
                await self._click_element([choice])
                await self._press_enter_to_continue()
            elif choice == "l":
                await self._list_elements([])
                await self._press_enter_to_continue()
            elif choice == "r":
                await self._find_elements([])
                await self._press_enter_to_continue()
            elif choice == "e":
                await self._export_elements([])
                await self._press_enter_to_continue()
            elif choice == "b":
                break
            else:
                print("❌ Invalid option")
                await asyncio.sleep(1)
    
    async def _menu_session(self) -> None:
        """Session management menu"""
        while True:
            print("\033[2J\033[H")  # Clear screen
            print("╔═══════════════════════════════════════╗")
            print("║          SESSION MENU                 ║")
            print("╚═══════════════════════════════════════╝")
            print()
            
            print("Options:")
            print("  1 │ Show login status")
            print("  2 │ Show session info")
            print("  3 │ Save current session")
            print("  4 │ Gmail automation test")
            print("  b │ Back to main menu")
            print()
            
            choice = await self._get_input("Select option: ")
            
            if choice == "1":
                await self._login_status([])
                await self._press_enter_to_continue()
            elif choice == "2":
                await self._session_info([])
                await self._press_enter_to_continue()
            elif choice == "3":
                await self._save_session([])
                await self._press_enter_to_continue()
            elif choice == "4":
                print("\n🧪 Starting Gmail automation test...")
                print("⚠️  This will exit interactive mode and run the test")
                confirm = await self._get_input("Continue? (y/N): ")
                if confirm.lower() == 'y':
                    print("🚀 Launching Gmail test... (exiting interactive mode)")
                    await asyncio.sleep(1)
                    self.running = False
                    # Note: User will need to run ./run.sh gmail-test separately
                    print("💡 Run: ./run.sh gmail-test")
                    return
            elif choice == "b":
                break
            else:
                print("❌ Invalid option")
                await asyncio.sleep(1)
    
    async def _menu_help(self) -> None:
        """Help menu"""
        print("\033[2J\033[H")  # Clear screen
        print("╔═══════════════════════════════════════╗")
        print("║              HELP GUIDE               ║")
        print("╚═══════════════════════════════════════╝")
        print()
        
        help_sections = [
            ("🌐 Navigation", [
                "• Use option 1 to navigate to websites",
                "• Quick access to Gmail, Google, or custom URLs",
                "• URLs are automatically validated and corrected"
            ]),
            ("🔍 Element Detection", [
                "• Option 2 finds all clickable elements on the page",
                "• Elements are numbered for easy interaction",
                "• Use Elements Menu (e) to interact with found elements"
            ]),
            ("🔐 Login System", [
                "• Option 3 provides login capabilities",
                "• Demo mode for safe testing (no real login)",
                "• Interactive mode for real credential entry",
                "• Session tracking and status monitoring"
            ]),
            ("📸 Screenshots", [
                "• Option 4 captures full-page screenshots",
                "• Automatic filename generation with timestamps",
                "• Saved in screenshots/ directory"
            ]),
            ("🎯 Element Actions", [
                "• Elements Menu (e) for detailed element interaction",
                "• Click elements by number",
                "• List, refresh, and export element data",
                "• JSON export for analysis"
            ])
        ]
        
        for title, items in help_sections:
            print(f"{title}:")
            for item in items:
                print(f"  {item}")
            print()
        
        print("💡 Tips:")
        print("  • Navigate to a website before trying to find elements")
        print("  • Use demo mode for safe testing without real credentials")
        print("  • Screenshots are saved automatically during key actions")
        print("  • Session data can be saved and restored")
        print()
        
        await self._press_enter_to_continue()
    
    async def _press_enter_to_continue(self) -> None:
        """Wait for user to press enter"""
        await self._get_input("\nPress Enter to continue...")
    
    async def _get_input(self, prompt: str) -> str:
        """Get user input asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)
    
    async def _process_command(self, user_input: str) -> None:
        """Process user command"""
        parts = user_input.split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            await self.commands[command](args)
        elif command.isdigit():
            # Direct element click by number
            await self._click_element([command])
        elif user_input.startswith(('http://', 'https://', 'www.')):
            # Direct URL navigation
            await self._navigate([user_input])
        else:
            print(f"Unknown command: {command}. Type 'help' for available commands.")
    
    async def _show_help(self, args: List[str]) -> None:
        """Show help information"""
        help_text = """
Available Commands:
  navigate, n, go <url>  - Navigate to URL
  elements, e, find      - Find clickable elements on page
  click, c <number>      - Click element by number
  list, l               - List found elements
  screenshot, s         - Take screenshot
  info, i               - Show page information
  export                - Export elements to JSON
  login, signin, auth   - Login to current website
  status                - Show login status
  session               - Show session information
  save_session          - Save current session
  help, h               - Show this help
  quit, q, exit         - Exit the application

Shortcuts:
  <number>              - Click element by number (e.g., type '5' to click element 5)
  <url>                 - Navigate directly to URL (if starts with http/https/www)

Examples:
  navigate gmail.com
  login
  find
  click 3
  screenshot
  status
        """
        print(help_text)
    
    async def _navigate(self, args: List[str]) -> None:
        """Navigate to URL"""
        if not args:
            url = await self._get_input("Enter URL: ")
        else:
            url = ' '.join(args)
        
        if not url.strip():
            print("URL cannot be empty")
            return
        
        print(f"Navigating to: {url}")
        success = await self.browser.navigate(url)
        
        if success:
            print(f"✓ Successfully navigated to: {self.browser.get_current_url()}")
            # Auto-find elements if configured
            if self.config.get('auto_screenshot'):
                print("📸 Screenshot saved automatically")
        else:
            print("✗ Navigation failed")
    
    async def _find_elements(self, args: List[str]) -> None:
        """Find clickable elements"""
        if not self.browser.is_ready():
            print("No page loaded. Navigate to a URL first.")
            return
        
        print("🔍 Finding clickable elements...")
        elements = await self.elements.find_clickable_elements()
        
        if elements:
            print(f"✓ Found {len(elements)} clickable elements:")
            self._display_elements_summary()
        else:
            print("No clickable elements found")
    
    async def _click_element(self, args: List[str]) -> None:
        """Click element by ID"""
        if not args:
            element_id = await self._get_input("Enter element number: ")
        else:
            element_id = args[0]
        
        try:
            element_id = int(element_id)
        except ValueError:
            print("Element ID must be a number")
            return
        
        if not self.elements or self.elements.get_element_count() == 0:
            print("No elements found. Use 'find' command first.")
            return
        
        element = self.elements.get_element_by_id(element_id)
        if not element:
            print(f"Element {element_id} not found")
            return
        
        print(f"🖱️ Clicking: {element.get('description', 'unknown element')}")
        success = await self.elements.click_element(element_id)
        
        if success:
            print("✓ Click successful")
            # Wait a moment for page changes
            await asyncio.sleep(1)
        else:
            print("✗ Click failed")
    
    async def _take_screenshot(self, args: List[str]) -> None:
        """Take screenshot"""
        if not self.browser.is_ready():
            print("No page loaded. Navigate to a URL first.")
            return
        
        filename = args[0] if args else None
        print("📸 Taking screenshot...")
        
        filepath = await self.browser.screenshot(filename)
        if filepath:
            print(f"✓ Screenshot saved: {filepath}")
        else:
            print("✗ Screenshot failed")
    
    async def _show_info(self, args: List[str]) -> None:
        """Show page information"""
        if not self.browser.is_ready():
            print("No page loaded")
            return
        
        info = await self.browser.get_page_info()
        
        print("\n📄 Page Information:")
        print(f"  URL: {info.get('url', 'unknown')}")
        print(f"  Title: {info.get('title', 'unknown')}")
        if 'viewport' in info:
            viewport = info['viewport']
            print(f"  Viewport: {viewport.get('width', 0)}x{viewport.get('height', 0)}")
        print(f"  Ready State: {info.get('ready_state', 'unknown')}")
        
        if self.elements:
            count = self.elements.get_element_count()
            print(f"  Clickable Elements: {count}")
        print()
    
    async def _export_elements(self, args: List[str]) -> None:
        """Export elements to JSON"""
        if not self.elements or self.elements.get_element_count() == 0:
            print("No elements found. Use 'find' command first.")
            return
        
        filename = args[0] if args else None
        filepath = await self.elements.export_elements(filename)
        
        if filepath:
            print(f"✓ Elements exported to: {filepath}")
        else:
            print("✗ Export failed")
    
    async def _list_elements(self, args: List[str]) -> None:
        """List found elements"""
        if not self.elements or self.elements.get_element_count() == 0:
            print("No elements found. Use 'find' command first.")
            return
        
        self._display_elements_summary()
    
    def _display_elements_summary(self) -> None:
        """Display summary of found elements"""
        if not self.elements:
            return
        
        summary = self.elements.get_element_summary()
        max_display = 20  # Limit display for readability
        
        print("\n📋 Clickable Elements:")
        for i, item in enumerate(summary[:max_display]):
            print(f"  {item}")
        
        if len(summary) > max_display:
            print(f"  ... and {len(summary) - max_display} more")
        
        print(f"\n💡 Use 'click <number>' to interact with elements")
        print()
    
    async def _login(self, args: List[str]) -> None:
        """Handle login command"""
        if not self.browser.is_ready():
            print("No page loaded. Navigate to a website first.")
            return
        
        if not self.login_manager:
            print("Login manager not initialized.")
            return
        
        # Get current URL for login
        current_url = self.browser.get_current_url()
        
        # Get credentials
        if len(args) >= 2:
            username = args[0]
            password = args[1]
        else:
            username = await self._get_input("Username/Email: ")
            password = await self._get_input("Password: ")
        
        if not username.strip() or not password.strip():
            print("Username and password cannot be empty")
            return
        
        print(f"🔐 Attempting login to: {current_url}")
        
        # Attempt login
        result = await self.login_manager.attempt_login(current_url, username, password)
        
        # Display result
        if result['demo_mode']:
            print("🎭 DEMO MODE - Login simulation completed")
            if result['success']:
                print("✅ Demo login analysis successful")
                if 'form_analysis' in result:
                    analysis = result['form_analysis']
                    print(f"📊 Form Analysis:")
                    print(f"  - Form detected: {analysis.get('form_detected', False)}")
                    print(f"  - Username field: {analysis.get('username_field', False)}")
                    print(f"  - Password field: {analysis.get('password_field', False)}")
                    print(f"  - Submit button: {analysis.get('submit_button', False)}")
                
                if 'demo_actions' in result:
                    print("🎬 Demo Actions:")
                    for action in result['demo_actions']:
                        print(f"  - {action}")
            else:
                print(f"❌ Demo failed: {result['message']}")
        else:
            if result['success']:
                print("✅ Login successful!")
                await self.browser.screenshot('login_success.png')
                print("📸 Login screenshot saved")
            else:
                print(f"❌ Login failed: {result['message']}")
    
    async def _login_status(self, args: List[str]) -> None:
        """Show current login status"""
        if not self.login_manager:
            print("Login manager not available")
            return
        
        status_info = self.login_manager.get_session_info()
        
        print("\n🔐 Login Status:")
        print(f"  Logged in: {'✅ Yes' if status_info['logged_in'] else '❌ No'}")
        print(f"  Demo mode: {'🎭 Enabled' if status_info['demo_mode'] else '🔓 Disabled'}")
        
        if status_info['logged_in']:
            print(f"  Username: {status_info.get('username', 'Unknown')}")
            print(f"  Current URL: {status_info.get('current_url', 'Unknown')}")
            print(f"  Login time: {status_info.get('login_timestamp', 'Unknown')}")
        
        print(f"  Login attempts: {status_info.get('attempts_made', 0)}/{status_info.get('max_attempts', 3)}")
        print()
    
    async def _session_info(self, args: List[str]) -> None:
        """Show detailed session information"""
        if not self.login_manager:
            print("Login manager not available")
            return
        
        session_info = self.login_manager.get_session_info()
        
        print("\n📄 Session Information:")
        for key, value in session_info.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        print()
    
    async def _save_session(self, args: List[str]) -> None:
        """Save current session"""
        if not self.login_manager:
            print("Login manager not available")
            return
        
        filename = args[0] if args else None
        filepath = await self.login_manager.save_session(filename)
        
        if filepath:
            print(f"💾 Session saved to: {filepath}")
        else:
            print("❌ Failed to save session")
    
    async def _quit(self, args: List[str]) -> None:
        """Quit the application"""
        print("👋 Goodbye!")
        self.running = False
    
    async def run_single_command(self, command: str, url: Optional[str] = None) -> bool:
        """Run a single command (non-interactive mode)"""
        try:
            await self.browser.start()
            self.elements = ElementManager(self.config, self.browser.page)
            self.login_manager = LoginManager(self.config, self.browser)
            
            if url:
                success = await self.browser.navigate(url)
                if not success:
                    print(f"Failed to navigate to: {url}")
                    return False
            
            if command == 'screenshot':
                filepath = await self.browser.screenshot()
                return filepath is not None
            
            elif command == 'find' or command == 'elements':
                elements = await self.elements.find_clickable_elements()
                if elements:
                    print(f"Found {len(elements)} clickable elements")
                    summary = self.elements.get_element_summary()
                    for item in summary:
                        print(item)
                    return True
                return False
            
            elif command == 'info':
                info = await self.browser.get_page_info()
                print(f"URL: {info.get('url')}")
                print(f"Title: {info.get('title')}")
                return True
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
        
        finally:
            await self.browser.stop()