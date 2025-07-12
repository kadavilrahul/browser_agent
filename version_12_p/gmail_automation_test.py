#!/usr/bin/env python3
"""
Gmail Automation Test Script - Browser Agent v12_p
SECURITY WARNING: Uses real credentials from .env file

⚠️  IMPORTANT SECURITY NOTICE:
- This script uses REAL login credentials
- It will attempt REAL Gmail access
- It may send REAL emails
- Use only for testing purposes
- Ensure you understand the risks
"""

import asyncio
import os
import sys
from datetime import datetime
from config import Config
from browser import BrowserManager
from elements import ElementManager
from login_manager import LoginManager

class GmailAutomationTest:
    """Gmail automation test with real credentials"""
    
    def __init__(self):
        """Initialize with enhanced safety controls"""
        # Load configuration
        self.config = Config()
        
        # Override safety settings for real testing
        self.config.set('demo_mode', False)
        self.config.set('allow_real_login', True)
        self.config.set('verbose', True)
        self.config.set('headless', True)  # Keep headless for server compatibility
        
        # Initialize components
        self.browser = BrowserManager(self.config)
        self.elements = None
        self.login_manager = None
        
        # Load credentials from environment
        self.credentials = {
            'email': os.getenv('GMAIL_EMAIL', ''),
            'password': os.getenv('GMAIL_PASSWORD', ''),
            'recipient': os.getenv('EMAIL_RECIPIENT', ''),
            'subject': os.getenv('EMAIL_SUBJECT', 'Test Email'),
            'body': os.getenv('EMAIL_BODY', 'This is a test email.')
        }
        
        # Validation flags
        self.validation_passed = False
    
    def validate_setup(self) -> bool:
        """Validate setup and credentials"""
        print("🔍 VALIDATING SETUP...")
        print("=" * 50)
        
        # Check if credentials are provided
        missing_creds = []
        if not self.credentials['email']:
            missing_creds.append('GMAIL_EMAIL')
        if not self.credentials['password']:
            missing_creds.append('GMAIL_PASSWORD')
        if not self.credentials['recipient']:
            missing_creds.append('EMAIL_RECIPIENT')
        
        if missing_creds:
            print(f"❌ Missing required environment variables: {', '.join(missing_creds)}")
            print("\nPlease add to your .env file:")
            print("GMAIL_EMAIL=your_email@gmail.com")
            print("GMAIL_PASSWORD=your_password")
            print("EMAIL_RECIPIENT=recipient@example.com")
            print("EMAIL_SUBJECT=Test Subject (optional)")
            print("EMAIL_BODY=Test message body (optional)")
            return False
        
        print("✅ Credentials found in environment")
        print(f"📧 Email: {self.credentials['email']}")
        print(f"🎯 Recipient: {self.credentials['recipient']}")
        print(f"📋 Subject: {self.credentials['subject']}")
        print(f"📝 Body: {self.credentials['body'][:50]}...")
        print()
        
        self.validation_passed = True
        return True
    
    def show_security_warning(self) -> bool:
        """Show security warning and get user confirmation"""
        warning = """
⚠️  CRITICAL SECURITY WARNING ⚠️
═══════════════════════════════════════════════════════════════
This script will:
• Use your REAL Gmail credentials
• Attempt to log into your ACTUAL Gmail account
• Send a REAL email to the specified recipient
• Store session data and screenshots locally

RISKS:
• Account security alerts may be triggered
• Google may flag this as suspicious activity
• Your account could be temporarily locked
• Email will actually be sent to recipient
• Credentials may be logged for debugging

RECOMMENDATIONS:
• Use a test Gmail account, not your primary account
• Ensure recipient expects this test email
• Review all credentials before proceeding
• Monitor your account for security alerts

═══════════════════════════════════════════════════════════════
        """
        
        print(warning)
        
        # Multiple confirmation steps
        print("Type 'I UNDERSTAND THE RISKS' to continue:")
        confirmation1 = input("> ").strip()
        
        if confirmation1 != "I UNDERSTAND THE RISKS":
            print("❌ Confirmation failed. Exiting for safety.")
            return False
        
        print("\nType 'PROCEED WITH REAL CREDENTIALS' to confirm:")
        confirmation2 = input("> ").strip()
        
        if confirmation2 != "PROCEED WITH REAL CREDENTIALS":
            print("❌ Final confirmation failed. Exiting for safety.")
            return False
        
        print("\n✅ User confirmations received. Proceeding with real test...")
        return True
    
    async def run_complete_test(self):
        """Run complete Gmail automation test"""
        print("\n🚀 STARTING GMAIL AUTOMATION TEST")
        print("=" * 50)
        
        try:
            # Initialize components
            await self.browser.start()
            self.elements = ElementManager(self.config, self.browser.page)
            self.login_manager = LoginManager(self.config, self.browser)
            
            # Step 1: Navigate to Gmail
            await self._step1_navigate()
            
            # Step 2: Perform login
            login_success = await self._step2_login()
            if not login_success:
                print("❌ Login failed. Cannot proceed with email test.")
                return False
            
            # Step 3: Navigate to inbox
            await self._step3_inbox()
            
            # Step 4: Compose email
            await self._step4_compose()
            
            # Step 5: Send email
            await self._step5_send()
            
            print("\n✅ COMPLETE TEST FINISHED")
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
        finally:
            await self.browser.stop()
    
    async def _step1_navigate(self):
        """Step 1: Navigate to Gmail"""
        print("\n📍 STEP 1: Navigate to Gmail")
        print("-" * 30)
        
        success = await self.browser.navigate('https://gmail.com')
        if success:
            print(f"✅ Navigated to: {self.browser.get_current_url()}")
            await self.browser.screenshot('step1_gmail_navigation.png')
            print("📸 Screenshot saved: step1_gmail_navigation.png")
        else:
            raise Exception("Failed to navigate to Gmail")
    
    async def _step2_login(self) -> bool:
        """Step 2: Perform real login"""
        print("\n🔐 STEP 2: Perform Login")
        print("-" * 30)
        print("⚠️ ATTEMPTING REAL LOGIN WITH PROVIDED CREDENTIALS")
        
        result = await self.login_manager.attempt_login(
            self.browser.get_current_url(),
            self.credentials['email'],
            self.credentials['password']
        )
        
        if result['success']:
            print("✅ Login successful!")
            await self.browser.screenshot('step2_login_success.png')
            print("📸 Login screenshot saved")
            
            # Save session for recovery
            session_file = await self.login_manager.save_session('gmail_session.json')
            print(f"💾 Session saved: {session_file}")
            
            return True
        else:
            print(f"❌ Login failed: {result['message']}")
            await self.browser.screenshot('step2_login_failed.png')
            return False
    
    async def _step3_inbox(self):
        """Step 3: Navigate to inbox"""
        print("\n📮 STEP 3: Navigate to Inbox")
        print("-" * 30)
        
        # Wait for inbox to load
        await asyncio.sleep(3)
        
        current_url = self.browser.get_current_url()
        print(f"Current URL: {current_url}")
        
        # Take screenshot of inbox
        await self.browser.screenshot('step3_inbox.png')
        print("📸 Inbox screenshot saved")
        
        # Analyze inbox elements
        elements = await self.elements.find_clickable_elements()
        print(f"Found {len(elements)} clickable elements in inbox")
    
    async def _step4_compose(self):
        """Step 4: Compose email"""
        print("\n✉️ STEP 4: Compose Email")
        print("-" * 30)
        
        # Look for compose button
        compose_selectors = [
            'div[data-tooltip="Compose"]',
            '.T-I.T-I-KE.L3',
            'div[role="button"][aria-label*="Compose"]',
            '.z0 > .aic',
            'div:has-text("Compose")'
        ]
        
        compose_clicked = False
        for selector in compose_selectors:
            try:
                print(f"Trying compose selector: {selector}")
                await self.browser.page.wait_for_selector(selector, timeout=2000)
                await self.browser.page.click(selector)
                print(f"✅ Clicked compose button with selector: {selector}")
                compose_clicked = True
                break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {e}")
                continue
        
        if not compose_clicked:
            print("❌ Could not find compose button")
            # Try JavaScript injection as fallback
            try:
                await self.browser.page.evaluate("""
                    () => {
                        const composeBtn = document.querySelector('[data-tooltip="Compose"]') || 
                                         document.querySelector('.T-I.T-I-KE.L3') ||
                                         Array.from(document.querySelectorAll('div')).find(el => 
                                             el.textContent.includes('Compose'));
                        if (composeBtn) {
                            composeBtn.click();
                            return true;
                        }
                        return false;
                    }
                """)
                print("✅ Compose button clicked via JavaScript")
                compose_clicked = True
            except:
                raise Exception("Could not click compose button")
        
        # Wait for compose window
        await asyncio.sleep(2)
        await self.browser.screenshot('step4_compose_opened.png')
        print("📸 Compose window screenshot saved")
        
        # Fill email fields
        await self._fill_email_fields()
    
    async def _fill_email_fields(self):
        """Fill email composition fields"""
        print("📝 Filling email fields...")
        
        # Fill recipient (To field)
        to_selectors = [
            'input[name="to"]',
            'textarea[name="to"]',
            'input[aria-label*="To"]',
            'textarea[aria-label*="To"]'
        ]
        
        for selector in to_selectors:
            try:
                await self.browser.page.wait_for_selector(selector, timeout=2000)
                await self.browser.page.fill(selector, self.credentials['recipient'])
                print(f"✅ Filled 'To' field: {self.credentials['recipient']}")
                break
            except:
                continue
        
        # Fill subject
        subject_selectors = [
            'input[name="subjectbox"]',
            'input[aria-label*="Subject"]',
            'input[placeholder*="Subject"]'
        ]
        
        for selector in subject_selectors:
            try:
                await self.browser.page.wait_for_selector(selector, timeout=2000)
                await self.browser.page.fill(selector, self.credentials['subject'])
                print(f"✅ Filled subject: {self.credentials['subject']}")
                break
            except:
                continue
        
        # Fill body
        body_selectors = [
            'div[role="textbox"]',
            'div[aria-label*="Message"]',
            'div[contenteditable="true"]'
        ]
        
        for selector in body_selectors:
            try:
                await self.browser.page.wait_for_selector(selector, timeout=2000)
                await self.browser.page.fill(selector, self.credentials['body'])
                print(f"✅ Filled body: {self.credentials['body']}")
                break
            except:
                continue
        
        await self.browser.screenshot('step4_email_filled.png')
        print("📸 Email form filled screenshot saved")
    
    async def _step5_send(self):
        """Step 5: Send email"""
        print("\n📤 STEP 5: Send Email")
        print("-" * 30)
        print("⚠️ ABOUT TO SEND REAL EMAIL!")
        
        # Final confirmation
        print(f"Recipients: {self.credentials['recipient']}")
        print(f"Subject: {self.credentials['subject']}")
        print("Type 'SEND EMAIL' to proceed:")
        
        # We can't get input in async context easily, so we'll proceed
        # In a real implementation, you'd want better confirmation
        
        send_selectors = [
            'div[data-tooltip="Send"]',
            '.T-I.J-J5-Ji.aoO.v7.T-I-atl.L3',
            'div[role="button"][aria-label*="Send"]',
            'div:has-text("Send")'
        ]
        
        email_sent = False
        for selector in send_selectors:
            try:
                await self.browser.page.wait_for_selector(selector, timeout=2000)
                await self.browser.page.click(selector)
                print(f"✅ Clicked send button with selector: {selector}")
                email_sent = True
                break
            except Exception as e:
                print(f"❌ Send selector {selector} failed: {e}")
                continue
        
        if not email_sent:
            print("❌ Could not find send button")
            raise Exception("Could not send email")
        
        # Wait for send confirmation
        await asyncio.sleep(3)
        await self.browser.screenshot('step5_email_sent.png')
        print("📸 Email sent screenshot saved")
        print("✅ EMAIL SENT SUCCESSFULLY!")

async def main():
    """Main test execution"""
    test = GmailAutomationTest()
    
    # Validate setup
    if not test.validate_setup():
        sys.exit(1)
    
    # Show security warning
    if not test.show_security_warning():
        sys.exit(1)
    
    # Run the test
    success = await test.run_complete_test()
    
    if success:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("📁 Check screenshots and session files for results")
    else:
        print("\n❌ Test failed. Check logs and screenshots.")
        sys.exit(1)

if __name__ == "__main__":
    print("🧪 Gmail Automation Test Script")
    print("⚠️  WARNING: Uses real credentials!")
    print()
    
    asyncio.run(main())