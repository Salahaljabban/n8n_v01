#!/bin/bash

# N8N Webhook Integration Fix Script
# Automates the process of fixing webhook integration issues

echo "🔧 N8N Webhook Integration Fix Script"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    case $2 in
        "success") echo -e "${GREEN}✅ $1${NC}" ;;
        "error") echo -e "${RED}❌ $1${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $1${NC}" ;;
        "info") echo -e "${BLUE}ℹ️  $1${NC}" ;;
        *) echo "$1" ;;
    esac
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_status "Error: .env file not found!" "error"
    exit 1
fi

# Load environment variables
source .env

print_status "Step 1: Checking N8N connectivity..." "info"

# Test N8N connectivity
n8n_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5678")
if [ "$n8n_response" = "200" ]; then
    print_status "N8N server is accessible" "success"
else
    print_status "N8N server not accessible (HTTP $n8n_response)" "error"
    exit 1
fi

print_status "Step 2: Testing current N8N API token..." "info"

# Test current API token
if [ -n "$N8N_API_TOKEN" ]; then
    api_response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $N8N_API_TOKEN" \
        "http://localhost:5678/api/v1/workflows")
    
    if [ "$api_response" = "200" ]; then
        print_status "Current API token is valid" "success"
        TOKEN_VALID=true
    else
        print_status "Current API token is invalid (HTTP $api_response)" "warning"
        TOKEN_VALID=false
    fi
else
    print_status "No API token found in .env file" "warning"
    TOKEN_VALID=false
fi

print_status "Step 3: Testing webhook endpoints..." "info"

# Test webhook endpoints
webhooks=("wazuh-webhook" "bridge-auth" "high-priority-alert" "incident-response" "chat")
webhook_status=()

for endpoint in "${webhooks[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
        "http://localhost:5678/webhook/$endpoint" \
        -H "Content-Type: application/json" \
        -d '{"test": "connectivity_check"}')
    
    case $response in
        "404")
            print_status "Webhook /$endpoint: NOT REGISTERED" "error"
            webhook_status+=("$endpoint:missing")
            ;;
        "200"|"201")
            print_status "Webhook /$endpoint: ACTIVE" "success"
            webhook_status+=("$endpoint:active")
            ;;
        "400"|"422")
            print_status "Webhook /$endpoint: REGISTERED (validation error)" "warning"
            webhook_status+=("$endpoint:registered")
            ;;
        "401")
            print_status "Webhook /$endpoint: AUTHORIZATION REQUIRED" "error"
            webhook_status+=("$endpoint:auth_error")
            ;;
        *)
            print_status "Webhook /$endpoint: Unknown status (HTTP $response)" "warning"
            webhook_status+=("$endpoint:unknown")
            ;;
    esac
done

print_status "Step 4: Checking workflow files..." "info"

# Check if workflow files exist
workflow_files=(
    "wazuh-webhook-receiver-workflow.json"
    "wazuh-auth-workflow.json"
    "wazuh-high-priority-alert-workflow.json"
    "wazuh-incident-response-workflow.json"
    "n8n-ollama-workflow.json"
    "wazuh-alert-monitoring-workflow.json"
    "wazuh-health-monitoring-workflow.json"
)

missing_files=()
for file in "${workflow_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found: $file" "success"
    else
        print_status "Missing: $file" "error"
        missing_files+=("$file")
    fi
done

echo ""
print_status "=== ANALYSIS SUMMARY ===" "info"
echo ""

# Count issues
issue_count=0

if [ "$TOKEN_VALID" = false ]; then
    print_status "❌ N8N API Token needs to be regenerated" "error"
    ((issue_count++))
fi

# Count missing/problematic webhooks
missing_webhooks=0
for status in "${webhook_status[@]}"; do
    if [[ $status == *":missing" ]] || [[ $status == *":auth_error" ]]; then
        ((missing_webhooks++))
        ((issue_count++))
    fi
done

if [ $missing_webhooks -gt 0 ]; then
    print_status "❌ $missing_webhooks webhook(s) need to be imported/activated" "error"
fi

if [ ${#missing_files[@]} -gt 0 ]; then
    print_status "❌ ${#missing_files[@]} workflow file(s) missing" "error"
    ((issue_count++))
fi

echo ""
if [ $issue_count -eq 0 ]; then
    print_status "🎉 All checks passed! Integration should be working." "success"
    echo ""
    print_status "Run the test suite to verify:" "info"
    echo "   python3 test-wazuh-integration.py"
else
    print_status "🔧 Found $issue_count issue(s) that need to be fixed." "warning"
    echo ""
    print_status "NEXT STEPS:" "info"
    echo ""
    
    if [ "$TOKEN_VALID" = false ]; then
        echo "1. Generate new N8N API token:"
        echo "   - Open http://localhost:5678 in browser"
        echo "   - Login with admin/admin123"
        echo "   - Go to Settings → Personal Access Tokens"
        echo "   - Create new token and update .env file"
        echo ""
    fi
    
    if [ $missing_webhooks -gt 0 ]; then
        echo "2. Import missing workflows:"
        echo "   - Open http://localhost:5678 in browser"
        echo "   - Click 'Import from File'"
        echo "   - Import and activate missing workflow files"
        echo ""
    fi
    
    echo "3. Re-run this script to verify fixes:"
    echo "   ./fix-webhook-integration.sh"
    echo ""
    echo "4. Run integration tests:"
    echo "   python3 test-wazuh-integration.py"
fi

echo ""
print_status "For detailed instructions, see: webhook-integration-fix-guide.md" "info"