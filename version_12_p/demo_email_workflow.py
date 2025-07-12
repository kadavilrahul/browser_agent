#!/usr/bin/env python3
"""
Email Workflow Demonstration - Browser Agent v12_p
Shows complete Gmail automation workflow with DEMO credentials only
"""

import asyncio
import json
from datetime import datetime
from config import Config
from browser import BrowserManager
from elements import ElementManager

class EmailWorkflowDemo:
    """Demonstrates complete email automation workflow safely"""
    
    def __init__(self):
        self.config = Config()
        self.config.set('headless', True)  # Always headless for safety
        self.config.set('verbose', True)
        self.browser = BrowserManager(self.config)
        self.elements = None
        
        # DEMO credentials - NOT real credentials
        self.demo_credentials = {
            'email': 'demo@example.com',
            'password': '***DEMO_PASSWORD***'
        }
        
        self.demo_email = {
            'to': 'demo@example.com',
            'subject': 'Demo Subject - Hello',
            'body': 'Demo Body - How are you?'
        }
    
    async def demonstrate_workflow(self):
        """Demonstrates the complete email automation workflow"""
        print("🎭 EMAIL AUTOMATION WORKFLOW DEMONSTRATION")
        print("=" * 50)
        print("⚠️  USING DEMO CREDENTIALS ONLY - NO REAL LOGIN")
        print()
        
        try:
            await self.browser.start()
            self.elements = ElementManager(self.config, self.browser.page)
            
            # Step 1: Navigate to Gmail
            await self._demo_step1_navigate()
            
            # Step 2: Analyze login page
            await self._demo_step2_analyze_login()
            
            # Step 3: Demonstrate form filling (without real credentials)
            await self._demo_step3_form_analysis()
            
            # Step 4: Demonstrate email composition workflow
            await self._demo_step4_email_composition()
            
            print("\n✅ DEMO COMPLETED SUCCESSFULLY")
            print("🔒 No real credentials used, no emails sent")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
        finally:
            await self.browser.stop()
    
    async def _demo_step1_navigate(self):
        """Step 1: Navigate to Gmail"""
        print("📍 STEP 1: Navigate to Gmail")
        print("-" * 30)
        
        success = await self.browser.navigate('gmail.com')
        if success:
            print(f"✅ Successfully navigated to: {self.browser.get_current_url()}")
            await self.browser.screenshot('step1_gmail_login.png')
            print("📸 Screenshot saved: step1_gmail_login.png")
        else:
            print("❌ Navigation failed")
        print()
    
    async def _demo_step2_analyze_login(self):
        """Step 2: Analyze login page elements"""
        print("🔍 STEP 2: Analyze Login Page")
        print("-" * 30)
        
        elements = await self.elements.find_clickable_elements()
        print(f"Found {len(elements)} interactive elements:")
        
        # Look for login-specific elements
        login_elements = self._identify_login_elements(elements)
        
        for element_type, element_data in login_elements.items():
            if element_data:
                print(f"  📧 {element_type}: {element_data['description']}")
            else:
                print(f"  ❌ {element_type}: Not found")
        
        await self.elements.export_elements('step2_login_elements.json')
        print("💾 Elements exported to: step2_login_elements.json")
        print()
    
    def _identify_login_elements(self, elements):
        """Identify login-specific elements"""
        login_elements = {
            'email_field': None,
            'password_field': None,
            'next_button': None,
            'submit_button': None
        }
        
        for element in elements:
            text = element.get('text', '').lower()
            tag = element.get('tag', '')
            element_type = element.get('type', '')
            
            # Identify email/username field
            if (tag == 'input' and 
                ('email' in element_type or 'text' in element_type) and
                not login_elements['email_field']):
                login_elements['email_field'] = element
            
            # Identify password field
            elif (tag == 'input' and 'password' in element_type):
                login_elements['password_field'] = element
            
            # Identify next/submit buttons
            elif tag == 'button':
                if 'next' in text:
                    login_elements['next_button'] = element
                elif any(word in text for word in ['sign in', 'login', 'submit']):
                    login_elements['submit_button'] = element
        
        return login_elements
    
    async def _demo_step3_form_analysis(self):
        """Step 3: Demonstrate form filling analysis (NO REAL FILLING)"""
        print("📝 STEP 3: Form Filling Analysis (DEMO MODE)")
        print("-" * 45)
        
        print(f"🎭 Would fill email field with: {self.demo_credentials['email']}")
        print(f"🎭 Would fill password field with: {self.demo_credentials['password']}")
        print("🎭 Would click 'Next' button")
        print("🎭 Would wait for authentication")
        
        # Instead of real filling, we'll just demonstrate the detection
        script = """
        () => {
            const emailFields = document.querySelectorAll('input[type="email"], input[type="text"]');
            const passwordFields = document.querySelectorAll('input[type="password"]');
            const buttons = document.querySelectorAll('button');
            
            return {
                emailFields: emailFields.length,
                passwordFields: passwordFields.length,
                buttons: buttons.length,
                formData: {
                    hasEmailField: emailFields.length > 0,
                    hasPasswordField: passwordFields.length > 0,
                    hasSubmitButton: Array.from(buttons).some(btn => 
                        btn.textContent.toLowerCase().includes('next') ||
                        btn.textContent.toLowerCase().includes('sign'))
                }
            };
        }
        """
        
        form_analysis = await self.browser.evaluate_script(script)
        print(f"📊 Form Analysis Results:")
        print(f"  - Email fields detected: {form_analysis.get('emailFields', 0)}")
        print(f"  - Password fields detected: {form_analysis.get('passwordFields', 0)}")
        print(f"  - Buttons detected: {form_analysis.get('buttons', 0)}")
        print(f"  - Ready for automation: {form_analysis.get('formData', {}).get('hasEmailField', False)}")
        print()
    
    async def _demo_step4_email_composition(self):
        """Step 4: Demonstrate email composition workflow"""
        print("✉️ STEP 4: Email Composition Workflow (DEMO MODE)")
        print("-" * 50)
        
        print("🎭 SIMULATED POST-LOGIN WORKFLOW:")
        print(f"  1. Would navigate to Gmail inbox")
        print(f"  2. Would click 'Compose' button")
        print(f"  3. Would fill 'To' field with: {self.demo_email['to']}")
        print(f"  4. Would fill 'Subject' field with: {self.demo_email['subject']}")
        print(f"  5. Would fill 'Body' field with: {self.demo_email['body']}")
        print(f"  6. Would click 'Send' button")
        
        # Demonstrate element detection for Gmail compose
        compose_elements = {
            'compose_button': "button[data-tooltip='Compose'], .T-I.T-I-KE.L3",
            'to_field': "input[name='to'], textarea[name='to']",
            'subject_field': "input[name='subjectbox'], input[placeholder*='Subject']",
            'body_field': "div[role='textbox'], textarea[aria-label*='Message']",
            'send_button': "div[data-tooltip='Send'], .T-I.J-J5-Ji.aoO.v7.T-I-atl.L3"
        }
        
        print("\n🔍 Gmail Compose Element Selectors:")
        for element_name, selector in compose_elements.items():
            print(f"  - {element_name}: {selector}")
        
        # Create a demo workflow JSON
        workflow = {
            'timestamp': datetime.now().isoformat(),
            'workflow': 'Gmail Email Automation',
            'steps': [
                {'step': 1, 'action': 'navigate', 'target': 'gmail.com'},
                {'step': 2, 'action': 'fill', 'target': 'email_field', 'value': self.demo_credentials['email']},
                {'step': 3, 'action': 'click', 'target': 'next_button'},
                {'step': 4, 'action': 'fill', 'target': 'password_field', 'value': '***HIDDEN***'},
                {'step': 5, 'action': 'click', 'target': 'submit_button'},
                {'step': 6, 'action': 'wait', 'target': 'inbox_loaded'},
                {'step': 7, 'action': 'click', 'target': 'compose_button'},
                {'step': 8, 'action': 'fill', 'target': 'to_field', 'value': self.demo_email['to']},
                {'step': 9, 'action': 'fill', 'target': 'subject_field', 'value': self.demo_email['subject']},
                {'step': 10, 'action': 'fill', 'target': 'body_field', 'value': self.demo_email['body']},
                {'step': 11, 'action': 'click', 'target': 'send_button'},
                {'step': 12, 'action': 'verify', 'target': 'email_sent'}
            ],
            'safety_notes': [
                'Demo uses placeholder credentials only',
                'No real authentication performed',
                'No emails actually sent',
                'All actions are simulated for demonstration'
            ]
        }
        
        with open('output/demo_email_workflow.json', 'w') as f:
            json.dump(workflow, f, indent=2)
        
        print("\n💾 Complete workflow saved to: output/demo_email_workflow.json")
        print("\n⚠️  SAFETY NOTES:")
        for note in workflow['safety_notes']:
            print(f"   - {note}")

async def main():
    """Run the email workflow demonstration"""
    demo = EmailWorkflowDemo()
    await demo.demonstrate_workflow()

if __name__ == "__main__":
    print("🚀 Starting Email Workflow Demonstration...")
    print("🔒 This demo shows capabilities without using real credentials")
    print()
    asyncio.run(main())