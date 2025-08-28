#!/bin/bash

# Reimport Updated Wazuh Workflows with Fixed Authentication
# This script reimports the workflows that were updated with correct Wazuh authentication

echo "🔄 Reimporting Updated Wazuh Workflows..."
echo "================================================"

# Load environment variables
source .env

# N8N API endpoint
N8N_API="http://localhost:5678/api/v1"

# Function to import workflow
import_workflow() {
    local workflow_file="$1"
    local workflow_name="$2"
    
    echo "📥 Importing: $workflow_name"
    
    if [ ! -f "$workflow_file" ]; then
        echo "❌ File not found: $workflow_file"
        return 1
    fi
    
    # Import workflow
    response=$(curl -s -X POST "$N8N_API/workflows/import" \
        -H "X-N8N-API-KEY: $N8N_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d @"$workflow_file")
    
    if echo "$response" | grep -q '"id"'; then
        workflow_id=$(echo "$response" | jq -r '.id // empty')
        echo "✅ Successfully imported: $workflow_name (ID: $workflow_id)"
        
        # Activate the workflow
        activate_response=$(curl -s -X POST "$N8N_API/workflows/$workflow_id/activate" \
            -H "X-N8N-API-KEY: $N8N_API_TOKEN")
        
        if echo "$activate_response" | grep -q '"active":true'; then
            echo "🟢 Activated: $workflow_name"
        else
            echo "⚠️  Import successful but activation may have failed: $workflow_name"
        fi
    else
        echo "❌ Failed to import: $workflow_name"
        echo "Response: $response"
    fi
    echo ""
}

# Import updated workflows
echo "Importing workflows with fixed Wazuh authentication..."
echo ""

import_workflow "wazuh-auth-workflow.json" "Wazuh Authentication"
import_workflow "wazuh-alert-monitoring-workflow.json" "Wazuh Alert Monitoring"
import_workflow "wazuh-health-monitoring-workflow.json" "Wazuh Health Monitoring"

echo "🔍 Checking workflow status..."
echo "================================================"

# List active workflows
workflows_response=$(curl -s -X GET "$N8N_API/workflows" \
    -H "X-N8N-API-KEY: $N8N_API_TOKEN")

if echo "$workflows_response" | grep -q '"data"'; then
    echo "📋 Active Workflows:"
    echo "$workflows_response" | jq -r '.data[] | "   • \(.name) (ID: \(.id)) - Active: \(.active)"'
else
    echo "❌ Failed to retrieve workflows list"
    echo "Response: $workflows_response"
fi

echo ""
echo "✅ Workflow reimport completed!"
echo "🧪 Run 'python3 test-wazuh-integration.py' to test the updated workflows"