#!/bin/bash

echo "Testing Donut MCP Server API endpoints..."
echo "=========================================="

BASE_URL="http://localhost:8000"

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "${BASE_URL}/health" | jq '.' 2>/dev/null || curl -s "${BASE_URL}/health"
echo ""

# Test root endpoint
echo "2. Testing root endpoint..."
curl -s "${BASE_URL}/" | jq '.' 2>/dev/null || curl -s "${BASE_URL}/"
echo ""

# Test process by paths endpoint
echo "3. Testing process by paths endpoint..."
if [ -f "examples/example1.jpg" ]; then
    curl -X POST "${BASE_URL}/process/paths" \
         -H "Content-Type: application/json" \
         -d '{"image_paths": ["examples/example1.jpg"]}' \
         | jq '.' 2>/dev/null || curl -X POST "${BASE_URL}/process/paths" \
         -H "Content-Type: application/json" \
         -d '{"image_paths": ["examples/example1.jpg"]}'
else
    echo "⚠️  examples/example1.jpg not found, skipping path test"
fi
echo ""

# Test file upload endpoint
echo "4. Testing file upload endpoint..."
if [ -f "examples/example1.jpg" ]; then
    curl -X POST "${BASE_URL}/process/file" \
         -F "file=@examples/example1.jpg" \
         | jq '.' 2>/dev/null || curl -X POST "${BASE_URL}/process/file" \
         -F "file=@examples/example1.jpg"
else
    echo "⚠️  examples/example1.jpg not found, skipping upload test"
fi
echo ""

echo "=========================================="
echo "API testing completed!"
echo ""
echo "For interactive API testing, visit: ${BASE_URL}/docs"
