#!/usr/bin/env python3

import os
import logging
import asyncio
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model and tokenizer
model = None
tokenizer = None
text_generator = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9

class ChatResponse(BaseModel):
    choices: List[Dict]
    model: str = "foundation-sec-8b"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Loading Foundation-Sec-8B-Instruct model...")
    await load_model()
    logger.info("Model loaded successfully!")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Foundation-Sec-8B API",
    description="API for Foundation-Sec-8B-Instruct cybersecurity model",
    version="1.0.0",
    lifespan=lifespan
)

async def load_model():
    global model, tokenizer, text_generator
    
    try:
        model_name = "fdtn-ai/Foundation-Sec-8B-Instruct"
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Load tokenizer with retry logic and force download
        logger.info("Loading tokenizer...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name, 
                    trust_remote_code=True,
                    force_download=True,  # Force fresh download
                    resume_download=False  # Don't resume corrupted downloads
                )
                break
            except Exception as e:
                logger.warning(f"Tokenizer loading attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise e
                # Wait before retry
                await asyncio.sleep(5)
        
        # Load model with appropriate settings for memory efficiency
        logger.info("Loading model...")
        if device == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        else:
            # Use more aggressive memory optimization for CPU
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,  # Use float16 even on CPU to save memory
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                device_map="cpu",
                max_memory={"cpu": "8GB"}  # Limit CPU memory usage
            )
        
        # Create text generation pipeline with memory optimization
        text_generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if device == "cuda" else -1,
            torch_dtype=torch.float16,  # Use float16 for both CUDA and CPU
            max_length=512,  # Limit max generation length
            batch_size=1,    # Process one request at a time
            return_full_text=False
        )
        
        logger.info("Model and pipeline created successfully!")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise e

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model": "foundation-sec-8b"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Foundation-Sec-8B API",
        "model": "foundation-sec-8b",
        "status": "running"
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completions endpoint"""
    if text_generator is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert messages to prompt format
        prompt = ""
        for message in request.messages:
            if message.role == "system":
                prompt += f"<|start_header_id|>system<|end_header_id|>\n\n{message.content}<|eot_id|>"
            elif message.role == "user":
                prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{message.content}<|eot_id|>"
            elif message.role == "assistant":
                prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{message.content}<|eot_id|>"
        
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        # Generate response
        outputs = text_generator(
            prompt,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            return_full_text=False
        )
        
        generated_text = outputs[0]['generated_text'].strip()
        
        # Remove any trailing tokens
        if "<|eot_id|>" in generated_text:
            generated_text = generated_text.split("<|eot_id|>")[0].strip()
        
        response = ChatResponse(
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": generated_text
                    },
                    "finish_reason": "stop"
                }
            ]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/generate")
async def generate_text(request: Dict):
    """Simple text generation endpoint"""
    if text_generator is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        prompt = request.get("prompt", "")
        max_tokens = request.get("max_tokens", 512)
        temperature = request.get("temperature", 0.7)
        
        outputs = text_generator(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            return_full_text=False
        )
        
        return {
            "generated_text": outputs[0]['generated_text'],
            "model": "foundation-sec-8b"
        }
        
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "foundation_sec_api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )