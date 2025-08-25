#!/bin/bash

# Test script for n8n + Ollama integration

echo "=== Testing Ollama API Integration ==="
echo

# Test 1: Check if Ollama is responding
echo "1. Testing Ollama API availability..."
response=$(curl -s -w "%{http_code}" http://localhost:11434/api/tags -o /tmp/ollama_test.json)
if [ "$response" = "200" ]; then
    echo "✅ Ollama API is responding (HTTP 200)"
    echo "Available models:"
    cat /tmp/ollama_test.json | grep -o '"name":"[^"]*"' | cut -d'"' -f4 || echo "No models found in response"
else
    echo "❌ Ollama API not responding (HTTP $response)"
fi
echo

# Test 2: Check if n8n is responding
echo "2. Testing n8n availability..."
n8n_response=$(curl -s -w "%{http_code}" http://localhost:5678 -o /dev/null)
if [ "$n8n_response" = "200" ]; then
    echo "✅ n8n is responding (HTTP 200)"
else
    echo "❌ n8n not responding (HTTP $n8n_response)"
fi
echo

# Test 3: Test Ollama chat API
echo "3. Testing Ollama chat functionality..."
chat_response=$(curl -s -X POST http://localhost:11434/api/chat \
    -H "Content-Type: application/json" \
    -d '{
        "model": "tinyllama",
        "messages": [
            {
                "role": "user",
                "content": "Say hello in one word"
            }
        ],
        "stream": false
    }' \
    --max-time 30)

if echo "$chat_response" | grep -q '"message"'; then
    echo "✅ Ollama chat API is working"
    echo "Response preview: $(echo "$chat_response" | grep -o '"content":"[^"]*"' | head -1)"
else
    echo "❌ Ollama chat API failed or timed out"
    echo "Response: $chat_response"
fi
echo

# Test 4: Check Docker containers status
echo "4. Checking Docker containers status..."
echo "n8n container:"
docker ps --filter "name=n8n" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo
echo "Ollama container:"
docker ps --filter "name=foundation-sec-ai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

echo "=== Integration Test Complete ==="
echo
echo "Next steps:"
echo "1. Open n8n at: http://localhost:5678"
echo "2. Import the workflow from: /home/sa/n8n-ollama-workflow.json"
echo "3. Test the webhook endpoint after importing"
echo "4. Check API configuration in: /home/sa/ollama-api-config.md"

# Cleanup
rm -f /tmp/ollama_test.json