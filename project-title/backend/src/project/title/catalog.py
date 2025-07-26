"""
Custom Catalog Indexes for Classroom Management

These indexes dramatically improve dashboard performance from O(n) to O(log n).
All indexes are additive - existing catalog functionality unchanged.
"""

from plone.indexer import indexer
from project.title.content.hall_pass import IHallPass
from project.title.content.seating_chart import ISeatingChart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@indexer(IHallPass)
def hall_pass_duration(obj):
    """Index for fast duration-based queries"""
    try:
        if hasattr(obj, "issue_time") and obj.issue_time:
            if hasattr(obj, "return_time") and obj.return_time:
                # Returned pass - calculate actual duration
                delta = obj.return_time - obj.issue_time
                return int(delta.total_seconds() / 60)  # minutes
            else:
                # Active pass - calculate current duration
                delta = datetime.now() - obj.issue_time
                return int(delta.total_seconds() / 60)  # minutes
    except Exception as e:
        logger.warning(f"Duration calculation failed: {e}")

    return 0  # Default for passes without proper times


@indexer(IHallPass)
def hall_pass_status(obj):
    """Index for fast status queries"""
    try:
        # Check workflow state first
        if hasattr(obj, "portal_workflow"):
            from plone import api

            try:
                return api.content.get_state(obj=obj)
            except:
                pass

        # Fallback to field-based status
        if hasattr(obj, "return_time") and obj.return_time:
            return "returned"
        elif hasattr(obj, "issue_time") and obj.issue_time:
            return "issued"
        else:
            return "draft"
    except Exception as e:
        logger.warning(f"Status calculation failed: {e}")
        return "unknown"


@indexer(ISeatingChart)
def seating_student_count(obj):
    """Index for fast student count queries"""
    try:
        if hasattr(obj, "students") and obj.students:
            return len(obj.students)
    except Exception as e:
        logger.warning(f"Student count calculation failed: {e}")

    return 0


@indexer(ISeatingChart)
def seating_last_updated(obj):
    """Index for recently modified seating charts"""
    try:
        if hasattr(obj, "modified"):
            return obj.modified()
    except Exception as e:
        logger.warning(f"Last updated calculation failed: {e}")

    return datetime.now()


# Generic classroom content indexer
def classroom_ready_status(obj):
    """Index for classroom readiness status"""
    try:
        # Different logic based on content type
        if IHallPass.providedBy(obj):
            return hall_pass_status(obj) != "draft"
        elif ISeatingChart.providedBy(obj):
            return bool(getattr(obj, "students", None))
        else:
            return True  # Default to ready
    except Exception as e:
        logger.warning(f"Readiness calculation failed: {e}")
        return False
