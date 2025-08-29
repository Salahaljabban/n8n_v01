#!/usr/bin/env python3
"""
N8N Owner Setup Script
This script sets up the initial owner account for a fresh N8N installation.

Note: Owner setup and login endpoints are part of the internal REST API used
for bootstrap and are intentionally not using the Public API. After owner
setup, prefer using the Public API (/api/v1) with N8N_API_TOKEN.
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def setup_n8n_owner():
    """
    Set up the initial N8N owner account
    """
    n8n_url = os.getenv("N8N_SERVER", "http://localhost:5678")
    
    # Owner setup data
    owner_data = {
        "email": "admin@n8n.local",
        "firstName": "Admin",
        "lastName": "User",
        "password": "admin123456"
    }
    
    try:
        # Try to set up the owner account
        print("Setting up N8N owner account...")
        response = requests.post(
            f"{n8n_url}/rest/owner",
            json=owner_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Owner account created successfully!")
            result = response.json()
            print(f"Owner ID: {result.get('id', 'N/A')}")
            print(f"Email: {result.get('email', 'N/A')}")
            return True
        elif response.status_code == 400:
            print("⚠️  Owner account may already exist")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ Failed to create owner account: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to N8N: {e}")
        return False

def test_login():
    """
    Test login with the created owner account
    """
    n8n_url = os.getenv("N8N_SERVER", "http://localhost:5678")
    
    login_data = {
        "email": "admin@n8n.local",
        "password": "admin123456"
    }
    
    try:
        print("\nTesting login...")
        response = requests.post(
            f"{n8n_url}/rest/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during login: {e}")
        return False

def main():
    print("N8N Owner Setup Script")
    print("=" * 50)
    
    # Setup owner account
    if setup_n8n_owner():
        # Test login
        test_login()
    
    print("\nSetup complete!")
    print(f"You can now access N8N at: {os.getenv('N8N_SERVER', 'http://localhost:5678')}")
    print("Login credentials:")
    print("  Email: admin@n8n.local")
    print("  Password: admin123456")

if __name__ == "__main__":
    main()