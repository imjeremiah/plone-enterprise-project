#!/bin/bash
set -euo pipefail

# Production Entrypoint for Classroom Management Backend
# Handles database initialization, health checks, and graceful startup

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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
PLONE_SITE_ID=${PLONE_SITE_ID:-Plone}
DB_HOST=${DB_HOST:-postgres}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-classroom_db}
DB_USER=${DB_USER:-classroom_user}
DB_PASSWORD=${DB_PASSWORD:-}
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}

# Wait for database to be ready
wait_for_db() {
    log "Waiting for PostgreSQL database at ${DB_HOST}:${DB_PORT}..."
    
    local retries=30
    while [ $retries -gt 0 ]; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
            log_success "Database is ready!"
            return 0
        fi
        
        log "Database not ready, waiting... ($retries retries left)"
        sleep 2
        retries=$((retries - 1))
    done
    
    log_error "Database connection timeout after 60 seconds"
    exit 1
}

# Wait for Redis (if configured)
wait_for_redis() {
    if [ -n "${REDIS_HOST:-}" ]; then
        log "Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}..."
        
        local retries=15
        while [ $retries -gt 0 ]; do
            if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
                log_success "Redis is ready!"
                return 0
            fi
            
            log "Redis not ready, waiting... ($retries retries left)"
            sleep 2
            retries=$((retries - 1))
        done
        
        log_warning "Redis connection timeout - continuing without Redis"
    fi
}

# Initialize Plone site if it doesn't exist
initialize_plone_site() {
    log "Checking if Plone site '${PLONE_SITE_ID}' exists..."
    
    # Start Zope in background for initialization
    python bin/instance start
    
    # Wait for Zope to start
    local retries=30
    while [ $retries -gt 0 ]; do
        if curl -s -f "http://localhost:8080/Control_Panel" >/dev/null 2>&1; then
            log_success "Zope is running"
            break
        fi
        sleep 2
        retries=$((retries - 1))
    done
    
    if [ $retries -eq 0 ]; then
        log_error "Zope failed to start for initialization"
        python bin/instance stop
        exit 1
    fi
    
    # Check if site exists
    if curl -s -f "http://localhost:8080/${PLONE_SITE_ID}" >/dev/null 2>&1; then
        log_success "Plone site '${PLONE_SITE_ID}' already exists"
    else
        log "Creating Plone site '${PLONE_SITE_ID}'..."
        
        # Create the site using the installation script
        python -c "
import sys
sys.path.insert(0, '/app/scripts')
from create_classroom_site import create_site_with_classroom_features
create_site_with_classroom_features('${PLONE_SITE_ID}')
" || {
            log_error "Failed to create Plone site"
            python bin/instance stop
            exit 1
        }
        
        log_success "Plone site '${PLONE_SITE_ID}' created successfully"
    fi
    
    # Stop background Zope
    python bin/instance stop
    
    # Wait for clean shutdown
    sleep 5
}

# Set up logging directories
setup_logging() {
    log "Setting up logging directories..."
    
    mkdir -p /var/log/classroom
    mkdir -p instance/var/log
    
    # Ensure proper permissions
    chown -R appuser:appuser /var/log/classroom instance/var/log
    
    log_success "Logging directories configured"
}

# Validate environment variables
validate_environment() {
    log "Validating environment configuration..."
    
    # Required variables
    local required_vars=("DB_HOST" "DB_NAME" "DB_USER")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Warning for missing optional variables
    if [ -z "${DB_PASSWORD:-}" ]; then
        log_warning "DB_PASSWORD not set - using password-less authentication"
    fi
    
    log_success "Environment validation passed"
}

# Set up database connection string
setup_database_config() {
    log "Configuring database connection..."
    
    local db_dsn
    if [ -n "${DB_PASSWORD:-}" ]; then
        db_dsn="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    else
        db_dsn="postgresql://${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    fi
    
    export RELSTORAGE_DSN="$db_dsn"
    
    log_success "Database configuration complete"
}

# Security setup
setup_security() {
    log "Applying security configuration..."
    
    # Set secure file permissions
    chmod 600 instance/etc/zope.conf
    
    # Configure security headers
    export SECURITY_HEADERS_ENABLED=true
    export CORS_ORIGINS="${CORS_ORIGINS:-https://classroom.yourdomain.com}"
    
    log_success "Security configuration applied"
}

# Performance tuning
setup_performance() {
    log "Applying performance optimizations..."
    
    # Set Zope thread configuration based on available resources
    local cpu_cores
    cpu_cores=$(nproc)
    
    if [ "$cpu_cores" -gt 4 ]; then
        export ZOPE_THREADS=8
    elif [ "$cpu_cores" -gt 2 ]; then
        export ZOPE_THREADS=4
    else
        export ZOPE_THREADS=2
    fi
    
    log "Configured for ${ZOPE_THREADS} threads on ${cpu_cores} CPU cores"
    
    # Set memory limits
    export PYTHON_EGG_CACHE=/var/cache/classroom
    
    log_success "Performance optimizations applied"
}

# Health check function
health_check() {
    local url="http://localhost:8080/${PLONE_SITE_ID}/@@security-middleware"
    
    if curl -s -f "$url" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Signal handlers for graceful shutdown
shutdown() {
    log "Received shutdown signal, stopping gracefully..."
    
    if [ -n "${ZOPE_PID:-}" ] && kill -0 "$ZOPE_PID" 2>/dev/null; then
        log "Stopping Zope process (PID: $ZOPE_PID)..."
        kill -TERM "$ZOPE_PID"
        
        # Wait for graceful shutdown
        local timeout=30
        while [ $timeout -gt 0 ] && kill -0 "$ZOPE_PID" 2>/dev/null; do
            sleep 1
            timeout=$((timeout - 1))
        done
        
        # Force kill if necessary
        if kill -0 "$ZOPE_PID" 2>/dev/null; then
            log_warning "Forcing Zope shutdown..."
            kill -KILL "$ZOPE_PID"
        fi
    fi
    
    log_success "Shutdown complete"
    exit 0
}

# Set up signal handlers
trap shutdown TERM INT

# Main execution
main() {
    log "🚀 Starting Classroom Management Backend (Production)"
    log "Version: 1.0.0"
    log "Environment: ${ENVIRONMENT:-production}"
    
    # Initialization steps
    validate_environment
    setup_logging
    setup_database_config
    setup_security
    setup_performance
    
    # Wait for external services
    wait_for_db
    wait_for_redis
    
    # Initialize Plone if needed
    if [ "${1:-}" = "instance" ] && [ "${2:-}" = "fg" ]; then
        initialize_plone_site
    fi
    
    log_success "Backend initialization complete"
    
    # Execute the main command
    log "Starting Zope with command: $*"
    
    if [ "${1:-}" = "instance" ] && [ "${2:-}" = "fg" ]; then
        # Run in foreground with PID tracking
        exec python bin/instance fg &
        ZOPE_PID=$!
        wait $ZOPE_PID
    else
        # Execute other commands directly
        exec "$@"
    fi
}

# Run main function with all arguments
main "$@" 