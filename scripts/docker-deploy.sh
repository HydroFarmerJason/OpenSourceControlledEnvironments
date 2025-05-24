#!/bin/bash
# Docker deployment script

set -euo pipefail

# Clone the repository
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check environment file
    if [[ ! -f "$ENV_FILE" ]]; then
        warning "Environment file not found. Creating from template..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            log "Created .env file. Please update it with your configuration."
            exit 0
        else
            error ".env.example not found. Cannot create environment file."
        fi
    fi
    
    log "Prerequisites check passed."
}

# Build images
build_images() {
    log "Building Docker images..."
    docker-compose build --no-cache
    log "Images built successfully."
}

# Start services
start_services() {
    log "Starting services..."
    docker-compose up -d
    log "Services started."
}

# Check service health
check_health() {
    log "Checking service health..."
    sleep 10  # Give services time to start
    
    # Check each service
    services=("farm-api" "farm-worker" "postgres" "redis")
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            log " $service is running"
        else
            error "$service is not running properly"
        fi
    done
    
    # Check API endpoint
    if curl -f -s http://localhost:5000/health > /dev/null; then
        log " API is responding"
    else
        warning "API health check failed"
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    docker-compose exec farm-api alembic upgrade head
    log "Migrations completed."
}

# Main deployment process
main() {
    log "Starting OpenSource Controlled Environments deployment..."
    
    check_prerequisites
    
    case "${1:-deploy}" in
        build)
            build_images
            ;;
        start)
            start_services
            check_health
            ;;
        stop)
            log "Stopping services..."
            docker-compose down
            log "Services stopped."
            ;;
        restart)
            log "Restarting services..."
            docker-compose restart
            check_health
            ;;
        logs)
            docker-compose logs -f "${2:-}"
            ;;
        deploy)
            build_images
            start_services
            run_migrations
            check_health
            log "Deployment completed successfully!"
            log "Access the application at: http://localhost:5000"
            log "Access Grafana at: http://localhost:3000 (admin/admin)"
            ;;
        *)
            echo "Usage: $0 {build|start|stop|restart|logs|deploy}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
