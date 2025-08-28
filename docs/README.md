# N8N-Wazuh SIEM Integration

A comprehensive security automation platform that integrates N8N workflow automation with Wazuh SIEM through a three-tier architecture, enhanced with Foundation-Sec AI for intelligent threat analysis.

## 🏗️ Architecture Overview

This integration implements a comprehensive three-tier architecture:

1. **N8N Layer** (localhost:5678) - Workflow automation and orchestration
2. **Wazuh SIEM Layer** (172.20.18.14:55000) - Direct API integration for security monitoring and alerting
3. **Foundation-Sec AI** (foundation-sec-ai:11434) - AI-powered threat analysis

## 📋 Components

### Core Services
- **N8N**: Workflow automation platform
- **Foundation-Sec AI**: Ollama-based security analysis AI
- (Removed) Bridge Server: All workflows now call Wazuh API directly
- **Wazuh SIEM**: Security information and event management

### N8N Workflows

1. **Wazuh Authentication Workflow** (`wazuh-auth-workflow.json`)
   - Authenticates directly against Wazuh API and returns token
   - Webhook trigger: `/webhook/bridge-auth`

2. **Alert Monitoring Workflow** (`wazuh-alert-monitoring-workflow.json`)
   - Polls Wazuh API every 2 minutes for alerts (with token)
   - Processes and routes alerts based on severity
   - Includes Wazuh API health checks

3. **High Priority Alert Workflow** (`wazuh-high-priority-alert-workflow.json`)
   - Processes critical security alerts with AI analysis
   - Integrates with Foundation-Sec AI for threat assessment
   - Webhook trigger: `/webhook/high-priority-alert`

4. **Incident Response Workflow** (`wazuh-incident-response-workflow.json`)
   - Automated response actions (IP blocking, host quarantine)
   - Security team notifications and ticket creation
   - Webhook trigger: `/webhook/incident-response`

5. **Webhook Receiver Workflow** (`wazuh-webhook-receiver-workflow.json`)
   - Real-time alert reception from Wazuh
   - Alert normalization and priority routing
   - Webhook trigger: `/webhook/wazuh-alerts`

6. **Wazuh Health Monitoring Workflow** (`wazuh-health-monitoring-workflow.json`)
   - Monitors Wazuh API and manager status every 5 minutes
   - Tracks connectivity and cluster state
   - Automated remediation planning for critical issues

7. **Ollama AI Chat Integration Workflow** (`n8n-ollama-workflow.json`)
   - Integrates AI-powered chat capabilities for security analysis
   - Webhook or manual execution
   - AI-powered security analysis
   - Natural language processing
   - Automated threat assessment
   - Response generation

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for testing)
- Access to Wazuh SIEM (172.20.18.14)
- Direct Wazuh API access at 172.20.18.14:55000

### Installation

1. **Clone and Setup**
   ```bash
   cd /home/sa/projects/n8n_sec
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Verify Services**
   ```bash
   # Check N8N
   curl http://localhost:5678/healthz
   
   # Check Foundation-Sec AI
   curl http://localhost:11434/api/tags
   ```

4. **Import Workflows**
   - Access N8N at http://localhost:5678
   - Import each workflow JSON file
   - Configure webhook URLs and credentials

5. **Run Integration Tests**
   ```bash
   python3 test-wazuh-integration.py
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# N8N Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password

# Wazuh Configuration (Direct API)
WAZUH_API_URL=https://172.20.18.14:55000
WAZUH_API_USER=wazuh
WAZUH_API_PASSWORD=MDymLhH.E?RZFtuUVV2KMW01X3b99y69

# Slack Configuration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### Notes

- Bridge server components have been deprecated. Workflows call the Wazuh API directly using tokens.

## 📊 Monitoring and Alerts

### Health Monitoring

- **Wazuh API Health**: Monitored every 5 minutes
- **Wazuh Connectivity**: Continuous monitoring
- **AI Service Status**: Integrated health checks
- **Alert Processing Metrics**: Real-time tracking

### Alert Routing

- **Low Priority (Level 1-5)**: Buffered processing
- **Medium Priority (Level 6-9)**: Real-time processing + Slack notification
- **High Priority (Level 10+)**: AI analysis + Automated response
- **Critical Incidents**: Immediate response + Security team notification

## 🧪 Testing

### Automated Testing

Run the comprehensive test suite:

```bash
python3 test-wazuh-integration.py
```

The test suite validates:
- ✅ N8N connectivity
- ✅ Wazuh API connectivity
- ✅ Wazuh API integration
- ✅ Foundation-Sec AI analysis
- ✅ Workflow execution
- ✅ Alert processing
- ✅ Incident response

### Manual Testing

1. **Test Webhook Reception**
   ```bash
   curl -X POST http://localhost:5678/webhook/wazuh-alerts \
     -H "Content-Type: application/json" \
     -d '{
       "id": "test-001",
       "rule": {"level": 8, "description": "Test alert"},
       "agent": {"name": "test-agent", "ip": "192.168.1.100"}
     }'
   ```

2. **Test High Priority Alert**
   ```bash
   curl -X POST http://localhost:5678/webhook/high-priority-alert \
     -H "Content-Type: application/json" \
     -d '{
       "id": "critical-001",
       "rule": {"level": 12, "description": "Critical breach"},
       "priority": "high"
     }'
   ```

## 📈 Performance Optimization

### N8N Workflows

- **Parallel Processing**: Concurrent alert handling
- **Error Handling**: Comprehensive retry logic
- **Resource Management**: Optimized execution

## 🔒 Security Considerations

### Authentication
- Secure token management for Wazuh API
- N8N basic authentication enabled

### Network Security
- Encrypted connections where possible
- Network segmentation compliance

### Data Protection
- Alert data encryption in transit
- Secure credential storage
- Audit logging enabled

## 🚨 Troubleshooting

### Common Issues

1. **Wazuh API Authentication Failed**
   ```bash
   # Test Wazuh API directly
   curl -u wazuh-api-user:password https://172.20.18.14:55000/
   ```

2. **AI Analysis Not Working**
   ```bash
   # Check Foundation-Sec AI
   docker logs foundation-sec-ai
   curl http://localhost:11434/api/tags
   ```

### Log Locations

- **N8N Logs**: `./n8n-data/logs/`
- **Docker Logs**: `docker logs <container_name>`
- **Test Results**: `./test-results.json`

## 📚 Documentation

Detailed documentation available in `.trae/documents/`:

- `n8n-wazuh-integration-guide.md` - Complete setup guide
- `n8n-wazuh-technical-architecture.md` - Technical specifications
- `n8n-wazuh-product-requirements.md` - Feature requirements


## 🤝 Contributing

1. Test all changes with the test suite
2. Update documentation for new features
3. Follow security best practices
4. Ensure compatibility with 4GB RAM constraint

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review test results and logs
3. Consult technical documentation
4. Contact security team for critical issues

## 📄 License

This project is part of the internal security infrastructure. All rights reserved.

---

**Status**: ✅ Production Ready  
**Last Updated**: August 2025  
**Version**: 1.0.0
