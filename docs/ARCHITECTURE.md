# N8N-Sec Project Architecture

This document provides a visual overview of the project’s components, deployment topology, and key data flows between services and workflows. Diagrams use Mermaid so you can preview them in most IDEs.

## Components Overview

```mermaid
graph TD
  U[Admin/User] -->|Basic Auth| N8N[N8N UI + Workflows (5678)]

  subgraph Docker Network: n8n-network
    N8N -->|HTTP POST (JSON)| FS[Foundation-Sec API (FastAPI) (8000)]
    FS -->|HTTP JSON| OLL[Ollama (LLM Backend) (11434)]
    N8N -->|HTTPS (Bearer Token)| WAZ[Wazuh API (55000)]
  end

  N8N -.->|Public API /api/v1 (X-N8N-API-KEY)| N8NAPI[(N8N Public API)]

  subgraph Workflows
    A1[Webhook Receiver /webhook/wazuh-webhook]
    A2[High Priority Alert /webhook/high-priority-alert]
    A3[Incident Response /webhook/incident-response]
    A4[Auth Bridge /webhook/bridge-auth]
    A5[AI Chat /webhook/chat]
    A6[Alert Monitoring (cron)]
    A7[Health Monitoring (cron)]
  end

  N8N --- A1 & A2 & A3 & A4 & A5 & A6 & A7

  classDef svc fill:#e8f0fe,stroke:#4a67d6,stroke-width:1px;
  classDef wf fill:#eef7ee,stroke:#45a049,stroke-width:1px;
  class N8N,FS,OLL,WAZ,N8NAPI svc;
  class A1,A2,A3,A4,A5,A6,A7 wf;
```

## Deployment Topology

```mermaid
flowchart LR
  subgraph Host
    direction TB
    UI[[Browser]]
    subgraph Docker Compose
      direction LR
      N8N[N8N Container\nPort 5678]:::box -->|/home/node/.n8n| VOL[(n8n-data volume)]
      FS[Foundation-Sec API\nPort 8000]:::box
      OLL[Ollama\nPort 11434\nvol: ~/.ollama]:::box --> OVL[(ollama_data volume)]
    end
  end

  UI -->|http://localhost:5678| N8N
  N8N -->|http://foundation-sec:8000| FS
  FS -->|http://foundation-sec-ai:11434| OLL
  N8N -->|https://<WAZUH_IP>:55000| WAZ[(Wazuh Server)]

  classDef box fill:#f9fbff,stroke:#6b8bd6,stroke-width:1px;
```

## Sequence: Wazuh Token + Health Check

```mermaid
sequenceDiagram
  autonumber
  participant S as Schedule Trigger
  participant N as N8N Workflow
  participant W as Wazuh API (55000)

  S->>N: Start health check (cron)
  N->>W: GET /security/user/authenticate?raw=true<br/>Basic Auth (env creds)
  W-->>N: 200 OK (raw JWT token)
  N->>W: GET /manager/status<br/>Authorization: Bearer <token>
  W-->>N: 200 OK (process statuses)
  N->>N: Evaluate health and issues
  N-->>N: Notify/Log/Plan remediation
```

## Sequence: Real-time Alert to High Priority AI Analysis

```mermaid
sequenceDiagram
  autonumber
  participant WZ as Wazuh (Alert Source)
  participant WR as Webhook Receiver (/webhook/wazuh-webhook)
  participant HPA as High Priority Alert (/webhook/high-priority-alert)
  participant FS as Foundation-Sec API (8000)
  participant IR as Incident Response (/webhook/incident-response)

  WZ->>WR: POST alert JSON
  WR->>WR: Normalize and score severity
  alt High/Critical
    WR->>HPA: POST alert JSON
    HPA->>FS: POST /v1/chat/completions (analysis)
    FS-->>HPA: AI analysis (threat level, recs)
    HPA->>IR: POST incident with recommendations
    IR->>IR: Plan actions (block/quarantine/forensics)
    IR->>WZ: POST /active-response (Bearer token)
    IR-->>HPA: Completion summary
  else Standard
    WR->>WR: Buffer/Log for polling
  end
```

## Sequence: Public API Import/Activate

```mermaid
sequenceDiagram
  autonumber
  participant Dev as Developer Script
  participant API as N8N Public API (/api/v1)
  participant N as N8N

  Dev->>API: POST /workflows (X-N8N-API-KEY)
  API-->>Dev: 201 Created (workflow id)
  Dev->>API: POST /workflows/{id}/activate
  API-->>Dev: 200 OK (active=true)
```

## Key Configuration

- N8N Public API: `X-N8N-API-KEY` via `N8N_API_TOKEN`
- N8N Base URL: `N8N_SERVER` (default `http://localhost:5678`)
- Wazuh API: `WAZUH_API_URL`, `WAZUH_API_USER`, `WAZUH_API_PASSWORD`
- SSL: Self-signed allowed in workflows (development); prefer trusted CA in production
- Docker network: `n8n-network` connects all containers

## Notes

- Token flow: Use Basic Auth only for `/security/user/authenticate?raw=true`, then Bearer token for protected endpoints like `/manager/status`, `/manager/info`, `/agents`, etc.
- Alert monitoring via indexer is optional; ensure `WAZUH_INDEXER_URL` is reachable before enabling related nodes.
- Public API standardization: scripts use `/api/v1` exclusively with `N8N_API_TOKEN`.

