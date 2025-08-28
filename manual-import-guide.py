#!/usr/bin/env python3
"""
N8N Manual Workflow Import Guide
Provides step-by-step instructions for importing workflows via web interface
"""

import os
import json
from pathlib import Path

def load_env_vars():
    """Load environment variables from .env file"""
    env_vars = {}
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def analyze_workflow(workflow_file):
    """Analyze workflow file and extract key information"""
    try:
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        name = workflow.get('name', 'Unknown')
        nodes = workflow.get('nodes', [])
        node_types = [node.get('type', 'unknown') for node in nodes]
        
        return {
            'name': name,
            'node_count': len(nodes),
            'node_types': list(set(node_types)),
            'has_webhook': 'n8n-nodes-base.webhook' in node_types,
            'has_http': 'n8n-nodes-base.httpRequest' in node_types
        }
    except Exception as e:
        return {'name': workflow_file, 'error': str(e)}

def main():
    print("🔧 N8N Manual Workflow Import Guide")
    print("=" * 50)
    
    # Load environment variables
    env_vars = load_env_vars()
    
    print("\n📋 Current Configuration:")
    print(f"   N8N URL: http://localhost:5678")
    print(f"   N8N Username: {env_vars.get('N8N_USERNAME', 'Not set')}")
    print(f"   Wazuh API URL: {env_vars.get('WAZUH_API_URL', 'Not set')}")
    print(f"   Wazuh Username: {env_vars.get('WAZUH_API_USER', 'Not set')}")
    
    # Find workflow files
    workflow_files = [f for f in os.listdir('.') if f.endswith('.json') and f != 'test-results.json']
    
    print(f"\n📄 Found {len(workflow_files)} workflow files:")
    
    workflows_info = []
    for workflow_file in sorted(workflow_files):
        info = analyze_workflow(workflow_file)
        workflows_info.append((workflow_file, info))
        
        if 'error' in info:
            print(f"   ❌ {workflow_file}: Error - {info['error']}")
        else:
            webhook_icon = "🌐" if info['has_webhook'] else "⚙️"
            print(f"   {webhook_icon} {info['name']} ({info['node_count']} nodes)")
    
    print("\n🚀 Manual Import Instructions:")
    print("=" * 50)
    
    print("\n1️⃣ Access N8N Web Interface:")
    print("   • Open browser and go to: http://localhost:5678")
    print(f"   • Login with: {env_vars.get('N8N_USERNAME', '[USERNAME_NOT_SET]')}")
    print(f"   • Password: {env_vars.get('N8N_PASSWORD', '[PASSWORD_NOT_SET]')}")
    
    print("\n2️⃣ Import Each Workflow:")
    print("   • Click 'Workflows' in the left sidebar")
    print("   • Click the '+' button or 'Add workflow'")
    print("   • Click the '⋯' menu (three dots) in the top right")
    print("   • Select 'Import from file'")
    print("   • Choose the workflow JSON file")
    print("   • Click 'Save' after import")
    
    print("\n3️⃣ Workflow Import Order (Recommended):")
    priority_order = [
        'wazuh-auth-workflow.json',
        'wazuh-webhook-receiver-workflow.json', 
        'wazuh-alert-monitoring-workflow.json',
        'wazuh-health-monitoring-workflow.json',
        'wazuh-high-priority-alert-workflow.json',
        'wazuh-incident-response-workflow.json',
        'n8n-ollama-workflow.json'
    ]
    
    for i, workflow_file in enumerate(priority_order, 1):
        if workflow_file in [f[0] for f in workflows_info]:
            info = next(f[1] for f in workflows_info if f[0] == workflow_file)
            webhook_note = " (Creates webhook endpoint)" if info.get('has_webhook') else ""
            print(f"   {i}. {workflow_file}{webhook_note}")
    
    print("\n4️⃣ Configure Workflow Credentials:")
    print("   After importing each workflow:")
    print("   • Open the workflow")
    print("   • Look for nodes with credential requirements (red warning icons)")
    print("   • Configure Wazuh API credentials:")
    print(f"     - URL: {env_vars.get('WAZUH_API_URL', 'https://172.20.18.14:55000')}")
    print(f"     - Username: {env_vars.get('WAZUH_API_USER', 'wazuh')}")
    print(f"     - Password: {env_vars.get('WAZUH_API_PASSWORD', '[PASSWORD_FROM_ENV]')}")
    
    print("\n5️⃣ Activate Workflows:")
    print("   • After configuring credentials, activate each workflow")
    print("   • Toggle the 'Active' switch in the top right of each workflow")
    print("   • Verify no error messages appear")
    
    print("\n6️⃣ Test Integration:")
    print("   • Run: python3 test-wazuh-integration.py")
    print("   • Check that all workflows respond correctly")
    print("   • Verify webhook endpoints are accessible")
    
    print("\n📝 Workflow Descriptions:")
    print("=" * 30)
    descriptions = {
        'wazuh-auth-workflow.json': 'Handles Wazuh API authentication',
        'wazuh-webhook-receiver-workflow.json': 'Receives and processes incoming webhooks',
        'wazuh-alert-monitoring-workflow.json': 'Monitors and processes Wazuh alerts',
        'wazuh-health-monitoring-workflow.json': 'Monitors Wazuh system health',
        'wazuh-high-priority-alert-workflow.json': 'Handles critical security alerts',
        'wazuh-incident-response-workflow.json': 'Automates incident response procedures',
        'n8n-ollama-workflow.json': 'AI integration for security analysis'
    }
    
    for workflow_file, info in workflows_info:
        if 'error' not in info:
            desc = descriptions.get(workflow_file, 'Custom workflow')
            print(f"   • {info['name']}: {desc}")
    
    print("\n✅ After completing these steps, your N8N Security Monitoring system will be fully operational!")
    print("\n🔍 Troubleshooting:")
    print("   • If workflows show errors, check credential configuration")
    print("   • Ensure Wazuh API is accessible from N8N container")
    print("   • Verify all required environment variables are set")
    print("   • Check Docker container logs if services are not responding")

if __name__ == "__main__":
    main()