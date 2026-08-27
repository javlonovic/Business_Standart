#!/bin/bash

# 🧪 Business Standart Platform - Local Testing Script
# This script helps you quickly start and test the platform locally

set -e  # Exit on error

echo "🚀 Business Standart Platform - Local Testing"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Docker
if command -v docker &> /dev/null; then
    print_success "Docker is installed"
    DOCKER_VERSION=$(docker --version)
    echo "  $DOCKER_VERSION"
else
    print_error "Docker is not installed"
    echo "  Please install Docker from: https://www.docker.com/get-started"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose is installed"
    COMPOSE_VERSION=$(docker-compose --version)
    echo "  $COMPOSE_VERSION"
else
    print_error "Docker Compose is not installed"
    echo "  Please install Docker Compose"
    exit 1
fi

# Check Flutter
if command -v flutter &> /dev/null; then
    print_success "Flutter is installed"
    FLUTTER_VERSION=$(flutter --version | head -n 1)
    echo "  $FLUTTER_VERSION"
else
    print_warning "Flutter is not installed (needed for frontend)"
    echo "  You can still test the backend API"
    echo "  Install Flutter from: https://docs.flutter.dev/get-started/install"
    SKIP_FRONTEND=true
fi

echo ""
echo "=============================================="
echo ""

# Start backend services
print_info "Starting backend services with Docker..."
echo ""

# Stop any existing containers
docker-compose down 2>/dev/null || true

# Start services
print_info "Starting PostgreSQL, Redis, Backend, Celery..."
docker-compose up -d

echo ""
print_info "Waiting for services to be ready (15 seconds)..."
sleep 15

# Check if services are running
echo ""
print_info "Checking service status..."
if docker-compose ps | grep -q "Up"; then
    print_success "Backend services are running"
    docker-compose ps
else
    print_error "Some services failed to start"
    docker-compose ps
    echo ""
    print_info "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "=============================================="
echo ""

# Apply migrations
print_info "Applying database migrations..."
docker-compose exec -T backend alembic upgrade head

if [ $? -eq 0 ]; then
    print_success "Database migrations applied"
else
    print_error "Migration failed"
    echo ""
    print_info "Try running manually: docker-compose exec backend alembic upgrade head"
    exit 1
fi

echo ""
echo "=============================================="
echo ""

# Test backend
print_info "Testing backend API..."
sleep 2

HEALTH_RESPONSE=$(curl -s http://localhost:8000/health || echo "failed")

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_success "Backend API is responding"
    echo "  Response: $HEALTH_RESPONSE"
else
    print_warning "Backend API is not responding yet"
    echo "  Waiting 5 more seconds..."
    sleep 5
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health || echo "failed")
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        print_success "Backend API is now responding"
    else
        print_error "Backend API is not responding"
        echo "  Check logs with: docker-compose logs backend"
    fi
fi

echo ""
echo "=============================================="
echo ""

# Start frontend if Flutter is available
if [ "$SKIP_FRONTEND" != true ]; then
    print_info "Starting Flutter frontend..."
    echo ""
    
    cd frontend
    
    # Check if dependencies are installed
    if [ ! -d ".dart_tool" ]; then
        print_info "Installing Flutter dependencies (first time)..."
        flutter pub get
    fi
    
    print_info "Building and starting Flutter web app..."
    print_info "This may take 1-2 minutes on first run..."
    echo ""
    
    # Start Flutter in background
    flutter run -d chrome --web-port 8080 &
    FLUTTER_PID=$!
    
    cd ..
    
    echo ""
    print_success "Frontend is starting..."
    print_info "Flutter PID: $FLUTTER_PID"
else
    print_info "Skipping frontend (Flutter not installed)"
fi

echo ""
echo "=============================================="
echo ""
echo "🎉 Platform is ready for testing!"
echo ""
echo "📝 Access URLs:"
echo "  • Frontend:       http://localhost:8080"
echo "  • Backend API:    http://localhost:8000"
echo "  • API Docs:       http://localhost:8000/docs"
echo "  • Health Check:   http://localhost:8000/health"
echo ""
echo "📚 Test the platform:"
echo "  1. Open http://localhost:8080 in your browser"
echo "  2. Register a new user (click 'Регистрация')"
echo "  3. Go to Calculator and create an estimate"
echo "  4. Create an order from the estimate"
echo "  5. Test the payment flow (simulation)"
echo ""
echo "🛠️  Useful commands:"
echo "  • View logs:      docker-compose logs -f"
echo "  • Stop services:  docker-compose down"
echo "  • Restart:        docker-compose restart"
echo ""
echo "📖 For detailed testing guide, see: LOCAL_TESTING_GUIDE.md"
echo ""
echo "=============================================="
echo ""

# Keep script running if frontend was started
if [ "$SKIP_FRONTEND" != true ]; then
    print_info "Press Ctrl+C to stop all services"
    echo ""
    
    # Wait for Flutter process
    wait $FLUTTER_PID 2>/dev/null || true
    
    print_info "Flutter stopped. Stopping backend services..."
    docker-compose down
    
    print_success "All services stopped"
fi
