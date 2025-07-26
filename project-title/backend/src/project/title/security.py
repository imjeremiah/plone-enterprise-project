"""
Security and Privacy Protection Module

Provides FERPA-compliant data handling, security utilities, and privacy protection
for the K-12 Classroom Management Platform. Ensures student data protection
and implements security best practices.
"""

import hashlib
import secrets
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse

from plone import api
from zope.annotation.interfaces import IAnnotations

logger = logging.getLogger(__name__)

# FERPA-compliant data classification
PII_FIELDS = {
    'direct_identifiers': [
        'student_name', 'full_name', 'first_name', 'last_name',
        'student_id', 'social_security', 'email', 'phone',
        'address', 'parent_name', 'guardian_name'
    ],
    'quasi_identifiers': [
        'birth_date', 'grade_level', 'classroom_number',
        'teacher_name', 'school_name'
    ],
    'sensitive_educational': [
        'special_needs', 'disciplinary_records', 'grades',
        'test_scores', 'iep_status', 'medical_info'
    ]
}

# Security headers for production deployment
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
}

# Content Security Policy for inline JS protection
CSP_POLICY = {
    'default-src': "'self'",
    'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",  # Volto requires unsafe-inline/eval
    'style-src': "'self' 'unsafe-inline'",
    'img-src': "'self' data: blob:",
    'font-src': "'self' data:",
    'connect-src': "'self'",
    'media-src': "'self'",
    'object-src': "'none'",
    'frame-src': "'none'",
    'worker-src': "'self'",
    'form-action': "'self'",
    'base-uri': "'self'",
    'upgrade-insecure-requests': '',
}


def anonymize_student_data(data: Dict[str, Any], 
                          preserve_educational_value: bool = True) -> Dict[str, Any]:
    """
    Remove PII from student data for FERPA compliance
    
    Args:
        data: Dictionary containing student data
        preserve_educational_value: Keep aggregated/statistical data
        
    Returns:
        Anonymized data dictionary safe for export/logging
    """
    if not isinstance(data, dict):
        return {}
    
    anonymized = {}
    
    for key, value in data.items():
        key_lower = key.lower()
        
        # Remove direct identifiers completely
        if any(identifier in key_lower for identifier in PII_FIELDS['direct_identifiers']):
            if 'name' in key_lower and preserve_educational_value:
                # Replace with pseudonym for tracking purposes
                anonymized[key] = generate_pseudonym(str(value))
            # Otherwise, skip the field entirely
            continue
            
        # Handle quasi-identifiers with care
        elif any(quasi in key_lower for quasi in PII_FIELDS['quasi_identifiers']):
            if preserve_educational_value:
                if 'grade' in key_lower:
                    # Keep grade level for educational analysis
                    anonymized[key] = value
                elif 'date' in key_lower:
                    # Generalize dates to month/year only
                    anonymized[key] = generalize_date(value)
                else:
                    # Hash other quasi-identifiers
                    anonymized[key] = hash_sensitive_data(str(value))
            continue
            
        # Remove sensitive educational records
        elif any(sensitive in key_lower for sensitive in PII_FIELDS['sensitive_educational']):
            # These should never be in exported data
            continue
            
        # Handle nested dictionaries and lists recursively
        elif isinstance(value, dict):
            nested_anonymized = anonymize_student_data(value, preserve_educational_value)
            if nested_anonymized:  # Only include if not empty
                anonymized[key] = nested_anonymized
                
        elif isinstance(value, list):
            anonymized_list = []
            for item in value:
                if isinstance(item, dict):
                    anonymized_item = anonymize_student_data(item, preserve_educational_value)
                    if anonymized_item:
                        anonymized_list.append(anonymized_item)
                elif not contains_pii(str(item)):
                    anonymized_list.append(item)
            if anonymized_list:
                anonymized[key] = anonymized_list
                
        # Include safe data as-is
        elif not contains_pii(str(value)):
            anonymized[key] = value
    
    return anonymized


def generate_pseudonym(original_name: str) -> str:
    """
    Generate consistent pseudonym for tracking while maintaining anonymity
    
    Args:
        original_name: Original student name
        
    Returns:
        Consistent pseudonym (e.g., "Student_A47B")
    """
    # Use first 4 characters of SHA-256 hash for consistency
    hash_value = hashlib.sha256(original_name.encode()).hexdigest()[:4].upper()
    return f"Student_{hash_value}"


