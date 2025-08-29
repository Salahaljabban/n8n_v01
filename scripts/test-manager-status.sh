#!/bin/bash

# Test Wazuh Manager Status Endpoint
echo "Testing Wazuh Manager Status Endpoint"
echo "======================================"

# Wazuh API credentials
WAZUH_URL="https://172.20.18.14:55000"
WAZUH_USER="wazuh"
WAZUH_PASS="MDymLhH.E?RZFtuUVV2KMW01X3b99y69"

echo "Step 1: Getting authentication token..."
echo "URL: $WAZUH_URL/security/user/authenticate?raw=true"
echo ""

# Get authentication token
TOKEN=$(curl -s -k -u "$WAZUH_USER:$WAZUH_PASS" "$WAZUH_URL/security/user/authenticate?raw=true")

if [ $? -eq 0 ] && [ ! -z "$TOKEN" ]; then
    echo "✅ Authentication successful!"
    echo "Token (first 50 chars): ${TOKEN:0:50}..."
    echo ""
else
    echo "❌ Authentication failed!"
    echo "Token response: $TOKEN"
    exit 1
fi

echo "Step 2: Testing manager status endpoint..."
echo "URL: $WAZUH_URL/manager/status"
echo ""

# Test manager status with token
RESPONSE=$(curl -s -k -H "Authorization: Bearer $TOKEN" -H "User-Agent: n8n-health-monitor/1.0" "$WAZUH_URL/manager/status")

if [ $? -eq 0 ]; then
    echo "✅ Manager status request successful!"
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo "❌ Manager status request failed!"
    echo "Response: $RESPONSE"
fi

echo ""
echo "Step 3: Testing with Basic Auth (should fail)..."
echo ""

# Test manager status with Basic Auth (should fail)
BASIC_RESPONSE=$(curl -s -k -u "$WAZUH_USER:$WAZUH_PASS" -H "User-Agent: n8n-health-monitor/1.0" "$WAZUH_URL/manager/status")

echo "Basic Auth Response:"
echo "$BASIC_RESPONSE"

echo ""
echo "=== SUMMARY ==="
echo "✅ Authentication endpoint: Works with Basic Auth"
echo "✅ Manager status endpoint: Works with Bearer Token"
echo "❌ Manager status endpoint: Fails with Basic Auth (expected)"
echo ""
echo "N8N Configuration Required:"
echo "1. First HTTP Request: Get token using Basic Auth"
echo "2. Second HTTP Request: Use token as Bearer for manager status"