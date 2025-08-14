#!/bin/bash

echo "Building and running Donut MCP Server with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Function to cleanup
cleanup() {
    echo "Cleaning up..."
    docker-compose down
    echo "Cleanup completed."
}

# Set trap to cleanup on script exit
trap cleanup EXIT

echo "Building and starting services with docker-compose..."
docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo "✅ Donut MCP Server is running successfully!"
    echo "🌐 Access the server at: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "❤️  Health Check: http://localhost:8000/health"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo "  View running containers: docker-compose ps"
    echo ""
    echo "Production mode (with nginx):"
    echo "  docker-compose --profile production up -d"
    echo ""
    echo "Testing the API:"
    echo "  curl http://localhost:8000/health"
    echo "  curl -X POST http://localhost:8000/process/paths -H 'Content-Type: application/json' -d '{\"image_paths\": [\"examples/example1.jpg\"]}'"
    
    # Wait a moment for the server to fully start
    echo ""
    echo "Waiting for server to be ready..."
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Server is responding to health checks!"
    else
        echo "⚠️  Server might still be starting up. Please wait a moment and try again."
    fi
    
else
    echo "❌ Failed to start the services"
    exit 1
fi

echo ""
echo "Press Ctrl+C to stop the services..."
# Keep the script running
docker-compose logs -f
