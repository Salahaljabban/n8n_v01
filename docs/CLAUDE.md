# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an n8n Security Integration Platform - a defensive cybersecurity system that combines workflow automation with AI-powered security analysis. The platform integrates n8n workflows with Wazuh SIEM through direct API connections and leverages the Foundation-Sec-8B cybersecurity-specialized AI model for threat analysis.

## Architecture

### Three-Tier Containerized System
- **n8n** (port 5678): Workflow automation and orchestration
- **foundation-sec-ai** (port 11434): Ollama AI model server hosting Foundation-Sec-8B
- **foundation-sec-8b** (port 8000): FastAPI middleware providing OpenAI-compatible endpoints

### Integration Patterns
- **Direct Integration**: n8n workflows connect directly to Wazuh SIEM (172.20.18.14:55000)
- **AI Integration**: Workflows use Foundation-Sec AI for threat analysis and incident response
- **Webhook Architecture**: Real-time alert processing through webhook endpoints

## Common Commands

### Container Management
```bash
# Start all services
docker-compose up -d --build

# Check container status  
docker ps

# View logs
docker logs n8n
docker logs foundation-sec-ai
docker logs foundation-sec-8b

# Restart specific service
docker-compose restart foundation-sec
```

### Testing and Validation
```bash
# Run comprehensive integration tests
python3 test-wazuh-integration.py

# Run basic integration tests  
./test-integration.sh

# Test individual components
curl http://localhost:5678/healthz          # n8n health
curl http://localhost:11434/api/tags        # Ollama models
curl http://localhost:8000/health           # Foundation-Sec API
```

### AI Model Management
```bash
# Check available models in Ollama
docker exec foundation-sec-ai ollama list

# Pull additional models
docker exec foundation-sec-ai ollama pull tinyllama
docker exec foundation-sec-ai ollama pull phi3:mini
```

### Workflow Management
Access n8n at `http://localhost:5678` and:
1. Import workflow JSON files from project root
2. Configure Wazuh API credentials in workflow nodes
3. Activate workflows using the toggle switch
4. Test webhooks at `/webhook/{endpoint-name}`

## Key Implementation Details

### API Architectures
- **foundation_sec_api_lite.py**: Lightweight proxy service that forwards requests to Ollama
- **foundation_sec_api.py**: Direct model loading with transformers library (memory intensive)
- Both provide OpenAI-compatible `/v1/chat/completions` endpoints

### Memory Management
- Ollama container: 12GB memory limit configured in docker-compose.yml
- Safe startup script (`start_api_safe.py`) monitors system resources
- Automatic termination if memory usage exceeds 80%

### Security Workflows
Seven pre-configured workflows handle different security scenarios:
- `wazuh-alert-monitoring-workflow.json`: Direct API polling every 2 minutes
- `wazuh-webhook-receiver-workflow.json`: Real-time alert reception  
- `wazuh-high-priority-alert-workflow.json`: AI-powered critical alert analysis
- `wazuh-incident-response-workflow.json`: Automated response actions
- `n8n-ollama-workflow.json`: Interactive AI chat capabilities

### Wazuh Integration
Direct Wazuh API integration pattern:
```json
{
  "method": "POST",
  "url": "https://172.20.18.14:55000/security/user/authenticate",
  "body": {"username": "admin", "password": "admin"},
  "options": {"allowUnauthorizedCerts": true}
}
```

### Configuration Management
- Environment variables in docker-compose.yml control service behavior
- Wazuh API credentials configured in N8N workflow nodes
- Model selection via `OLLAMA_URL` environment variable
- Network configuration uses bridge network `n8n-network`

## Recent Improvements (Completed)

### ✅ API Stability Fixed
- **Issue**: Missing `import os` causing foundation-sec-8b container restart loop
- **Resolution**: Added missing import, container now stable and healthy
- **Status**: `curl http://localhost:8000/health` returns healthy status

### ✅ Memory Optimization Implemented
- **Issue**: Foundation-Sec-8B requires 15.6GB but only 10.4GB available
- **Resolution**: Default to tinyllama model, optimized API parameters
- **Models**: tinyllama (637MB) as default, Foundation-Sec-8B available on request
- **Configuration**: Reduced context window (2048), limited tokens (256), optimized parameters

### ✅ Direct Wazuh Integration Ready
- **Status**: Workflows pre-configured for direct API integration (172.20.18.14:55000)
- **Architecture**: Removed bridge server dependencies from workflows
- **Authentication**: Direct Wazuh API authentication handling implemented

### ⚠️ Workflow Import Required
- **Status**: Workflows created but require manual import through N8N UI
- **Guide**: See `WORKFLOW_SETUP.md` for detailed import instructions
- **Automation**: `import-workflows.py` script created but requires N8N authentication

## Troubleshooting

### Common Issues
1. **Workflow 404 errors**: Import and activate workflows via N8N UI at http://localhost:5678
2. **AI model memory issues**: System now defaults to tinyllama for memory efficiency
3. **API connection failures**: Verify containers are running with `docker-compose ps`
4. **Foundation-Sec-8B out of memory**: Use tinyllama or increase system memory allocation

### Debug Commands
```bash
# Check test results
cat test-results.json

# Monitor container health
docker-compose ps
docker inspect foundation-sec-ai --format='{{.State.Health.Status}}'

# Check n8n workflow execution logs
tail -f n8n-data/n8nEventLog.log
```

## Development Notes

### Defensive Security Focus
This is strictly a defensive cybersecurity platform. All components are designed for threat detection, vulnerability assessment, and security automation. No offensive capabilities should be added.

### Resource Constraints
The system is optimized for environments with memory constraints:
- CPU-only PyTorch installation specified in requirements
- Lightweight model fallbacks (tinyllama, phi3:mini) available
- Resource monitoring and automatic termination safeguards

### Model Configuration
Foundation-Sec-8B uses custom Ollama template in `Modelfile.foundation-sec` with cybersecurity-focused system prompts and optimized parameters (temperature: 0.7, top_p: 0.9, context: 4096).
