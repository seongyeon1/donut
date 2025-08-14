#!/bin/bash

echo "Building and running Donut app with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Remove existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -q '^donut-container$'; then
    echo "Removing existing container..."
    docker rm -f donut-container
fi

# Remove existing image if it exists
if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q '^donut-app:latest$'; then
    echo "Removing existing image..."
    docker rmi donut-app:latest
fi

echo "Building Docker image..."
# Try building with main Dockerfile first
if docker build -t donut-app .; then
    echo "Build successful with main Dockerfile"
else
    echo "Build failed with main Dockerfile, trying alternative..."
    if docker build -f Dockerfile.alternative -t donut-app .; then
        echo "Build successful with alternative Dockerfile"
    else
        echo "Build failed with both Dockerfiles. Please check the error messages above."
        exit 1
    fi
fi

echo "Running container..."
docker run -d \
  --name donut-container \
  -p 7860:7860 \
  -v $(pwd)/examples:/app/examples \
  -v $(pwd)/flagged:/app/flagged \
  donut-app

if [ $? -eq 0 ]; then
    echo "✅ Donut app is running successfully!"
    echo "🌐 Access the app at: http://localhost:7860"
    echo ""
    echo "Useful commands:"
    echo "  View logs: docker logs donut-container"
    echo "  Stop app: docker stop donut-container"
    echo "  Remove container: docker rm donut-container"
    echo "  Remove image: docker rmi donut-app"
else
    echo "❌ Failed to run the container"
    exit 1
fi
