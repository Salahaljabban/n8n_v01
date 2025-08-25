# N8N-Wazuh Integration Windows Server Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the N8N-Wazuh SIEM integration bridge server on Windows Server 2019/2022 at IP address 192.168.30.100.

## Prerequisites
- Windows Server 2019/2022 (4GB RAM minimum)
- Administrator privileges
- Network connectivity to:
  - Wazuh server at 172.20.18.14:55000
  - N8N server for webhook callbacks
- Python 3.8+ (will be installed if not present)

## Quick Installation

### Option 1: Automated Installation (Recommended)

1. **Download the installation files** to the Windows Server:
   ```cmd
   # Create installation directory
   mkdir C:\WazuhBridge\install
   cd C:\WazuhBridge\install
   
   # Copy the following files to this directory:
   # - app.py
   # - wazuh_bridge_service.py
   # - install.bat
   # - Deploy-WazuhBridge.ps1
   # - manage-service.bat
   # - configure-firewall.bat
   ```

2. **Run the installation script** as Administrator:
   ```cmd
   # Right-click Command Prompt -> Run as Administrator
   cd C:\WazuhBridge\install
   install.bat
   ```

3. **Verify installation**:
   ```cmd
   manage-service.bat status
   manage-service.bat test
   ```

### Option 2: PowerShell Deployment

1. **Open PowerShell as Administrator**
2. **Run the deployment script**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\Deploy-WazuhBridge.ps1
   ```

3. **Custom configuration**:
   ```powershell
   .\Deploy-WazuhBridge.ps1 -InstallPath "C:\WazuhBridge" -ApiKey "custom-api-key" -ServerPort 5000
   ```

## Manual Installation

### Step 1: Install Python

1. **Download Python 3.11** from https://www.python.org/downloads/
2. **Run installer with these options**:
   - ✅ Add Python to PATH
   - ✅ Install for all users
   - ✅ Install pip
   - ❌ Install documentation (save space)

3. **Verify installation**:
   ```cmd
   python --version
   pip --version
   ```

### Step 2: Install Python Dependencies

```cmd
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
python -m pip install flask==2.3.3
python -m pip install requests==2.31.0
python -m pip install pywin32==306
python -m pip install waitress==2.1.2
```

### Step 3: Create Directory Structure

```cmd
# Create installation directories
mkdir "C:\Program Files\WazuhBridge"
mkdir "C:\ProgramData\WazuhBridge\logs"
mkdir "C:\ProgramData\WazuhBridge\config"
mkdir "C:\ProgramData\WazuhBridge\data"
```

### Step 4: Deploy Application Files

1. **Copy `app.py`** to `C:\Program Files\WazuhBridge\app.py`
2. **Copy `wazuh_bridge_service.py`** to `C:\Program Files\WazuhBridge\wazuh_bridge_service.py`

### Step 5: Create Configuration

Create `C:\ProgramData\WazuhBridge\config\config.json`:
```json
{
  "WAZUH_API_URL": "https://172.20.18.14:55000",
  "WAZUH_USERNAME": "admin",
  "WAZUH_PASSWORD": "admin",
  "API_KEY": "wazuh-bridge-api-key",
  "MAX_BUFFER_SIZE": 1000,
  "SERVER_PORT": 5000,
  "SERVER_HOST": "0.0.0.0"
}
```

### Step 6: Install Windows Service

```cmd
# Navigate to installation directory
cd "C:\Program Files\WazuhBridge"

# Install the service
python wazuh_bridge_service.py install

# Configure service for automatic startup
sc config WazuhBridgeService start= auto
sc description WazuhBridgeService "Bridge service for N8N-Wazuh SIEM integration on Windows Server"
```

### Step 7: Configure Windows Firewall

```cmd
# Create firewall rule for inbound traffic
netsh advfirewall firewall add rule name="Wazuh Bridge Server" dir=in action=allow protocol=TCP localport=5000

# Create firewall rule for Wazuh API access
netsh advfirewall firewall add rule name="Wazuh API Access" dir=out action=allow protocol=TCP remoteport=55000 remoteip=172.20.18.14
```

### Step 8: Start the Service

```cmd
# Start the service
net start WazuhBridgeService

# Verify service status
sc query WazuhBridgeService
```

## Service Management

### Using Batch Scripts

```cmd
# Start service
manage-service.bat start

# Stop service
manage-service.bat stop

# Restart service
manage-service.bat restart

# Check status
manage-service.bat status

# View logs
manage-service.bat logs

# Test connectivity
manage-service.bat test

# Show configuration
manage-service.bat config
```

### Using Windows Services Console

1. **Open Services**: `services.msc`
2. **Find**: "WazuhBridgeService"
3. **Right-click** for options: Start, Stop, Restart, Properties

### Using Command Line

```cmd
# Service control
net start WazuhBridgeService
net stop WazuhBridgeService

# Service status
sc query WazuhBridgeService

# Service configuration
sc qc WazuhBridgeService
```

## Firewall Management

### Configure Firewall

```cmd
# Install firewall rules
configure-firewall.bat install

# Check firewall status
configure-firewall.bat status

# Test connectivity
configure-firewall.bat test

# Remove firewall rules
configure-firewall.bat remove
```

### Manual Firewall Configuration

```cmd
# Allow inbound on port 5000
netsh advfirewall firewall add rule name="Wazuh Bridge Server - Inbound" dir=in action=allow protocol=TCP localport=5000

# Allow outbound to Wazuh API
netsh advfirewall firewall add rule name="Wazuh API Access" dir=out action=allow protocol=TCP remoteport=55000 remoteip=172.20.18.14

