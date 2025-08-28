# Windows Deployment Guide — N8N + Wazuh (Direct API)

## Overview
This guide shows how to deploy and configure the N8N–Wazuh integration on Windows using a direct connection to the Wazuh API. No bridge server is required.

## Prerequisites
- Windows Server 2019/2022 or Windows 10/11
- Administrator privileges
- Docker Desktop for Windows
- Network access to Wazuh API: `https://172.20.18.14:55000`
- Valid Wazuh API credentials

## Setup

1) Install Docker Desktop for Windows
- Download and install from https://www.docker.com/products/docker-desktop/
- Enable “Start Docker Desktop when you log in”

2) Get the project
- Open PowerShell and clone or copy the repo to a working folder, e.g. `C:\n8n_sec`

3) Create `.env`
- In the project root, create a file named `.env` with:

```
WAZUH_API_URL=https://172.20.18.14:55000
WAZUH_API_USER=<your_wazuh_user>
WAZUH_API_PASSWORD=<your_wazuh_password>
```

4) Start services
```
cd C:\n8n_sec
docker-compose up -d
```

5) Access N8N
- Open http://localhost:5678 and complete the initial setup.

## Import Workflows
In N8N, import these JSON files from the repo in this order:
- `wazuh-alert-monitoring-workflow.json`
- `wazuh-webhook-receiver-workflow.json`
- `wazuh-high-priority-alert-workflow.json`
- `wazuh-incident-response-workflow.json`
- `n8n-ollama-workflow.json` (optional)

Then activate the workflows.

## Configure Environment
The workflows use environment variables. Docker Compose loads your `.env` and injects them into the `n8n` container, where N8N exposes them as `$env.*` in nodes.

If you update `.env`, apply changes:
```
docker-compose up -d --force-recreate n8n
```

## Testing

1) Verify N8N
```
Invoke-RestMethod -Uri 'http://localhost:5678/healthz'
```

2) Test Wazuh authentication (PowerShell)
```
$body = @{ username = $Env:WAZUH_API_USER; password = $Env:WAZUH_API_PASSWORD } | ConvertTo-Json
Invoke-RestMethod -SkipCertificateCheck -Method Post `
  -Uri "$Env:WAZUH_API_URL/security/user/authenticate" `
  -ContentType 'application/json' -Body $body
```

3) Fetch alerts with the token
```
$auth   = Invoke-RestMethod -SkipCertificateCheck -Method Post `
  -Uri "$Env:WAZUH_API_URL/security/user/authenticate" `
  -ContentType 'application/json' -Body $body
$token  = $auth.data.token
Invoke-RestMethod -SkipCertificateCheck -Method Get `
  -Uri "$Env:WAZUH_API_URL/alerts" -Headers @{ Authorization = "Bearer $token" }
```

4) Test N8N webhooks
```
# Webhook receiver
Invoke-RestMethod -Method Post -Uri 'http://localhost:5678/webhook/wazuh-alerts' `
  -ContentType 'application/json' `
  -Body (@{ rule = @{ level = 7; description = 'Test alert' } ; agent = @{ name = 'win-agent' } } | ConvertTo-Json)

# Auth workflow (uses env creds if body omitted)
Invoke-RestMethod -Method Post -Uri 'http://localhost:5678/webhook/bridge-auth' `
  -ContentType 'application/json' -Body (@{ } | ConvertTo-Json)
```

## Troubleshooting
- TLS: Use `-SkipCertificateCheck` for lab/self-signed endpoints.
- Credentials: Ensure `.env` has `WAZUH_API_USER` and `WAZUH_API_PASSWORD`, then recreate the n8n container.
- Connectivity: Confirm firewall allows outbound to `172.20.18.14:55000`.
- N8N logs: `docker logs n8n`
- App data/logs: `n8n-data\`

## Security
- Do not commit `.env` to source control.
- Use least-privilege Wazuh accounts for API access.
- Rotate credentials regularly.

## Maintenance
- Update env values in `.env`; apply with `docker-compose up -d --force-recreate n8n`.
- Keep Docker Desktop up to date.
- Periodically prune unused images/containers.

