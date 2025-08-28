# N8N Webhook Integration Fix Guide

## 🎯 Current Status After Webhook-Based Testing

The test suite has been successfully updated to use N8N webhook URLs instead of API endpoints. However, several issues need to be resolved:

### ✅ Working Components
- **N8N Connectivity**: Server accessible ✅
- **AI Chat Workflow**: Webhook `/webhook/chat` working ✅
- **Foundation-Sec AI**: Service accessible (model needs setup) ⚠️

### ❌ Issues to Fix

#### 1. Missing Webhook Registration (HTTP 404)
**Problem**: `wazuh-alerts` webhook not registered
```
HTTP 404: The requested webhook "POST wazuh-alerts" is not registered.
```
**Solution**: Import and activate `wazuh-webhook-receiver-workflow.json`

#### 2. Invalid N8N API Token (HTTP 401)
**Problem**: Current API token expired/invalid
```
HTTP 401: Authorization is required!
```
**Solution**: Generate new N8N API token

#### 3. Webhook Authorization Issues
**Problem**: Multiple workflows failing with authorization errors
**Affected Workflows**:
- `/webhook/bridge-auth`
- `/webhook/high-priority-alert` 
- `/webhook/incident-response`

## 🔧 Step-by-Step Fix Instructions

### Step 1: Generate New N8N API Token

1. **Access N8N Web Interface**:
   ```bash
   # Open in browser
   http://localhost:5678
   ```

2. **Login with credentials**:
   - Username: `admin`
   - Password: `admin123`

3. **Generate API Token**:
   - Go to Settings → Personal Access Tokens
   - Click "Create Token"
   - Name: `integration-testing`
   - Copy the generated token

4. **Update .env file**:
   ```bash
   # Replace the N8N_API_TOKEN value
   N8N_API_TOKEN=your_new_token_here
   ```

### Step 2: Import Missing Workflows

1. **Import wazuh-webhook-receiver-workflow.json**:
   - In N8N web interface, click "Import from File"
   - Select `wazuh-webhook-receiver-workflow.json`
   - Click "Import"

2. **Activate the workflow**:
   - Open the imported workflow
   - Click the toggle switch in top-right to activate
   - Verify webhook path is `/webhook/wazuh-alerts`

### Step 3: Verify Workflow Status

**Check all workflows are imported and active**:
```bash
# Run the status check script
./quick-fix-check.sh
```

**Expected active workflows**:
- ✅ `/webhook/wazuh-alerts` (wazuh-webhook-receiver)
- ✅ `/webhook/bridge-auth` (wazuh-auth)
- ✅ `/webhook/high-priority-alert` (wazuh-high-priority-alert)
- ✅ `/webhook/incident-response` (wazuh-incident-response)
- ✅ `/webhook/chat` (n8n-ollama)
- ✅ Alert Monitoring (scheduled)
- ✅ Health Monitoring (scheduled)

### Step 4: Test the Fixed Integration

```bash
# Run the updated test suite
python3 test-wazuh-integration.py
```

**Expected Results After Fix**:
- Success Rate: 80-90%
- All webhook endpoints should return HTTP 200
- Only AI model test may show warnings (requires model setup)

## 🔍 Troubleshooting

### If webhooks still return 404:
1. Verify workflow is imported
2. Ensure workflow is activated (toggle switch ON)
3. Check webhook path matches expected endpoint

### If webhooks return 401:
1. Verify N8N API token is updated in .env
2. Restart test script to reload environment
3. Check token permissions in N8N settings

### If scheduled workflows fail:
1. Verify Wazuh credentials in .env
2. Check Wazuh API connectivity
3. Ensure workflows are active in N8N

## 📊 Expected Test Results After Fix

| Test | Expected Status | Notes |
|------|----------------|-------|
| N8N Connectivity | ✅ PASS | Already working |
| Wazuh API Connectivity | ✅ PASS | Credentials verified |
| Webhook Receiver Workflow | ✅ PASS | After import/activation |
| Wazuh Authentication Workflow | ✅ PASS | After token fix |
| Alert Monitoring Workflow | ✅ PASS | After token fix |
| High Priority Alert Workflow | ✅ PASS | After import/activation |
| Incident Response Workflow | ✅ PASS | After import/activation |
| AI Chat Workflow | ✅ PASS | Already working |
| Foundation-Sec AI Integration | ⚠️ WARN | Model setup needed |
| Wazuh Health Monitoring Workflow | ✅ PASS | After token fix |

**Target Success Rate**: 90% (9/10 tests passing, 1 warning)

## 🚀 Next Steps

1. **Immediate**: Fix N8N API token and import missing workflows
2. **Short-term**: Set up AI model for Foundation-Sec integration
3. **Long-term**: Monitor webhook performance and add alerting

---

**Status**: 🔧 **READY FOR IMPLEMENTATION**
**Priority**: 🔥 **HIGH** - Required for production deployment