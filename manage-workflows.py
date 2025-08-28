#!/usr/bin/env python3
"""
N8N Workflow Management Script
Activates essential Wazuh security workflows and deactivates unnecessary ones
"""

import requests
import json
import os
from typing import Dict, List

# Load environment variables
with open('.env', 'r') as f:
    env_content = f.read()
    for line in env_content.split('\n'):
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key] = value

N8N_API_KEY = os.environ.get('N8N_API_TOKEN')
N8N_BASE_URL = 'http://localhost:5678/api/v1'

# Essential workflows that should be ACTIVE
ESSENTIAL_WORKFLOWS = {
    'wazuh-direct-webhook-receiver-workflow': 'Real-time Wazuh Webhook Receiver',
    'wazuh-direct-auth-workflow': 'Wazuh Authentication', 
    'wazuh-direct-alert-monitoring-workflow': 'Wazuh Alert Monitoring',
    'wazuh-direct-incident-response-workflow': 'Wazuh Incident Response',
    'wazuh-high-priority-alert-workflow': 'Wazuh High Priority Alert',
    'wazuh-api-health-monitoring-workflow': 'Wazuh Health Monitoring',
    'ollama-chat-workflow': 'Ollama AI Chat Integration'
}

# Workflows that should be DEACTIVATED (demos, duplicates, unused)
DEACTIVATE_WORKFLOWS = {
    'MA0ZqW0uLT0MmaZ5': 'Demo: My first AI Agent in n8n',
    'KFecjG2u6B0G8xwT': 'My workflow',
    'GS8Fv17eQ9zBHmm7': 'Direct API Polling',
    'qS6mD8J7NTjCkt5k': 'Webhook processing (duplicate)',
    'vRBbpdwBw3YZHEDO': 'Alert Reception (duplicate)',
    'qpeUjZNEYKmE8Jvn': 'AI-Powered Analysis'
}

def get_workflows() -> List[Dict]:
    """Get all workflows from N8N"""
    headers = {'X-N8N-API-KEY': N8N_API_KEY}
    response = requests.get(f'{N8N_BASE_URL}/workflows', headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Error getting workflows: {response.status_code} - {response.text}")
        return []

def activate_workflow(workflow_id: str) -> bool:
    """Activate a workflow"""
    headers = {'X-N8N-API-KEY': N8N_API_KEY, 'Content-Type': 'application/json'}
    data = {'active': True}
    response = requests.patch(f'{N8N_BASE_URL}/workflows/{workflow_id}', 
                            headers=headers, json=data)
    return response.status_code == 200

def deactivate_workflow(workflow_id: str) -> bool:
    """Deactivate a workflow"""
    headers = {'X-N8N-API-KEY': N8N_API_KEY, 'Content-Type': 'application/json'}
    data = {'active': False}
    response = requests.patch(f'{N8N_BASE_URL}/workflows/{workflow_id}', 
                            headers=headers, json=data)
    return response.status_code == 200

def main():
    print("🔧 N8N Workflow Management")
    print("=" * 50)
    
    workflows = get_workflows()
    if not workflows:
        print("❌ Failed to get workflows")
        return
    
    print(f"📊 Found {len(workflows)} workflows")
    print()
    
    # Track changes
    activated = []
    deactivated = []
    already_correct = []
    
    # Process each workflow
    for workflow in workflows:
        workflow_id = workflow['id']
        workflow_name = workflow['name']
        is_active = workflow['active']
        
        # Check if this is an essential workflow
        should_be_active = (
            workflow_id in ESSENTIAL_WORKFLOWS or 
            any(essential_name.lower() in workflow_name.lower() 
                for essential_name in ESSENTIAL_WORKFLOWS.values())
        )
        
        # Check if this should be deactivated
        should_be_deactivated = (
            workflow_id in DEACTIVATE_WORKFLOWS or
            any(deactivate_name.lower() in workflow_name.lower() 
                for deactivate_name in DEACTIVATE_WORKFLOWS.values())
        )
        
        if should_be_active and not is_active:
            print(f"🟢 Activating: {workflow_name}")
            if activate_workflow(workflow_id):
                activated.append(workflow_name)
            else:
                print(f"❌ Failed to activate: {workflow_name}")
                
        elif should_be_deactivated and is_active:
            print(f"🔴 Deactivating: {workflow_name}")
            if deactivate_workflow(workflow_id):
                deactivated.append(workflow_name)
            else:
                print(f"❌ Failed to deactivate: {workflow_name}")
                
        elif should_be_active and is_active:
            already_correct.append(f"✅ {workflow_name} (already active)")
            
        elif not should_be_active and not should_be_deactivated and not is_active:
            already_correct.append(f"⚪ {workflow_name} (inactive, no change needed)")
    
    # Summary
    print()
    print("📋 SUMMARY")
    print("=" * 50)
    
    if activated:
        print(f"🟢 Activated ({len(activated)}):")
        for name in activated:
            print(f"   • {name}")
        print()
    
    if deactivated:
        print(f"🔴 Deactivated ({len(deactivated)}):")
        for name in deactivated:
            print(f"   • {name}")
        print()
    
    if already_correct:
        print(f"✅ Already Correct ({len(already_correct)}):")
        for status in already_correct:
            print(f"   • {status}")
        print()
    
    print(f"🎯 Essential Wazuh workflows: {len(ESSENTIAL_WORKFLOWS)}")
    print(f"🔧 Total changes made: {len(activated) + len(deactivated)}")
    
    # Verify essential workflows are active
    print()
    print("🔍 VERIFICATION")
    print("=" * 50)
    
    updated_workflows = get_workflows()
    essential_active = 0
    
    for workflow in updated_workflows:
        workflow_id = workflow['id']
        workflow_name = workflow['name']
        is_active = workflow['active']
        
        if (workflow_id in ESSENTIAL_WORKFLOWS or 
            any(essential_name.lower() in workflow_name.lower() 
                for essential_name in ESSENTIAL_WORKFLOWS.values())):
            
            if is_active:
                print(f"✅ {workflow_name}: ACTIVE")
                essential_active += 1
            else:
                print(f"❌ {workflow_name}: INACTIVE")
    
    print()
    print(f"🎯 Essential workflows active: {essential_active}/{len(ESSENTIAL_WORKFLOWS)}")
    
    if essential_active == len(ESSENTIAL_WORKFLOWS):
        print("🎉 All essential Wazuh workflows are now active!")
    else:
        print("⚠️  Some essential workflows may need manual attention")

if __name__ == '__main__':
    main()