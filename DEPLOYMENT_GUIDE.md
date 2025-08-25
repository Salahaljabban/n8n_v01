# N8N-Wazuh Integration Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the N8N-Wazuh SIEM integration with a three-tier architecture using a bridge server.

## Prerequisites
- Docker and Docker Compose installed
- N8N, Foundation-Sec AI, and Ollama services running
- Bridge server (192.168.30.100) with Python Flask API
- Wazuh server accessible from bridge server

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
   - `wazuh-bridge-auth-workflow.json` - Bridge server authentication
   - `wazuh-webhook-receiver-workflow.json` - Real-time alert receiver
   - `wazuh-alert-monitoring-workflow.json` - Periodic alert polling
   
   **Processing Workflows:**
   - `wazuh-high-priority-alert-workflow.json` - AI-powered alert analysis
   - `wazuh-incident-response-workflow.json` - Automated response actions
   
   **Monitoring Workflows:**
   - `wazuh-bridge-health-monitoring-workflow.json` - Bridge server health checks

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
   - Bridge server API key: `wazuh-bridge-api-key`
   - Slack webhook URLs (if using Slack notifications)
   - Email SMTP settings (if using email notifications)

3. **Update endpoint URLs if needed:**
   - Bridge server: `http://192.168.30.100:5000`
   - Foundation-Sec AI: `http://foundation-sec-ai:11434`
   - Wazuh API: Configure on bridge server

4. **Save the workflow**
5. **Activate the workflow** using the toggle switch in top-right

### 5. Bridge Server Setup

The bridge server acts as an intermediary between N8N and Wazuh, providing:
- API key authentication
- Alert buffering and optimization
- Health monitoring
- Memory-efficient operations (optimized for 4GB RAM)
- Cross-platform support (Linux and Windows Server)

#### Platform-Specific Deployment

**Windows Server Deployment (Recommended for 192.168.30.100)**

For Windows Server 2019/2022 deployment, see the dedicated Windows Deployment Guide.

Quick Windows installation:
```cmd
# Download installation files to Windows Server
mkdir C:\WazuhBridge\install
cd C:\WazuhBridge\install

# Run automated installation as Administrator
install.bat

# Verify installation
manage-service.bat status
manage-service.bat test
```

#### Linux Deployment (Alternative)

#### Install Bridge Server on 192.168.30.100
```bash
# On the bridge server (192.168.30.100)
sudo apt update
sudo apt install python3 python3-pip nginx -y

# Create application directory
sudo mkdir -p /opt/wazuh-bridge
cd /opt/wazuh-bridge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask gunicorn requests python-dotenv psutil
```

#### Create Bridge Server Application
Create `/opt/wazuh-bridge/app.py`:
```python
from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import threading
import time
import psutil

app = Flask(__name__)

# Configuration
WAZUH_API_URL = os.getenv('WAZUH_API_URL', 'https://172.20.18.14:55000')
WAZUH_USERNAME = os.getenv('WAZUH_USERNAME', 'admin')
WAZUH_PASSWORD = os.getenv('WAZUH_PASSWORD', 'admin')
API_KEY = os.getenv('API_KEY', 'wazuh-bridge-api-key')
MAX_BUFFER_SIZE = int(os.getenv('MAX_BUFFER_SIZE', '1000'))

# In-memory alert buffer (optimized for limited RAM)
alert_buffer = []
buffer_lock = threading.Lock()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add rotating file handler
file_handler = RotatingFileHandler('/opt/wazuh-bridge/logs/app.log', maxBytes=10485760, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def verify_api_key(request):
    """Verify API key from request headers"""
    provided_key = request.headers.get('X-API-Key')
    return provided_key == API_KEY

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    if not verify_api_key(request):
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Get system metrics
    memory = psutil.virtual_memory()
    
    with buffer_lock:
        buffered_count = len(alert_buffer)
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'buffered_alerts': buffered_count,
        'uptime': time.time() - start_time,
        'memory_usage': {
            'used_mb': round(memory.used / 1024 / 1024, 2),
            'available_mb': round(memory.available / 1024 / 1024, 2),
            'percent': memory.percent
        }
    })

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Authenticate with Wazuh API"""
    if not verify_api_key(request):
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        auth_url = f"{WAZUH_API_URL}/security/user/authenticate"
        auth_data = {
            'user': WAZUH_USERNAME,
            'password': WAZUH_PASSWORD
        }
        
        response = requests.post(auth_url, json=auth_data, verify=False, timeout=10)
        
        if response.status_code == 200:
            token = response.json().get('data', {}).get('token')
            return jsonify({
                'status': 'authenticated',
                'token': token,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        else:
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            return jsonify({'error': 'Authentication failed'}), 401
            
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return jsonify({'error': 'Authentication error'}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get buffered alerts"""
    if not verify_api_key(request):
        return jsonify({'error': 'Invalid API key'}), 401
    
    with buffer_lock:
        alerts = alert_buffer.copy()
        alert_buffer.clear()  # Clear buffer after reading
    
    return jsonify({
        'alerts': alerts,
        'count': len(alerts),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/alerts', methods=['POST'])
def buffer_alert():
    """Buffer incoming alerts"""
    if not verify_api_key(request):
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        alert_data = request.get_json()
        
        with buffer_lock:
            # Add timestamp
            alert_data['buffered_at'] = datetime.utcnow().isoformat() + 'Z'
            
            # Add to buffer
            alert_buffer.append(alert_data)
            
            # Maintain buffer size (FIFO)
            if len(alert_buffer) > MAX_BUFFER_SIZE:
                removed = alert_buffer.pop(0)
                logger.warning(f"Buffer full, removed oldest alert: {removed.get('id', 'unknown')}")
        
        return jsonify({
            'status': 'buffered',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        logger.error(f"Error buffering alert: {str(e)}")
        return jsonify({'error': 'Failed to buffer alert'}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get system and application metrics"""
    if not verify_api_key(request):
        return jsonify({'error': 'Invalid API key'}), 401
    
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    
    with buffer_lock:
        buffered_count = len(alert_buffer)
    
    return jsonify({
        'system': {
            'memory': {
                'used_mb': round(memory.used / 1024 / 1024, 2),
                'available_mb': round(memory.available / 1024 / 1024, 2),
                'percent': memory.percent
            },
            'cpu_percent': cpu,
            'uptime': time.time() - start_time
        },
        'application': {
            'buffered_alerts': buffered_count,
            'max_buffer_size': MAX_BUFFER_SIZE,
            'buffer_utilization': round((buffered_count / MAX_BUFFER_SIZE) * 100, 2)
        },
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

if __name__ == '__main__':
    start_time = time.time()
    
    # Create logs directory
    os.makedirs('/opt/wazuh-bridge/logs', exist_ok=True)
    
    logger.info("Starting Wazuh Bridge Server")
    logger.info(f"Wazuh API URL: {WAZUH_API_URL}")
    logger.info(f"Max buffer size: {MAX_BUFFER_SIZE}")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
```

