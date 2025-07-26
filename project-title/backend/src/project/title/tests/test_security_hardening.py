"""
Security Hardening Test Suite

Comprehensive tests for Phase 4 security hardening features including:
- FERPA compliance and data anonymization
- Rate limiting functionality
- CORS validation
- Security headers
- Audit logging
- PII detection and protection
"""

import unittest
from datetime import datetime
from plone.app.testing import PLONE_INTEGRATION_TESTING
from zope.annotation.interfaces import IAnnotations

from project.title.security import (
    anonymize_student_data,
    secure_qr_data,
    contains_pii,
    validate_cors_origin,
    check_rate_limit,
    audit_log_hall_pass,
    generate_pseudonym,
    hash_sensitive_data,
    sanitize_input,
    get_security_headers,
    get_csp_header,
)


class TestSecurityHardening(unittest.TestCase):
    """Test security hardening features"""

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        """Set up test environment"""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_data_anonymization_ferpa_compliance(self):
        """Test FERPA-compliant data anonymization"""
        # Test data with various types of PII
        test_data = {
            "student_name": "John Doe",
            "first_name": "John",
            "last_name": "Doe",
            "student_id": "12345",
            "email": "john.doe@school.com",
            "grade_level": "5th",
            "birth_date": "2010-05-15",
            "test_scores": [85, 92, 78],
            "special_needs": "ADHD",
            "parent_name": "Jane Doe",
            "destination": "Library",
            "safe_data": "This is safe",
        }

        anonymized = anonymize_student_data(test_data)

        # Verify PII is removed or anonymized
        self.assertNotEqual(anonymized.get("student_name"), "John Doe")
        self.assertTrue(anonymized.get("student_name", "").startswith("Student_"))
        self.assertNotIn("first_name", anonymized)
        self.assertNotIn("last_name", anonymized)
        self.assertNotIn("student_id", anonymized)
        self.assertNotIn("email", anonymized)
        self.assertNotIn("special_needs", anonymized)
        self.assertNotIn("parent_name", anonymized)

        # Verify safe educational data is preserved
        self.assertEqual(anonymized.get("grade_level"), "5th")
        self.assertEqual(anonymized.get("destination"), "Library")
        self.assertEqual(anonymized.get("safe_data"), "This is safe")

        # Verify date generalization
        self.assertEqual(anonymized.get("birth_date"), "2010-05")

    def test_secure_qr_data_no_pii(self):
        """Test QR code data contains no PII"""
        hall_pass_data = {
            "id": "pass_123",
            "student_name": "John Doe",
            "teacher": "Ms. Smith",
            "issue_time": "2025-01-15T10:30:00",
            "destination": "Library",
            "duration": 15,
        }

        secure_data = secure_qr_data(hall_pass_data)

        # Verify no PII in QR data
        self.assertNotIn("student_name", secure_data)
        self.assertNotEqual(secure_data.get("teacher_code"), "Ms. Smith")

        # Verify essential data is preserved
        self.assertEqual(secure_data.get("pass_id"), "pass_123")
        self.assertEqual(secure_data.get("destination"), "Library")
        self.assertEqual(secure_data.get("duration"), 15)

        # Verify verification code is present
        self.assertIn("verification", secure_data)
        self.assertEqual(len(secure_data["verification"]), 6)

    def test_pii_detection(self):
        """Test PII pattern detection"""
        # Test cases for PII detection
        test_cases = [
            ("john.doe@school.com", True),  # Email
            ("555-123-4567", True),  # Phone
            ("123-45-6789", True),  # SSN
            ("123 Main Street", True),  # Address
            ("Library destination", False),  # Safe text
            ("Grade 5 mathematics", False),  # Safe educational content
            ("Student participation", False),  # Safe classroom data
        ]

        for text, expected_pii in test_cases:
            with self.subTest(text=text):
                self.assertEqual(contains_pii(text), expected_pii)

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        user_id = "test_user"
        action = "test_action"

        # Test normal usage within limits
        for i in range(5):
            result = check_rate_limit(user_id, action, limit=10, window=3600)
            self.assertTrue(result, f"Request {i+1} should be allowed")

        # Test rate limit enforcement
        for i in range(10):  # Exceed the limit
            check_rate_limit(user_id, action, limit=5, window=3600)

        # This should be rate limited
        result = check_rate_limit(user_id, action, limit=5, window=3600)
        self.assertFalse(result, "Request should be rate limited")

    def test_cors_validation(self):
        """Test CORS origin validation"""
        allowed_origins = [
            "http://localhost:3000",
            "https://classroom.domain.com",
            "*.subdomain.com",
        ]

        # Test valid origins
        valid_cases = [
            "http://localhost:3000",
            "https://classroom.domain.com",
            "https://app.subdomain.com",
        ]

        for origin in valid_cases:
            with self.subTest(origin=origin):
                self.assertTrue(validate_cors_origin(origin, allowed_origins))

        # Test invalid origins
        invalid_cases = [
            "http://evil.com",
            "https://phishing.site",
            "http://localhost:8000",  # Different port
            "",
        ]

        for origin in invalid_cases:
            with self.subTest(origin=origin):
                self.assertFalse(validate_cors_origin(origin, allowed_origins))

    def test_audit_logging(self):
        """Test audit logging functionality"""
        # Clear any existing audit log
        annotations = IAnnotations(self.portal, {})
        annotations["security_audit_log"] = []

        # Test audit log creation
        audit_log_hall_pass(
            action="test_action",
            hall_pass_id="test_pass_123",
            user_id="test_user",
            details={"test": "data"},
        )

        # Verify audit log entry
        audit_log = annotations.get("security_audit_log", [])
        self.assertEqual(len(audit_log), 1)

        entry = audit_log[0]
        self.assertEqual(entry["action"], "test_action")
        self.assertEqual(entry["hall_pass_id"], "test_pass_123")
        self.assertIn("timestamp", entry)
        self.assertIn("user_id", entry)
        self.assertIn("ip_address", entry)

        # Verify user ID is hashed for privacy
        self.assertNotEqual(entry["user_id"], "test_user")
        self.assertEqual(len(entry["user_id"]), 8)  # Hash length

    def test_input_sanitization(self):
        """Test input sanitization"""
        test_cases = [
            ('<script>alert("xss")</script>', "scriptalert(xss)/script"),
            ("Normal text", "Normal text"),
            ('Text with "quotes"', "Text with quotes"),
            ("Text with <tags>", "Text with tags"),
            ("A" * 2000, "A" * 1000),  # Length truncation
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = sanitize_input(input_text, max_length=1000)
                self.assertEqual(result, expected)

    def test_security_headers_configuration(self):
        """Test security headers configuration"""
        headers = get_security_headers()

        # Verify essential security headers are present
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Referrer-Policy",
        ]

        for header in required_headers:
            with self.subTest(header=header):
                self.assertIn(header, headers)
                self.assertIsNotNone(headers[header])

        # Verify CSP header generation
        csp_header = get_csp_header()
        self.assertIn("default-src 'self'", csp_header)
        self.assertIn("script-src", csp_header)
        self.assertIn("object-src 'none'", csp_header)

    def test_pseudonym_consistency(self):
        """Test pseudonym generation consistency"""
        # Same input should generate same pseudonym
        name = "John Doe"
        pseudonym1 = generate_pseudonym(name)
        pseudonym2 = generate_pseudonym(name)

        self.assertEqual(pseudonym1, pseudonym2)
        self.assertTrue(pseudonym1.startswith("Student_"))
        self.assertEqual(len(pseudonym1), 12)  # "Student_" + 4 char hash

        # Different inputs should generate different pseudonyms
        different_pseudonym = generate_pseudonym("Jane Smith")
        self.assertNotEqual(pseudonym1, different_pseudonym)

    def test_sensitive_data_hashing(self):
        """Test sensitive data hashing"""
        data = "sensitive information"

        # Hash should be consistent
        hash1 = hash_sensitive_data(data)
        hash2 = hash_sensitive_data(data)
        self.assertEqual(hash1, hash2)

        # Hash should be 8 characters
        self.assertEqual(len(hash1), 8)

        # Different data should produce different hashes
        different_hash = hash_sensitive_data("different data")
        self.assertNotEqual(hash1, different_hash)

    def test_nested_data_anonymization(self):
        """Test anonymization of nested data structures"""
        nested_data = {
            "student_info": {
                "student_name": "John Doe",
                "grade_level": "5th",
                "contact": {"email": "parent@example.com", "phone": "555-1234"},
            },
            "activities": [
                {"student_name": "John Doe", "activity": "Reading"},
                {"student_name": "Jane Smith", "activity": "Math"},
            ],
            "safe_data": "This should remain",
        }

        anonymized = anonymize_student_data(nested_data)

        # Verify nested PII is removed/anonymized
        self.assertNotEqual(anonymized["student_info"]["student_name"], "John Doe")
        self.assertNotIn("contact", anonymized["student_info"])

        # Verify safe data is preserved
        self.assertEqual(anonymized["safe_data"], "This should remain")
        self.assertEqual(anonymized["student_info"]["grade_level"], "5th")

    def test_audit_log_retention(self):
        """Test audit log retention limits"""
        annotations = IAnnotations(self.portal, {})

        # Create more than 1000 audit entries to test retention
        audit_log = []
        for i in range(1100):
            audit_log.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": f"test_action_{i}",
                    "hall_pass_id": f"pass_{i}",
                    "user_id": f"user_{i}",
                }
            )

        annotations["security_audit_log"] = audit_log

        # Add one more entry through the audit function
        audit_log_hall_pass(
            action="final_test", hall_pass_id="final_pass", user_id="final_user"
        )

        # Verify retention limit is enforced
        final_log = annotations.get("security_audit_log", [])
        self.assertLessEqual(len(final_log), 1000)

        # Verify the latest entry is preserved
        self.assertEqual(final_log[-1]["action"], "final_test")


def test_suite():
    """Create test suite"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSecurityHardening))
    return suite


if __name__ == "__main__":
    unittest.main()
