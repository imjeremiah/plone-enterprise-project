"""
Content types for Classroom Management Platform
"""

# Import content types to make them available for registration
from .seating_chart import ISeatingChart, SeatingChart
from .hall_pass import IHallPass, HallPass

__all__ = [
    "ISeatingChart",
    "SeatingChart",
    "IHallPass",
    "HallPass",
]
