#!/usr/bin/env python3
"""
Wazuh API Credentials Configuration Helper for N8N
This script helps diagnose and fix Wazuh API authentication issues in N8N workflows.
"""

import requests
import json
import base64
import os
from urllib.parse import quote

def test_wazuh_api_direct():
    """
    Test Wazuh API authentication directly
    """
    wazuh_url = "https://172.20.18.14:55000"
    username = "wazuh"
    password = "MDymLhH.E?RZFtuUVV2KMW01X3b99y69"
    
    print("Testing Wazuh API Authentication")
    print("=" * 50)
    
    try:
        # Test authentication endpoint
        response = requests.get(
            f"{wazuh_url}/security/user/authenticate",
            auth=(username, password),
            verify=False,  # Ignore SSL certificate issues
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Wazuh API authentication successful!")
            result = response.json()
            print(f"Token received: {result.get('data', {}).get('token', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Wazuh API authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Wazuh API: {e}")
        return False

def generate_basic_auth_header():
    """
    Generate the correct Basic Auth header for Wazuh API
    """
    username = "wazuh"
    password = "MDymLhH.E?RZFtuUVV2KMW01X3b99y69"
    
    # Create base64 encoded credentials
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    print("\nWazuh API Credentials Configuration")
    print("=" * 50)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Base64 Encoded: {encoded_credentials}")
    print(f"Authorization Header: Basic {encoded_credentials}")
    
    return encoded_credentials

def print_n8n_configuration_guide():
    """
    Print step-by-step guide for configuring Wazuh credentials in N8N
    """
    print("\nN8N Configuration Guide")
    print("=" * 50)
    print("To fix the Wazuh API authentication in N8N:")
    print()
    print("1. In N8N, go to Settings > Credentials")
    print("2. Create a new credential or edit existing 'WAZUH_API' credential")
    print("3. Select 'Basic Auth' as the credential type")
    print("4. Configure the following:")
    print(f"   - User: wazuh")
    print(f"   - Password: MDymLhH.E?RZFtuUVV2KMW01X3b99y69")
    print()
    print("5. In your HTTP Request node:")
    print(f"   - URL: https://172.20.18.14:55000/")
    print("   - Authentication: Generic Credential Type > Basic Auth")
    print("   - Select your WAZUH_API credential")
    print("   - Enable 'Ignore SSL Issues (Insecure)'")
    print()
    print("6. Test the connection by executing the workflow")

def test_wazuh_endpoints():
    """
    Test various Wazuh API endpoints
    """
    wazuh_url = "https://172.20.18.14:55000"
    username = "wazuh"
    password = "MDymLhH.E?RZFtuUVV2KMW01X3b99y69"
    
    endpoints = [
        "/",
        "/security/user/authenticate",
        "/agents",
        "/manager/info"
    ]
    
    print("\nTesting Wazuh API Endpoints")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{wazuh_url}{endpoint}",
                auth=(username, password),
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK ({response.status_code})")
            else:
                print(f"❌ {endpoint}: Failed ({response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Error - {e}")

def main():
    print("Wazuh API Credentials Configuration Helper")
    print("=" * 60)
    
    # Test direct API access
    if test_wazuh_api_direct():
        # Generate credentials
        generate_basic_auth_header()
        
        # Test endpoints
        test_wazuh_endpoints()
        
        # Print configuration guide
        print_n8n_configuration_guide()
        
        print("\n" + "=" * 60)
        print("✅ Wazuh API is accessible. Follow the configuration guide above.")
    else:
        print("\n" + "=" * 60)
        print("❌ Wazuh API is not accessible. Check network connectivity and credentials.")

if __name__ == "__main__":
    main()