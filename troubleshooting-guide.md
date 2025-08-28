# N8N Security Monitoring System - Troubleshooting Guide

## Issues Identified from Test Results

### 1. Wazuh API Connectivity - Auth failed: HTTP 401

**Status**: ✅ RESOLVED - Wazuh credentials are working

**Verification**:
```bash
curl -k -u wazuh:"MDymLhH.E?RZFtuUVV2KMW01X3b99y69" -X GET "https://172.20.18.14:55000/security/user/authenticate"
# Returns: HTTP 200 OK
```

**Root Cause**: The test script may have SSL verification issues or incorrect request formatting.

**Solution**: Update test script to use proper SSL handling:
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# In requests calls, add:
verify=False, timeout=30
```

### 2. Webhook Receiver Workflow - HTTP 404: "POST wazuh-alerts" webhook not registered

**Status**: ❌ NEEDS ACTION - Workflows not imported/activated

**Root Cause**: N8N workflows are not imported or not activated.

**Solution Steps**:

#### Step 1: Check Current N8N Workflows
```bash
# Access N8N web interface
open http://localhost:5678
# Login with: s.jabban@ashealth.ae / P@ssw0rd6480
```

#### Step 2: Import Missing Workflows
1. Navigate to N8N web interface (http://localhost:5678)
2. Click "Import from File" or "+" button
3. Import each workflow JSON file:
   - `wazuh-webhook-receiver-workflow.json`
   - `wazuh-auth-workflow.json`
   - `wazuh-alert-monitoring-workflow.json`
   - `wazuh-high-priority-alert-workflow.json`
   - `wazuh-incident-response-workflow.json`
   - `wazuh-health-monitoring-workflow.json`
   - `n8n-ollama-workflow.json`

#### Step 3: Activate Workflows
1. For each imported workflow:
   - Open the workflow
   - Click the toggle switch in the top-right corner to activate
   - Ensure the status shows "Active"

#### Step 4: Verify Webhook Registration
```bash
# Test webhook endpoints
curl -X POST http://localhost:5678/webhook/wazuh-alerts \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 3. Wazuh Authentication Workflow - No authentication token received

**Status**: ❌ NEEDS ACTION - Workflow not active

**Root Cause**: The bridge-auth workflow is not imported/activated.

**Solution**:
1. Import `wazuh-auth-workflow.json`
2. Activate the workflow
3. Test the endpoint:
```bash
curl -X POST http://localhost:5678/webhook/bridge-auth \
  -H "Content-Type: application/json" \
  -d '{"username": "wazuh", "password": "MDymLhH.E?RZFtuUVV2KMW01X3b99y69"}'
```

### 4. Alert Monitoring Workflow - Token acquisition failed

**Status**: ❌ NEEDS ACTION - Depends on auth workflow

**Root Cause**: This workflow depends on the authentication workflow being active.

**Solution**:
1. First fix the authentication workflow (issue #3)
2. Import and activate `wazuh-alert-monitoring-workflow.json`
3. Ensure workflow has correct Wazuh API credentials

### 5. Wazuh Health Monitoring Workflow - Token acquisition failed

**Status**: ❌ NEEDS ACTION - Same as issue #4

**Root Cause**: Same dependency on authentication workflow.

**Solution**:
1. Import and activate `wazuh-health-monitoring-workflow.json`
2. Configure direct Wazuh API access or use auth workflow

## N8N API Token Issue

**Problem**: Current N8N API token returns "Unauthorized"

**Solution**: Generate new API token

1. Access N8N web interface: http://localhost:5678
2. Login with credentials from .env file
3. Go to Settings → API Keys
4. Generate new API key
5. Update .env file with new token

## Quick Fix Script

Create and run this script to verify fixes:

```bash
#!/bin/bash
echo "=== N8N Security System Quick Fix ==="

# 1. Test Wazuh API
echo "Testing Wazuh API..."
curl -k -s -u wazuh:"MDymLhH.E?RZFtuUVV2KMW01X3b99y69" \
  "https://172.20.18.14:55000/security/user/authenticate" | grep -q "token" && \
  echo "✅ Wazuh API: OK" || echo "❌ Wazuh API: FAIL"

# 2. Test N8N connectivity
echo "Testing N8N connectivity..."
curl -s http://localhost:5678 > /dev/null && \
  echo "✅ N8N Server: OK" || echo "❌ N8N Server: FAIL"

# 3. Test webhook endpoints
echo "Testing webhook endpoints..."
for endpoint in wazuh-alerts bridge-auth high-priority-alert incident-response chat; do
  response=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    "http://localhost:5678/webhook/$endpoint" \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}')
  
  if [ "$response" = "404" ]; then
    echo "❌ Webhook $endpoint: NOT REGISTERED"
  else
    echo "✅ Webhook $endpoint: REGISTERED (HTTP $response)"
  fi
done

echo "\n=== Next Steps ==="
echo "1. Import workflows via N8N web interface: http://localhost:5678"
echo "2. Activate all imported workflows"
echo "3. Generate new N8N API token if needed"
echo "4. Re-run integration tests"
```

## Priority Action Items

1. **HIGH**: Import and activate all N8N workflows
2. **HIGH**: Generate new N8N API token
3. **MEDIUM**: Update test script SSL handling
4. **LOW**: Configure workflow credentials if needed

## Verification Commands

After implementing fixes, run these commands to verify:

```bash
# Test all components
python3 test-wazuh-integration.py

# Check specific webhook
curl -X POST http://localhost:5678/webhook/wazuh-alerts \
  -H "Content-Type: application/json" \
  -d '{"alert_id": "test-001", "severity": "high"}'

# Verify Wazuh API
curl -k -u wazuh:"MDymLhH.E?RZFtuUVV2KMW01X3b99y69" \
  "https://172.20.18.14:55000/security/user/authenticate"
```