# Allow HTTPS outbound
netsh advfirewall firewall add rule name="Wazuh Bridge - HTTPS Outbound" dir=out action=allow protocol=TCP remoteport=443

# Allow DNS outbound
netsh advfirewall firewall add rule name="Wazuh Bridge - DNS Outbound" dir=out action=allow protocol=UDP remoteport=53
```

## Testing and Validation

### Health Check

```cmd
# Test using curl (if available)
curl -H "X-API-Key: wazuh-bridge-api-key" http://192.168.30.100:5000/api/health

# Test using PowerShell
powershell -Command "Invoke-RestMethod -Uri 'http://192.168.30.100:5000/api/health' -Headers @{'X-API-Key'='wazuh-bridge-api-key'}"
```

### Expected Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00.000Z",
  "buffered_alerts": 0,
  "uptime": 3600,
  "memory_usage": {
    "used_mb": 45,
    "available_mb": 3955
  }
}
```

### API Endpoints Testing

```powershell
# Health check
Invoke-RestMethod -Uri 'http://192.168.30.100:5000/api/health' -Headers @{'X-API-Key'='wazuh-bridge-api-key'}

# Authentication test
Invoke-RestMethod -Uri 'http://192.168.30.100:5000/api/auth' -Method POST -Headers @{'X-API-Key'='wazuh-bridge-api-key'}

# Metrics
Invoke-RestMethod -Uri 'http://192.168.30.100:5000/api/metrics' -Headers @{'X-API-Key'='wazuh-bridge-api-key'}

# Get alerts
Invoke-RestMethod -Uri 'http://192.168.30.100:5000/api/alerts' -Headers @{'X-API-Key'='wazuh-bridge-api-key'}
```

## Troubleshooting

### Common Issues

#### Service Won't Start
1. **Check Python installation**:
   ```cmd
   python --version
   ```

2. **Check dependencies**:
   ```cmd
   python -c "import flask, requests, win32serviceutil; print('All dependencies OK')"
   ```

3. **Check configuration file**:
   ```cmd
   type "C:\ProgramData\WazuhBridge\config\config.json"
   ```

4. **Check Windows Event Log**:
   - Open Event Viewer
   - Navigate to Windows Logs > Application
   - Look for WazuhBridgeService events

#### Connectivity Issues
1. **Test Wazuh connectivity**:
   ```cmd
   telnet 172.20.18.14 55000
   ```

2. **Check firewall rules**:
   ```cmd
   netsh advfirewall firewall show rule name="Wazuh Bridge Server - Inbound"
   ```

3. **Check port binding**:
   ```cmd
   netstat -an | find ":5000"
   ```

#### Memory Issues (4GB RAM)
1. **Monitor memory usage**:
   ```cmd
   tasklist /fi "imagename eq python.exe"
   ```

2. **Adjust buffer size** in config.json:
   ```json
   {
     "MAX_BUFFER_SIZE": 500
   }
   ```

3. **Restart service** after configuration changes:
   ```cmd
   manage-service.bat restart
   ```

### Log Files

- **Application logs**: `C:\ProgramData\WazuhBridge\logs\app.log`
- **Service logs**: `C:\ProgramData\WazuhBridge\logs\service.log`
- **Deployment logs**: `C:\ProgramData\WazuhBridge\logs\deployment.log`
- **Windows Event Log**: Event Viewer > Windows Logs > Application

### Performance Monitoring

```cmd
# Check service performance
manage-service.bat test

# Monitor memory usage
tasklist /fi "imagename eq python.exe" /fo table

# Check network connections
netstat -an | find ":5000"

# Monitor CPU usage
wmic process where name="python.exe" get ProcessId,PageFileUsage,WorkingSetSize
```

## Security Considerations

### File Permissions
- Configuration files should be readable only by Administrators and SYSTEM
- Log files should be writable by the service account
- Application files should be read-only for the service account

### Network Security
- Use strong API keys (change default `wazuh-bridge-api-key`)
- Restrict firewall rules to specific source IPs if possible
- Consider using HTTPS with proper certificates in production
- Monitor access logs for unauthorized attempts

### Service Account
- Consider running the service under a dedicated service account
- Grant minimal required permissions
- Regularly rotate API keys and passwords

## Integration with N8N

Once the bridge server is running, configure N8N workflows to use:

- **Bridge Server URL**: `http://192.168.30.100:5000`
- **API Key**: `wazuh-bridge-api-key` (or your custom key)
- **Health Check**: `http://192.168.30.100:5000/api/health`
- **Authentication**: `http://192.168.30.100:5000/api/auth`
- **Alerts**: `http://192.168.30.100:5000/api/alerts`

## Maintenance

### Regular Tasks
1. **Monitor service status** daily
2. **Check log files** weekly
3. **Review memory usage** weekly
4. **Update Python packages** monthly
5. **Backup configuration** before changes

### Updates
1. **Stop the service**:
   ```cmd
   net stop WazuhBridgeService
   ```

2. **Backup current installation**:
   ```cmd
   xcopy "C:\Program Files\WazuhBridge" "C:\Backup\WazuhBridge_%date%" /E /I
   ```

3. **Update files** and **restart service**:
   ```cmd
   net start WazuhBridgeService
   ```

## Support

For issues and support:
1. Check the troubleshooting section above
2. Review log files for error messages
3. Verify network connectivity and firewall rules
4. Test API endpoints manually
5. Check Windows Event Log for service-related errors

---

**Note**: This bridge server is optimized for Windows Server environments with limited resources (4GB RAM). The configuration includes memory management and efficient alert buffering to work within these constraints.