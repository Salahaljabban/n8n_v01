#!/usr/bin/env python3

import requests
import json
import time

def test_foundation_sec_api():
    """Test Foundation-Sec API step by step to identify the issue"""
    
    print("🔧 Foundation-Sec API Debug Test")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test 2: Simple chat completion with tinyllama (default)
    print("\n2. Testing chat completion with tinyllama...")
    try:
        payload = {
            "model": "tinyllama",  # This should use tinyllama
            "messages": [
                {"role": "user", "content": "test"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Model used: {result.get('model', 'unknown')}")
            print(f"   Response: {result['choices'][0]['message']['content'][:100]}...")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Foundation-Sec model specifically
    print("\n3. Testing with Foundation-Sec model...")
    try:
        payload = {
            "model": "foundation-sec",
            "messages": [
                {"role": "user", "content": "What is a network intrusion?"}
            ],
            "max_tokens": 30
        }
        
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            timeout=60  # Longer timeout for larger model
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Model used: {result.get('model', 'unknown')}")
            print(f"   Response: {result['choices'][0]['message']['content'][:150]}...")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_foundation_sec_api()