#!/bin/bash

# N8N Workflow Import Script
# Imports all workflow JSON files using curl

# Load environment variables
source .env
API_TOKEN="$N8N_API_TOKEN"
N8N_URL="http://localhost:5678"

echo "N8N Workflow Import Tool"
echo "======================================="

# Find all workflow JSON files
workflow_files=(*.json)

echo "📄 Found ${#workflow_files[@]} workflow files:"
for file in "${workflow_files[@]}"; do
    if [[ "$file" != "test-results.json" ]]; then
        echo "   - $file"
    fi
done
echo

success_count=0
fail_count=0

# Import each workflow
for file in "${workflow_files[@]}"; do
    if [[ "$file" != "test-results.json" ]]; then
        echo "📥 Processing: $file"
        
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
            -H "Authorization: Bearer $API_TOKEN" \
            -H "Content-Type: application/json" \
            -X POST "$N8N_URL/rest/workflows" \
            -d @"$file")
        
        http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
        body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
        
        if [[ "$http_code" -eq 201 ]] || [[ "$http_code" -eq 200 ]]; then
            echo "✅ Successfully imported: $file"
            ((success_count++))
        else
            echo "❌ Failed to import $file: HTTP $http_code"
            if [[ -n "$body" ]]; then
                echo "   Error: $body"
            fi
            ((fail_count++))
        fi
        echo
    fi
done

echo "📊 Import Summary:"
echo "   Total files: $((success_count + fail_count))"
echo "   Successfully imported: $success_count"
echo "   Failed: $fail_count"
echo

if [[ $fail_count -eq 0 ]]; then
    echo "✅ All workflows imported successfully!"
    
    # List imported workflows
    echo
    echo "📋 Checking imported workflows:"
    curl -s -H "Authorization: Bearer $API_TOKEN" "$N8N_URL/rest/workflows" | \
        python3 -c "import sys, json; data=json.load(sys.stdin); [print(f'   - {w[\"name\"]} (ID: {w[\"id\"]})') for w in data]"
else
    echo "❌ Some workflows failed to import"
fi