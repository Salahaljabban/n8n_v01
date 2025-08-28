# N8N-Wazuh Integration Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the N8N-Wazuh SIEM integration with direct two-tier architecture.

## Prerequisites
- Docker and Docker Compose installed
- N8N, Foundation-Sec AI, and Ollama services running
- Direct network connectivity to Wazuh server at 172.20.18.14:55000
- Valid Wazuh API credentials

## Deployment Steps

### 1. Verify Services Status
```bash
# Check all services are running
docker-compose ps

# Expected output:
# n8n                 Up      0.0.0.0:5678->5678/tcp
# foundation-sec-ai   Up      0.0.0.0:11434->11434/tcp
# foundation-sec-8b   Up      0.0.0.0:8000->8000/tcp
```

### 2. Access N8N Interface
1. Open browser and navigate to: `http://localhost:5678`
2. Complete initial setup if first time
3. Login to N8N dashboard

### 3. Import Workflows

#### Method 1: Manual Import (Recommended)
1. In N8N dashboard, click **"+ Add workflow"**
2. Click **"Import from file"** or **"Import from URL"**
3. Import each workflow file in this order:

   **Core Workflows:**
   - `wazuh-alert-monitoring-workflow.json` - Direct Wazuh API alert monitoring
   - `wazuh-webhook-receiver-workflow.json` - Real-time alert receiver
   - `n8n-ollama-workflow.json` - AI-powered chat integration
   
   **Processing Workflows:**
   - `wazuh-high-priority-alert-workflow.json` - AI-powered alert analysis
   - `wazuh-incident-response-workflow.json` - Automated response actions

#### Method 2: Copy-Paste Import
1. Open each `.json` file in a text editor
2. Copy the entire JSON content
3. In N8N, click **"+ Add workflow"**
4. Click **"Import from clipboard"**
5. Paste the JSON content and click **"Import"**

### 4. Configure Workflow Settings

For each imported workflow:

1. **Open the workflow** in N8N editor
2. **Review and update credentials:**
   - Wazuh API credentials (username/password)
   - Slack webhook URLs (if using Slack notifications)
   - Email SMTP settings (if using email notifications)

3. **Update endpoint URLs if needed:**
   - Wazuh API: `https://172.20.18.14:55000`
   - Foundation-Sec AI: `http://foundation-sec-ai:11434`
   - Ollama API: `http://foundation-sec-ai:11434`

4. **Save the workflow**
5. **Activate the workflow** using the toggle switch in top-right

### 5. Direct Wazuh Integration Setup

The direct integration connects N8N workflows directly to Wazuh API, providing:
- Direct API authentication with Wazuh
- Real-time alert processing
- Simplified architecture
- Reduced latency and complexity
- Enhanced security through direct encrypted communication

#### Configuration Steps

**Wazuh API Configuration**

1. **Verify Wazuh API Access**:
```bash
# Test Wazuh API connectivity
curl -k -X POST "https://172.20.18.14:55000/security/user/authenticate" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin"}'
```

2. **Configure N8N Environment Variables**:
```bash
# Set Wazuh API credentials in N8N environment
export WAZUH_API_URL="https://172.20.18.14:55000"
export WAZUH_API_USER="<wazuh_username>"
export WAZUH_API_PASSWORD="<wazuh_password>"
```

#### Direct Integration Testing

