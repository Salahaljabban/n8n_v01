# Repository Guidelines

## Project Structure & Module Organization
- `foundation_sec_api.py` / `foundation_sec_api_lite.py`: FastAPI services for Foundation‑Sec (full vs. Ollama‑backed lite).
- `start_api_safe.py`: Memory‑safe launcher with process monitoring.
- `docker-compose.yml`: Orchestrates `n8n`, `foundation-sec` API, and `ollama`.
- `wazuh-*-workflow.json`: Importable N8N workflows for direct Wazuh API integration.
- `n8n-data/`: Persistent N8N app data and logs.
- `test-wazuh-integration.py`, `test-integration.sh`: Integration and smoke tests.
- `*.md` guides: `README.md`, deployment and ops docs under root and `.trae/`.

## Build, Test, and Development Commands
- Start services: `docker-compose up -d`
- Check status: `docker-compose ps`
- Run integration tests: `python3 test-wazuh-integration.py`
- Quick smoke test: `bash test-integration.sh`
- Dev API (lite): `uvicorn foundation_sec_api_lite:app --host 0.0.0.0 --port 8000`
- Health checks: `curl http://localhost:5678/healthz`, `curl http://localhost:11434/api/tags`, `curl http://localhost:8000/health`

## Coding Style & Naming Conventions
- Python 3.8+, 4‑space indentation, type hints where practical.
- Filenames: snake_case for Python (`foundation_sec_api.py`); kebab‑case for workflows (`wazuh-incident-response-workflow.json`).
- FastAPI: use Pydantic models for request/response; keep endpoints small and composable.
- Lint/format: prefer `black` (line length 100) and `ruff` if available; otherwise match existing style.

## Testing Guidelines
- Primary: `python3 test-wazuh-integration.py` validates N8N, direct Wazuh API connectivity, Ollama, and workflows.
- Webhook checks: POST to `/webhook/wazuh-alerts`, `/webhook/high-priority-alert`, `/webhook/incident-response` as shown in `README.md`.
- Add new tests under `tests/` (if introduced) using `pytest`, name `test_<area>.py`. Include minimal fixtures and clear assertions.
- Save artifacts to `test-results.json` (existing pattern).

## Commit & Pull Request Guidelines
- Commit style: Conventional Commits (e.g., `feat: add Wazuh API health monitoring workflow`, `fix: harden AI health check`).
- PRs must include: purpose and scope, linked issues, test evidence (commands and results), screenshots of N8N changes, and notes for config/doc updates.
- If modifying `docker-compose.yml`, workflows, or env usage, update `README.md` and deployment docs accordingly.

## Security & Configuration Tips
- Never commit secrets; use `.env` values referenced in `README.md` and deployment guides.
- Validate external calls and timeouts; configure appropriate timeouts for direct Wazuh API calls.
- Log paths: `./n8n-data/logs/`, Docker logs via `docker logs <container>`. Redact sensitive data in examples.