def hash_sensitive_data(data: str) -> str:
    """
    Create one-way hash of sensitive data for tracking purposes
    
    Args:
        data: Sensitive data to hash
        
    Returns:
        SHA-256 hash (first 8 characters for readability)
    """
    return hashlib.sha256(data.encode()).hexdigest()[:8]


def generalize_date(date_value: Union[str, datetime]) -> str:
    """
    Generalize date to month/year for privacy protection
    
    Args:
        date_value: Date string or datetime object
        
    Returns:
        Generalized date string (YYYY-MM format)
    """
    try:
        if isinstance(date_value, str):
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    date_obj = datetime.strptime(date_value, fmt)
                    break
                except ValueError:
                    continue
            else:
                return "UNKNOWN"
        elif isinstance(date_value, datetime):
            date_obj = date_value
        else:
            return "UNKNOWN"
            
        return date_obj.strftime('%Y-%m')
    except Exception:
        return "UNKNOWN"


def contains_pii(text: str) -> bool:
    """
    Check if text contains potential PII using pattern matching
    
    Args:
        text: Text to analyze
        
    Returns:
        True if potential PII detected
    """
    if not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    # Check for common PII patterns
    patterns = [
        r'\b\d{3}-?\d{2}-?\d{4}\b',  # SSN pattern
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone number
        r'\b\d{1,5}\s[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr)\b',  # Address
    ]
    
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    
    # Check for direct identifier keywords
    for identifier in PII_FIELDS['direct_identifiers']:
        if identifier.replace('_', ' ') in text_lower:
            return True
    
    return False


