#!/usr/bin/env python3
import requests
import json
import sys
import os

# N8N Configuration
N8N_BASE_URL = "http://localhost:5678"
N8N_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OGRlNzY3MC0wNjdmLTQ3YmEtYWU4Ni05ZjdlMDg0MzliNWMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU2MzY5OTIyfQ.aw4hvEM5ndrvLjkEx938ROsy0WM8Kn-2eOEE3f4X87s"

def import_workflow(workflow_file_path):
    """Import a single workflow file to N8N"""
    
    # Check if file exists
    if not os.path.exists(workflow_file_path):
        print(f"Error: Workflow file not found: {workflow_file_path}")
        return False
    
    # Read workflow file
    try:
        with open(workflow_file_path, 'r') as f:
            original_workflow_data = json.load(f)
        
        # Clean workflow data - remove fields that N8N doesn't accept for import
        original_settings = original_workflow_data.get('settings', {})
        clean_settings = {
            'timezone': original_settings.get('timezone', 'UTC')
        }
        
        clean_workflow = {
            'name': original_workflow_data.get('name'),
            'nodes': original_workflow_data.get('nodes', []),
            'connections': original_workflow_data.get('connections', {}),
            'settings': clean_settings
        }
        
        # Remove any None values
        workflow_data = {k: v for k, v in clean_workflow.items() if v is not None}
        
    except Exception as e:
        print(f"Error reading workflow file: {e}")
        return False
    
    # Prepare headers
    headers = {
        'X-N8N-API-KEY': N8N_API_TOKEN,
        'Content-Type': 'application/json'
    }
    
    # Import workflow
    import_url = f"{N8N_BASE_URL}/api/v1/workflows"
    
    try:
        response = requests.post(import_url, headers=headers, json=workflow_data)
        
        if response.status_code in [200, 201]:
            workflow_info = response.json()
            workflow_id = workflow_info.get('id')
            print(f"✅ Successfully imported workflow: {workflow_info.get('name', 'Unknown')}")
            print(f"   Workflow ID: {workflow_id}")
            
            # Activate the workflow if it was originally active
            if original_workflow_data.get('active', False):
                print(f"   Activating workflow...")
                activate_workflow(workflow_id)
            
            return True
        else:
            print(f"❌ Failed to import workflow: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing workflow: {e}")
        return False

def activate_workflow(workflow_id):
    """Activate a workflow by ID"""
    
    headers = {
        'X-N8N-API-KEY': N8N_API_TOKEN,
        'Content-Type': 'application/json'
    }
    
    activate_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
    
    try:
        response = requests.post(activate_url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Successfully activated workflow ID: {workflow_id}")
            return True
        else:
            print(f"❌ Failed to activate workflow: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error activating workflow: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 import-single-workflow.py <workflow_file_path>")
        print("Example: python3 import-single-workflow.py workflows/ai-chat-workflow.json")
        sys.exit(1)
    
    workflow_file = sys.argv[1]
    
    print(f"Importing workflow: {workflow_file}")
    print(f"N8N Server: {N8N_BASE_URL}")
    print("-" * 50)
    
    # Import the workflow
    success = import_workflow(workflow_file)
    
    if success:
        print("\n🎉 Workflow import completed successfully!")
    else:
        print("\n💥 Workflow import failed!")
        sys.exit(1)