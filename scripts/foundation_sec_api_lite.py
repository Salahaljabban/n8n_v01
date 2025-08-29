#!/usr/bin/env python3
"""
Lightweight Foundation-Sec API that uses Ollama container
This avoids loading the heavy model directly and prevents VM freezing
"""

import asyncio
import logging
import os
import requests
import json
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "foundation-sec"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

# Global variables / provider config
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
ai_provider = os.getenv("AI_PROVIDER", "ollama").lower()  # "ollama" or "deepseek"
# DeepSeek settings (OpenAI-compatible)
deepseek_base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_default_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
model_name = "foundation-sec"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Foundation-Sec API Lite...")
    await check_ollama_connection()
    yield
    # Shutdown
    logger.info("Shutting down...")

async def check_ollama_connection():
    """Check if Ollama is running and the model is available"""
    try:
        # Skip check if provider is DeepSeek
        if ai_provider != "ollama":
            logger.info("AI provider is not Ollama; skipping local model check")
            return

        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            logger.info(f"Available models: {model_names}")

            if any('foundation-sec' in name for name in model_names):
                logger.info("Foundation-Sec model found in Ollama!")
            else:
                logger.warning("Foundation-Sec model not found. Available models listed above.")
        else:
            logger.error(f"Failed to connect to Ollama: {response.status_code}")
    except Exception as e:
        logger.error(f"Error connecting to Ollama: {str(e)}")
        logger.info("Make sure Ollama container is running: docker ps")

app = FastAPI(
    title="Foundation-Sec-8B API Lite",
    description="Lightweight API for Foundation-Sec model via Ollama",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if ai_provider == "deepseek":
            # Try to check DeepSeek API availability (model list if available)
            url = f"{deepseek_base}/v1/models"
            headers = {"Accept": "application/json"}
            if deepseek_api_key:
                headers["Authorization"] = f"Bearer {deepseek_api_key}"
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code in (200, 401, 403):
                # Consider reachable even if unauthorized, since some free endpoints may not require key
                return {"status": "reachable", "backend": "deepseek", "base": deepseek_base}
            raise HTTPException(status_code=503, detail="DeepSeek API not responding")
        # Default: Ollama health
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "model": "foundation-sec", "backend": "ollama"}
        else:
            raise HTTPException(status_code=503, detail="Ollama not responding")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama connection failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Foundation-Sec-8B API Lite",
        "model": "foundation-sec",
        "backend": "ollama",
        "status": "running"
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        # Route to provider by env or by model hint
        target_provider = ai_provider
        if request.model and isinstance(request.model, str) and request.model.lower().startswith("deepseek"):
            target_provider = "deepseek"

        if target_provider == "deepseek":
            # Forward to DeepSeek (OpenAI-compatible)
            ds_model = request.model or deepseek_default_model
            payload = {
                "model": ds_model,
                "messages": [ {"role": m.role, "content": m.content} for m in request.messages ],
                "max_tokens": min(request.max_tokens if request.max_tokens else 256, 1024),
                "temperature": request.temperature if request.temperature is not None else 0.7,
                "stream": False
            }
            url = f"{deepseek_base}/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            if deepseek_api_key:
                headers["Authorization"] = f"Bearer {deepseek_api_key}"

            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"DeepSeek error: {resp.text}")
            ds = resp.json()

            # Normalize to ChatResponse
            return ChatResponse(
                id=str(ds.get("id", f"chatcmpl-{int(time.time())}")),
                created=int(ds.get("created", time.time())),
                model=str(ds.get("model", ds_model)),
                choices=ds.get("choices", []),
                usage=ds.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
            )

        # Default: use Ollama
        # Convert messages to a single prompt
        prompt = ""
        for message in request.messages:
            if message.role == "system":
                prompt += f"System: {message.content}\n"
            elif message.role == "user":
                prompt += f"User: {message.content}\n"
            elif message.role == "assistant":
                prompt += f"Assistant: {message.content}\n"
        prompt += "Assistant: "

        # Memory-efficient defaults
        selected_model = "tinyllama:latest"
        if hasattr(request, 'model') and request.model and 'foundation-sec-8b-force' in request.model.lower():
            selected_model = "bogdancsn/foundation-sec-8b:latest"

        ollama_request = {
            "model": selected_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature if request.temperature else 0.7,
                "num_predict": min(request.max_tokens if request.max_tokens else 256, 256),
                "num_ctx": 2048,
                "top_k": 20,
                "top_p": 0.9
            }
        }

        response = requests.post(f"{ollama_url}/api/generate", json=ollama_request, timeout=60)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Ollama request failed: {response.text}")

        ollama_response = response.json()
        generated_text = ollama_response.get('response', '')

        return ChatResponse(
            id=f"chatcmpl-{hash(prompt) % 1000000}",
            created=int(time.time()),
            model=request.model or selected_model,
            choices=[{
                "index": 0,
                "message": {"role": "assistant", "content": generated_text},
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(prompt.split()) + len(generated_text.split())
            }
        )
        
    except requests.RequestException as e:
        logger.error(f"Ollama request error: {str(e)}")
        raise HTTPException(status_code=503, detail="Model service unavailable")
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/models")
async def list_models():
    """List available models"""
    try:
        if ai_provider == "deepseek":
            # Return a static list for DeepSeek
            models = [
                {"id": deepseek_default_model, "object": "model", "created": 0, "owned_by": "deepseek"},
                {"id": "deepseek-reasoner", "object": "model", "created": 0, "owned_by": "deepseek"}
            ]
            return {"object": "list", "data": models}

        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            ollama_models = response.json().get('models', [])
            models = []
            for model in ollama_models:
                models.append({
                    "id": model['name'],
                    "object": "model",
                    "created": 0,
                    "owned_by": "ollama"
                })
            return {"object": "list", "data": models}
        else:
            raise HTTPException(status_code=503, detail="Cannot fetch models from Ollama")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error fetching models: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser(description="Foundation-Sec API Lite")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the API on")
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")
