#!/bin/sh
set -eu

# Production Entrypoint for Classroom Management Frontend
# Handles environment configuration, health checks, and startup

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Configuration defaults
BACKEND_HOST=${BACKEND_HOST:-backend}
BACKEND_PORT=${BACKEND_PORT:-8080}
FRONTEND_PORT=${PORT:-3000}
API_PATH=${API_PATH:-/Plone}
INTERNAL_API_PATH=${INTERNAL_API_PATH:-http://backend:8080/Plone}
PUBLIC_URL=${PUBLIC_URL:-http://localhost:3000}

# Wait for backend to be ready
wait_for_backend() {
    log "Waiting for backend at ${BACKEND_HOST}:${BACKEND_PORT}..."
    
    local retries=60  # 2 minutes with 2-second intervals
    while [ $retries -gt 0 ]; do
        if nc -z "$BACKEND_HOST" "$BACKEND_PORT" >/dev/null 2>&1; then
            log_success "Backend is ready!"
            return 0
        fi
        
        log "Backend not ready, waiting... ($retries retries left)"
        sleep 2
        retries=$((retries - 1))
    done
    
    log_warning "Backend connection timeout - starting frontend anyway"
    return 0  # Don't fail, frontend can start without backend initially
}

# Test backend API connectivity
test_backend_api() {
    log "Testing backend API connectivity..."
    
    local api_url="http://${BACKEND_HOST}:${BACKEND_PORT}${API_PATH}"
    
    if curl -s -f "${api_url}/@@plone_site" >/dev/null 2>&1; then
        log_success "Backend API is accessible"
        return 0
    else
        log_warning "Backend API not yet accessible - frontend will retry automatically"
        return 0  # Don't fail startup
    fi
}

# Configure environment for production
configure_environment() {
    log "Configuring production environment..."
    
    # Set API paths based on environment
    export RAZZLE_API_PATH="http://${BACKEND_HOST}:${BACKEND_PORT}${API_PATH}"
    export RAZZLE_INTERNAL_API_PATH="$INTERNAL_API_PATH"
    
    # Production optimizations
    export NODE_ENV=production
    export RAZZLE_DISABLE_SSR_CACHE=true
    
    # Security settings
    export RAZZLE_DISABLE_SSR_ON_ERROR=true
    export RAZZLE_SENTRY_DSN="${SENTRY_DSN:-}"
    
    # Performance settings
    export UV_THREADPOOL_SIZE=128
    export NODE_OPTIONS="--max-old-space-size=2048"
    
    log_success "Environment configured"
    log "  API Path: $RAZZLE_API_PATH"
    log "  Internal API: $RAZZLE_INTERNAL_API_PATH"
    log "  Public URL: $PUBLIC_URL"
}

# Validate build artifacts
validate_build() {
    log "Validating build artifacts..."
    
    # Check if build directory exists and has content
    if [ ! -d "/app/build" ]; then
        log_error "Build directory not found"
        exit 1
    fi
    
    if [ ! -f "/app/build/server.js" ]; then
        log_error "Server build not found"
        exit 1
    fi
    
    if [ ! -d "/app/build/public" ]; then
        log_error "Client build not found"
        exit 1
    fi
    
    log_success "Build artifacts validated"
}

# Set up logging
setup_logging() {
    log "Setting up logging..."
    
    # Create log directories
    mkdir -p /var/log/volto
    
    # Configure log rotation (basic)
    export LOG_LEVEL="${LOG_LEVEL:-info}"
    
    log_success "Logging configured"
}

# Performance monitoring setup
setup_monitoring() {
    log "Setting up performance monitoring..."
    
    # Enable performance monitoring if configured
    if [ -n "${ENABLE_PERFORMANCE_MONITORING:-}" ]; then
        export RAZZLE_PERFORMANCE_MONITORING=true
        log "Performance monitoring enabled"
    fi
    
    # Configure error tracking
    if [ -n "${SENTRY_DSN:-}" ]; then
        export RAZZLE_SENTRY_DSN="$SENTRY_DSN"
        log "Error tracking configured"
    fi
    
    log_success "Monitoring setup complete"
}

# Security headers configuration
setup_security() {
    log "Applying security configuration..."
    
    # Security environment variables
    export RAZZLE_SECURITY_HEADERS=true
    export RAZZLE_CSP_ENABLED=true
    
    # HTTPS enforcement in production
    if [ "${ENVIRONMENT:-}" = "production" ]; then
        export RAZZLE_FORCE_HTTPS=true
        export RAZZLE_SECURE_COOKIES=true
    fi
    
    log_success "Security configuration applied"
}

# Health check function
health_check() {
    local health_url="http://localhost:${FRONTEND_PORT}/"
    
    if curl -s -f "$health_url" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Signal handlers for graceful shutdown
shutdown() {
    log "Received shutdown signal, stopping gracefully..."
    
    if [ -n "${VOLTO_PID:-}" ] && kill -0 "$VOLTO_PID" 2>/dev/null; then
        log "Stopping Volto process (PID: $VOLTO_PID)..."
        kill -TERM "$VOLTO_PID"
        
        # Wait for graceful shutdown
        local timeout=30
        while [ $timeout -gt 0 ] && kill -0 "$VOLTO_PID" 2>/dev/null; do
            sleep 1
            timeout=$((timeout - 1))
        done
        
        # Force kill if necessary
        if kill -0 "$VOLTO_PID" 2>/dev/null; then
            log_warning "Forcing Volto shutdown..."
            kill -KILL "$VOLTO_PID"
        fi
    fi
    
    log_success "Shutdown complete"
    exit 0
}

# Set up signal handlers
trap shutdown TERM INT

# Pre-flight checks
preflight_checks() {
    log "Running pre-flight checks..."
    
    # Check Node.js version
    local node_version
    node_version=$(node --version)
    log "Node.js version: $node_version"
    
    # Check available memory
    local memory_info
    if command -v free >/dev/null 2>&1; then
        memory_info=$(free -h | grep '^Mem:' | awk '{print $2}')
        log "Available memory: $memory_info"
    fi
    
    # Check disk space
    local disk_space
    disk_space=$(df -h /app | tail -1 | awk '{print $4}')
    log "Available disk space: $disk_space"
    
    log_success "Pre-flight checks complete"
}

# Main execution
main() {
    log "🚀 Starting Classroom Management Frontend (Production)"
    log "Version: 1.0.0"
    log "Environment: ${ENVIRONMENT:-production}"
    
    # Initialization steps
    preflight_checks
    validate_build
    setup_logging
    setup_monitoring
    setup_security
    configure_environment
    
    # Wait for dependencies
    wait_for_backend
    test_backend_api
    
    log_success "Frontend initialization complete"
    
    # Start the application
    log "Starting Volto server on port ${FRONTEND_PORT}..."
    
    cd /app
    
    # Start Volto in production mode
    if [ -n "${DEBUG:-}" ]; then
        log "Debug mode enabled"
        exec node build/server.js &
    else
        exec node build/server.js &
    fi
    
    VOLTO_PID=$!
    log_success "Volto started with PID: $VOLTO_PID"
    
    # Wait for the process
    wait $VOLTO_PID
}

# Health check mode
if [ "${1:-}" = "health" ]; then
    if health_check; then
        echo "Frontend is healthy"
        exit 0
    else
        echo "Frontend health check failed"
        exit 1
    fi
fi

# Run main function with all arguments
main "$@" 