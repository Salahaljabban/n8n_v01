# N8N-Wazuh SIEM Integration

A comprehensive security automation platform that integrates N8N workflow automation with Wazuh SIEM through a three-tier architecture, enhanced with Foundation-Sec AI for intelligent threat analysis.

## 🏗️ Architecture Overview

This project implements a **direct two-tier security monitoring architecture** that integrates N8N workflow automation directly with Wazuh SIEM:

```
N8N Workflows ←→ Wazuh SIEM
(172.20.18.13)   (172.20.18.14:55000)
```

### Architecture Layers

1. **N8N Automation Layer** (`172.20.18.13`)
   - Workflow orchestration and automation
   - Direct Wazuh API integration
   - Alert processing and response automation
   - Integration with external systems

2. **Wazuh SIEM Layer** (`172.20.18.14:55000`)
   - Security event collection and analysis
   - Alert generation and management
   - RESTful API for direct integration
   - Compliance reporting and dashboards

## 📋 Components

### Core Services
- **N8N**: Workflow automation platform with direct Wazuh integration
- **Wazuh**: Security Information and Event Management (SIEM) with RESTful API
- **Docker**: Containerization platform for all services

### N8N Workflows

1. **Direct Wazuh Alert Monitoring Workflow** (`wazuh-alert-monitoring-workflow.json`)
   - Monitors Wazuh alerts through direct API integration
   - Scheduled polling or webhook triggers
   - Direct Wazuh API authentication
   - Real-time alert processing
   - Alert filtering and categorization
   - Automated response actions

2. **Direct Webhook Receiver Workflow** (`wazuh-direct-webhook-receiver-workflow.json`)
   - Receives and processes webhooks directly from Wazuh
   - HTTP webhook from Wazuh SIEM
   - Direct webhook validation and authentication
   - Alert data processing
   - Response automation
   - Error handling and logging

3. **Ollama AI Chat Integration Workflow** (`n8n-ollama-workflow.json`)
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
- Bridge server setup on Active Directory server (192.168.30.100)

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

# Wazuh Configuration
WAZUH_API_URL=https://172.20.18.14:55000
WAZUH_API_USER=wazuh-api-user
WAZUH_API_PASSWORD=wazuh-api-password

# Direct Wazuh Integration
WAZUH_API_TIMEOUT=30
WAZUH_MAX_RETRIES=3
WAZUH_REQUEST_TIMEOUT=10

# Slack Configuration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### Direct Integration Setup

#### Prerequisites
- N8N instance running on 172.20.18.13
- Wazuh SIEM accessible at 172.20.18.14:55000
- Valid Wazuh API credentials
- Network connectivity between N8N and Wazuh

#### Configuration Steps

1. **Configure Wazuh API Access**:
   - Ensure Wazuh API is enabled and accessible
   - Create API user with appropriate permissions
   - Note down API credentials for N8N configuration

2. **Import N8N Workflows**:
   ```bash
   # Import workflows into N8N
   # Use N8N web interface to import JSON workflow files
   ```

3. **Configure Environment Variables**:
   - Set Wazuh API credentials in N8N
   - Configure webhook endpoints
   - Test API connectivity

#### Direct Integration Features
- **Simplified Architecture**: Direct API communication
- **Real-time Processing**: Immediate alert handling
- **Reduced Latency**: No intermediate proxy layer
- **Enhanced Security**: Direct encrypted communication
- **Scalability**: Native API rate limiting and load balancing

## 📊 Monitoring and Alerts

### Health Monitoring

- **Direct Wazuh API Health**: Monitored every 5 minutes
- **Wazuh Connectivity**: Direct API monitoring
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
- ✅ Bridge server functionality
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

### Bridge Server (4GB RAM)

- **Memory Management**: Optimized for 4GB constraint
- **Alert Buffering**: Efficient queue management
- **Connection Pooling**: Reduced overhead
- **Caching**: Strategic response caching

### N8N Workflows

- **Parallel Processing**: Concurrent alert handling
- **Error Handling**: Comprehensive retry logic
- **Resource Management**: Optimized execution

## 🔒 Security Considerations

### Authentication
- API key authentication for bridge server
- Secure token management for Wazuh API
- N8N basic authentication enabled

### Network Security
- Firewall rules for bridge server communication
- Encrypted connections where possible
- Network segmentation compliance

### Data Protection
- Alert data encryption in transit
- Secure credential storage
- Audit logging enabled

## 🚨 Troubleshooting

### Common Issues

1. **Wazuh API Connection Failed**
   ```bash
   # Test Wazuh API directly
   curl -k -X POST "https://172.20.18.14:55000/security/user/authenticate" \
        -H "Content-Type: application/json" \
        -d '{"username":"your-username","password":"your-password"}'
   
   # Check firewall rules
   sudo ufw status
   ```

2. **Wazuh API Authentication Failed**
   ```bash
   # Test Wazuh API directly
   curl -u wazuh-api-user:password https://172.20.18.14:55000/
   ```

3. **AI Analysis Not Working**
   ```bash
   # Check Foundation-Sec AI
   docker logs foundation-sec-ai
   curl http://localhost:11434/api/tags
   ```

4. **High Memory Usage on Bridge Server**
   ```bash
   # Monitor memory usage
   free -h
   
   # Restart bridge service
   sudo systemctl restart wazuh-bridge
   ```

### Log Locations

- **N8N Logs**: `./n8n-data/logs/`
- **Bridge Server Logs**: `/var/log/wazuh-bridge/`
- **Docker Logs**: `docker logs <container_name>`
- **Test Results**: `./test-results.json`

## 📚 Documentation

Detailed documentation available in `.trae/documents/`:

- `n8n-wazuh-integration-guide.md` - Complete setup guide
- `n8n-wazuh-technical-architecture.md` - Technical specifications
- `n8n-wazuh-product-requirements.md` - Feature requirements
- `n8n-wazuh-bridge-alternatives.md` - Alternative solutions

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
**Last Updated**: January 2025  
**Version**: 1.0.0# n8n
# n8n_v01
