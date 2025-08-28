# N8N Security Workflows Setup Guide

## Quick Setup Instructions

### Step 1: Access N8N Dashboard
1. Open browser and navigate to: **http://localhost:5678**
2. Complete initial setup if first-time user
3. Create admin account if prompted

### Step 2: Import Security Workflows (✅ CORRECTED)

**All workflow files have been corrected with proper webhook paths and JSON syntax!**

Import these 7 workflow files in this order:

#### Core Infrastructure (Import First)
1. **n8n-ollama-workflow.json** - AI Chat Integration
   - Provides `/webhook/chat` endpoint
   - Tests Foundation-Sec AI integration
   - Webhook trigger for interactive security analysis

2. **wazuh-webhook-receiver-workflow.json** - Real-time Alert Reception  
   - Webhook: `/webhook/wazuh-alerts` ✅ CORRECTED
   - Receives alerts from Wazuh SIEM
   - Routes alerts by priority level
   - JSON syntax fixed (backtick escaping)

#### Authentication and Health Monitoring
3. **wazuh-bridge-auth-workflow.json** - API Authentication
   - Webhook: `/webhook/bridge-auth` ✅ CORRECTED (was `/webhook/wazuh/auth`)
   - Manages Wazuh API tokens
   - Handles authentication refreshing

4. **wazuh-bridge-health-monitoring-workflow.json** - System Health
   - Runs every 5 minutes
   - Monitors system connectivity
   - Tracks API response times

#### Alert Processing
5. **wazuh-alert-monitoring-workflow.json** - Direct API Polling
   - Runs every 2 minutes
   - Direct connection to Wazuh (172.20.18.14:55000)
   - Fetches alerts via API

6. **wazuh-high-priority-alert-workflow.json** - AI-Powered Analysis
   - Webhook: `/webhook/high-priority-alert`
   - Uses Foundation-Sec AI for threat analysis
   - Processes critical security incidents

#### Response Actions  
7. **wazuh-incident-response-workflow.json** - Automated Response
   - Webhook: `/webhook/incident-response`
   - Implements security response actions
   - IP blocking, host quarantine, notifications

### Step 3: Import Process

For each workflow file:

1. **In N8N Dashboard:**
   - Click **"+ Add workflow"** (top right)
   - Select **"Import from file"** or use **Ctrl+I**

2. **Select File:**
   - Browse to workflow JSON file
   - Click **"Import"**

3. **Configure Workflow:**
   - Review imported nodes
   - Update any credentials if needed:
     - **Wazuh API**: `https://172.20.18.14:55000` 
     - **Username**: `wazuh` ✅ VERIFIED WORKING
     - **Password**: `MDymLhH.E?RZFtuUVV2KMW01X3b99y69` ✅ VERIFIED WORKING
   - **Foundation-Sec AI**: `http://foundation-sec-ai:11434`

4. **Activate Workflow:**
   - Click the **toggle switch** in top-right to activate
   - Ensure switch shows **"Active"**

5. **Save Changes:**
   - Click **"Save"** (Ctrl+S)

### Step 4: Verify Setup

After importing all workflows:

1. **Check Active Workflows:**
   - Go to **Workflows** page
   - Verify 7 workflows are **"Active"**

2. **Test Webhook Endpoints:**
   ```bash
   # Test AI Chat
   curl -X POST http://localhost:5678/webhook/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Test security analysis"}'
   
   # Test Alert Reception
   curl -X POST http://localhost:5678/webhook/wazuh-alerts \
     -H "Content-Type: application/json" \
     -d '{"rule": {"level": 8}, "agent": {"name": "test"}}'
   ```

3. **Monitor Executions:**
   - Go to **Executions** page
   - Check for successful workflow runs
   - Review any error messages

### Step 5: Configure Credentials

Set up these credential types in N8N:

#### Wazuh API Credentials
- **Type**: HTTP Header Auth or Basic Auth
- **URL**: `https://172.20.18.14:55000`
- **Username**: `admin`
- **Password**: `admin`
- **Headers**: `Authorization: Basic <base64(username:password)>`

#### Foundation-Sec AI
- **URL**: `http://foundation-sec-ai:11434`
- **No authentication required** (internal Docker network)

### Troubleshooting

#### Common Issues:

1. **"Webhook not registered" errors:**
   - Import and activate workflows
   - Check webhook paths in workflow nodes
   - Verify workflows are saved and active

2. **Wazuh API connection failed:**
   - Test connectivity: `curl -k https://172.20.18.14:55000/`
   - Verify credentials in workflow nodes
   - Check SSL certificate settings (use `allowUnauthorizedCerts: true`)

3. **AI service not responding:**
   - Verify containers: `docker ps`
   - Check AI health: `curl http://localhost:11434/api/tags`
   - Restart if needed: `docker-compose restart ollama foundation-sec`

#### Validation Commands:

```bash
# Check all containers
docker-compose ps

# Test API endpoints
curl http://localhost:5678/healthz        # N8N
curl http://localhost:11434/api/tags      # Ollama AI  
curl http://localhost:8000/health         # Foundation-Sec API

# Run comprehensive tests
python3 test-wazuh-integration.py
```

### Next Steps

Once workflows are active:

1. **Configure Notifications:**
   - Add Slack/email endpoints for alerts
   - Set up notification preferences

2. **Customize Response Actions:**
   - Configure IP blocking lists
   - Set up quarantine procedures
   - Define escalation rules

3. **Monitor Operations:**
   - Review execution logs daily
   - Monitor system performance
   - Adjust polling intervals as needed

---

**🔗 Quick Links:**
- N8N Dashboard: http://localhost:5678
- Workflow Executions: http://localhost:5678/executions  
- API Health Check: http://localhost:8000/health