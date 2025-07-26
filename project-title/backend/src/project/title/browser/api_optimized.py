"""
Optimized API Endpoints for Phase 4 Performance Enhancement

Provides batched updates, minimized query overhead, and optimized JSON responses
for the classroom management platform. Focuses on:
- Batching multiple data requests into single API calls
- Minimizing database queries through smart caching
- Optimizing JSON response sizes
- Real-time update efficiency
"""

from Products.Five.browser import BrowserView
from plone import api
from plone.memoize import ram
from zope.annotation.interfaces import IAnnotations
from datetime import datetime, timedelta
import json
import time
import logging

from .cors_helper import set_cors_headers
from ..optimizations import get_dashboard_aggregates, get_user_dashboard_data, measure_performance, optimize_catalog_query

logger = logging.getLogger(__name__)


class BatchedAPIView(BrowserView):
    """Batched API endpoints for optimal performance"""
    
    def __call__(self):
        """Route requests to appropriate optimized endpoints"""
        # Handle CORS
        is_preflight = set_cors_headers(self.request, self.request.response)
        if is_preflight:
            return ''
        
        # Get requested endpoints from query parameter
        endpoints = self.request.get('endpoints', '').split(',')
        batch_data = {}
        
        for endpoint in endpoints:
            endpoint = endpoint.strip()
            if endpoint == 'dashboard':
                batch_data['dashboard'] = self.get_dashboard_batch()
            elif endpoint == 'hall_passes':
                batch_data['hall_passes'] = self.get_hall_passes_batch()
            elif endpoint == 'seating':
                batch_data['seating'] = self.get_seating_batch()
            elif endpoint == 'participation':
                batch_data['participation'] = self.get_participation_batch()
            elif endpoint == 'timers':
                batch_data['timers'] = self.get_timers_batch()
        
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps({
            'timestamp': datetime.now().isoformat(),
            'data': batch_data,
            'performance': {
                'batched_endpoints': len(endpoints),
                'cache_optimized': True
            }
        })
    
    @measure_performance
    def get_dashboard_batch(self):
        """Get dashboard data optimized for batched requests"""
        return get_dashboard_aggregates()
    
    @ram.cache(lambda *args: time.time() // 30)  # 30-second cache
    def get_hall_passes_batch(self):
        """Get hall pass data with minimal queries"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            
            # Optimized query using performance indexes
            query = optimize_catalog_query({
                'portal_type': 'HallPass',
                'review_state': 'active',
                'sort_on': 'hall_pass_issue_time',
                'sort_limit': 20  # Limit for performance
            })
            
            brains = catalog(**query)
            
            passes_data = []
            current_time = datetime.now()
            
            for brain in brains:
                try:
                    # Get minimal data without loading full objects when possible
                    pass_data = {
                        'id': brain.getId,
                        'title': brain.Title,
                        'url': brain.getURL(),
                        'created': brain.created.ISO8601(),
                        'modified': brain.modified.ISO8601()
                    }
                    
                    # Only load object for essential annotation data
                    if hasattr(brain, 'hall_pass_issue_time'):
                        pass_data['issue_time'] = brain.hall_pass_issue_time
                    else:
                        # Fallback to object loading only when needed
                        obj = brain.getObject()
                        annotations = IAnnotations(obj, {})
                        pass_data['issue_time'] = annotations.get('hall_pass_issue_time')
                        pass_data['duration'] = annotations.get('hall_pass_duration', 10)
                        pass_data['student'] = annotations.get('student_name', 'Unknown')
                        pass_data['destination'] = annotations.get('destination', 'Not specified')
                    
                    passes_data.append(pass_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing hall pass {brain.getId}: {e}")
                    continue
            
            return {
                'active_passes': passes_data,
                'count': len(passes_data),
                'last_updated': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in hall passes batch: {e}")
            return {'error': str(e), 'active_passes': [], 'count': 0}
    
    @ram.cache(lambda *args: time.time() // 60)  # 60-second cache for seating
    def get_seating_batch(self):
        """Get seating chart data with optimized queries"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            
            # Get recent seating charts efficiently
            query = optimize_catalog_query({
                'portal_type': 'Document',
                'Subject': ['seating-chart'],
                'sort_on': 'modified',
                'sort_order': 'descending',
                'sort_limit': 5
            })
            
            brains = catalog(**query)
            
            charts_data = []
            for brain in brains:
                try:
                    chart_data = {
                        'id': brain.getId,
                        'title': brain.Title,
                        'modified': brain.modified.ISO8601(),
                        'url': brain.getURL(),
                        'creator': brain.Creator
                    }
                    
                    # Get student count from annotations without loading full chart data
                    obj = brain.getObject()
                    annotations = IAnnotations(obj, {})
                    arrangement = annotations.get('seating_arrangement', {})
                    
                    chart_data['student_count'] = len(arrangement.get('students', []))
                    chart_data['layout'] = arrangement.get('layout', 'grid')
                    
                    charts_data.append(chart_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing seating chart {brain.getId}: {e}")
                    continue
            
            return {
                'charts': charts_data,
                'count': len(charts_data),
                'has_active_chart': len(charts_data) > 0
            }
            
        except Exception as e:
            logger.error(f"Error in seating batch: {e}")
            return {'error': str(e), 'charts': [], 'count': 0}
    
    @ram.cache(lambda *args: time.time() // 30)  # 30-second cache
    def get_participation_batch(self):
        """Get participation data with optimized calculations"""
        try:
            portal = api.portal.get()
            annotations = IAnnotations(portal, {})
            participation_data = annotations.get('participation_tracking', {})
            
            current_time = datetime.now()
            today_str = current_time.strftime('%Y-%m-%d')
            
            # Get today's picks efficiently
            daily_picks = participation_data.get('daily_picks', {})
            today_picks = daily_picks.get(today_str, {})
            
            # Calculate statistics
            pick_counts = list(today_picks.values()) if today_picks else []
            
            stats = {
                'students_picked_today': len(today_picks),
                'total_picks_today': sum(pick_counts),
                'fairness_score': 100.0,
                'last_updated': current_time.isoformat()
            }
            
            if pick_counts:
                # Efficient fairness calculation
                avg_picks = sum(pick_counts) / len(pick_counts)
                variance = sum((x - avg_picks) ** 2 for x in pick_counts) / len(pick_counts)
                stats['fairness_score'] = max(0, 100 - (variance * 10))
                stats['avg_picks_per_student'] = round(avg_picks, 1)
                stats['min_picks'] = min(pick_counts)
                stats['max_picks'] = max(pick_counts)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in participation batch: {e}")
            return {'error': str(e), 'students_picked_today': 0}
    
    @ram.cache(lambda *args: time.time() // 10)  # 10-second cache for timers
    def get_timers_batch(self):
        """Get active timers with real-time status"""
        try:
            portal = api.portal.get()
            annotations = IAnnotations(portal, {})
            timer_data = annotations.get('classroom_timers', {})
            
            current_time = datetime.now()
            active_timers = []
            
            for timer_id, timer_info in timer_data.items():
                if timer_info.get('is_running', False):
                    start_time_str = timer_info.get('start_time')
                    if start_time_str:
                        try:
                            start_time = datetime.fromisoformat(start_time_str)
                            elapsed = (current_time - start_time).total_seconds()
                            duration = timer_info.get('duration', 300)  # 5 minutes default
                            remaining = max(0, duration - elapsed)
                            
                            active_timers.append({
                                'id': timer_id,
                                'title': timer_info.get('title', 'Timer'),
                                'duration': duration,
                                'elapsed': round(elapsed),
                                'remaining': round(remaining),
                                'is_finished': remaining <= 0,
                                'start_time': start_time_str
                            })
                        except Exception:
                            continue
            
            return {
                'active_timers': active_timers,
                'count': len(active_timers),
                'last_updated': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in timers batch: {e}")
            return {'error': str(e), 'active_timers': [], 'count': 0}


class OptimizedSeatingChartAPI(BrowserView):
    """Optimized seating chart API with minimal data transfer"""
    
    def __call__(self):
        """Handle seating chart requests with optimized responses"""
        is_preflight = set_cors_headers(self.request, self.request.response)
        if is_preflight:
            return ''
        
        method = self.request.get('REQUEST_METHOD', 'GET')
        chart_id = self.request.get('chart_id')
        
        if method == 'POST':
            return self.update_seating_optimized()
        elif chart_id:
            return self.get_chart_optimized(chart_id)
        else:
            return self.list_charts_optimized()
    
    @measure_performance
    def update_seating_optimized(self):
        """Update seating with minimal data validation"""
        try:
            chart_id = self.request.get('chart_id')
            arrangement_data = json.loads(self.request.get('arrangement_data', '{}'))
            
            # Validate essential data only
            if not chart_id or not arrangement_data:
                self.request.response.setStatus(400)
                return json.dumps({'error': 'Missing required data'})
            
            # Get chart object efficiently
            catalog = api.portal.get_tool('portal_catalog')
            brains = catalog(getId=chart_id)
            
            if not brains:
                self.request.response.setStatus(404)
                return json.dumps({'error': 'Chart not found'})
            
            chart_obj = brains[0].getObject()
            annotations = IAnnotations(chart_obj, {})
            
            # Update with minimal processing
            current_arrangement = annotations.get('seating_arrangement', {})
            current_arrangement.update({
                'students': arrangement_data.get('students', []),
                'layout': arrangement_data.get('layout', 'grid'),
                'last_modified': datetime.now().isoformat(),
                'optimized_update': True
            })
            
            annotations['seating_arrangement'] = current_arrangement
            chart_obj.reindexObject()
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({
                'success': True,
                'chart_id': chart_id,
                'student_count': len(arrangement_data.get('students', [])),
                'last_modified': current_arrangement['last_modified']
            })
            
        except Exception as e:
            logger.error(f"Error updating seating chart: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': str(e)})
    
    @ram.cache(lambda *args: (time.time() // 30, args[1] if len(args) > 1 else 'default'))
    def get_chart_optimized(self, chart_id):
        """Get specific chart with optimized data structure"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            brains = catalog(getId=chart_id)
            
            if not brains:
                self.request.response.setStatus(404)
                return json.dumps({'error': 'Chart not found'})
            
            chart_obj = brains[0].getObject()
            annotations = IAnnotations(chart_obj, {})
            arrangement = annotations.get('seating_arrangement', {})
            
            # Return optimized data structure
            chart_data = {
                'id': chart_id,
                'title': chart_obj.title,
                'students': arrangement.get('students', []),
                'layout': arrangement.get('layout', 'grid'),
                'last_modified': arrangement.get('last_modified', chart_obj.modified().ISO8601()),
                'student_count': len(arrangement.get('students', [])),
                'is_optimized': True
            }
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps(chart_data)
            
        except Exception as e:
            logger.error(f"Error getting chart: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': str(e)})
    
    def list_charts_optimized(self):
        """List charts with minimal metadata only"""
        try:
            catalog = api.portal.get_tool('portal_catalog')
            brains = catalog(
                portal_type='Document',
                Subject=['seating-chart'],
                sort_on='modified',
                sort_order='descending'
            )
            
            charts = []
            for brain in brains[:10]:  # Limit to 10 most recent
                charts.append({
                    'id': brain.getId,
                    'title': brain.Title,
                    'modified': brain.modified.ISO8601(),
                    'creator': brain.Creator
                })
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({
                'charts': charts,
                'count': len(charts),
                'total_available': len(brains)
            })
            
        except Exception as e:
            logger.error(f"Error listing charts: {e}")
            self.request.response.setStatus(500)
            return json.dumps({'error': str(e)}) 