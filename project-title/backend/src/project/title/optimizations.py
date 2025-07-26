"""
Backend performance optimization utilities for Classroom Management Platform.

Provides caching, database query optimization, and performance monitoring.
All functions designed for high-concurrency classroom environments.
"""

import time
from datetime import datetime, timedelta
from plone.memoize import ram
from plone import api
from zope.annotation.interfaces import IAnnotations
import logging

logger = logging.getLogger(__name__)


def _cache_key_time_30s(*args):
    """Cache key that invalidates every 30 seconds"""
    return time.time() // 30


def _cache_key_user_context(method, self, *args):
    """Cache key that includes user context for personalized data"""
    portal = api.portal.get()
    user = api.user.get_current()
    return (
        time.time() // 30,
        user.getId() if user else "anonymous",
        portal.absolute_url(),
    )


@ram.cache(lambda method, *args: time.time() // 30)  # 30-second cache
def get_dashboard_aggregates():
    """
    Get aggregated dashboard data with 30-second caching.

    Returns aggregated data for teacher dashboard including:
    - Active hall passes count
    - Recent seating chart updates
    - Timer states across classrooms
    - Participation statistics
    - Performance metrics
    """
    portal = api.portal.get()
    catalog = api.portal.get_tool("portal_catalog")

    # Use optimized indexes for fast queries
    current_time = datetime.now()
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

    aggregates = {
        "timestamp": current_time.isoformat(),
        "hall_passes": {"active": 0, "today_total": 0, "overdue": 0},
        "seating_charts": {"updated_today": 0, "total_arrangements": 0},
        "timers": {"active_count": 0, "total_runtime_today": 0},
        "participation": {"students_picked_today": 0, "fairness_score": 100.0},
        "performance": {"avg_response_time": 0, "cache_hit_ratio": 0.95},
    }

    try:
        # Optimized hall pass queries using performance indexes
        hall_pass_brains = catalog(
            portal_type="HallPass",
            review_state="active",
            sort_on="hall_pass_issue_time",
        )

        overdue_count = 0
        today_count = 0

        for brain in hall_pass_brains:
            try:
                obj = brain.getObject()
                annotations = IAnnotations(obj, {})
                issue_time = annotations.get("hall_pass_issue_time")
                duration = annotations.get("hall_pass_duration", 10)  # minutes

                if issue_time:
                    issue_dt = datetime.fromisoformat(issue_time)
                    if issue_dt >= today_start:
                        today_count += 1

                    # Check if overdue (duration + 5 minute grace period)
                    expected_return = issue_dt + timedelta(minutes=duration + 5)
                    if current_time > expected_return:
                        overdue_count += 1

            except Exception:
                continue  # Skip corrupted data

        aggregates["hall_passes"]["active"] = len(hall_pass_brains)
        aggregates["hall_passes"]["today_total"] = today_count
        aggregates["hall_passes"]["overdue"] = overdue_count

        # Seating chart aggregation
        seating_brains = catalog(
            portal_type="Document",
            Subject=["seating-chart"],
            modified={"query": today_start, "range": "min"},
        )
        aggregates["seating_charts"]["updated_today"] = len(seating_brains)

        # Timer and participation data from annotations
        try:
            portal_annotations = IAnnotations(portal, {})
            timer_data = portal_annotations.get("classroom_timers", {})
            participation_data = portal_annotations.get("participation_tracking", {})

            # Count active timers
            active_timers = sum(
                1 for timer in timer_data.values() if timer.get("is_running", False)
            )
            aggregates["timers"]["active_count"] = active_timers

            # Calculate participation fairness
            if participation_data:
                picks_today = participation_data.get("daily_picks", {})
                today_str = today_start.strftime("%Y-%m-%d")
                today_picks = picks_today.get(today_str, {})

                if today_picks:
                    pick_counts = list(today_picks.values())
                    if pick_counts:
                        # Calculate fairness score (100 - variance percentage)
                        avg_picks = sum(pick_counts) / len(pick_counts)
                        variance = sum((x - avg_picks) ** 2 for x in pick_counts) / len(
                            pick_counts
                        )
                        fairness = max(
                            0, 100 - (variance * 10)
                        )  # Scale variance to percentage
                        aggregates["participation"]["fairness_score"] = round(
                            fairness, 1
                        )
                        aggregates["participation"]["students_picked_today"] = len(
                            today_picks
                        )

        except Exception:
            pass  # Use defaults if annotation data unavailable

    except Exception as e:
        # Log error but return partial data
        api.portal.show_message(
            f"Dashboard aggregation warning: {str(e)}",
            request=getattr(portal, "REQUEST", None),
        )

    return aggregates


@ram.cache(_cache_key_user_context)
def get_user_dashboard_data(user_id):
    """
    Get personalized dashboard data for specific user
    Cached per user with 30-second invalidation
    """
    api.portal.get()
    user = api.user.get(user_id)

    if not user:
        return {}

    user_data = {
        "user_id": user_id,
        "display_name": user.getProperty("fullname") or user_id,
        "classrooms": [],
        "preferences": {},
        "recent_activity": [],
    }

    try:
        # Get user's classrooms (folders they own/manage)
        catalog = api.portal.get_tool("portal_catalog")
        user_folders = catalog(
            portal_type="Folder",
            Creator=user_id,
            sort_on="modified",
            sort_order="reverse",
        )

        for brain in user_folders[:5]:  # Limit to 5 most recent
            try:
                folder = brain.getObject()
                annotations = IAnnotations(folder, {})

                classroom_info = {
                    "title": brain.Title,
                    "url": brain.getURL(),
                    "last_modified": brain.modified.strftime("%Y-%m-%d %H:%M"),
                    "has_seating_chart": "seating_arrangement" in annotations,
                    "active_timers": len(annotations.get("classroom_timers", {})),
                    "student_count": len(annotations.get("student_roster", [])),
                }
                user_data["classrooms"].append(classroom_info)

            except Exception:
                continue

    except Exception:
        pass  # Return partial data

    return user_data


def clear_dashboard_cache():
    """Clear all dashboard-related caches"""
    ram.invalidate_cache()


def optimize_catalog_query(query_dict):
    """
    Optimize catalog queries by rewriting them for better performance

    Args:
        query_dict: Original catalog query dictionary

    Returns:
        Optimized query dictionary with better indexes and sorting
    """
    optimized = query_dict.copy()

    # Use performance indexes when available
    if "portal_type" in optimized and optimized["portal_type"] == "HallPass":
        # Add hall pass specific optimizations
        if "review_state" not in optimized:
            optimized["hall_pass_status"] = "active"  # Use custom index

        # Optimize date ranges
        if "modified" in optimized:
            optimized["hall_pass_issue_time"] = optimized.pop("modified")

    # Limit result size for dashboard queries
    if "sort_limit" not in optimized:
        optimized["sort_limit"] = 50  # Reasonable default

    return optimized


def batch_update_annotations(objects, annotation_key, update_func):
    """
    Efficiently batch update annotations across multiple objects

    Args:
        objects: List of objects to update
        annotation_key: Key for annotation data
        update_func: Function to transform annotation data
    """
    for obj in objects:
        try:
            annotations = IAnnotations(obj, {})
            current_data = annotations.get(annotation_key, {})
            new_data = update_func(current_data)

            if new_data != current_data:
                annotations[annotation_key] = new_data
                obj._p_changed = True  # Mark as changed for ZODB

        except Exception:
            continue  # Skip objects that can't be updated


def measure_performance(func):
    """
    Decorator to measure function performance
    Useful for identifying bottlenecks during optimization
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Log performance metrics
        duration = end_time - start_time
        func_name = getattr(func, "__name__", "unknown")

        if duration > 0.5:  # Log slow operations
            portal = api.portal.get()
            if portal:
                api.portal.show_message(
                    f"Performance alert: {func_name} took {duration:.2f}s",
                    request=getattr(portal, "REQUEST", None),
                )

        return result

    return wrapper
