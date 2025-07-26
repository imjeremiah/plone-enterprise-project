"""
Event Handlers for Feature Integration

All handlers are designed to enhance existing functionality
without breaking current features.
"""

from zope.component import adapter
from plone import api
from datetime import datetime
import logging

from .events import (
    IHallPassIssuedEvent,
    IHallPassReturnedEvent, 
    IHallPassWarningEvent,
    ISeatingChartUpdatedEvent,
    ITimerCompletedEvent,
    ISubstituteFolderGeneratedEvent
)

logger = logging.getLogger(__name__)


@adapter(IHallPassIssuedEvent)
def handle_hall_pass_issued(event):
    """Handle hall pass issued event"""
    try:
        obj = event.object
        student_name = getattr(event, 'student_name', 'Unknown')
        destination = getattr(event, 'destination', 'Unknown')
        
        logger.info(f"🎫 Hall pass issued: {student_name} → {destination}")
        
        # Update dashboard cache (non-breaking)
        try:
            portal = api.portal.get()
            annotations = getattr(portal, '__annotations__', None)
            if annotations is not None:
                cache_key = 'dashboard_hall_pass_cache'
                cache_data = annotations.get(cache_key, {})
                cache_data['last_issued'] = {
                    'student': student_name,
                    'destination': destination,
                    'time': datetime.now().isoformat(),
                    'id': obj.getId()
                }
                annotations[cache_key] = cache_data
        except Exception as cache_error:
            logger.warning(f"Dashboard cache update failed: {cache_error}")
        
        # Trigger notification (if notification system available)
        try:
            # This would integrate with notification system if present
            pass
        except Exception as notify_error:
            logger.info(f"Notification system unavailable: {notify_error}")
            
    except Exception as e:
        logger.error(f"Hall pass issued handler failed: {e}")


@adapter(IHallPassReturnedEvent)
def handle_hall_pass_returned(event):
    """Handle hall pass returned event"""
    try:
        obj = event.object
        duration = getattr(event, 'duration', 0)
        
        logger.info(f"🏠 Hall pass returned after {duration} minutes")
        
        # Update statistics (non-breaking)
        try:
            portal = api.portal.get()
            annotations = getattr(portal, '__annotations__', None)
            if annotations is not None:
                stats_key = 'hall_pass_statistics'
                stats = annotations.get(stats_key, {
                    'total_passes': 0,
                    'total_duration': 0,
                    'average_duration': 0
                })
                
                stats['total_passes'] += 1
                stats['total_duration'] += duration
                stats['average_duration'] = stats['total_duration'] / stats['total_passes']
                
                annotations[stats_key] = stats
        except Exception as stats_error:
            logger.warning(f"Statistics update failed: {stats_error}")
            
    except Exception as e:
        logger.error(f"Hall pass returned handler failed: {e}")


@adapter(ISeatingChartUpdatedEvent)
def handle_seating_chart_updated(event):
    """Handle seating chart updated event"""
    try:
        obj = event.object
        student_count = getattr(event, 'student_count', 0)
        
        logger.info(f"📝 Seating chart updated: {obj.title} ({student_count} students)")
        
        # Update random picker student list (non-breaking)
        try:
            portal = api.portal.get()
            annotations = getattr(portal, '__annotations__', None)
            if annotations is not None:
                picker_key = 'random_picker_students'
                if hasattr(obj, 'students') and obj.students:
                    annotations[picker_key] = list(obj.students)
                    logger.info(f"✅ Random picker updated with {len(obj.students)} students")
        except Exception as picker_error:
            logger.warning(f"Random picker update failed: {picker_error}")
        
        # Clear dashboard cache for fresh data
        try:
            portal = api.portal.get()
            annotations = getattr(portal, '__annotations__', None)
            if annotations is not None:
                cache_key = 'dashboard_seating_cache'
                if cache_key in annotations:
                    del annotations[cache_key]
        except Exception as cache_error:
            logger.warning(f"Cache clearing failed: {cache_error}")
            
    except Exception as e:
        logger.error(f"Seating chart updated handler failed: {e}")


@adapter(ITimerCompletedEvent)
def handle_timer_completed(event):
    """Handle timer completed event"""
    try:
        timer_data = event.get_timer_data()
        duration = timer_data.get('duration', 0)
        timer_type = timer_data.get('timer_type', 'unknown')
        
        logger.info(f"⏰ Timer completed: {timer_type} ({duration}s)")
        
        # Log timer usage statistics (non-breaking)
        try:
            portal = api.portal.get()
            annotations = getattr(portal, '__annotations__', None)
            if annotations is not None:
                timer_stats_key = 'timer_usage_stats'
                stats = annotations.get(timer_stats_key, {})
                
                if timer_type not in stats:
                    stats[timer_type] = {
                        'count': 0,
                        'total_duration': 0,
                        'average_duration': 0
                    }
                
                stats[timer_type]['count'] += 1
                stats[timer_type]['total_duration'] += duration
                stats[timer_type]['average_duration'] = (
                    stats[timer_type]['total_duration'] / stats[timer_type]['count']
                )
                
                annotations[timer_stats_key] = stats
        except Exception as stats_error:
            logger.warning(f"Timer statistics update failed: {stats_error}")
            
    except Exception as e:
        logger.error(f"Timer completed handler failed: {e}")


# Event firing helpers (to be called from existing features)
def fire_hall_pass_issued(hall_pass_obj, student_name=None, destination=None):
    """Helper to fire hall pass issued event"""
    try:
        from zope.event import notify
        from .events import HallPassIssuedEvent
        
        event = HallPassIssuedEvent(
            hall_pass_obj, 
            student_name=student_name, 
            destination=destination
        )
        notify(event)
    except Exception as e:
        logger.warning(f"Event firing failed (non-critical): {e}")


def fire_seating_chart_updated(seating_chart_obj, student_count=None):
    """Helper to fire seating chart updated event"""
    try:
        from zope.event import notify
        from .events import SeatingChartUpdatedEvent
        
        event = SeatingChartUpdatedEvent(seating_chart_obj, student_count=student_count)
        notify(event)
    except Exception as e:
        logger.warning(f"Event firing failed (non-critical): {e}") 