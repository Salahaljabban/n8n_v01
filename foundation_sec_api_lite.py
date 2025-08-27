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

# Global variables
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
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
        # Check if Ollama is running
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
        # Convert messages to Ollama format
        prompt = ""
        for message in request.messages:
            if message.role == "system":
                prompt += f"System: {message.content}\n"
            elif message.role == "user":
                prompt += f"User: {message.content}\n"
            elif message.role == "assistant":
                prompt += f"Assistant: {message.content}\n"
        
        prompt += "Assistant: "
        
        # Use memory-efficient model selection
        # Default to tinyllama for memory constraints, fallback to Foundation-Sec-8B if requested
        model_name = "tinyllama:latest"  # Memory-efficient default
        if hasattr(request, 'model') and request.model and 'foundation-sec' in request.model.lower():
            model_name = "bogdancsn/foundation-sec-8b:latest"
        
        # Prepare Ollama request with memory-optimized settings
        ollama_request = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature if request.temperature else 0.7,
                "num_predict": min(request.max_tokens if request.max_tokens else 256, 256),  # Limit tokens for memory efficiency
                "num_ctx": 2048,  # Reduced context window
                "top_k": 20,      # Reduced top_k for efficiency
                "top_p": 0.9
            }
        }
        
        # Make request to Ollama
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=ollama_request,
            timeout=60
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama request failed: {response.text}"
            )
        
        ollama_response = response.json()
        generated_text = ollama_response.get('response', '')
        
        # Format response in OpenAI format
        return ChatResponse(
            id=f"chatcmpl-{hash(prompt) % 1000000}",
            created=int(asyncio.get_event_loop().time()),
            model=request.model,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": generated_text
                    },
                    "finish_reason": "stop"
                }
            ],
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
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/models")
async def list_models():
    """List available models"""
    try:
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