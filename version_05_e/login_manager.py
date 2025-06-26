import json
import os

CREDENTIALS_FILE = 'credentials.json'

# Common selectors for popular websites
COMMON_SELECTORS = {
    'google.com': {
        'username_selector': 'input[type="email"]',
        'password_selector': 'input[type="password"]',
        'submit_selector': 'button[type="submit"]'
    },
    'gmail.com': {
        'username_selector': 'input[type="email"]',
        'password_selector': 'input[type="password"]',
        'submit_selector': 'button[type="submit"]'
    },
    'facebook.com': {
        'username_selector': 'input[name="email"]',
        'password_selector': 'input[name="pass"]',
        'submit_selector': 'button[name="login"]'
    },
    'twitter.com': {
        'username_selector': 'input[name="username"]',
        'password_selector': 'input[name="password"]',
        'submit_selector': 'button[type="submit"]'
    },
    'linkedin.com': {
        'username_selector': 'input[name="session_key"]',
        'password_selector': 'input[name="session_password"]',
        'submit_selector': 'button[type="submit"]'
    },
    'github.com': {
        'username_selector': 'input[name="login"]',
        'password_selector': 'input[name="password"]',
        'submit_selector': 'input[type="submit"]'
    },
    'default': {
        'username_selector': 'input[type="email"], input[type="text"], input[name*="user"], input[name*="email"]',
        'password_selector': 'input[type="password"]',
        'submit_selector': 'button[type="submit"], input[type="submit"], button:contains("Login"), button:contains("Sign in")'
    }
}

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_credentials(website, username, password, login_url, username_selector=None, password_selector=None, submit_selector=None):
    credentials = load_credentials()
    
    # Use common selectors if not provided
    if not username_selector or not password_selector or not submit_selector:
        # Check if we have specific selectors for this website
        domain = website.lower().replace('www.', '')
        if domain in COMMON_SELECTORS:
            selectors = COMMON_SELECTORS[domain]
        else:
            selectors = COMMON_SELECTORS['default']
        
        username_selector = username_selector or selectors['username_selector']
        password_selector = password_selector or selectors['password_selector']
        submit_selector = submit_selector or selectors['submit_selector']
    
    credentials[website] = {
        'username': username,
        'password': password,
        'login_url': login_url,
        'username_selector': username_selector,
        'password_selector': password_selector,
        'submit_selector': submit_selector
    }
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f, indent=4)

def get_all_credentials():
    """Retrieves all saved credentials."""
    return load_credentials()

def get_credentials(website):
    """Gets credentials for a specific website."""
    credentials = get_all_credentials()
    return credentials.get(website)

def login():
    """Prompts user to enter and save credentials for a website."""
    print("\n=== Add/Update Website Credentials ===")
    print("Enter the website domain (e.g., google.com, facebook.com)")
    website = input("Website: ").strip().lower()
    
    if not website:
        print("Website cannot be empty.")
        return
    
    print(f"\nEnter your login credentials for {website}")
    username = input("Username/Email: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("Username and password cannot be empty.")
        return
    
    # Construct login URL if not provided
    login_url = input(f"Login URL (press Enter for https://{website}): ").strip()
    if not login_url:
        login_url = f"https://{website}"
    elif not login_url.startswith("http://") and not login_url.startswith("https://"):
        login_url = f"https://{login_url}"
    
    # Check if we need custom selectors
    print("\nDo you want to use custom CSS selectors? (Only needed if automatic login fails)")
    use_custom = input("Use custom selectors? (y/N): ").strip().lower()
    
    if use_custom == 'y':
        print("\nEnter CSS selectors (leave empty to use defaults):")
        username_selector = input("Username field selector: ").strip()
        password_selector = input("Password field selector: ").strip()
        submit_selector = input("Submit button selector: ").strip()
        save_credentials(website, username, password, login_url, username_selector, password_selector, submit_selector)
    else:
        save_credentials(website, username, password, login_url)
    
    print(f"\n✓ Credentials saved for {website}")
    print("The browser agent will use these credentials to automatically log in.")

def list_credentials():
    """Lists all saved websites (without showing passwords)."""
    credentials = load_credentials()
    if not credentials:
        print("No saved credentials found.")
        return
    
    print("\n=== Saved Websites ===")
    for i, website in enumerate(credentials.keys(), 1):
        print(f"{i}. {website}")
    print()

def delete_credentials(website):
    """Deletes credentials for a specific website."""
    credentials = load_credentials()
    if website in credentials:
        del credentials[website]
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f, indent=4)
        print(f"Credentials deleted for {website}")
    else:
        print(f"No credentials found for {website}")

if __name__ == "__main__":
    # When run directly, show the login prompt
    login()