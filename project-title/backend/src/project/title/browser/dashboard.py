"""
Teacher's Daily Command Center Dashboard Browser View

Aggregates real-time data from all classroom management features:
- Current seating arrangements
- Active hall passes with duration tracking
- Participation statistics and fairness scores
- Active timers and alerts
- Quick classroom statistics

Provides both full page view and AJAX data endpoints for real-time updates.
OPTIMIZED: Uses performance optimizations from optimizations.py module.
"""

from Products.Five.browser import BrowserView
from plone import api
from plone.memoize import ram
from zope.annotation.interfaces import IAnnotations
from datetime import datetime, timedelta
import json
import logging
import time

from .cors_helper import set_cors_headers
from ..optimizations import get_dashboard_aggregates, get_user_dashboard_data, measure_performance

logger = logging.getLogger(__name__)


class TeacherDashboard(BrowserView):
    """Real-time classroom command center"""
    
    def __call__(self):
        """Handle requests - return JSON for AJAX, HTML for page view"""
        logger.info("🎛️ Teacher Dashboard accessed")
        
        # Handle CORS headers for frontend integration
        is_preflight = set_cors_headers(self.request, self.request.response)
        if is_preflight:
            return ''
        
        # Check if this is an AJAX request for data updates
        if self.request.get('ajax_update'):
            return self.get_dashboard_data()
        
        # Otherwise return the main dashboard page (would be template-based in full implementation)
        return self.index()
    
    @measure_performance
    def get_dashboard_data(self):
        """Aggregate all classroom management data for real-time dashboard - OPTIMIZED"""
        logger.info("📊 Aggregating dashboard data (cached optimization)")
        
        # Use optimized cached aggregation
        dashboard_data = get_dashboard_aggregates()
        
        # Add user-specific personalization
        user = api.user.get_current()
        if user:
            user_data = get_user_dashboard_data(user.getId())
            dashboard_data['user_context'] = user_data
        
        try:
            # Add legacy format compatibility for existing frontend components
            dashboard_data.update({
                'seating': self.get_current_seating_optimized(),
                'hall_passes': dashboard_data.get('hall_passes', {}),
                'participation': dashboard_data.get('participation', {}),
                'alerts': self.get_classroom_alerts_optimized(),
                'quick_stats': {
                    'active_passes': dashboard_data['hall_passes']['active'],
                    'overdue_passes': dashboard_data['hall_passes']['overdue'],
                    'students_picked_today': dashboard_data['participation']['students_picked_today'],
                    'fairness_score': dashboard_data['participation']['fairness_score']
                },
                'system_status': {
                    'cache_performance': dashboard_data['performance']['cache_hit_ratio'],
                    'response_time': dashboard_data['performance']['avg_response_time'],
                    'status': 'optimized'
                }
            })
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps(dashboard_data)
            
        except Exception as e:
            logger.error(f"Error getting optimized dashboard data: {e}")
            self.request.response.setStatus(500)
            return json.dumps({
                'error': 'Failed to load dashboard data',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    @ram.cache(lambda *args: time.time() // 60)  # 60-second cache for seating
    def get_current_seating_optimized(self):
        """Get active seating chart information - OPTIMIZED"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            charts = catalog(
                portal_type='SeatingChart',
                sort_on='modified',
                sort_order='descending',
                sort_limit=5
            )
            
            if not charts:
                return {
                    'status': 'no_charts',
                    'message': 'No seating charts available',
                    'charts': []
                }
            
            # Get the most recent chart
            latest_chart = charts[0].getObject()
            students = getattr(latest_chart, 'students', [])
            
            return {
                'status': 'active',
                'current_chart': {
                    'title': latest_chart.title,
                    'student_count': len(students),
                    'last_modified': latest_chart.modified().ISO8601(),
                    'url': latest_chart.absolute_url(),
                    'id': latest_chart.getId()
                },
                'total_charts': len(charts),
                'students': students[:20] if students else []  # Limit for performance
            }
            
        except Exception as e:
            logger.error(f"Error getting seating data: {e}")
            return {
                'status': 'error',
                'message': f'Error loading seating data: {e}',
                'charts': []
            }
    
    def get_active_passes(self):
        """Get unreturned hall passes with duration tracking"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            now = datetime.now()
            today = now.date()
            
            # Get all passes issued today
            passes = catalog(
                portal_type='HallPass',
                created={'query': today, 'range': 'min'}
            )
            
            active_passes = []
            total_issued_today = len(passes)
            
            for brain in passes:
                try:
                    pass_obj = brain.getObject()
                    issue_time = getattr(pass_obj, 'issue_time', None)
                    return_time = getattr(pass_obj, 'return_time', None)
                    
                    # Only include unreturned passes
                    if not return_time and issue_time:
                        if isinstance(issue_time, str):
                            # Parse ISO string if needed
                            issue_time = datetime.fromisoformat(issue_time.replace('Z', '+00:00'))
                        
                        duration_minutes = int((now - issue_time).total_seconds() / 60)
                        
                        active_passes.append({
                            'id': pass_obj.getId(),
                            'student': getattr(pass_obj, 'student_name', 'Unknown'),
                            'destination': getattr(pass_obj, 'destination', 'Unknown'),
                            'duration': duration_minutes,
                            'alert_level': self.get_alert_level(duration_minutes),
                            'issue_time': issue_time.isoformat(),
                            'url': pass_obj.absolute_url()
                        })
                        
                except Exception as e:
                    logger.warning(f"Error processing hall pass {brain.getId()}: {e}")
                    continue
            
            # Sort by duration (longest first)
            active_passes.sort(key=lambda x: x['duration'], reverse=True)
            
            return {
                'active_count': len(active_passes),
                'total_today': total_issued_today,
                'passes': active_passes,
                'alerts': [p for p in active_passes if p['alert_level'] in ['yellow', 'red']]
            }
            
        except Exception as e:
            logger.error(f"Error getting hall pass data: {e}")
            return {
                'active_count': 0,
                'total_today': 0,
                'passes': [],
                'alerts': []
            }
    
    def get_alert_level(self, duration_minutes):
        """Determine alert level based on hall pass duration"""
        if duration_minutes > 20:
            return 'red'      # Critical - student out too long
        elif duration_minutes > 10:
            return 'yellow'   # Warning - monitor student
        return 'green'        # Normal duration
    
    @ram.cache(lambda *args: time.time() // 60)  # 60-second cache for participation
    def get_participation_stats(self):
        """Get today's participation statistics from random picker"""
        try:
            portal = api.portal.get()
            annotations = IAnnotations(portal)
            today_key = f"participation_{datetime.now().date()}"
            stats = annotations.get(today_key, {})
            
            if not stats:
                return {
                    'status': 'no_data',
                    'total_picks': 0,
                    'unique_students': 0,
                    'fairness_score': 100,
                    'most_picked': None,
                    'least_picked': None,
                    'recent_picks': []
                }
            
            # Calculate fairness score (lower variance = higher fairness)
            picks = list(stats.values())
            if picks:
                avg_picks = sum(picks) / len(picks)
                variance = sum((p - avg_picks) ** 2 for p in picks) / len(picks)
                fairness_score = max(0, 100 - (variance * 20))  # Scale variance to 0-100
            else:
                fairness_score = 100
            
            # Find most and least picked students
            most_picked = max(stats.items(), key=lambda x: x[1]) if stats else (None, 0)
            least_picked = min(stats.items(), key=lambda x: x[1]) if stats else (None, 0)
            
            return {
                'status': 'active',
                'total_picks': sum(stats.values()),
                'unique_students': len(stats),
                'fairness_score': round(fairness_score, 1),
                'most_picked': {'name': most_picked[0], 'count': most_picked[1]} if most_picked[0] else None,
                'least_picked': {'name': least_picked[0], 'count': least_picked[1]} if least_picked[0] else None,
                'distribution': dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
            }
            
        except Exception as e:
            logger.error(f"Error getting participation stats: {e}")
            return {
                'status': 'error',
                'total_picks': 0,
                'unique_students': 0,
                'fairness_score': 0,
                'most_picked': None,
                'least_picked': None
            }
    
    def get_classroom_alerts(self):
        """Generate relevant alerts and notifications for teacher"""
        alerts = []
        current_time = datetime.now()
        
        try:
            # Check for long-duration hall passes
            hall_pass_data = self.get_active_passes()
            for pass_alert in hall_pass_data.get('alerts', []):
                if pass_alert['alert_level'] == 'red':
                    alerts.append({
                        'type': 'warning',
                        'priority': 'high',
                        'icon': 'exclamation triangle',
                        'title': 'Student Out Too Long',
                        'message': f"{pass_alert['student']} has been out for {pass_alert['duration']} minutes",
                        'action': f"Check on {pass_alert['student']}",
                        'timestamp': current_time.isoformat(),
                        'category': 'hall_pass'
                    })
                elif pass_alert['alert_level'] == 'yellow':
                    alerts.append({
                        'type': 'info',
                        'priority': 'medium',
                        'icon': 'clock',
                        'title': 'Monitor Student',
                        'message': f"{pass_alert['student']} out for {pass_alert['duration']} minutes",
                        'action': 'Monitor return time',
                        'timestamp': current_time.isoformat(),
                        'category': 'hall_pass'
                    })
            
            # Check participation fairness
            participation = self.get_participation_stats()
            if participation['fairness_score'] < 70:
                alerts.append({
                    'type': 'warning',
                    'priority': 'medium',
                    'icon': 'balance scale',
                    'title': 'Participation Imbalance',
                    'message': f"Fairness score: {participation['fairness_score']}%",
                    'action': 'Consider using random picker',
                    'timestamp': current_time.isoformat(),
                    'category': 'participation'
                })
            
            # End of day reminders
            if current_time.hour >= 14:  # After 2 PM
                alerts.append({
                    'type': 'info',
                    'priority': 'low',
                    'icon': 'folder',
                    'title': 'End of Day Prep',
                    'message': 'Consider generating substitute folder if needed tomorrow',
                    'action': 'Generate substitute materials',
                    'timestamp': current_time.isoformat(),
                    'category': 'preparation'
                })
            
            # No seating chart reminder
            seating = self.get_current_seating()
            if seating['status'] == 'no_charts':
                alerts.append({
                    'type': 'warning',
                    'priority': 'medium',
                    'icon': 'users',
                    'title': 'No Seating Chart',
                    'message': 'No seating arrangements found for today',
                    'action': 'Create seating chart',
                    'timestamp': current_time.isoformat(),
                    'category': 'seating'
                })
            
            # Sort alerts by priority
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            alerts.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            
            return alerts[:10]  # Limit to 10 most important alerts
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            return [{
                'type': 'error',
                'priority': 'high',
                'icon': 'warning sign',
                'title': 'System Error',
                'message': 'Unable to load classroom alerts',
                'action': 'Check system status',
                'timestamp': current_time.isoformat(),
                'category': 'system'
            }]
    
    @ram.cache(lambda *args: time.time() // 30)  # 30-second cache for alerts
    def get_classroom_alerts_optimized(self):
        """Generate alerts using optimized data - PERFORMANCE ENHANCED"""
        alerts = []
        current_time = datetime.now()
        
        try:
            # Use cached dashboard data for faster alert generation
            dashboard_data = get_dashboard_aggregates()
            
            # Generate alerts based on cached data
            hall_passes = dashboard_data.get('hall_passes', {})
            
            # High priority: Overdue hall passes
            if hall_passes.get('overdue', 0) > 0:
                alerts.append({
                    'type': 'warning',
                    'priority': 'high',
                    'icon': 'exclamation triangle',
                    'title': 'Students Overdue',
                    'message': f"{hall_passes['overdue']} students past expected return time",
                    'action': 'Check on overdue students',
                    'timestamp': current_time.isoformat(),
                    'category': 'hall_pass'
                })
            
            # Medium priority: Multiple active passes
            if hall_passes.get('active', 0) > 3:
                alerts.append({
                    'type': 'info',
                    'priority': 'medium',
                    'icon': 'users',
                    'title': 'Multiple Students Out',
                    'message': f"{hall_passes['active']} students currently out",
                    'action': 'Monitor classroom supervision',
                    'timestamp': current_time.isoformat(),
                    'category': 'hall_pass'
                })
            
            # Participation fairness alerts
            participation = dashboard_data.get('participation', {})
            fairness_score = participation.get('fairness_score', 100)
            
            if fairness_score < 70:
                alerts.append({
                    'type': 'warning',
                    'priority': 'medium',
                    'icon': 'balance scale',
                    'title': 'Participation Imbalance',
                    'message': f"Fairness score: {fairness_score}% - consider using random picker",
                    'action': 'Use random student picker',
                    'timestamp': current_time.isoformat(),
                    'category': 'participation'
                })
            
            # Performance alerts
            performance = dashboard_data.get('performance', {})
            if performance.get('avg_response_time', 0) > 1.0:
                alerts.append({
                    'type': 'info',
                    'priority': 'low',
                    'icon': 'clock',
                    'title': 'System Performance',
                    'message': f"Response time: {performance['avg_response_time']:.2f}s",
                    'action': 'System running normally',
                    'timestamp': current_time.isoformat(),
                    'category': 'system'
                })
            
            # End of day preparation (optimized check)
            if current_time.hour >= 14:  # After 2 PM
                alerts.append({
                    'type': 'info',
                    'priority': 'low',
                    'icon': 'folder',
                    'title': 'End of Day Prep',
                    'message': 'Consider generating substitute folder for tomorrow',
                    'action': 'Generate substitute materials',
                    'timestamp': current_time.isoformat(),
                    'category': 'preparation'
                })
            
            # Sort by priority
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            alerts.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            
            return alerts[:8]  # Limit for UI performance
            
        except Exception as e:
            logger.error(f"Error generating optimized alerts: {e}")
            return [{
                'type': 'error',
                'priority': 'high',
                'icon': 'warning sign',
                'title': 'Alert System Error',
                'message': 'Unable to load optimized alerts',
                'action': 'Check system status',
                'timestamp': current_time.isoformat(),
                'category': 'system'
            }]
    
    def get_quick_stats(self):
        """Get quick overview statistics for the stats bar"""
        try:
            # Get student count from latest seating chart
            seating = self.get_current_seating()
            students_present = seating.get('current_chart', {}).get('student_count', 0)
            
            # Get hall pass stats
            hall_passes = self.get_active_passes()
            active_passes = hall_passes.get('active_count', 0)
            
            # Get participation stats
            participation = self.get_participation_stats()
            fairness_score = participation.get('fairness_score', 100)
            
            # Get time info
            current_time = datetime.now()
            
            return {
                'students_present': students_present,
                'active_passes': active_passes,
                'fairness_score': fairness_score,
                'current_time': current_time.strftime('%I:%M %p'),
                'current_date': current_time.strftime('%B %d, %Y'),
                'day_of_week': current_time.strftime('%A')
            }
            
        except Exception as e:
            logger.error(f"Error getting quick stats: {e}")
            return {
                'students_present': 0,
                'active_passes': 0,
                'fairness_score': 0,
                'current_time': datetime.now().strftime('%I:%M %p'),
                'current_date': datetime.now().strftime('%B %d, %Y'),
                'day_of_week': datetime.now().strftime('%A')
            }
    
    @ram.cache(lambda *args: time.time() // 300)  # 5-minute cache for system status
    def get_system_status(self):
        """Get overall system health and status"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            
            # Count content by type
            seating_charts = len(catalog(portal_type='SeatingChart'))
            hall_passes = len(catalog(portal_type='HallPass'))
            documents = len(catalog(portal_type='Document'))
            
            return {
                'status': 'healthy',
                'content_counts': {
                    'seating_charts': seating_charts,
                    'hall_passes': hall_passes,
                    'documents': documents
                },
                'features_available': {
                    'seating_charts': seating_charts > 0,
                    'hall_passes': True,  # Always available
                    'random_picker': True,  # Always available
                    'timer': True,  # Always available
                    'substitute_folder': True  # Always available
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            } 