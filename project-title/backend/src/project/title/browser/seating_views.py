"""
Browser views for seating chart position updates

Handles AJAX requests from frontend drag-drop interface to update
student positions and grid data in the backend.
"""

from Products.Five.browser import BrowserView
from plone import api
import json
import logging

logger = logging.getLogger(__name__)


class SeatingChartUpdateView(BrowserView):
    """Handle position updates for seating charts"""

    def __call__(self):
        """Process POST requests to update student positions"""
        # Handle CORS preflight requests
        if self.request.get('REQUEST_METHOD') == 'OPTIONS':
            self.request.response.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000')
            self.request.response.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.request.response.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization')
            self.request.response.setHeader('Access-Control-Allow-Credentials', 'true')
            self.request.response.setStatus(200)
            return ''

        if self.request.get('REQUEST_METHOD') != 'POST':
            self.request.response.setStatus(405)
            return json.dumps({'error': 'Method not allowed'})

        # Set CORS headers for actual requests
        self.request.response.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.request.response.setHeader('Access-Control-Allow-Credentials', 'true')

        try:
            # Parse request data
            request_data = json.loads(self.request.get('BODY', '{}'))
            
            # Update position
            if 'student' in request_data and 'row' in request_data and 'col' in request_data:
                return self.update_position(request_data)
            
            # Update entire grid
            elif 'grid_data' in request_data:
                return self.update_grid(request_data)
            
            else:
                self.request.response.setStatus(400)
                return json.dumps({'error': 'Invalid request data'})

        except Exception as e:
            logger.error(f"Error updating seating chart: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': 'Internal server error'})

    def update_position(self, data):
        """Update single student position"""
        try:
            student = data['student']
            row = int(data['row'])
            col = int(data['col'])
            
            # Get current grid data
            current_data = json.loads(self.context.grid_data or '{}')
            
            # Remove student from current position
            students = current_data.get('students', {})
            for pos_key, student_name in list(students.items()):
                if student_name == student:
                    del students[pos_key]
            
            # Add student to new position
            position_key = f"{row},{col}"
            students[position_key] = student
            
            # Update context
            updated_data = {
                'students': students,
                'empty_desks': current_data.get('empty_desks', []),
                'notes': current_data.get('notes', {})
            }
            
            self.context.grid_data = json.dumps(updated_data)
            
            # Reindex for search
            self.context.reindexObject()
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({
                'success': True,
                'student': student,
                'position': {'row': row, 'col': col},
                'message': f'Moved {student} to position ({row}, {col})'
            })
            
        except Exception as e:
            logger.error(f"Error updating position: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': str(e)})

    def update_grid(self, data):
        """Update entire grid data (for auto-arrange)"""
        try:
            grid_data = data['grid_data']
            
            # Validate JSON
            parsed_data = json.loads(grid_data)
            
            # Update context
            self.context.grid_data = grid_data
            
            # Reindex for search
            self.context.reindexObject()
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({
                'success': True,
                'message': 'Grid layout updated successfully',
                'students_count': len(parsed_data.get('students', {}))
            })
            
        except Exception as e:
            logger.error(f"Error updating grid: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': str(e)})


class SeatingChartStatsView(BrowserView):
    """Provide statistics for seating chart"""

    def __call__(self):
        """Return JSON statistics about the seating chart"""
        # Handle CORS preflight requests
        if self.request.get('REQUEST_METHOD') == 'OPTIONS':
            self.request.response.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000')
            self.request.response.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.request.response.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization')
            self.request.response.setHeader('Access-Control-Allow-Credentials', 'true')
            self.request.response.setStatus(200)
            return ''

        # Set CORS headers for actual requests
        self.request.response.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.request.response.setHeader('Access-Control-Allow-Credentials', 'true')

        try:
            grid_data = json.loads(self.context.grid_data or '{}')
            students = self.context.students or []
            
            total_students = len(students)
            seated_students = len(grid_data.get('students', {}))
            empty_desks = len(grid_data.get('empty_desks', []))
            total_desks = (self.context.grid_rows or 5) * (self.context.grid_cols or 6)
            
            stats = {
                'total_students': total_students,
                'seated_students': seated_students,
                'unseated_students': total_students - seated_students,
                'empty_desks': empty_desks,
                'available_desks': total_desks - seated_students - empty_desks,
                'total_desks': total_desks,
                'utilization_rate': round((seated_students / total_desks) * 100, 1) if total_desks > 0 else 0
            }
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps(stats)
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': str(e)}) 