#!/bin/bash
echo "=== N8N Security System Quick Fix Check ==="
echo "Timestamp: $(date)"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found"
    exit 1
fi

echo ""
echo "=== 1. Testing Wazuh API Connectivity ==="
response=$(curl -k -s -w "%{http_code}" -u "$WAZUH_API_USER:$WAZUH_API_PASSWORD" \
  "$WAZUH_API_URL/security/user/authenticate" -o /tmp/wazuh_response.json)

if [ "$response" = "200" ]; then
    echo "✅ Wazuh API: Authentication successful (HTTP 200)"
    echo "   User: $WAZUH_API_USER"
    echo "   URL: $WAZUH_API_URL"
else
    echo "❌ Wazuh API: Authentication failed (HTTP $response)"
    echo "   Response: $(cat /tmp/wazuh_response.json 2>/dev/null || echo 'No response')"
fi

echo ""
echo "=== 2. Testing N8N Server Connectivity ==="
response=$(curl -s -w "%{http_code}" http://localhost:5678 -o /dev/null)
if [ "$response" = "200" ]; then
    echo "✅ N8N Server: Accessible (HTTP 200)"
    echo "   URL: http://localhost:5678"
else
    echo "❌ N8N Server: Not accessible (HTTP $response)"
fi

echo ""
echo "=== 3. Testing N8N API Token ==="
api_response=$(curl -s -w "%{http_code}" \
  -H "Authorization: Bearer $N8N_API_TOKEN" \
  "http://localhost:5678/rest/workflows" -o /tmp/n8n_response.json)

if [ "$api_response" = "200" ]; then
    echo "✅ N8N API Token: Valid"
    workflow_count=$(cat /tmp/n8n_response.json | jq '. | length' 2>/dev/null || echo "unknown")
    echo "   Workflows found: $workflow_count"
else
    echo "❌ N8N API Token: Invalid or expired (HTTP $api_response)"
    echo "   Response: $(cat /tmp/n8n_response.json 2>/dev/null || echo 'No response')"
fi

echo ""
echo "=== 4. Testing Webhook Endpoints ==="
webhooks=("wazuh-alerts" "bridge-auth" "high-priority-alert" "incident-response" "chat")

for endpoint in "${webhooks[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
        "http://localhost:5678/webhook/$endpoint" \
        -H "Content-Type: application/json" \
        -d '{"test": "connectivity_check"}')
    
    case $response in
        "404")
            echo "❌ Webhook /$endpoint: NOT REGISTERED (HTTP 404)"
            ;;
        "200"|"201")
            echo "✅ Webhook /$endpoint: ACTIVE (HTTP $response)"
            ;;
        "400"|"422")
            echo "⚠️  Webhook /$endpoint: REGISTERED but validation error (HTTP $response)"
            ;;
        *)
            echo "❓ Webhook /$endpoint: Unknown status (HTTP $response)"
            ;;
    esac
done

echo ""
echo "=== 5. Docker Services Status ==="
echo "Checking Docker containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(n8n|ollama|foundation)"

echo ""
echo "=== 6. Workflow Files Available ==="
echo "Checking workflow JSON files..."
workflow_files=("wazuh-webhook-receiver-workflow.json" "wazuh-auth-workflow.json" \
                "wazuh-alert-monitoring-workflow.json" "wazuh-high-priority-alert-workflow.json" \
                "wazuh-incident-response-workflow.json" "wazuh-health-monitoring-workflow.json" \
                "n8n-ollama-workflow.json")

for file in "${workflow_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file: Available"
    else
        echo "❌ $file: Missing"
    fi
done

echo ""
echo "=== Summary and Next Steps ==="
echo ""
echo "🔧 IMMEDIATE ACTIONS NEEDED:"
echo "1. Access N8N web interface: http://localhost:5678"
echo "   Login: $N8N_USERNAME"
echo "   Password: [from .env file]"
echo ""
echo "2. Import missing workflows (those showing 404 errors above)"
echo "3. Activate imported workflows using the toggle switch"
echo "4. Generate new N8N API token if current one is invalid"
echo ""
echo "📋 VERIFICATION:"
echo "After completing the above steps, run:"
echo "   python3 test-wazuh-integration.py"
echo ""
echo "📁 TROUBLESHOOTING:"
echo "For detailed instructions, see: troubleshooting-guide.md"
echo ""

# Cleanup temp files
rm -f /tmp/wazuh_response.json /tmp/n8n_response.json

echo "=== Quick Fix Check Complete ==="