#!/usr/bin/env python3

import requests
import base64
import os
import json
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_wazuh_auth():
    """Test Wazuh authentication using credentials from environment"""
    
    # Get credentials from environment
    wazuh_url = os.getenv('WAZUH_API_URL', 'https://172.20.18.14:55000')
    username = os.getenv('WAZUH_API_USER', 'wazuh')
    password = os.getenv('WAZUH_API_PASSWORD')
    
    if not password:
        print("❌ WAZUH_API_PASSWORD not found in environment")
        return None
        
    print(f"🔐 Testing authentication to: {wazuh_url}")
    print(f"   Username: {username}")
    
    # Test basic authentication
    auth_url = f"{wazuh_url}/security/user/authenticate?raw=true"
    
    try:
        # Create basic auth header
        auth_string = f"{username}:{password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        print(f"📡 Making request to: {auth_url}")
        response = requests.post(auth_url, headers=headers, verify=False, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Length: {len(response.text)} chars")
        
        if response.status_code == 200:
            token = response.text.strip()
            if len(token) > 50:  # JWT tokens are much longer
                print(f"✅ Authentication successful!")
                print(f"   Token: {token[:50]}...")
                
                # Test token with a simple API call
                test_url = f"{wazuh_url}/manager/info"
                test_headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                test_response = requests.get(test_url, headers=test_headers, verify=False, timeout=10)
                if test_response.status_code == 200:
                    print("✅ Token validation successful!")
                    manager_info = test_response.json()
                    print(f"   Wazuh Version: {manager_info.get('data', {}).get('version', 'Unknown')}")
                    return token
                else:
                    print(f"❌ Token validation failed: {test_response.status_code}")
                    return None
            else:
                print(f"❌ Invalid token received: {token}")
                return None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return None

def create_wazuh_credentials_file():
    """Create a credentials configuration file for n8n"""
    
    username = os.getenv('WAZUH_API_USER', 'wazuh')  
    password = os.getenv('WAZUH_API_PASSWORD')
    
    if not password:
        print("❌ Cannot create credentials file - password not found")
        return False
        
    # Create base64 encoded credentials for basic auth
    auth_string = f"{username}:{password}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode()
    
    credentials = {
        "wazuh_basic_auth": {
            "username": username,
            "password": password,
            "auth_header": f"Basic {auth_b64}"
        }
    }
    
    with open('wazuh-credentials.json', 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print("✅ Created wazuh-credentials.json")
    return True

if __name__ == "__main__":
    print("🔧 Wazuh Authentication Troubleshooter")
    print("=" * 50)
    
    # Load environment variables from .env file
    if os.path.exists('.env'):
        print("📁 Loading environment from .env file...")
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('\'"')
                    os.environ[key] = value
        print("✅ Environment loaded")
    
    # Test authentication
    token = test_wazuh_auth()
    
    if token:
        print("\n🎯 Next Steps:")
        print("1. Use this token format in n8n workflows")
        print("2. Update workflow authentication to use environment variables")
        
        # Create credentials file
        create_wazuh_credentials_file()
        
    else:
        print("\n🔧 Troubleshooting Steps:")
        print("1. Verify Wazuh server is accessible: https://172.20.18.14:55000")
        print("2. Check credentials in .env file")
        print("3. Test manual authentication")