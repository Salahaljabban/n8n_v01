# AI Providers Configuration

This project can route AI requests from N8N to either the local Ollama backend (default) or to the public DeepSeek API using the Foundation‑Sec API Lite as a wrapper.

## Options

- Ollama (default): Runs locally in the `ollama` container. Low‑memory default model (`tinyllama`) is used unless explicitly forced.
- DeepSeek (optional): Routes OpenAI‑compatible Chat Completions to the DeepSeek API.

## Switch Provider

Set the provider via environment variable for the `foundation-sec` service:

```env
# .env
AI_PROVIDER=deepseek            # or 'ollama' (default)
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY   # optional if the endpoint allows anonymous access
DEEPSEEK_MODEL=deepseek-chat    # optional, defaults to 'deepseek-chat'
```

Restart the stack after changes:

```bash
docker-compose up -d --force-recreate foundation-sec
```

## How It Works

- N8N calls `foundation-sec:8000/v1/chat/completions` (OpenAI‑style).
- If `AI_PROVIDER=deepseek`, the wrapper forwards to `DEEPSEEK_BASE_URL/v1/chat/completions` with the same messages and returns the response in OpenAI format.
- If `AI_PROVIDER=ollama`, the wrapper builds a single prompt and uses `tinyllama` through Ollama’s `/api/generate` (memory friendly). Set the request `model` to `foundation-sec-8b-force` to use the 8B model if available.

## Per‑Request Override

- If you pass a `model` that starts with `deepseek...` in the request body, the wrapper will route to DeepSeek for that request even if `AI_PROVIDER=ollama`.

Example (N8N HTTP Request node body):

```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"}
  ]
}
```

## Health & Models

- Health: `GET /health` reports provider reachability (Ollama or DeepSeek).
- Models: `GET /models` lists local Ollama models or DeepSeek logical models (e.g., `deepseek-chat`, `deepseek-reasoner`).

## Notes

- For production, obtain and set a `DEEPSEEK_API_KEY` if required by the API endpoint you use.
- Network egress must be allowed from the `foundation-sec` container to reach DeepSeek.
- N8N workflows do not change; switching providers is transparent.

