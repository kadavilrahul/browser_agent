#!/usr/bin/env python3
"""
Interactive Browser Controller

This script provides real-time browser interaction where you can:
1. Control the browser with commands
2. Navigate to any website
3. Interact with elements
4. Keep the browser open indefinitely
5. Execute JavaScript
6. Fill forms and click buttons
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
from web_browsing_agent import WebBrowsingAgent

# Load environment variables
load_dotenv()

class InteractiveBrowser:
    def __init__(self):
        self.agent = None
        self.running = True
        
    async def start(self):
        """Start the interactive browser session"""
        print("🌐 Starting Interactive Browser...")
        print("=" * 50)
        
        # Start the browser agent
        self.agent = WebBrowsingAgent()
        await self.agent.__aenter__()
        await self.agent.new_page()
        
        print("✅ Browser is now open and ready!")
        print("🎯 You can now interact with the browser using commands below.")
        print("=" * 50)
        
        # Start the interactive loop
        await self.interactive_loop()
        
    async def interactive_loop(self):
        """Main interactive command loop"""
        while self.running:
            try:
                print("\n" + "=" * 50)
                print("🎮 BROWSER CONTROL COMMANDS:")
                print("=" * 50)
                print("1. 'go <url>' - Navigate to a website")
                print("2. 'click <selector>' - Click an element")
                print("3. 'type <selector> <text>' - Type text in an element")
                print("4. 'js <code>' - Execute JavaScript")
                print("5. 'screenshot' - Take a screenshot")
                print("6. 'current' - Show current URL")
                print("7. 'title' - Show page title")
                print("8. 'elements' - List clickable elements")
                print("9. 'wait <seconds>' - Wait for specified seconds")
                print("10. 'help' - Show this help")
                print("11. 'exit' - Close browser and exit")
                print("=" * 50)
                
                # Get user command
                command = input("\n🎯 Enter command: ").strip()
                
                if not command:
                    continue
                    
                # Parse and execute command
                await self.execute_command(command)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Received Ctrl+C. Closing browser...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
        await self.cleanup()
        
    async def execute_command(self, command):
        """Execute a user command"""
        parts = command.split(' ', 2)
        cmd = parts[0].lower()
        
        try:
            if cmd == 'go' and len(parts) >= 2:
                url = parts[1]
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                print(f"🔍 Navigating to {url}...")
                await self.agent.navigate(url)
                print(f"✅ Successfully navigated to {self.agent.page.url}")
                
            elif cmd == 'click' and len(parts) >= 2:
                selector = parts[1]
                print(f"👆 Clicking element: {selector}")
                await self.agent.page.click(selector)
                print("✅ Element clicked")
                
            elif cmd == 'type' and len(parts) >= 3:
                selector = parts[1]
                text = parts[2]
                print(f"⌨️ Typing '{text}' in element: {selector}")
                await self.agent.page.fill(selector, text)
                print("✅ Text entered")
                
            elif cmd == 'js' and len(parts) >= 2:
                js_code = ' '.join(parts[1:])
                print(f"🔧 Executing JavaScript: {js_code}")
                result = await self.agent.page.evaluate(js_code)
                print(f"✅ Result: {result}")
                
            elif cmd == 'screenshot':
                filename = f"interactive_screenshot_{int(asyncio.get_event_loop().time())}.png"
                await self.agent.take_screenshot(filename)
                print(f"📸 Screenshot saved: {filename}")
                
            elif cmd == 'current':
                print(f"🌐 Current URL: {self.agent.page.url}")
                
            elif cmd == 'title':
                title = await self.agent.page.title()
                print(f"📄 Page Title: {title}")
                
            elif cmd == 'elements':
                print("🔍 Finding clickable elements...")
                elements = await self.agent.page.query_selector_all('a, button, input[type="submit"], input[type="button"]')
                print(f"📋 Found {len(elements)} clickable elements:")
                for i, elem in enumerate(elements[:10]):  # Show first 10
                    try:
                        tag = await elem.evaluate('el => el.tagName')
                        text = await elem.evaluate('el => el.textContent || el.value || el.placeholder || "No text"')
                        text = text.strip()[:50]  # Limit text length
                        print(f"  {i+1}. <{tag.lower()}> {text}")
                    except:
                        print(f"  {i+1}. Element (could not read)")
                        
            elif cmd == 'wait' and len(parts) >= 2:
                try:
                    seconds = float(parts[1])
                    print(f"⏰ Waiting {seconds} seconds...")
                    await asyncio.sleep(seconds)
                    print("✅ Wait complete")
                except ValueError:
                    print("❌ Invalid number for wait time")
                    
            elif cmd == 'help':
                # Help is shown in the main loop
                pass
                
            elif cmd == 'exit':
                print("👋 Closing browser...")
                self.running = False
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except Exception as e:
            print(f"❌ Command failed: {e}")
            
    async def cleanup(self):
        """Clean up browser resources"""
        if self.agent:
            await self.agent.__aexit__(None, None, None)
        print("✅ Browser closed. Goodbye!")

async def main():
    """Main function"""
    print("🚀 INTERACTIVE BROWSER CONTROLLER")
    print("=" * 50)
    print("This will open a browser that you can control with commands.")
    print("The browser will stay open until you type 'exit' or press Ctrl+C.")
    print("=" * 50)
    
    # Check if we should use headless mode
    headless = os.getenv('HEADLESS', 'true').lower() == 'true'
    if headless:
        print("ℹ️  Running in headless mode (no visible window)")
        print("   Use 'screenshot' command to see what's happening")
    else:
        print("👁️  Running in visible mode (browser window will appear)")
    
    print("=" * 50)
    input("Press Enter to start the browser...")
    
    # Start interactive browser
    browser = InteractiveBrowser()
    await browser.start()

if __name__ == "__main__":
    asyncio.run(main())