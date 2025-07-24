"""
Digital Hall Pass Content Type for Classroom Management

This content type allows teachers to issue digital hall passes with QR codes
for student movement tracking and time accountability.
"""

from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from datetime import datetime
import json
import logging
import uuid
import qrcode
import io
import base64

logger = logging.getLogger(__name__)


class IHallPass(model.Schema):
    """Schema for digital hall pass with QR tracking"""
    
    model.fieldset(
        'basic',
        label='Pass Information',
        fields=['student_name', 'destination', 'notes']
    )
    
    model.fieldset(
        'tracking',
        label='Time Tracking',
        fields=['issue_time', 'return_time', 'expected_duration', 'pass_code']
    )
    
    # Student and destination information
    student_name = schema.TextLine(
        title="Student Name",
        description="Name of the student requesting the pass",
        required=True,
    )
    
    destination = schema.Choice(
        title="Destination",
        description="Where the student is going",
        vocabulary="project.title.vocabularies.hall_pass_destinations",
        required=True,
        default="Restroom",
    )
    
    notes = schema.Text(
        title="Notes",
        description="Optional notes about this pass (teacher use only)",
        required=False,
    )
    
    # Time tracking fields
    issue_time = schema.Datetime(
        title="Issue Time",
        description="When this pass was issued",
        required=True,
        defaultFactory=datetime.now,
    )
    
    return_time = schema.Datetime(
        title="Return Time", 
        description="When the student returned (if applicable)",
        required=False,
    )
    
    expected_duration = schema.Int(
        title="Expected Duration (minutes)",
        description="How long this pass should take",
        required=False,
        default=5,
        min=1,
        max=60,
    )
    
    # QR code data
    pass_code = schema.TextLine(
        title="Pass Code",
        description="Unique code for QR verification",
        required=False,
    )


@implementer(IHallPass)
class HallPass(Item):
    """Digital hall pass implementation with QR generation and time tracking"""
    
    def __init__(self, id=None):
        super(HallPass, self).__init__(id)
        # Generate unique pass code on creation
        if not hasattr(self, 'pass_code') or not self.pass_code:
            self.pass_code = str(uuid.uuid4())[:8].upper()
    
    def generate_qr_code(self):
        """Generate QR code for this pass
        
        Returns:
            str: Base64 encoded QR code image
        """
        try:
            # Create pass data (minimal PII for security)
            pass_data = {
                'id': self.getId(),
                'code': self.pass_code,
                'destination': self.destination,
                'issued': self.issue_time.isoformat() if self.issue_time else datetime.now().isoformat(),
                'school': 'classroom_mgmt'  # Identifier for our system
            }
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(pass_data))
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for web display
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Failed to generate QR code for pass {self.getId()}: {e}")
            return None
    
    def get_duration_minutes(self):
        """Calculate how long this pass has been active
        
        Returns:
            int: Duration in minutes
        """
        if not self.issue_time:
            return 0
            
        end_time = self.return_time if self.return_time else datetime.now()
        delta = end_time - self.issue_time
        return int(delta.total_seconds() / 60)
    
    def is_overdue(self):
        """Check if this pass is overdue
        
        Returns:
            bool: True if pass is overdue
        """
        if self.return_time:  # Already returned
            return False
            
        duration = self.get_duration_minutes()
        expected = self.expected_duration or 5
        
        return duration > expected
    
    def get_alert_level(self):
        """Get alert level based on duration
        
        Returns:
            str: 'green', 'yellow', or 'red'
        """
        if self.return_time:
            return 'green'  # Returned
            
        duration = self.get_duration_minutes()
        expected = self.expected_duration or 5
        
        if duration > expected + 5:  # More than 5 minutes overdue
            return 'red'
        elif duration > expected:  # Past expected time
            return 'yellow'
        else:
            return 'green'  # On time
    
    def mark_returned(self):
        """Mark this pass as returned
        
        Returns:
            bool: True if successfully marked as returned
        """
        try:
            self.return_time = datetime.now()
            self.reindexObject()
            
            logger.info(f"Pass {self.getId()} marked as returned for {self.student_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark pass {self.getId()} as returned: {e}")
            return False
    
    def is_active(self):
        """Check if this pass is currently active
        
        Returns:
            bool: True if pass is active (not returned)
        """
        return self.return_time is None
    
    def get_pass_data(self):
        """Get pass data for API responses
        
        Returns:
            dict: Pass data suitable for JSON serialization
        """
        return {
            'id': self.getId(),
            'student_name': self.student_name,
            'destination': self.destination,
            'notes': self.notes or '',
            'issue_time': self.issue_time.isoformat() if self.issue_time else None,
            'return_time': self.return_time.isoformat() if self.return_time else None,
            'expected_duration': self.expected_duration or 5,
            'duration_minutes': self.get_duration_minutes(),
            'is_overdue': self.is_overdue(),
            'alert_level': self.get_alert_level(),
            'is_active': self.is_active(),
            'pass_code': self.pass_code,
            'qr_code': self.generate_qr_code(),
            'url': self.absolute_url(),
        } 