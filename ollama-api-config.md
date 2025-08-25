# Ollama API Configuration for n8n Integration

## API Endpoint Information

**Base URL:** `http://foundation-sec-ai:11434`
**Alternative URL (from host):** `http://localhost:11434`

## Available Models

- `tinyllama` - Ultra-lightweight model (637MB) - **RECOMMENDED for nested Docker/low-memory environments**
- `phi3:mini` - Lightweight model (2.3GB) - May have memory issues in constrained environments

## API Endpoints

### 1. List Available Models
```
GET /api/tags
```

### 2. Chat Completion
```
POST /api/chat
Content-Type: application/json

{
  "model": "phi3:mini",
  "messages": [
    {
      "role": "user",
      "content": "Your message here"
    }
  ],
  "stream": false
}
```

### 3. Generate Completion
```
POST /api/generate
Content-Type: application/json

{
  "model": "tinyllama",
  "prompt": "Your prompt here",
  "stream": false
}
```

## n8n HTTP Request Node Configuration

### For Chat Completion:
- **Method:** POST
- **URL:** `http://foundation-sec-ai:11434/api/chat`
- **Headers:** 
  - `Content-Type: application/json`
- **Body (JSON):**
```json
{
  "model": "tinyllama",
  "messages": [
    {
      "role": "user",
      "content": "{{ $json.message }}"
    }
  ],
  "stream": false
}
```

## Response Format

The API returns JSON responses with the following structure:
```json
{
  "model": "phi3:mini",
  "created_at": "2025-08-21T18:00:00.000Z",
  "message": {
    "role": "assistant",
    "content": "AI response here"
  },
  "done": true
}
```

## Notes

- The AI service is running in CPU mode due to nested Docker environment
- Use `phi3:mini` model for better performance in low-memory scenarios
- The service is accessible from within the Docker network using `foundation-sec-ai:11434`
- From the host system, use `localhost:11434`