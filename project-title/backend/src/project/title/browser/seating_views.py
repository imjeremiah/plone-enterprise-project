"""
Seating Chart Browser Views for Classroom Management

Handles grid updates and student positioning for interactive seating charts.
All views are backward compatible and designed to work with existing content.
"""

from Products.Five.browser import BrowserView
from plone import api
from plone.memoize import ram
from zope.interface import implementer
# Temporarily comment out event handler to resolve startup issues
# from ..event_handlers import fire_seating_chart_updated
import json
import logging

from .cors_helper import set_cors_headers

logger = logging.getLogger(__name__)


class SeatingChartUpdateView(BrowserView):
    """Handle seating chart position updates via AJAX"""

    def __call__(self):
        """Handle grid position updates from frontend"""
        # Handle CORS headers for frontend integration
        is_preflight = set_cors_headers(self.request, self.request.response)
        if is_preflight:
            return ''
            
        if self.request.method != 'POST':
            self.request.response.setStatus(405)
            return json.dumps({'error': 'Method not allowed'})

        self.request.response.setHeader('Content-Type', 'application/json')

        try:
            # Parse request data
            if hasattr(self.request, 'body'):
                data = json.loads(self.request.body.decode('utf-8'))
            else:
                data = {}

            student_name = data.get('student_name')
            row = data.get('row')
            col = data.get('col')

            if not all([student_name, row is not None, col is not None]):
                self.request.response.setStatus(400)
                return json.dumps({'error': 'Missing required parameters'})

            # Update the seating chart
            if hasattr(self.context, 'update_position'):
                success = self.context.update_position(student_name, int(row), int(col))
                if success:
                    logger.info(f"Updated position: {student_name} to ({row}, {col})")
                    
                    # Fire event for integration (when available)
                    # fire_seating_chart_updated(self.context, student_count=len(self.context.students or []))
                    
                    return json.dumps({'success': True, 'message': 'Position updated'})
                else:
                    self.request.response.setStatus(400)
                    return json.dumps({'error': 'Failed to update position'})
            else:
                self.request.response.setStatus(400)
                return json.dumps({'error': 'Context does not support position updates'})

        except json.JSONDecodeError:
            self.request.response.setStatus(400)
            return json.dumps({'error': 'Invalid JSON data'})
        except Exception as e:
            logger.error(f"Seating chart update error: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': 'Internal server error'})

    def update_grid(self):
        """Update entire grid data"""
        try:
            # Parse request data
            if hasattr(self.request, 'body'):
                data = json.loads(self.request.body.decode('utf-8'))
                grid_data = data.get('grid_data', {})
                
                # Update context with new grid data
                self.context.grid_data = json.dumps(grid_data)
                
                logger.info(f"Updated grid data for {self.context.getId()}")
                
                # Fire event for integration (when available)
                # fire_seating_chart_updated(self.context, student_count=len(grid_data.get('students', {})))
                
                return json.dumps({'success': True, 'message': 'Grid updated'})
            else:
                return json.dumps({'error': 'No data provided'})
                
        except Exception as e:
            logger.error(f"Grid update error: {e}")
            return json.dumps({'error': str(e)})

    def update_grid_enhanced(self):
        """Enhanced grid update with event integration"""
        try:
            # Call existing update functionality first
            result = self.update_grid()
            
            # Fire event for integration (when available)
            try:
                student_count = 0
                if hasattr(self.context, 'students') and self.context.students:
                    student_count = len(self.context.students)
                
                # fire_seating_chart_updated(self.context, student_count=student_count)
            except Exception as event_error:
                logger.info(f"Seating event firing skipped (non-critical): {event_error}")
            
            return result
        except Exception as e:
            logger.error(f"Enhanced grid update failed: {e}")
            # Fall back to original method
            return self.update_grid()

    @ram.cache(lambda *args: f"seating_stats_{args[1].context.getId()}")
    def get_seating_statistics(self):
        """Get seating chart statistics with caching"""
        try:
            grid = self.context.get_grid()
            students = grid.get('students', {})
            
            stats = {
                'total_positions': len(students),
                'available_positions': (self.context.grid_rows * self.context.grid_cols) - len(students),
                'utilization_percent': round((len(students) / (self.context.grid_rows * self.context.grid_cols)) * 100, 1),
                'last_modified': self.context.modified().ISO8601()
            }
            
            return json.dumps(stats)
        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return json.dumps({'error': 'Failed to calculate statistics'})


class SeatingChartStatsView(BrowserView):
    """Provide statistics for seating chart - Required by ZCML"""

    def __call__(self):
        """Return JSON statistics about the seating chart"""
        # Handle CORS headers for frontend integration
        is_preflight = set_cors_headers(self.request, self.request.response)
        if is_preflight:
            return ''
            
        self.request.response.setHeader('Content-Type', 'application/json')

        try:
            if hasattr(self.context, 'grid_data'):
                grid_data = json.loads(self.context.grid_data or '{}')
            else:
                grid_data = {}
            
            students = grid_data.get('students', {})
            
            # Calculate basic statistics
            total_students = len(self.context.students or [])
            seated_students = len(students)
            total_desks = (getattr(self.context, 'grid_rows', 5) * getattr(self.context, 'grid_cols', 6))
            
            stats = {
                'total_students': total_students,
                'seated_students': seated_students,
                'unseated_students': total_students - seated_students,
                'total_desks': total_desks,
                'available_desks': total_desks - seated_students,
                'utilization_rate': round((seated_students / total_desks) * 100, 1) if total_desks > 0 else 0,
                'last_modified': self.context.modified().ISO8601() if hasattr(self.context, 'modified') else None
            }
            
            return json.dumps(stats)
            
        except Exception as e:
            logger.error(f"Error getting seating stats: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': str(e)}) 