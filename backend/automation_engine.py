"""
AI-Driven Web Automation Engine
Demonstrates automated SaaS user management using Playwright and simulated AI
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, Page, Browser
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAdapter:
    """
    Simulated AI adapter for DOM parsing and UI element detection
    In production, this would integrate with real LLMs like OpenAI, Anthropic, or Google
    """
    
    def __init__(self):
        self.confidence_threshold = 0.8
        
    async def parse_dom_for_table_data(self, page_content: str, page_url: str) -> Dict[str, Any]:
        """
        Simulate AI parsing of DOM to extract table structure and data
        Real implementation would send DOM to LLM with appropriate prompts
        """
        logger.info("AI Adapter: Analyzing DOM structure for table data extraction")
        
        # Simulate AI decision-making process
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # For demo purposes, return selectors that work with our mock SaaS portal
        if "mock-saas" in page_url or "users" in page_url:
            return {
                "table_selector": "table#users",
                "row_selector": "table#users tbody tr",
                "columns": {
                    "name": {"selector": "td:nth-child(1)", "confidence": 0.95},
                    "email": {"selector": "td:nth-child(2)", "confidence": 0.95},
                    "role": {"selector": "td:nth-child(3)", "confidence": 0.90},
                    "status": {"selector": "td:nth-child(4)", "confidence": 0.90},
                    "last_login": {"selector": "td:nth-child(5)", "confidence": 0.85}
                },
                "next_page_selector": "button:has-text('Next')",
                "confidence": 0.92
            }
        else:
            # Generic table detection
            return {
                "table_selector": "table",
                "row_selector": "table tbody tr, table tr",
                "columns": {
                    "col1": {"selector": "td:nth-child(1)", "confidence": 0.70},
                    "col2": {"selector": "td:nth-child(2)", "confidence": 0.70},
                    "col3": {"selector": "td:nth-child(3)", "confidence": 0.70}
                },
                "confidence": 0.65
            }
    
    async def detect_form_fields(self, page_content: str, form_context: str) -> Dict[str, Any]:
        """
        Simulate AI detection of form fields for user provisioning
        """
        logger.info(f"AI Adapter: Detecting form fields for {form_context}")
        await asyncio.sleep(0.3)
        
        if "add-user" in form_context or "create" in form_context.lower():
            return {
                "form_selector": "form",
                "fields": {
                    "name": {"selector": "input[name='name'], input[id='name']", "confidence": 0.95},
                    "email": {"selector": "input[name='email'], input[id='email']", "confidence": 0.95},
                    "role": {"selector": "select[name='role'], select[id='role']", "confidence": 0.90}
                },
                "submit_button": {"selector": "button[type='submit'], button:has-text('Create')", "confidence": 0.90},
                "confidence": 0.92
            }
        else:
            return {
                "form_selector": "form",
                "fields": {},
                "confidence": 0.50
            }
    
    async def adapt_to_ui_changes(self, previous_selectors: Dict, current_dom: str) -> Dict[str, Any]:
        """
        Simulate AI adaptation to UI changes by suggesting alternative selectors
        """
        logger.info("AI Adapter: Adapting to UI changes")
        await asyncio.sleep(0.4)
        
        # Simulate generating alternative selectors
        alternatives = []
        for field, config in previous_selectors.get("columns", {}).items():
            alternatives.append({
                "field": field,
                "selectors": [
                    config["selector"],
                    f"[data-testid='{field}']",
                    f".{field}-column",
                    f"td:contains('{field.title()}')"
                ],
                "confidence": max(0.6, config.get("confidence", 0.8) - 0.1)
            })
        
        return {
            "adapted_selectors": alternatives,
            "confidence": 0.85,
            "changes_detected": True
        }

class AutomationEngine:
    """
    Main automation engine using Playwright for browser automation
    """
    
    def __init__(self):
        self.ai_adapter = AIAdapter()
        self.browser: Optional[Browser] = None
        self.session_data = {}
        
    async def start_browser(self) -> Browser:
        """Initialize browser instance"""
        if self.browser:
            return self.browser
            
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        return self.browser
    
    async def close_browser(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    async def authenticate(self, base_url: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Handle authentication including MFA simulation
        """
        browser = await self.start_browser()
        page = await browser.new_page()
        
        logs = []
        
        try:
            # Navigate to login page
            login_url = f"{base_url}/mock-saas"
            await page.goto(login_url)
            logs.append(f"Navigated to login page: {login_url}")
            
            # Wait for login form
            await page.wait_for_selector('input[name="username"]', timeout=10000)
            logs.append("Login form detected")
            
            # Fill credentials
            await page.fill('input[name="username"]', credentials.get('username', 'admin'))
            await page.fill('input[name="password"]', credentials.get('password', 'password'))
            logs.append("Credentials entered")
            
            # Submit login
            await page.click('button[type="submit"]')
            logs.append("Login form submitted")
            
            # Handle MFA if present
            try:
                await page.wait_for_selector('input[name="otp"]', timeout=5000)
                logs.append("MFA challenge detected")
                
                # Enter OTP (demo: use 123456)
                await page.fill('input[name="otp"]', '123456')
                await page.click('button:has-text("Verify")')
                logs.append("MFA code submitted")
                
            except Exception:
                logs.append("No MFA required or MFA step skipped")
            
            # Wait for successful authentication
            await page.wait_for_selector('text="User Management"', timeout=10000)
            logs.append("Authentication successful - dashboard loaded")
            
            # Store session data
            cookies = await page.context.cookies()
            self.session_data = {
                'cookies': cookies,
                'authenticated': True,
                'timestamp': datetime.now().isoformat()
            }
            
            await page.close()
            
            return {
                'success': True,
                'logs': logs,
                'session_stored': True
            }
            
        except Exception as e:
            logs.append(f"Authentication failed: {str(e)}")
            await page.close()
            return {
                'success': False,
                'error': str(e),
                'logs': logs
            }
    
    async def scrape_users(self, base_url: str, max_pages: int = 3) -> Dict[str, Any]:
        """
        Scrape user data from SaaS portal using AI-guided selectors
        """
        if not self.session_data.get('authenticated'):
            return {'error': 'Not authenticated', 'users': []}
            
        browser = await self.start_browser()
        page = await browser.new_page()
        
        # Restore session
        if self.session_data.get('cookies'):
            await page.context.add_cookies(self.session_data['cookies'])
        
        logs = []
        all_users = []
        
        try:
            # Navigate to users page
            users_url = f"{base_url}/mock-saas"
            await page.goto(users_url)
            logs.append(f"Navigated to users page: {users_url}")
            
            # Wait for user table
            await page.wait_for_selector('table', timeout=10000)
            logs.append("User table detected")
            
            current_page = 1
            
            while current_page <= max_pages:
                # Get DOM content for AI analysis
                page_content = await page.content()
                
                # Use AI adapter to determine table structure
                table_config = await self.ai_adapter.parse_dom_for_table_data(
                    page_content, users_url
                )
                logs.append(f"AI analysis complete - confidence: {table_config['confidence']}")
                
                if table_config['confidence'] < 0.7:
                    logs.append("Low confidence in table structure - attempting fallback")
                    # Implement fallback logic here
                
                # Extract user data using AI-provided selectors
                rows = await page.query_selector_all(table_config['row_selector'])
                page_users = []
                
                for row in rows:
                    user_data = {}
                    for field, config in table_config['columns'].items():
                        try:
                            cell = await row.query_selector(config['selector'])
                            if cell:
                                user_data[field] = await cell.inner_text()
                        except Exception:
                            user_data[field] = ""
                    
                    if user_data.get('name') or user_data.get('email'):
                        page_users.append(user_data)
                
                all_users.extend(page_users)
                logs.append(f"Page {current_page}: Extracted {len(page_users)} users")
                
                # Check for next page
                try:
                    next_button = await page.query_selector(table_config.get('next_page_selector', 'button:has-text("Next")'))
                    if next_button and await next_button.is_enabled():
                        await next_button.click()
                        await page.wait_for_timeout(2000)  # Wait for page load
                        current_page += 1
                    else:
                        logs.append("No more pages available")
                        break
                except Exception:
                    logs.append("Pagination navigation failed or not available")
                    break
            
            await page.close()
            
            return {
                'success': True,
                'users': all_users,
                'total_scraped': len(all_users),
                'pages_processed': current_page,
                'logs': logs
            }
            
        except Exception as e:
            logs.append(f"Scraping failed: {str(e)}")
            await page.close()
            return {
                'success': False,
                'error': str(e),
                'users': [],
                'logs': logs
            }
    
    async def provision_user(self, base_url: str, user_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Automate user provisioning using AI-guided form interaction
        """
        if not self.session_data.get('authenticated'):
            return {'error': 'Not authenticated', 'success': False}
            
        browser = await self.start_browser()
        page = await browser.new_page()
        
        # Restore session
        if self.session_data.get('cookies'):
            await page.context.add_cookies(self.session_data['cookies'])
        
        logs = []
        
        try:
            # Navigate to users page first
            users_url = f"{base_url}/mock-saas"
            await page.goto(users_url)
            logs.append(f"Navigated to users page: {users_url}")
            
            # Click Add User button
            await page.wait_for_selector('button:has-text("Add User")', timeout=10000)
            await page.click('button:has-text("Add User")')
            logs.append("Clicked Add User button")
            
            # Wait for dialog/form to appear
            await page.wait_for_selector('form', timeout=5000)
            logs.append("Add user form detected")
            
            # Get form structure using AI
            page_content = await page.content()
            form_config = await self.ai_adapter.detect_form_fields(page_content, "add-user")
            logs.append(f"AI form analysis complete - confidence: {form_config['confidence']}")
            
            # Fill form fields using AI-provided selectors
            for field, value in user_data.items():
                if field in form_config['fields']:
                    selector = form_config['fields'][field]['selector']
                    try:
                        if 'select' in selector:
                            await page.select_option(selector, value)
                        else:
                            await page.fill(selector, value)
                        logs.append(f"Filled {field} field with value: {value}")
                    except Exception as e:
                        logs.append(f"Failed to fill {field}: {str(e)}")
            
            # Submit form
            submit_selector = form_config['submit_button']['selector']
            await page.click(submit_selector)
            logs.append("Form submitted")
            
            # Wait for success indication
            await page.wait_for_timeout(2000)
            
            # Verify user was created by checking if it appears in the table
            verification_passed = False
            try:
                if user_data.get('email'):
                    await page.wait_for_selector(f'text="{user_data["email"]}"', timeout=5000)
                    verification_passed = True
                    logs.append("User creation verified - email found in table")
            except Exception:
                logs.append("Could not verify user creation")
            
            await page.close()
            
            return {
                'success': verification_passed,
                'user_data': user_data,
                'verified': verification_passed,
                'logs': logs
            }
            
        except Exception as e:
            logs.append(f"User provisioning failed: {str(e)}")
            await page.close()
            return {
                'success': False,
                'error': str(e),
                'logs': logs
            }
    
    async def deprovision_user(self, base_url: str, user_identifier: str) -> Dict[str, Any]:
        """
        Automate user deprovisioning
        """
        if not self.session_data.get('authenticated'):
            return {'error': 'Not authenticated', 'success': False}
            
        browser = await self.start_browser()
        page = await browser.new_page()
        
        # Restore session
        if self.session_data.get('cookies'):
            await page.context.add_cookies(self.session_data['cookies'])
        
        logs = []
        
        try:
            # Navigate to users page
            users_url = f"{base_url}/mock-saas"
            await page.goto(users_url)
            logs.append(f"Navigated to users page: {users_url}")
            
            # Search for user if search functionality exists
            try:
                search_input = await page.query_selector('input[placeholder*="Search"]')
                if search_input:
                    await search_input.fill(user_identifier)
                    await page.wait_for_timeout(1000)
                    logs.append(f"Searched for user: {user_identifier}")
            except Exception:
                logs.append("Search functionality not available or failed")
            
            # Find user row and delete button
            user_row = await page.query_selector(f'tr:has-text("{user_identifier}")')
            if user_row:
                delete_button = await user_row.query_selector('button:has-text("Remove"), button:has-text("Delete")')
                if delete_button:
                    await delete_button.click()
                    logs.append(f"Clicked delete button for user: {user_identifier}")
                    
                    # Handle confirmation dialog if present
                    try:
                        await page.wait_for_selector('button:has-text("Confirm"), button:has-text("Yes")', timeout=2000)
                        await page.click('button:has-text("Confirm"), button:has-text("Yes")')
                        logs.append("Confirmed user deletion")
                    except Exception:
                        logs.append("No confirmation dialog or confirmation failed")
                    
                    # Wait for UI update
                    await page.wait_for_timeout(2000)
                    
                    # Verify user was deleted
                    verification_passed = True
                    try:
                        await page.wait_for_selector(f'text="{user_identifier}"', timeout=2000)
                        verification_passed = False
                        logs.append("User still visible - deletion may have failed")
                    except Exception:
                        logs.append("User no longer visible - deletion verified")
                    
                    await page.close()
                    
                    return {
                        'success': verification_passed,
                        'user_identifier': user_identifier,
                        'verified': verification_passed,
                        'logs': logs
                    }
                else:
                    logs.append("Delete button not found")
            else:
                logs.append(f"User not found: {user_identifier}")
            
            await page.close()
            
            return {
                'success': False,
                'error': 'User not found or delete button not available',
                'logs': logs
            }
            
        except Exception as e:
            logs.append(f"User deprovisioning failed: {str(e)}")
            await page.close()
            return {
                'success': False,
                'error': str(e),
                'logs': logs
            }

# Example usage and testing functions
async def demo_automation_workflow():
    """
    Demonstrate the complete automation workflow
    """
    engine = AutomationEngine()
    base_url = "http://localhost:3000"  # Adjust based on your setup
    
    try:
        # Step 1: Authenticate
        print("Step 1: Authenticating...")
        auth_result = await engine.authenticate(base_url, {
            'username': 'admin',
            'password': 'password'
        })
        print(f"Authentication: {'Success' if auth_result['success'] else 'Failed'}")
        
        if not auth_result['success']:
            return
        
        # Step 2: Scrape existing users
        print("\nStep 2: Scraping users...")
        scrape_result = await engine.scrape_users(base_url, max_pages=2)
        print(f"Scraped {scrape_result.get('total_scraped', 0)} users")
        
        # Step 3: Provision new user
        print("\nStep 3: Provisioning user...")
        provision_result = await engine.provision_user(base_url, {
            'name': 'Test Automation User',
            'email': 'automation.test@example.com',
            'role': 'user'
        })
        print(f"Provisioning: {'Success' if provision_result['success'] else 'Failed'}")
        
        # Step 4: Deprovision user
        print("\nStep 4: Deprovisioning user...")
        deprovision_result = await engine.deprovision_user(base_url, 'automation.test@example.com')
        print(f"Deprovisioning: {'Success' if deprovision_result['success'] else 'Failed'}")
        
    finally:
        await engine.close_browser()

if __name__ == "__main__":
    asyncio.run(demo_automation_workflow())