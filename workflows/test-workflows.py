#!/usr/bin/env python3

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_all_workflows():
    """Get all workflows from N8N"""
    url = f"{os.getenv('N8N_SERVER', 'http://localhost:5678')}/api/v1/workflows"
    headers = {
        'X-N8N-API-KEY': os.getenv('N8N_API_TOKEN')
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get workflows: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting workflows: {e}")
        return None

def test_webhook_endpoint(webhook_url, workflow_name, test_data=None):
    """Test a webhook endpoint"""
    if not test_data:
        test_data = {
            "test": True,
            "message": f"Test message for {workflow_name}",
            "timestamp": time.time()
        }
    
    try:
        response = requests.post(webhook_url, json=test_data, timeout=10)
        if response.status_code in [200, 201, 202]:
            print(f"✅ Webhook test successful for {workflow_name}")
            return True
        else:
            print(f"⚠️  Webhook responded with status {response.status_code} for {workflow_name}")
            return False
    except requests.exceptions.Timeout:
        print(f"⏰ Webhook timeout for {workflow_name} (may still be processing)")
        return False
    except Exception as e:
        print(f"❌ Webhook test failed for {workflow_name}: {e}")
        return False

def extract_webhook_urls(workflow):
    """Extract webhook URLs from workflow nodes"""
    webhook_urls = []
    nodes = workflow.get('nodes', [])
    
    for node in nodes:
        if node.get('type') == 'n8n-nodes-base.webhook':
            webhook_path = node.get('parameters', {}).get('path', '')
            if webhook_path:
                base_url = os.getenv('N8N_SERVER', 'http://localhost:5678')
                webhook_url = f"{base_url}/webhook/{webhook_path}"
                webhook_urls.append(webhook_url)
    
    return webhook_urls

def test_ai_service_connectivity():
    """Test connectivity to AI services"""
    print("\n🤖 Testing AI Service Connectivity")
    print("-" * 50)
    
    # Test Ollama service
    try:
        ollama_url = "http://localhost:11434/api/tags"
        response = requests.get(ollama_url, timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is accessible")
        else:
            print(f"⚠️  Ollama service responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama service not accessible: {e}")

def test_wazuh_connectivity():
    """Test connectivity to Wazuh services"""
    print("\n🛡️  Testing Wazuh Connectivity")
    print("-" * 50)
    
    wazuh_ip = "172.20.18.14"
    
    # Test Wazuh API
    try:
        wazuh_url = f"https://{wazuh_ip}:55000"
        response = requests.get(wazuh_url, timeout=5, verify=False)
        print("✅ Wazuh API endpoint is accessible")
    except Exception as e:
        print(f"❌ Wazuh API not accessible: {e}")
    
    # Test Wazuh Dashboard
    try:
        dashboard_url = f"https://{wazuh_ip}:443"
        response = requests.get(dashboard_url, timeout=5, verify=False)
        print("✅ Wazuh Dashboard endpoint is accessible")
    except Exception as e:
        print(f"❌ Wazuh Dashboard not accessible: {e}")

def main():
    print("Testing N8N Workflows")
    print(f"N8N Server: {os.getenv('N8N_SERVER', 'http://localhost:5678')}")
    print("=" * 60)
    
    # Get all workflows
    workflows_data = get_all_workflows()
    if not workflows_data:
        print("❌ Failed to retrieve workflows")
        return
    
    workflows = workflows_data.get('data', [])
    if not workflows:
        print("❌ No workflows found")
        return
    
    # Filter for our imported workflows
    target_workflows = [
        'Ollama AI Chat Integration',
        'Wazuh High Priority Alert',
        'Wazuh Alert Monitoring',
        'Wazuh Authentication',
        'Wazuh Health Monitoring',
        'Wazuh Incident Response',
        'Real-time Wazuh Webhook Receiver'
    ]
    
    print(f"\n📋 Testing {len(target_workflows)} imported workflows")
    print("-" * 60)
    
    tested_count = 0
    successful_tests = 0
    
    for workflow in workflows:
        workflow_name = workflow.get('name', 'Unknown')
        if workflow_name in target_workflows:
            tested_count += 1
            is_active = workflow.get('active', False)
            
            print(f"\n🔍 Testing: {workflow_name}")
            print(f"   Status: {'Active' if is_active else 'Inactive'}")
            print(f"   ID: {workflow.get('id')}")
            
            if not is_active:
                print("   ⚠️  Workflow is not active - skipping webhook tests")
                continue
            
            # Extract and test webhook URLs
            webhook_urls = extract_webhook_urls(workflow)
            if webhook_urls:
                print(f"   Found {len(webhook_urls)} webhook(s)")
                for i, webhook_url in enumerate(webhook_urls, 1):
                    print(f"   Webhook {i}: {webhook_url}")
                    if test_webhook_endpoint(webhook_url, workflow_name):
                        successful_tests += 1
            else:
                print("   ℹ️  No webhooks found in this workflow")
                successful_tests += 1  # Count as successful if no webhooks to test
    
    # Test external service connectivity
    test_ai_service_connectivity()
    test_wazuh_connectivity()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Summary:")
    print(f"   Workflows tested: {tested_count}")
    print(f"   Successful tests: {successful_tests}")
    print(f"   Failed tests: {tested_count - successful_tests}")
    
    if successful_tests == tested_count:
        print("\n🎉 All workflow tests completed successfully!")
    else:
        print(f"\n⚠️  {tested_count - successful_tests} workflows had issues")
    
    print("\n💡 Next steps:")
    print("   1. Access N8N interface at http://localhost:5678")
    print("   2. Review workflow configurations")
    print("   3. Test with real Wazuh alerts")
    print("   4. Monitor workflow executions")

if __name__ == "__main__":
    main()