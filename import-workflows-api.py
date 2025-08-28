#!/usr/bin/env python3
"""
N8N Workflow Import Script
Automatically imports and activates workflows using N8N API
"""

import requests
import json
import os
from pathlib import Path
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
    
    # First, get the login page to establish session
    response = session.get(f"{base_url}/signin")
    if response.status_code != 200:
        print(f"❌ Failed to access N8N login page: {response.status_code}")
        return None
    
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

def get_workflows(session, base_url="http://localhost:5678"):
    """Get list of existing workflows"""
    response = session.get(f"{base_url}/rest/workflows")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get workflows: {response.status_code}")
        return []

def import_workflow(session, workflow_file, base_url="http://localhost:5678"):
    """Import a workflow from JSON file"""
    try:
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        # Remove id if present to create new workflow
        if 'id' in workflow_data:
            del workflow_data['id']
        
        # Set workflow as active
        workflow_data['active'] = True
        
        response = session.post(f"{base_url}/rest/workflows", json=workflow_data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Successfully imported: {workflow_file} (ID: {result.get('id', 'unknown')})")
            return True
        else:
            print(f"❌ Failed to import {workflow_file}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing {workflow_file}: {str(e)}")
        return False

def activate_workflow(session, workflow_id, base_url="http://localhost:5678"):
    """Activate a workflow"""
    response = session.patch(f"{base_url}/rest/workflows/{workflow_id}/activate")
    if response.status_code == 200:
        print(f"✅ Activated workflow ID: {workflow_id}")
        return True
    else:
        print(f"❌ Failed to activate workflow {workflow_id}: {response.status_code}")
        return False

def main():
    print("🔧 N8N Workflow Import Script")
    print("==============================")
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
    
    # Get existing workflows
    existing_workflows = get_workflows(session)
    existing_names = [w.get('name', '') for w in existing_workflows]
    print(f"📊 Found {len(existing_workflows)} existing workflows")
    
    # Workflow files to import
    workflow_files = [
        "wazuh-webhook-receiver-workflow.json",
        "wazuh-auth-workflow.json", 
        "wazuh-high-priority-alert-workflow.json",
        "wazuh-incident-response-workflow.json",
        "n8n-ollama-workflow.json",
        "wazuh-alert-monitoring-workflow.json",
        "wazuh-health-monitoring-workflow.json"
    ]
    
    imported_count = 0
    skipped_count = 0
    
    for workflow_file in workflow_files:
        if not os.path.exists(workflow_file):
            print(f"⚠️  Workflow file not found: {workflow_file}")
            continue
        
        # Check if workflow already exists
        try:
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
            workflow_name = workflow_data.get('name', '')
            
            if workflow_name in existing_names:
                print(f"⏭️  Skipping {workflow_file} - already exists: {workflow_name}")
                skipped_count += 1
                continue
                
        except Exception as e:
            print(f"⚠️  Could not read {workflow_file}: {str(e)}")
            continue
        
        # Import workflow
        if import_workflow(session, workflow_file):
            imported_count += 1
    
    print()
    print("📊 IMPORT SUMMARY:")
    print(f"   ✅ Imported: {imported_count} workflows")
    print(f"   ⏭️  Skipped: {skipped_count} workflows (already exist)")
    print(f"   📋 Total existing: {len(existing_workflows)} workflows")
    
    if imported_count > 0:
        print()
        print("🎉 Workflow import completed successfully!")
        print("📝 Next steps:")
        print("   1. Run: ./fix-webhook-integration.sh")
        print("   2. Run: python3 test-wazuh-integration.py")
    else:
        print()
        print("ℹ️  No new workflows were imported.")
        print("   All workflows may already be present in N8N.")

if __name__ == "__main__":
    main()