"""
Seating Chart Content Type for Classroom Management

This content type allows teachers to create interactive seating arrangements
with drag-drop positioning and student roster management.
"""

from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
import json
import logging

logger = logging.getLogger(__name__)


class ISeatingChart(model.Schema):
    """Schema for seating chart with drag-drop student positioning"""
    
    model.fieldset(
        'basic',
        label='Basic Information',
        fields=['title', 'description', 'class_period', 'subject']
    )
    
    model.fieldset(
        'students',
        label='Students & Seating',
        fields=['students', 'grid_rows', 'grid_cols', 'grid_data']
    )
    
    # Basic classroom information
    title = schema.TextLine(
        title="Class Name",
        description="Name for this seating chart (e.g., 'Period 3 Math')",
        required=True,
    )
    
    description = schema.Text(
        title="Description",
        description="Optional notes about this seating arrangement",
        required=False,
    )
    
    class_period = schema.TextLine(
        title="Class Period",
        description="Period or time when this class meets",
        required=False,
    )
    
    subject = schema.TextLine(
        title="Subject",
        description="Subject being taught (Math, English, etc.)",
        required=False,
    )
    
    # Student roster
    students = schema.List(
        title="Class Roster",
        description="List of student names for this class",
        value_type=schema.TextLine(title="Student Name"),
        required=False,
        default=[],
    )
    
    # Grid configuration
    grid_rows = schema.Int(
        title="Number of Rows",
        description="How many rows of desks in the classroom",
        required=True,
        default=5,
        min=2,
        max=10,
    )
    
    grid_cols = schema.Int(
        title="Number of Columns", 
        description="How many columns of desks in the classroom",
        required=True,
        default=6,
        min=2,
        max=12,
    )
    
    # JSON storage for positions
    grid_data = schema.Text(
        title="Seating Grid Data",
        description="JSON data storing student positions and desk arrangements",
        required=False,
        default='{"students": {}, "empty_desks": [], "notes": {}}',
    )


@implementer(ISeatingChart)
class SeatingChart(Container):
    """Seating chart implementation with grid management methods"""
    
    def get_grid(self):
        """Parse grid data as Python object with error handling"""
        try:
            return json.loads(self.grid_data or '{}')
        except (json.JSONDecodeError, AttributeError):
            logger.warning(f"Invalid grid data in {self.getId()}, resetting")
            return {"students": {}, "empty_desks": [], "notes": {}}
    
    def update_position(self, student_name, row, col):
        """Update student position in grid
        
        Args:
            student_name (str): Name of the student to move
            row (int): Target row (0-indexed)
            col (int): Target column (0-indexed)
            
        Returns:
            bool: True if position updated successfully
        """
        if not student_name or student_name not in self.students:
            logger.warning(f"Student {student_name} not in roster for {self.getId()}")
            return False
            
        # Validate position bounds
        if not (0 <= row < self.grid_rows and 0 <= col < self.grid_cols):
            logger.warning(f"Position ({row}, {col}) out of bounds for {self.getId()}")
            return False
        
        grid = self.get_grid()
        
        # Remove student from previous position
        grid['students'] = {pos: name for pos, name in grid['students'].items() 
                           if name != student_name}
        
        # Add student to new position
        position_key = f"{row},{col}"
        grid['students'][position_key] = student_name
        
        # Save updated grid
        self.grid_data = json.dumps(grid)
        
        logger.info(f"Moved {student_name} to ({row}, {col}) in {self.getId()}")
        return True
    
    def get_student_position(self, student_name):
        """Get current position of a student
        
        Args:
            student_name (str): Name of student to find
            
        Returns:
            tuple: (row, col) or None if not positioned
        """
        grid = self.get_grid()
        for position, name in grid['students'].items():
            if name == student_name:
                row, col = map(int, position.split(','))
                return (row, col)
        return None
    
    def get_empty_positions(self):
        """Get list of empty desk positions
        
        Returns:
            list: List of (row, col) tuples for empty desks
        """
        grid = self.get_grid()
        occupied_positions = set(grid['students'].keys())
        
        empty_positions = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                position_key = f"{row},{col}"
                if position_key not in occupied_positions:
                    empty_positions.append((row, col))
                    
        return empty_positions
    
    def clear_all_positions(self):
        """Clear all student positions (emergency reset)"""
        self.grid_data = json.dumps({"students": {}, "empty_desks": [], "notes": {}})
        logger.info(f"Cleared all positions in {self.getId()}")
    
    def auto_arrange_students(self):
        """Automatically arrange students in grid (simple left-to-right fill)"""
        grid = self.get_grid()
        grid['students'] = {}
        
        position_index = 0
        for student in self.students:
            if position_index >= (self.grid_rows * self.grid_cols):
                break  # More students than desks
                
            row = position_index // self.grid_cols
            col = position_index % self.grid_cols
            position_key = f"{row},{col}"
            grid['students'][position_key] = student
            position_index += 1
        
        self.grid_data = json.dumps(grid)
        logger.info(f"Auto-arranged {len(self.students)} students in {self.getId()}") 