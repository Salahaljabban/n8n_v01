#!/usr/bin/env python3

import requests
import json
import os
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
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting workflows: {e}")
        return None

def activate_workflow(workflow_id, workflow_name):
    """Activate a specific workflow"""
    url = f"{os.getenv('N8N_SERVER', 'http://localhost:5678')}/api/v1/workflows/{workflow_id}/activate"
    headers = {
        'X-N8N-API-KEY': os.getenv('N8N_API_TOKEN'),
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code in [200, 201]:
            print(f"✅ Successfully activated workflow: {workflow_name}")
            return True
        else:
            print(f"❌ Failed to activate workflow {workflow_name}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error activating workflow {workflow_name}: {e}")
        return False

def main():
    print("Activating N8N Workflows")
    print(f"N8N Server: {os.getenv('N8N_SERVER', 'http://localhost:5678')}")
    print("-" * 50)
    
    # Get all workflows
    workflows_data = get_all_workflows()
    if not workflows_data:
        print("❌ Failed to retrieve workflows")
        return
    
    workflows = workflows_data.get('data', [])
    if not workflows:
        print("❌ No workflows found")
        return
    
    print(f"Found {len(workflows)} workflows")
    print("-" * 50)
    
    activated_count = 0
    failed_count = 0
    
    for workflow in workflows:
        workflow_id = workflow.get('id')
        workflow_name = workflow.get('name', 'Unknown')
        is_active = workflow.get('active', False)
        
        if is_active:
            print(f"⚡ Workflow '{workflow_name}' is already active")
            activated_count += 1
        else:
            print(f"🔄 Activating workflow: {workflow_name}")
            if activate_workflow(workflow_id, workflow_name):
                activated_count += 1
            else:
                failed_count += 1
    
    print("-" * 50)
    print(f"📊 Summary:")
    print(f"   Total workflows: {len(workflows)}")
    print(f"   Active workflows: {activated_count}")
    print(f"   Failed activations: {failed_count}")
    
    if failed_count == 0:
        print("\n🎉 All workflows are now active!")
    else:
        print(f"\n⚠️  {failed_count} workflows failed to activate")

if __name__ == "__main__":
    main()