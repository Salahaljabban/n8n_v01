#!/usr/bin/env python3
"""
Wazuh API Authentication Methods Test
This script tests different authentication methods to help configure N8N correctly.
"""

import requests
import json
import base64
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_basic_auth_method():
    """
    Test Basic Auth method (what N8N should use)
    """
    print("Testing Basic Auth Method")
    print("-" * 30)
    
    url = "https://172.20.18.14:55000/security/user/authenticate"
    username = "wazuh"
    password = "MDymLhH.E?RZFtuUVV2KMW01X3b99y69"
    
    try:
        response = requests.get(
            url,
            auth=(username, password),
            verify=False,
            timeout=10,
            headers={'User-Agent': 'n8n-health-monitor/1.0'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Basic Auth successful!")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return data.get('data', {}).get('token')
        else:
            print(f"❌ Basic Auth failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_token_auth_method(token):
    """
    Test Token Auth method (after getting token)
    """
    if not token:
        print("\nSkipping token auth test - no token available")
        return
        
    print("\nTesting Token Auth Method")
    print("-" * 30)
    
    url = "https://172.20.18.14:55000/manager/info"
    
    try:
        response = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {token}',
                'User-Agent': 'n8n-health-monitor/1.0'
            },
            verify=False,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token Auth successful!")
            data = response.json()
            print(f"Manager Info: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Token Auth failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_direct_endpoint_access():
    """
    Test direct access to the endpoint you're trying to reach
    """
    print("\nTesting Direct Endpoint Access")
    print("-" * 35)
    
    url = "https://172.20.18.14:55000/"
    username = "wazuh"
    password = "MDymLhH.E?RZFtuUVV2KMW01X3b99y69"
    
    try:
        response = requests.get(
            url,
            auth=(username, password),
            verify=False,
            timeout=10,
            headers={'User-Agent': 'n8n-health-monitor/1.0'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ Direct endpoint access successful!")
            print(f"Response length: {len(response.text)} characters")
            print(f"First 200 chars: {response.text[:200]}...")
        else:
            print(f"❌ Direct endpoint access failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def print_n8n_troubleshooting_steps():
    """
    Print specific troubleshooting steps for N8N
    """
    print("\n" + "=" * 60)
    print("N8N TROUBLESHOOTING STEPS")
    print("=" * 60)
    
    print("\n1. CREDENTIAL CONFIGURATION:")
    print("   - Go to N8N Settings > Credentials")
    print("   - Create new 'Basic Auth' credential named 'WAZUH_API'")
    print("   - Username: wazuh")
    print("   - Password: MDymLhH.E?RZFtuUVV2KMW01X3b99y69")
    
    print("\n2. HTTP REQUEST NODE CONFIGURATION:")
    print("   - Method: GET")
    print("   - URL: https://172.20.18.14:55000/")
    print("   - Authentication: Generic Credential Type > Basic Auth")
    print("   - Credential: Select 'WAZUH_API'")
    print("   - Headers: User-Agent = n8n-health-monitor/1.0")
    print("   - Options: Enable 'Ignore SSL Issues (Insecure)'")
    print("   - Timeout: 10000")
    
    print("\n3. COMMON ISSUES TO CHECK:")
    print("   ❌ Wrong credential type (should be Basic Auth, not Bearer Token)")
    print("   ❌ Incorrect URL format (should end with /)")
    print("   ❌ SSL certificate issues (enable 'Ignore SSL Issues')")
    print("   ❌ Network connectivity (check if Wazuh server is accessible)")
    print("   ❌ Credential not selected in HTTP Request node")
    
    print("\n4. VERIFICATION STEPS:")
    print("   ✅ Test credential by clicking 'Test' in credential settings")
    print("   ✅ Execute the workflow and check the output")
    print("   ✅ Check N8N logs for detailed error messages")

def main():
    print("Wazuh API Authentication Methods Test")
    print("=" * 50)
    
    # Test basic auth (what N8N should use)
    token = test_basic_auth_method()
    
    # Test token auth (for reference)
    test_token_auth_method(token)
    
    # Test direct endpoint access
    test_direct_endpoint_access()
    
    # Print troubleshooting guide
    print_n8n_troubleshooting_steps()

if __name__ == "__main__":
    main()