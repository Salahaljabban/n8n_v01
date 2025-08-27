#!/usr/bin/env python3
"""
N8N Manual Workflow Import Guide
Provides step-by-step instructions for manual workflow import
"""

import json
import glob
from pathlib import Path

def validate_workflow_files():
    """Validate all workflow JSON files"""
    workflow_patterns = [
        "*workflow*.json",
        "wazuh-*.json",
        "n8n-*.json"
    ]
    
    workflow_files = []
    for pattern in workflow_patterns:
        workflow_files.extend(glob.glob(pattern))
    
    workflow_files = sorted(list(set(workflow_files)))
    
    print("🔍 Validating workflow files...")
    print("=" * 50)
    
    valid_files = []
    invalid_files = []
    
    for filepath in workflow_files:
        try:
            with open(filepath, 'r') as f:
                workflow_data = json.load(f)
            
            # Basic validation
            if 'nodes' in workflow_data and 'connections' in workflow_data:
                valid_files.append(filepath)
                print(f"✅ {filepath} - Valid")
            else:
                invalid_files.append(filepath)
                print(f"⚠️  {filepath} - Missing required fields")
                
        except json.JSONDecodeError as e:
            invalid_files.append(filepath)
            print(f"❌ {filepath} - JSON Error: {e}")
        except Exception as e:
            invalid_files.append(filepath)
            print(f"❌ {filepath} - Error: {e}")
    
    print(f"\n📊 Validation Summary:")
    print(f"   Valid files: {len(valid_files)}")
    print(f"   Invalid files: {len(invalid_files)}")
    
    return valid_files, invalid_files

def print_manual_import_instructions(valid_files):
    """Print manual import instructions"""
    print("\n📋 MANUAL IMPORT INSTRUCTIONS")
    print("=" * 50)
    
    print("\n🌐 Step 1: Access N8N Dashboard")
    print("   1. Open browser: http://localhost:5678")
    print("   2. Complete initial setup if prompted")
    print("   3. Create admin account if needed")
    
    print("\n📥 Step 2: Import Workflows (Recommended Order)")
    
    # Define import order
    import_order = [
        "n8n-ollama-workflow.json",
        "wazuh-webhook-receiver-workflow.json", 
        "wazuh-auth-workflow.json",
        "wazuh-health-monitoring-workflow.json",
        "wazuh-alert-monitoring-workflow.json",
        "wazuh-high-priority-alert-workflow.json",
        "wazuh-incident-response-workflow.json"
    ]
    
    for i, filename in enumerate(import_order, 1):
        if filename in valid_files:
            print(f"\n   {i}. Import {filename}:")
            print(f"      • Click '+ Add workflow' (top right)")
            print(f"      • Select 'Import from file' or press Ctrl+I")
            print(f"      • Browse and select: {filename}")
            print(f"      • Click 'Import'")
            print(f"      • Toggle 'Active' switch (top right)")
            print(f"      • Click 'Save' (Ctrl+S)")
    
    print("\n⚙️  Step 3: Configure Credentials")
    print("   For workflows requiring Wazuh connection:")
    print("   • Wazuh API URL: https://172.20.18.14:55000")
    print("   • Username: admin")
    print("   • Password: admin")
    print("   • Foundation-Sec AI: http://foundation-sec-ai:11434")
    
    print("\n✅ Step 4: Verify Setup")
    print("   1. Go to 'Workflows' page")
    print("   2. Verify all workflows show 'Active' status")
    print("   3. Test webhook endpoints:")
    print("")
    print("   # Test AI Chat")
    print("   curl -X POST http://localhost:5678/webhook/chat \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"Test security analysis\"}'")
    print("")
    print("   # Test Alert Reception")
    print("   curl -X POST http://localhost:5678/webhook/wazuh-alerts \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"rule\": {\"level\": 8}, \"agent\": {\"name\": \"test\"}}'")

def main():
    print("N8N Manual Workflow Import Guide")
    print("=" * 40)
    
    # Validate workflow files
    valid_files, invalid_files = validate_workflow_files()
    
    if invalid_files:
        print(f"\n⚠️  Warning: {len(invalid_files)} files have issues and need fixing:")
        for f in invalid_files:
            print(f"   - {f}")
    
    if valid_files:
        print_manual_import_instructions(valid_files)
        print("\n🎯 The automated script failed due to N8N authentication requirements.")
        print("   Use the manual import process above for reliable workflow import.")
    else:
        print("\n❌ No valid workflow files found. Please check the JSON syntax.")

if __name__ == "__main__":
    main()
