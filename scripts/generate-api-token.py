#!/usr/bin/env python3
"""
N8N API Token Generator
Generates a new API token using N8N web interface session
"""

import requests
import json
import os
import sys

def load_env():
    """Load environment variables from .env file"""
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def login_to_n8n(username, password, base_url="http://localhost:5678"):
    """Login to N8N and get session cookies"""
    session = requests.Session()
    
    # Login with credentials
    login_data = {
        "emailOrLdapLoginId": username,
        "password": password
    }
    
    response = session.post(f"{base_url}/rest/login", json=login_data)
    if response.status_code == 200:
        print(f"✅ Successfully logged in to N8N as {username}")
        return session
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def create_api_token(session, base_url="http://localhost:5678"):
    """Create a new API token"""
    token_data = {
        "name": "integration-testing-token"
    }
    
    response = session.post(f"{base_url}/rest/users/api-tokens", json=token_data)
    
    if response.status_code in [200, 201]:
        result = response.json()
        token = result.get('apiKey') or result.get('token') or result.get('data', {}).get('apiKey')
        if token:
            print(f"✅ Successfully created API token: {token[:20]}...")
            return token
        else:
            print(f"⚠️  Token created but format unexpected: {result}")
            return None
    else:
        print(f"❌ Failed to create API token: {response.status_code} - {response.text}")
        return None

def update_env_file(new_token):
    """Update .env file with new API token"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Read current .env content
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update the N8N_API_TOKEN line
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith('N8N_API_TOKEN='):
            lines[i] = f"N8N_API_TOKEN={new_token}\n"
            updated = True
            break
    
    # If token line doesn't exist, add it
    if not updated:
        lines.append(f"N8N_API_TOKEN={new_token}\n")
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.writelines(lines)
    
    print("✅ Updated .env file with new API token")
    return True

def test_api_token(token, base_url="http://localhost:5678"):
    """Test the new API token"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{base_url}/api/v1/workflows", headers=headers)
    
    if response.status_code == 200:
        workflows = response.json()
        print(f"✅ API token is working! Found {len(workflows)} workflows")
        return True
    else:
        print(f"❌ API token test failed: {response.status_code} - {response.text}")
        return False

def main():
    print("🔧 N8N API Token Generator")
    print("============================")
    print()
    
    # Load environment variables
    env_vars = load_env()
    username = env_vars.get('N8N_USERNAME')
    password = env_vars.get('N8N_PASSWORD')
    
    if not username or not password:
        print("❌ N8N credentials not found in .env file")
        sys.exit(1)
    
    print(f"📋 Using credentials: {username}")
    
    # Login to N8N
    session = login_to_n8n(username, password)
    if not session:
        sys.exit(1)
    
    # Create new API token
    new_token = create_api_token(session)
    if not new_token:
        print("❌ Failed to create API token")
        sys.exit(1)
    
    # Update .env file
    if not update_env_file(new_token):
        sys.exit(1)
    
    # Test the new token
    if test_api_token(new_token):
        print()
        print("🎉 API token generation completed successfully!")
        print("📝 Next steps:")
        print("   1. Run: ./fix-webhook-integration.sh")
        print("   2. Run: python3 test-wazuh-integration.py")
    else:
        print("❌ API token test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()