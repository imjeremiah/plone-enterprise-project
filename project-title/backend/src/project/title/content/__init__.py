"""
Content types for Classroom Management Platform
"""

# Import content types to make them available for registration
from .seating_chart import ISeatingChart, SeatingChart

__all__ = [
    'ISeatingChart',
    'SeatingChart',
]