def secure_qr_data(hall_pass_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure QR code data contains no PII for FERPA compliance
    
    Args:
        hall_pass_data: Hall pass data for QR code
        
    Returns:
        Secure data safe for QR code generation
    """
    # Only include essential, non-PII data in QR codes
    secure_data = {
        'pass_id': hall_pass_data.get('id', ''),
        'issue_time': hall_pass_data.get('issue_time', ''),
        'destination': hall_pass_data.get('destination', ''),
        'duration': hall_pass_data.get('duration', 10),
        'teacher_code': hash_sensitive_data(hall_pass_data.get('teacher', 'unknown')),
        'verification': generate_verification_code(hall_pass_data)
    }
    
    # Remove any potential PII
    return anonymize_student_data(secure_data, preserve_educational_value=False)


def generate_verification_code(data: Dict[str, Any]) -> str:
    """
    Generate verification code for hall pass authenticity
    
    Args:
        data: Hall pass data
        
    Returns:
        6-character verification code
    """
    # Create hash from non-PII data for verification
    verification_string = f"{data.get('id', '')}{data.get('issue_time', '')}"
    hash_value = hashlib.sha256(verification_string.encode()).hexdigest()
    return hash_value[:6].upper()


def validate_cors_origin(origin: str, allowed_origins: List[str]) -> bool:
    """
    Validate CORS origin against whitelist
    
    Args:
        origin: Origin to validate
        allowed_origins: List of allowed origins
        
    Returns:
        True if origin is allowed
    """
    if not origin:
        return False
    
    try:
        parsed = urlparse(origin)
        
        # Check exact matches first
        if origin in allowed_origins:
            return True
        
        # Check domain patterns
        for allowed in allowed_origins:
            if allowed.startswith('*.'):
                # Wildcard subdomain matching
                domain = allowed[2:]
                if parsed.netloc.endswith(domain):
                    return True
            elif allowed.startswith('http'):
                # Exact URL matching
                if origin == allowed:
                    return True
        
        return False
        
    except Exception as e:
        logger.warning(f"CORS origin validation error: {e}")
        return False


def generate_csrf_token() -> str:
    """Generate secure CSRF token"""
    return secrets.token_urlsafe(32)


def validate_csrf_token(token: str, session_token: str) -> bool:
    """Validate CSRF token against session"""
    return secrets.compare_digest(token, session_token)


def audit_log_hall_pass(action: str, hall_pass_id: str, 
                       user_id: str, details: Dict[str, Any] = None):
    """
    Create audit log entry for hall pass operations
    
    Args:
        action: Action performed (issued, returned, overdue, etc.)
        hall_pass_id: Hall pass identifier
        user_id: User performing action
        details: Additional non-PII details
    """
    try:
        portal = api.portal.get()
        annotations = IAnnotations(portal, {})
        
        # Get or create audit log
        audit_log = annotations.get('security_audit_log', [])
        
        # Create sanitized log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'hall_pass_id': hall_pass_id,
            'user_id': hash_sensitive_data(user_id),  # Hash user ID for privacy
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent_summary(),
            'details': anonymize_student_data(details or {}, preserve_educational_value=False)
        }
        
        audit_log.append(log_entry)
        
        # Keep only last 1000 entries to prevent unbounded growth
        if len(audit_log) > 1000:
            audit_log = audit_log[-1000:]
        
        annotations['security_audit_log'] = audit_log
        
        # Also log to Python logger for external monitoring
        logger.info(f"AUDIT: {action} for pass {hall_pass_id} by user {hash_sensitive_data(user_id)}")
        
    except Exception as e:
        logger.error(f"Audit logging failed: {e}")


def get_client_ip() -> str:
    """Get client IP address from request"""
    try:
        request = api.env.getRequest()
        # Check for forwarded headers (load balancer/proxy)
        forwarded_for = request.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded_for:
            # Get first IP from chain
            return forwarded_for.split(',')[0].strip()
        
        forwarded = request.get('HTTP_X_FORWARDED', '')
        if forwarded:
            return forwarded.strip()
        
        real_ip = request.get('HTTP_X_REAL_IP', '')
        if real_ip:
            return real_ip.strip()
        
        # Fallback to remote address
        return request.get('REMOTE_ADDR', 'unknown')
        
    except Exception:
        return 'unknown'


def get_user_agent_summary() -> str:
    """Get summarized user agent for logging"""
    try:
        request = api.env.getRequest()
        user_agent = request.get('HTTP_USER_AGENT', '')
        
        # Extract browser/OS summary to avoid full UA string logging
        if 'Chrome' in user_agent:
            browser = 'Chrome'
        elif 'Firefox' in user_agent:
            browser = 'Firefox'
        elif 'Safari' in user_agent:
            browser = 'Safari'
        elif 'Edge' in user_agent:
            browser = 'Edge'
        else:
            browser = 'Other'
        
        if 'Windows' in user_agent:
            os = 'Windows'
        elif 'Mac' in user_agent:
            os = 'Mac'
        elif 'Linux' in user_agent:
            os = 'Linux'
        elif 'iOS' in user_agent:
            os = 'iOS'
        elif 'Android' in user_agent:
            os = 'Android'
        else:
            os = 'Other'
        
        return f"{browser}/{os}"
        
    except Exception:
        return 'unknown'


def get_security_headers() -> Dict[str, str]:
    """Get security headers for HTTP responses"""
    return SECURITY_HEADERS.copy()


def get_csp_header() -> str:
    """Generate Content Security Policy header"""
    csp_directives = []
    for directive, sources in CSP_POLICY.items():
        if sources:
            csp_directives.append(f"{directive} {sources}")
        else:
            csp_directives.append(directive)
    
    return "; ".join(csp_directives)


def check_rate_limit(user_id: str, action: str, limit: int = 60, 
                    window: int = 3600) -> bool:
    """
    Check if user is within rate limits for specific action
    
    Args:
        user_id: User identifier
        action: Action being performed
        limit: Number of actions allowed
        window: Time window in seconds
        
    Returns:
        True if within limits, False if rate limited
    """
    try:
        portal = api.portal.get()
        annotations = IAnnotations(portal, {})
        
        rate_limits = annotations.get('rate_limits', {})
        current_time = datetime.now()
        
        # Create key for this user/action combination
        key = f"{hash_sensitive_data(user_id)}:{action}"
        
        if key not in rate_limits:
            rate_limits[key] = []
        
        # Clean old entries outside the window
        rate_limits[key] = [
            timestamp for timestamp in rate_limits[key]
            if current_time - datetime.fromisoformat(timestamp) < timedelta(seconds=window)
        ]
        
        # Check if under limit
        if len(rate_limits[key]) >= limit:
            return False
        
        # Add current request
        rate_limits[key].append(current_time.isoformat())
        annotations['rate_limits'] = rate_limits
        
        return True
        
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True  # Allow by default if check fails


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(input_str, str):
        return ""
    
    # Truncate to max length
    sanitized = input_str[:max_length]
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>&"\']', '', sanitized)
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    return sanitized.strip()


# Security constants for production configuration
PRODUCTION_SECURITY_CONFIG = {
    'cors_origins': [
        'https://project-title.yourdomain.com',
        'https://classroom.yourdomain.com'
    ],
    'rate_limits': {
        'api_random_picker': 30,  # 30 picks per hour
        'hall_pass_create': 20,   # 20 passes per hour
        'login_attempts': 5,      # 5 attempts per hour
    },
    'session_timeout': 3600,  # 1 hour
    'audit_retention_days': 365,  # 1 year for compliance
} 