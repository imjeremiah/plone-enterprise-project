"""
Production Security Configuration

Environment-specific security settings for production deployment.
This file should be customized based on your production environment
and security requirements.
"""

import os
from typing import Dict, List, Any


def get_production_security_config() -> Dict[str, Any]:
    """
    Get production security configuration based on environment variables
    
    Returns:
        Dictionary with security configuration
    """
    
    # Base production configuration
    config = {
        # CORS Origins - CRITICAL: Update these for your production domains
        'cors_origins': [
            os.getenv('FRONTEND_URL', 'https://classroom.yourdomain.com'),
            os.getenv('BACKEND_URL', 'https://api.yourdomain.com'),
            # Add additional allowed origins as needed
        ],
        
        # Rate Limiting Configuration
        'rate_limits': {
            'api_random_picker': int(os.getenv('RATE_LIMIT_PICKER', '30')),      # 30 picks per hour
            'hall_pass_create': int(os.getenv('RATE_LIMIT_HALL_PASS', '20')),   # 20 passes per hour
            'login_attempts': int(os.getenv('RATE_LIMIT_LOGIN', '5')),           # 5 login attempts per hour
            'api_general': int(os.getenv('RATE_LIMIT_GENERAL', '100')),          # 100 API calls per hour
            'dashboard_refresh': int(os.getenv('RATE_LIMIT_DASHBOARD', '200')),  # 200 dashboard updates per hour
        },
        
        # Session Configuration
        'session_timeout': int(os.getenv('SESSION_TIMEOUT', '3600')),  # 1 hour default
        'session_secure': os.getenv('SESSION_SECURE', 'true').lower() == 'true',
        'session_httponly': True,
        'session_samesite': 'Lax',
        
        # Audit and Logging
        'audit_retention_days': int(os.getenv('AUDIT_RETENTION_DAYS', '365')),  # 1 year
        'audit_log_level': os.getenv('AUDIT_LOG_LEVEL', 'INFO'),
        'security_log_path': os.getenv('SECURITY_LOG_PATH', '/var/log/classroom/security.log'),
        
        # Content Security Policy
        'csp_strict_mode': os.getenv('CSP_STRICT_MODE', 'false').lower() == 'true',
        'csp_report_uri': os.getenv('CSP_REPORT_URI', '/security/csp-report'),
        
        # Additional Security Headers
        'security_headers': {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': f"max-age={os.getenv('HSTS_MAX_AGE', '31536000')}; includeSubDomains",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        },
        
        # Data Protection (FERPA Compliance)
        'ferpa_compliance': {
            'enabled': True,
            'anonymize_exports': True,
            'pii_detection_enabled': True,
            'audit_data_access': True,
            'data_retention_days': int(os.getenv('DATA_RETENTION_DAYS', '2555')),  # 7 years for educational records
        },
        
        # File Upload Security
        'file_upload': {
            'max_file_size': int(os.getenv('MAX_FILE_SIZE', '10485760')),  # 10MB default
            'allowed_extensions': ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'],
            'virus_scanning_enabled': os.getenv('VIRUS_SCANNING', 'false').lower() == 'true',
        },
        
        # API Security
        'api_security': {
            'require_api_key': os.getenv('REQUIRE_API_KEY', 'false').lower() == 'true',
            'api_key_header': 'X-API-Key',
            'jwt_secret_key': os.getenv('JWT_SECRET_KEY', ''),
            'jwt_expiration_hours': int(os.getenv('JWT_EXPIRATION_HOURS', '24')),
        },
        
        # Monitoring and Alerting
        'monitoring': {
            'security_alerts_enabled': True,
            'alert_email': os.getenv('SECURITY_ALERT_EMAIL', 'admin@yourdomain.com'),
            'failed_login_threshold': int(os.getenv('FAILED_LOGIN_THRESHOLD', '5')),
            'suspicious_activity_threshold': int(os.getenv('SUSPICIOUS_ACTIVITY_THRESHOLD', '10')),
        },
        
        # Backup and Recovery
        'backup': {
            'encrypt_backups': True,
            'backup_retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '90')),
            'offsite_backup_enabled': os.getenv('OFFSITE_BACKUP', 'false').lower() == 'true',
        }
    }
    
    # Environment-specific overrides
    environment = os.getenv('ENVIRONMENT', 'production').lower()
    
    if environment == 'development':
        config.update(_get_development_overrides())
    elif environment == 'staging':
        config.update(_get_staging_overrides())
    elif environment == 'production':
        config.update(_get_production_overrides())
    
    return config


def _get_development_overrides() -> Dict[str, Any]:
    """Development environment security overrides"""
    return {
        'cors_origins': [
            'http://localhost:3000',
            'http://localhost:8080',
            'http://project-title.localhost',
            'https://project-title.localhost',
        ],
        'session_secure': False,  # Allow HTTP in development
        'rate_limits': {
            'api_random_picker': 100,  # More lenient for development
            'hall_pass_create': 50,
            'login_attempts': 20,
            'api_general': 500,
            'dashboard_refresh': 1000,
        },
        'csp_strict_mode': False,  # Relaxed CSP for development
    }


def _get_staging_overrides() -> Dict[str, Any]:
    """Staging environment security overrides"""
    return {
        'cors_origins': [
            'https://staging-classroom.yourdomain.com',
            'https://staging-api.yourdomain.com',
        ],
        'rate_limits': {
            'api_random_picker': 50,  # Moderate limits for staging
            'hall_pass_create': 30,
            'login_attempts': 10,
            'api_general': 200,
            'dashboard_refresh': 500,
        },
        'audit_retention_days': 30,  # Shorter retention for staging
    }


def _get_production_overrides() -> Dict[str, Any]:
    """Production environment security overrides"""
    return {
        # Strict production settings
        'session_secure': True,
        'csp_strict_mode': True,
        'ferpa_compliance': {
            'enabled': True,
            'anonymize_exports': True,
            'pii_detection_enabled': True,
            'audit_data_access': True,
            'data_retention_days': 2555,  # 7 years
        },
        'monitoring': {
            'security_alerts_enabled': True,
            'alert_email': os.getenv('SECURITY_ALERT_EMAIL', 'security@yourdomain.com'),
            'failed_login_threshold': 3,  # Stricter in production
            'suspicious_activity_threshold': 5,
        }
    }


def validate_security_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate security configuration and return list of warnings/errors
    
    Args:
        config: Security configuration to validate
        
    Returns:
        List of validation messages
    """
    warnings = []
    
    # Check CORS origins
    cors_origins = config.get('cors_origins', [])
    if not cors_origins:
        warnings.append("CRITICAL: No CORS origins configured")
    elif any('localhost' in origin for origin in cors_origins):
        warnings.append("WARNING: localhost origins found in production config")
    
    # Check session security
    if not config.get('session_secure', False):
        warnings.append("WARNING: Session cookies not marked as secure")
    
    # Check HTTPS enforcement
    if config.get('environment') == 'production':
        if not any('https://' in origin for origin in cors_origins):
            warnings.append("CRITICAL: No HTTPS origins in production")
    
    # Check API security
    api_security = config.get('api_security', {})
    if api_security.get('require_api_key') and not api_security.get('jwt_secret_key'):
        warnings.append("CRITICAL: API key required but JWT secret not configured")
    
    # Check monitoring
    monitoring = config.get('monitoring', {})
    if not monitoring.get('alert_email'):
        warnings.append("WARNING: No security alert email configured")
    
    # Check audit retention
    audit_retention = config.get('audit_retention_days', 0)
    if audit_retention < 365:
        warnings.append("WARNING: Audit retention less than 1 year may not meet compliance requirements")
    
    return warnings


def get_security_config_summary() -> Dict[str, Any]:
    """Get summary of current security configuration for monitoring"""
    config = get_production_security_config()
    
    return {
        'environment': os.getenv('ENVIRONMENT', 'unknown'),
        'cors_origins_count': len(config.get('cors_origins', [])),
        'rate_limits_configured': len(config.get('rate_limits', {})),
        'session_secure': config.get('session_secure', False),
        'ferpa_enabled': config.get('ferpa_compliance', {}).get('enabled', False),
        'audit_retention_days': config.get('audit_retention_days', 0),
        'security_headers_count': len(config.get('security_headers', {})),
        'monitoring_enabled': config.get('monitoring', {}).get('security_alerts_enabled', False),
        'last_updated': os.getenv('CONFIG_LAST_UPDATED', 'unknown'),
    }


# Export the configuration function for use in security module
__all__ = ['get_production_security_config', 'validate_security_config', 'get_security_config_summary'] 