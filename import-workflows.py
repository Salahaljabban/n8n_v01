#!/usr/bin/env python3
"""
N8N Workflow Import and Activation Script
Automates the import and activation of all security workflows
"""

import json
import requests
import glob
import time
import sys
import os
from pathlib import Path

class N8NWorkflowManager:
    def __init__(self, n8n_url="http://localhost:5678", api_key: str | None = None):
        self.n8n_url = n8n_url
        self.session = requests.Session()
        # Support n8n API key via env or arg
        self.api_key = api_key or os.getenv("N8N_API_KEY")
        if self.api_key:
            # Add both header styles to cover REST and Public API
            self.session.headers.update({
                "X-N8N-API-KEY": self.api_key,
                "n8n-api-key": self.api_key,
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })
        self.imported_workflows = []

    def check_n8n_status(self):
        """Check if N8N is accessible"""
        try:
            response = self.session.get(f"{self.n8n_url}/healthz", timeout=10)
            if response.status_code == 200:
                print("✅ N8N is accessible and ready")
                return True
            else:
                print(f"❌ N8N health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to N8N: {e}")
            return False

    def load_workflow_file(self, filepath):
        """Load workflow JSON from file"""
        try:
            with open(filepath, 'r') as f:
                workflow_data = json.load(f)
            return workflow_data
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return None

    def import_workflow(self, workflow_data, filename):
        """Import workflow into N8N via API"""
        try:
            # Create workflow payload
            payload = {
                "name": workflow_data.get("name", Path(filename).stem),
                "nodes": workflow_data.get("nodes", []),
                "connections": workflow_data.get("connections", {}),
                "active": True,  # Automatically activate
                "settings": workflow_data.get("settings", {}),
                "staticData": workflow_data.get("staticData", {})
            }

            # Try Public API first, then fallback to legacy REST
            endpoints = [
                f"{self.n8n_url}/api/v1/workflows",
                f"{self.n8n_url}/rest/workflows",
            ]
            last_error = None
            response = None
            for ep in endpoints:
                try:
                    response = self.session.post(ep, json=payload, timeout=30)
                    if response.status_code in (200, 201):
                        break
                except Exception as e:
                    last_error = e
                    continue

            if response.status_code == 200:
                workflow_id = response.json().get("id")
                workflow_name = payload["name"]
                print(f"✅ Imported and activated: {workflow_name} (ID: {workflow_id})")
                self.imported_workflows.append({
                    "id": workflow_id,
                    "name": workflow_name,
                    "file": filename
                })
                return True
            else:
                print(f"❌ Failed to import {filename}: HTTP {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error importing {filename}: {e}")
            return False

    def get_workflow_files(self):
        """Get all workflow JSON files"""
        workflow_patterns = [
            "*workflow*.json",
            "wazuh-*.json",
            "n8n-*.json"
        ]
        
        workflow_files = []
        for pattern in workflow_patterns:
            workflow_files.extend(glob.glob(pattern))
        
        # Remove duplicates and sort
        return sorted(list(set(workflow_files)))

    def import_all_workflows(self):
        """Import all workflow files"""
        workflow_files = self.get_workflow_files()
        
        if not workflow_files:
            print("❌ No workflow files found")
            return False

        print(f"📄 Found {len(workflow_files)} workflow files:")
        for f in workflow_files:
            print(f"   - {f}")
        print()

        success_count = 0
        for workflow_file in workflow_files:
            print(f"📥 Processing: {workflow_file}")
            
            workflow_data = self.load_workflow_file(workflow_file)
            if workflow_data:
                if self.import_workflow(workflow_data, workflow_file):
                    success_count += 1
                    time.sleep(2)  # Brief pause between imports
            print()

        print(f"📊 Import Summary:")
        print(f"   Total files: {len(workflow_files)}")
        print(f"   Successfully imported: {success_count}")
        print(f"   Failed: {len(workflow_files) - success_count}")
        
        if self.imported_workflows:
            print(f"\n🔗 Active workflows:")
            for workflow in self.imported_workflows:
                print(f"   - {workflow['name']} (ID: {workflow['id']})")
        
        return success_count > 0

    def test_webhook_endpoints(self):
        """Test webhook endpoints for imported workflows"""
        print("\n🔗 Testing webhook endpoints:")
        
        test_endpoints = [
            "/webhook/wazuh-alerts",
            "/webhook/high-priority-alert", 
            "/webhook/incident-response",
            "/webhook/bridge-auth",
            "/webhook/chat"
        ]
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(f"{self.n8n_url}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:
                    status = "✅ Available" if response.status_code == 200 else "⚠️  Registered but inactive"
                    print(f"   {endpoint}: {status}")
                else:
                    print(f"   {endpoint}: ❌ HTTP {response.status_code}")
            except Exception as e:
                print(f"   {endpoint}: ❌ Connection failed")

def main():
    print("N8N Security Workflow Import Tool")
    print("=" * 40)
    
    manager = N8NWorkflowManager(api_key=os.getenv("N8N_API_KEY"))
    
    # Check N8N status
    if not manager.check_n8n_status():
        print("\n❌ N8N is not accessible. Please start N8N and try again.")
        print("   Command: docker-compose up -d n8n")
        sys.exit(1)
    
    print()
    
    # Import workflows
    success = manager.import_all_workflows()
    
    if success:
        # Test webhook endpoints
        manager.test_webhook_endpoints()
        
        print(f"\n✅ Workflow import completed successfully!")
        print(f"🌐 Access N8N dashboard: {manager.n8n_url}")
        print(f"📋 Check executions: {manager.n8n_url}/executions")
    else:
        print(f"\n❌ Workflow import failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