#### Create Environment File
Create `/opt/wazuh-bridge/.env`:
```bash
WAZUH_API_URL=https://172.20.18.14:55000
WAZUH_USERNAME=admin
WAZUH_PASSWORD=admin
API_KEY=wazuh-bridge-api-key
MAX_BUFFER_SIZE=1000
```

#### Create Systemd Service
Create `/etc/systemd/system/wazuh-bridge.service`:
```ini
[Unit]
Description=Wazuh Bridge Server for N8N Integration
After=network.target

[Service]
Type=simple
User=wazuh-bridge
Group=wazuh-bridge
WorkingDirectory=/opt/wazuh-bridge
EnvironmentFile=/opt/wazuh-bridge/.env
ExecStart=/usr/bin/python3 /opt/wazuh-bridge/app.py
Restart=always
RestartSec=10

# Resource limits (optimized for 4GB RAM)
MemoryLimit=512M
CPUQuota=50%

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/wazuh-bridge/logs

[Install]
WantedBy=multi-user.target
```

#### Start Bridge Server
```bash
# Create user and directories
sudo useradd -r -s /bin/false wazuh-bridge
sudo mkdir -p /opt/wazuh-bridge/logs
sudo chown -R wazuh-bridge:wazuh-bridge /opt/wazuh-bridge

# Set permissions
sudo chown -R wazuh-bridge:wazuh-bridge /opt/wazuh-bridge

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable wazuh-bridge
sudo systemctl start wazuh-bridge

# Check status
sudo systemctl status wazuh-bridge
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

2. **Test bridge server:**
   ```bash
   curl -H "X-API-Key: wazuh-bridge-api-key" \
     http://192.168.30.100:5000/api/health
   ```

3. **Check N8N executions:**
   - Go to N8N dashboard
   - Click "Executions" to see workflow runs
   - Verify workflows are triggering correctly

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
3. **Monitor memory usage** on bridge server
4. **Configure alert buffering** based on volume

#### Monitoring Setup
1. **Enable N8N workflow monitoring**
2. **Set up bridge server health checks**
3. **Configure alerting** for failed workflows
4. **Monitor Foundation-Sec AI** performance

## Troubleshooting

### Common Issues

1. **Workflows not triggering:**
   - Verify workflows are activated
   - Check webhook URLs are correct
   - Verify API keys and credentials

2. **Bridge server connection errors:**
   - Check bridge server is running: `systemctl status wazuh-bridge`
   - Verify network connectivity
   - Check firewall rules

3. **AI analysis failures:**
   - Verify Foundation-Sec AI is running
   - Check if AI models are loaded
   - Review AI service logs

### Log Locations
- N8N logs: `/home/sa/projects/n8n_sec/n8n-data/n8nEventLog.log`
- Bridge server logs: `journalctl -u wazuh-bridge -f`
- Docker logs: `docker-compose logs -f`

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review workflow execution logs in N8N
3. Check service status and logs
4. Refer to the technical architecture documentation

## Next Steps

1. **Configure Wazuh** to send alerts to bridge server
2. **Set up monitoring dashboards**
3. **Configure notification channels** (Slack, email)
4. **Implement custom response actions**
5. **Set up backup and recovery procedures**