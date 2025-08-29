# N8N Wazuh API Configuration Fix Guide

## Problem Analysis

Based on the test results, the issue is that you're trying to access the Wazuh API root endpoint (`https://172.20.18.14:55000/`) which requires authentication, but N8N is not properly sending the Basic Auth credentials.

## Test Results Summary

✅ **Authentication endpoint works**: `/security/user/authenticate` returns 200 OK  
✅ **Token-based requests work**: `/manager/info` with Bearer token returns 200 OK  
❌ **Root endpoint fails**: `/` returns 401 "No authorization token provided"  

## Solution Steps

### Step 1: Fix the N8N Credential Configuration

1. **Access N8N Web Interface**:
   - Open: http://192.168.208.49:5678
   - Complete initial setup if not done

2. **Create/Edit Wazuh Credential**:
   - Go to **Settings** → **Credentials**
   - Create new credential or edit existing `WAZUH_API`
   - **Credential Type**: `Basic Auth`
   - **Name**: `WAZUH_API`
   - **Username**: `wazuh`
   - **Password**: `MDymLhH.E?RZFtuUVV2KMW01X3b99y69`
   - Click **Save**

### Step 2: Fix the HTTP Request Node Configuration

1. **Open your workflow** (likely `wazuh-health-monitoring-workflow`)

2. **Edit the HTTP Request node** with these exact settings:
   ```
   Method: GET
   URL: https://172.20.18.14:55000/security/user/authenticate
   
   Authentication:
   ├── Generic Credential Type: Basic Auth
   └── Credential: WAZUH_API
   
   Headers:
   ├── User-Agent: n8n-health-monitor/1.0
   
   Options:
   ├── ✅ Ignore SSL Issues (Insecure)
   └── Timeout: 10000
   ```

### Step 3: Alternative Endpoints to Use

Instead of the root endpoint `/`, use these working endpoints:

| Purpose | Endpoint | Description |
|---------|----------|-------------|
| **Authentication** | `/security/user/authenticate` | Get auth token |
| **Manager Info** | `/manager/info` | Wazuh manager details |
| **Agents List** | `/agents` | List all agents |
| **Alerts** | `/alerts` | Get security alerts |
| **Rules** | `/rules` | Get detection rules |

### Step 4: Two-Step Authentication Workflow

For endpoints that require Bearer tokens, use this pattern:

1. **First HTTP Request Node**: Get authentication token
   ```
   URL: https://172.20.18.14:55000/security/user/authenticate
   Method: GET
   Auth: Basic Auth (WAZUH_API credential)
   ```

2. **Second HTTP Request Node**: Use the token
   ```
   URL: https://172.20.18.14:55000/manager/info
   Method: GET
   Headers: Authorization = Bearer {{$node["HTTP Request"].json["data"]["token"]}}
   ```

## Quick Fix for Your Current Issue

**Change your current URL from**:
```
https://172.20.18.14:55000/
```

**To**:
```
https://172.20.18.14:55000/security/user/authenticate
```

This endpoint works with Basic Auth and will return a successful response.

## Verification Steps

1. **Test the credential**:
   - In N8N credential settings, click "Test"
   - Should show success message

2. **Execute the workflow**:
   - Should return JSON response with authentication token
   - No more "Authorization failed" errors

3. **Check the response**:
   ```json
   {
     "data": {
       "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
     },
     "error": 0
   }
   ```

## Common Mistakes to Avoid

❌ **Using root endpoint** (`/`) - requires token auth  
❌ **Wrong credential type** - must be "Basic Auth"  
❌ **Missing SSL ignore** - Wazuh uses self-signed cert  
❌ **Wrong username/password** - must match .env file  
❌ **Not selecting credential** - must link to WAZUH_API credential  

## Next Steps

After fixing this authentication issue:

1. Import remaining workflows
2. Configure each workflow's Wazuh endpoints
3. Test all workflows end-to-end
4. Activate workflows for monitoring

---

**Need Help?** Run the test scripts in this directory to verify Wazuh API connectivity.