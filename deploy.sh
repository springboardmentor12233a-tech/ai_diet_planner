#!/bin/bash
# AI NutriCare System - Deployment Script for Linux/Mac

set -e  # Exit on error

echo "==================================="
echo "AI NutriCare System - Deployment"
echo "==================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with required environment variables:"
    echo "  OPENAI_API_KEY=your-key"
    echo "  USDA_API_KEY=your-key"
    echo "  NUTRICARE_ENCRYPTION_KEY=your-key"
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Check required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$USDA_API_KEY" ]; then
    echo "Error: USDA_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$NUTRICARE_ENCRYPTION_KEY" ]; then
    echo "Warning: NUTRICARE_ENCRYPTION_KEY not set. Generating new key..."
    NEW_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    echo "NUTRICARE_ENCRYPTION_KEY=$NEW_KEY" >> .env
    export NUTRICARE_ENCRYPTION_KEY=$NEW_KEY
    echo "Generated and saved new encryption key to .env"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data models exports logs

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Build Docker image
echo ""
echo "Building Docker image..."
docker-compose build

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "Checking service status..."
docker-compose ps

# Display logs
echo ""
echo "Recent logs:"
docker-compose logs --tail=20

echo ""
echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "Access the application at: http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  View status:      docker-compose ps"
echo ""