**Test Direct Wazuh API Connection**
```bash
# Test authentication
curl -k -X POST "https://172.20.18.14:55000/security/user/authenticate" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin"}'

# Test API endpoints
curl -k -X GET "https://172.20.18.14:55000/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test alerts endpoint
curl -k -X GET "https://172.20.18.14:55000/alerts" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### N8N Workflow Configuration

**Configure Direct Wazuh API Nodes:**

1. **HTTP Request Node Configuration for Wazuh Authentication:**
```json
{
  "method": "POST",
  "url": "={{ $env.WAZUH_API_URL + '/security/user/authenticate' }}",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "username": "{{$env.WAZUH_API_USER}}",
    "password": "{{$env.WAZUH_API_PASSWORD}}"
  },
  "options": {
    "allowUnauthorizedCerts": true
  }
}
```

2. **HTTP Request Node Configuration for Alert Retrieval:**
```json
{
  "method": "GET",
  "url": "={{ $env.WAZUH_API_URL + '/alerts' }}",
  "headers": {
    "Authorization": "={{ 'Bearer ' + $json.data.token }}"
  },
  "options": {
    "allowUnauthorizedCerts": true
  }
}
```





#### Environment Variables Configuration (Docker Compose)

Provide credentials via a `.env` file and restart n8n:

```env
WAZUH_API_URL=https://172.20.18.14:55000
WAZUH_API_USER=<wazuh_username>
WAZUH_API_PASSWORD=<wazuh_password>
```

Apply changes:

```bash
docker-compose up -d --force-recreate n8n
```



**Workflow Testing:**

Test your direct integration workflows:

```bash
# Test workflow execution via N8N API
curl -X POST "http://localhost:5678/webhook/test-wazuh" \
     -H "Content-Type: application/json" \
     -d '{"test": true}'

# Check N8N logs for any errors
docker logs n8n

# Monitor workflow executions in N8N UI
# Navigate to: http://localhost:5678/executions
```

### 6. Test Integration

#### Run Integration Tests
```bash
# From the project directory
python3 test-wazuh-integration.py
```

#### Manual Testing
1. **Test webhook receiver:**
   ```bash
   curl -X POST http://localhost:5678/webhook/wazuh-alerts \
     -H "Content-Type: application/json" \
     -d '{"rule":{"level":12,"description":"High severity alert"},"agent":{"name":"test-agent"},"timestamp":"2024-01-15T10:30:00Z"}'
   ```

2. **Test direct Wazuh API connection:**
   ```bash
   # Test authentication
   curl -k -X POST "https://172.20.18.14:55000/security/user/authenticate" \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin"}'
   
   # Test alerts endpoint with token
   curl -k -X GET "https://172.20.18.14:55000/alerts" \
        -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Check N8N executions:**
   - Go to N8N dashboard
   - Click "Executions" to see workflow runs
   - Verify workflows are triggering correctly

4. **Monitor system resources:**
   - N8N container performance
   - Direct Wazuh API response times
   - Network connectivity to Wazuh server

### 7. Production Configuration

#### Security Hardening
1. **Change default API keys**
2. **Enable HTTPS** for all communications
3. **Configure firewall rules**
4. **Set up proper authentication** for N8N
5. **Enable audit logging**

#### Performance Optimization
1. **Configure resource limits** in docker-compose.yml
2. **Set up log rotation**
3. **Tune API timeouts/retries** in workflows based on volume

#### Monitoring Setup
1. **Enable N8N workflow monitoring**
2. **Set up Wazuh API health checks** (base URL, manager and cluster status)
3. **Configure alerting** for failed workflows
4. **Monitor Foundation-Sec AI** performance

## Troubleshooting

### Common Issues

1. **Wazuh API connection failed:**
   - Verify network connectivity: `ping 172.20.18.14`
   - Check Wazuh server status and API availability
   - Test direct API authentication with curl

2. **Wazuh API authentication failed:**
   - Verify Wazuh credentials in N8N environment variables
   - Check Wazuh user permissions and API access
   - Test authentication endpoint directly

3. **N8N workflow errors:**
   - Check N8N execution logs
   - Verify Wazuh API endpoints and credentials in workflow nodes
   - Test individual workflow nodes
   - Check SSL certificate issues (use allowUnauthorizedCerts: true)

4. **Performance issues:**
   - Monitor N8N container resources
   - Adjust API timeout values if needed
   - Check network latency to Wazuh server

### Log Locations
- N8N logs: `./n8n-data/n8nEventLog.log`
- Docker logs: `docker-compose logs -f`

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review workflow execution logs in N8N
3. Check service status and logs
4. Refer to the technical architecture documentation

## Next Steps

1. **Set up monitoring dashboards**
2. **Configure notification channels** (Slack, email)
3. **Implement custom response actions**
4. **Set up backup and recovery procedures**
