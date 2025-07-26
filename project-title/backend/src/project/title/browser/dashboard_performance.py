"""
High-Performance Dashboard Queries

Uses custom indexes for O(log n) performance instead of O(n) scanning.
Falls back gracefully to existing queries if indexes unavailable.
"""

from Products.Five.browser import BrowserView
from plone import api
from plone.memoize import ram
from datetime import datetime, timedelta
import time
import json
import logging

logger = logging.getLogger(__name__)


class PerformanceDashboard(BrowserView):
    """Enhanced dashboard with optimized queries"""
    
    def __call__(self):
        """Handle dashboard performance requests"""
        # Set comprehensive CORS headers for frontend integration
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        self.request.response.setHeader('Access-Control-Allow-Credentials', 'true')
        self.request.response.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.request.response.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization, X-Requested-With')
        self.request.response.setHeader('Access-Control-Max-Age', '3600')
        
        # Handle preflight OPTIONS request
        if self.request.method == 'OPTIONS':
            self.request.response.setStatus(200)
            return ''
        
        # Return performance metrics
        return self.get_performance_metrics()
    
    @ram.cache(lambda *args: time.time() // 30)  # 30-second cache
    def get_optimized_hall_passes(self):
        """Use indexed queries for hall pass data"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            
            # Try optimized indexed query first
            try:
                active_passes = catalog(
                    portal_type='HallPass',
                    hall_pass_status='issued',  # Uses custom index
                    sort_on='hall_pass_duration',  # Uses custom index
                    sort_order='descending'
                )
                
                results = []
                for brain in active_passes:
                    try:
                        obj = brain.getObject()
                        duration = brain.hall_pass_duration or 0
                        
                        results.append({
                            'id': obj.getId(),
                            'student': getattr(obj, 'student_name', 'Unknown'),
                            'destination': getattr(obj, 'destination', 'Unknown'),
                            'duration': duration,
                            'alert_level': self.get_alert_level(duration),
                            'workflow_state': brain.hall_pass_status,
                            'url': obj.absolute_url()
                        })
                    except Exception as e:
                        logger.warning(f"Error processing brain: {e}")
                        continue
                
                logger.info(f"✅ Optimized query found {len(results)} active passes")
                return {
                    'active_passes': results,
                    'active_count': len(results),
                    'performance_mode': 'optimized'
                }
                
            except Exception as index_error:
                logger.warning(f"Index not available, falling back: {index_error}")
                # Fall back to existing dashboard method
                from .dashboard import TeacherDashboard
                fallback = TeacherDashboard(self.context, self.request)
                result = fallback.get_active_passes()
                result['performance_mode'] = 'fallback'
                return result
                
        except Exception as e:
            logger.error(f"Dashboard query failed: {e}")
            return {
                'active_passes': [],
                'active_count': 0,
                'performance_mode': 'error',
                'error': str(e)
            }
    
    @ram.cache(lambda *args: time.time() // 60)  # 60-second cache
    def get_optimized_seating_stats(self):
        """Use indexed queries for seating chart data"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            
            # Try optimized query
            try:
                charts = catalog(
                    portal_type='SeatingChart',
                    sort_on='seating_last_updated',  # Uses custom index
                    sort_order='descending',
                    sort_limit=5
                )
                
                if charts:
                    latest_brain = charts[0]
                    latest_chart = latest_brain.getObject()
                    
                    return {
                        'status': 'active',
                        'current_chart': {
                            'title': latest_chart.title,
                            'student_count': latest_brain.seating_student_count or 0,
                            'last_modified': latest_chart.modified().ISO8601(),
                            'url': latest_chart.absolute_url(),
                            'id': latest_chart.getId()
                        },
                        'total_charts': len(charts),
                        'performance_mode': 'optimized'
                    }
                else:
                    return {
                        'status': 'no_charts',
                        'message': 'No seating charts available',
                        'performance_mode': 'optimized'
                    }
                    
            except Exception as index_error:
                logger.warning(f"Seating index not available, falling back: {index_error}")
                # Fall back to existing method
                from .dashboard import TeacherDashboard
                fallback = TeacherDashboard(self.context, self.request)
                result = fallback.get_current_seating()
                result['performance_mode'] = 'fallback'
                return result
                
        except Exception as e:
            logger.error(f"Seating query failed: {e}")
            return {
                'status': 'error',
                'message': f'Error loading seating data: {e}',
                'performance_mode': 'error'
            }
    
    def get_performance_metrics(self):
        """Provide performance metrics for monitoring"""
        start_time = time.time()
        
        # Test query performance
        hall_pass_data = self.get_optimized_hall_passes()
        seating_data = self.get_optimized_seating_stats()
        
        end_time = time.time()
        query_time = round((end_time - start_time) * 1000, 2)  # milliseconds
        
        metrics = {
            'query_time_ms': query_time,
            'hall_pass_mode': hall_pass_data.get('performance_mode', 'unknown'),
            'seating_mode': seating_data.get('performance_mode', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'index_status': self.check_index_availability()
        }
        
        # Set CORS headers for this response too
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        self.request.response.setHeader('Content-Type', 'application/json')
        self.request.response.setStatus(200)
        return json.dumps(metrics)
    
    def check_index_availability(self):
        """Check which custom indexes are available"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            available_indexes = catalog.indexes()
            
            custom_indexes = [
                'hall_pass_duration',
                'hall_pass_status', 
                'seating_student_count',
                'seating_last_updated',
                'classroom_ready'
            ]
            
            status = {}
            for index_name in custom_indexes:
                status[index_name] = index_name in available_indexes
            
            return status
        except Exception as e:
            logger.error(f"Index availability check failed: {e}")
            return {}
    
    def get_alert_level(self, duration):
        """Determine alert level based on duration"""
        if duration > 15:
            return 'red'
        elif duration > 10:
            return 'yellow'
        return 'green' 