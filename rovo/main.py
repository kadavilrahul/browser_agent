#!/usr/bin/env python3
"""
ROVO Browser Agent - Minimalistic Agentic Browser Automation
"""
import asyncio
import argparse
import sys
from config import Config
from browser_manager import BrowserManager
from agents import BrowserCrew

class RovoBrowserAgent:
    """Main ROVO Browser Agent application"""
    
    def __init__(self, config_file: str = None):
        self.config = Config(config_file)
        self.browser_manager = BrowserManager(self.config)
        self.crew = None
        self.running = False
    
    async def start(self):
        """Start the browser agent"""
        try:
            print("🚀 Starting ROVO Browser Agent...")
            
            # Start browser
            await self.browser_manager.start()
            
            # Create crew
            self.crew = BrowserCrew(self.browser_manager, self.config)
            
            self.running = True
            print("✅ ROVO Browser Agent is ready!")
            
        except Exception as e:
            print(f"❌ Failed to start: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the browser agent"""
        try:
            self.running = False
            if self.browser_manager:
                await self.browser_manager.close()
            print("🔒 ROVO Browser Agent stopped")
        except Exception as e:
            print(f"❌ Shutdown error: {e}")
    
    def navigate_and_analyze(self, url: str) -> str:
        """Simple navigation and analysis"""
        if not self.running:
            return "❌ Agent not started"
        
        print(f"🎯 Executing: Navigate and analyze {url}")
        result = self.crew.execute_simple_navigation(url)
        return result
    
    def goal_based_browsing(self, url: str, goal: str) -> str:
        """Goal-based browsing"""
        if not self.running:
            return "❌ Agent not started"
        
        print(f"🎯 Executing: {goal} on {url}")
        result = self.crew.execute_goal_based_browsing(url, goal)
        return result
    
    def full_automation(self, url: str, goal: str, element_to_click: str = None) -> str:
        """Full automation workflow"""
        if not self.running:
            return "❌ Agent not started"
        
        print(f"🎯 Executing: Full automation for '{goal}' on {url}")
        result = self.crew.execute_full_automation(url, goal, element_to_click)
        return result
    
    async def interactive_mode(self):
        """Interactive command-line interface"""
        print("\n" + "="*60)
        print("🤖 ROVO BROWSER AGENT - INTERACTIVE MODE")
        print("="*60)
        print("Commands:")
        print("  nav <url>                    - Navigate and analyze")
        print("  goal <url> <goal>           - Goal-based browsing")
        print("  auto <url> <goal> [element] - Full automation")
        print("  screenshot                  - Take screenshot")
        print("  info                       - Get page info")
        print("  help                       - Show this help")
        print("  quit                       - Exit")
        print("="*60)
        
        while self.running:
            try:
                command = input("\n🎮 ROVO> ").strip()
                
                if not command:
                    continue
                
                parts = command.split(' ', 2)
                cmd = parts[0].lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    break
                elif cmd == 'help':
                    print("Available commands: nav, goal, auto, screenshot, info, help, quit")
                elif cmd == 'nav' and len(parts) >= 2:
                    url = parts[1]
                    result = self.navigate_and_analyze(url)
                    print(f"\n📋 Result:\n{result}")
                elif cmd == 'goal' and len(parts) >= 3:
                    url = parts[1]
                    goal = parts[2]
                    result = self.goal_based_browsing(url, goal)
                    print(f"\n📋 Result:\n{result}")
                elif cmd == 'auto' and len(parts) >= 3:
                    url = parts[1]
                    goal_and_element = parts[2].split(' ', 1)
                    goal = goal_and_element[0]
                    element = goal_and_element[1] if len(goal_and_element) > 1 else None
                    result = self.full_automation(url, goal, element)
                    print(f"\n📋 Result:\n{result}")
                elif cmd == 'screenshot':
                    success = await self.browser_manager.take_screenshot()
                    if success:
                        print("📸 Screenshot taken")
                    else:
                        print("❌ Screenshot failed")
                elif cmd == 'info':
                    info = await self.browser_manager.get_page_info()
                    print(f"📄 Page Info: {info}")
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Received Ctrl+C. Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ROVO Browser Agent - Agentic Browser Automation')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--url', help='URL to navigate to')
    parser.add_argument('--goal', help='Goal for the browsing session')
    parser.add_argument('--element', help='Element to interact with')
    parser.add_argument('--mode', choices=['nav', 'goal', 'auto', 'interactive'], 
                       default='interactive', help='Execution mode')
    parser.add_argument('--headless', type=bool, help='Run in headless mode')
    
    args = parser.parse_args()
    
    # Create agent
    agent = RovoBrowserAgent(args.config)
    
    # Override headless setting if provided
    if args.headless is not None:
        agent.config._config['headless'] = args.headless
    
    try:
        # Start agent
        await agent.start()
        
        # Execute based on mode
        if args.mode == 'interactive':
            await agent.interactive_mode()
        elif args.mode == 'nav' and args.url:
            result = agent.navigate_and_analyze(args.url)
            print(f"\n📋 Result:\n{result}")
        elif args.mode == 'goal' and args.url and args.goal:
            result = agent.goal_based_browsing(args.url, args.goal)
            print(f"\n📋 Result:\n{result}")
        elif args.mode == 'auto' and args.url and args.goal:
            result = agent.full_automation(args.url, args.goal, args.element)
            print(f"\n📋 Result:\n{result}")
        else:
            print("❌ Invalid arguments for selected mode")
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Application error: {e}")
        return 1
    
    finally:
        await agent.stop()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted")
        sys.exit(1)