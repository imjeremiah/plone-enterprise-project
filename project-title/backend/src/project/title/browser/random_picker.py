"""
Random Student Picker Browser View for Classroom Management

Handles fair random student selection with history tracking to ensure
equitable participation across all students in a class.
"""

from Products.Five.browser import BrowserView
from plone import api
from zope.annotation.interfaces import IAnnotations
import json
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RandomStudentPickerView(BrowserView):
    """Fair random student selection with history tracking"""

    def __call__(self):
        """Handle both GET (render page) and POST (pick student) requests"""
        # Handle CORS preflight requests
        if self.request.get("REQUEST_METHOD") == "OPTIONS":
            self.request.response.setHeader(
                "Access-Control-Allow-Origin", "http://localhost:3000"
            )
            self.request.response.setHeader(
                "Access-Control-Allow-Methods", "GET, POST, OPTIONS"
            )
            self.request.response.setHeader(
                "Access-Control-Allow-Headers", "Content-Type, Accept, Authorization"
            )
            self.request.response.setHeader("Access-Control-Allow-Credentials", "true")
            self.request.response.setStatus(200)
            return ""

        # Set CORS headers for actual requests
        self.request.response.setHeader(
            "Access-Control-Allow-Origin", "http://localhost:3000"
        )
        self.request.response.setHeader("Access-Control-Allow-Credentials", "true")

        if self.request.get("REQUEST_METHOD") == "POST":
            # Check if this is a reset request
            try:
                request_data = json.loads(self.request.get("BODY", "{}"))
                if request_data.get("action") == "reset_history":
                    return self.reset_daily_history()
            except (json.JSONDecodeError, ValueError):
                pass

            return self.pick_student()
        elif self.request.get("ajax_data"):
            return self.get_picker_data()

        # Default: render the picker page
        return self.index()

    def get_students(self):
        """Get student list from context (seating chart) or fallback data"""
        students = []

        # Try to get students from current context if it's a seating chart
        if hasattr(self.context, "students") and self.context.students:
            students = list(self.context.students)
        else:
            # Fallback: search for seating charts in current folder/site
            catalog = api.portal.get_tool("portal_catalog")
            charts = catalog(
                portal_type="SeatingChart",
                sort_on="modified",
                sort_order="descending",
                sort_limit=5,
            )

            for brain in charts:
                chart = brain.getObject()
                if hasattr(chart, "students") and chart.students:
                    students.extend(chart.students)
                    break  # Use the most recent chart with students

        # Remove duplicates while preserving order
        seen = set()
        unique_students = []
        for student in students:
            if student not in seen:
                seen.add(student)
                unique_students.append(student)

        # If no students found, provide test data
        if not unique_students:
            unique_students = [
                "Alice Johnson",
                "Bob Smith",
                "Carol Williams",
                "David Brown",
                "Emma Davis",
                "Frank Miller",
                "Grace Wilson",
                "Henry Moore",
                "Ivy Taylor",
                "Jack Anderson",
                "Kate Thomas",
                "Liam Jackson",
                "Maya White",
                "Noah Harris",
                "Olivia Martin",
                "Paul Thompson",
            ]

        return unique_students

    def pick_student(self):
        """Select student using fairness weighting algorithm"""
        try:
            students = self.get_students()
            if not students:
                self.request.response.setStatus(400)
                return json.dumps({"error": "No students available"})

            history = self.get_pick_history()

            # Calculate weights based on pick history (recent picks get lower weight)
            weights = []
            current_time = datetime.now()

            for student in students:
                # Get last pick time (default to long ago if never picked)
                last_picked = history.get(student, {}).get("last_picked", 0)
                times_picked = history.get(student, {}).get("count", 0)

                # Calculate time-based weight (longer since last pick = higher weight)
                if last_picked:
                    time_since_pick = (
                        current_time - datetime.fromtimestamp(last_picked)
                    ).total_seconds()
                    time_weight = min(time_since_pick / 3600, 24)  # Max 24 hour weight
                else:
                    time_weight = 24  # Never picked gets max weight

                # Calculate frequency-based weight (fewer picks = higher weight)
                max_picks = max([h.get("count", 0) for h in history.values()] + [1])
                frequency_weight = max_picks - times_picked + 1

                # Combine weights (both time and frequency matter)
                final_weight = time_weight * frequency_weight
                weights.append(max(final_weight, 0.1))  # Minimum weight of 0.1

            # Weighted random selection
            selected = random.choices(students, weights=weights)[0]

            # Update history
            self.update_pick_history(selected)

            # Calculate fairness score
            fairness_score = self.calculate_fairness_score(history, selected)

            response_data = {
                "success": True,
                "selected": selected,
                "timestamp": current_time.isoformat(),
                "fairness_score": fairness_score,
                "total_students": len(students),
                "selection_weights": dict(
                    zip(students, [round(w, 2) for w in weights])
                ),
            }

            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps(response_data)

        except Exception as e:
            logger.error(f"Error in pick_student: {e}")
            self.request.response.setStatus(500)
            return json.dumps({"error": "Selection failed", "details": str(e)})

    def get_picker_data(self):
        """Return current picker state and statistics"""
        try:
            students = self.get_students()
            history = self.get_pick_history()

            # Calculate statistics
            stats = {
                "total_students": len(students),
                "students": students,
                "pick_history": self.format_history_for_display(history),
                "fairness_score": self.calculate_fairness_score(history),
                "session_picks": self.get_session_picks(),
            }

            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps(stats)

        except Exception as e:
            logger.error(f"Error getting picker data: {e}")
            self.request.response.setStatus(500)
            return json.dumps({"error": "Failed to get picker data"})

    def get_pick_history(self):
        """Retrieve picking history from annotations"""
        try:
            # Store history on the site root for persistence across contexts
            portal = api.portal.get()
            annotations = IAnnotations(portal)

            # Get today's date for daily reset
            today = datetime.now().date().isoformat()
            daily_key = f"picker_history_{today}"

            return annotations.get(daily_key, {})
        except Exception as e:
            logger.error(f"Error getting pick history: {e}")
            return {}

    def update_pick_history(self, student_name):
        """Update picking history with new selection"""
        try:
            portal = api.portal.get()
            annotations = IAnnotations(portal)

            today = datetime.now().date().isoformat()
            daily_key = f"picker_history_{today}"

            history = annotations.get(daily_key, {})

            if student_name not in history:
                history[student_name] = {"count": 0, "picks": []}

            # Update count and add timestamp
            history[student_name]["count"] += 1
            history[student_name]["last_picked"] = datetime.now().timestamp()
            history[student_name]["picks"].append(datetime.now().isoformat())

            # Keep only last 10 picks to prevent unlimited growth
            if len(history[student_name]["picks"]) > 10:
                history[student_name]["picks"] = history[student_name]["picks"][-10:]

            annotations[daily_key] = history

            logger.info(
                f"Updated pick history for {student_name}: {history[student_name]['count']} times"
            )

        except Exception as e:
            logger.error(f"Error updating pick history: {e}")

    def calculate_fairness_score(self, history, selected_student=None):
        """Calculate fairness score (0-100) based on pick distribution"""
        if not history:
            return 100  # Perfect fairness with no history

        try:
            picks = [student_data.get("count", 0) for student_data in history.values()]

            if not picks or all(p == 0 for p in picks):
                return 100

            # Calculate variance in pick counts
            avg_picks = sum(picks) / len(picks)
            variance = sum((p - avg_picks) ** 2 for p in picks) / len(picks)

            # Convert variance to fairness score (lower variance = higher fairness)
            # This is a simple heuristic - perfect fairness is 100, maximum unfairness approaches 0
            max_possible_variance = avg_picks**2  # Theoretical maximum
            if max_possible_variance > 0:
                fairness = 100 * (1 - min(variance / max_possible_variance, 1))
            else:
                fairness = 100

            return round(fairness, 1)

        except Exception as e:
            logger.error(f"Error calculating fairness score: {e}")
            return 50  # Neutral score on error

    def format_history_for_display(self, history):
        """Format history data for frontend display"""
        formatted = {}
        for student, data in history.items():
            formatted[student] = {
                "count": data.get("count", 0),
                "last_picked": data.get("last_picked"),
                "recent_picks": data.get("picks", [])[-3:],  # Last 3 picks
            }
        return formatted

    def get_session_picks(self):
        """Get picks made in current session (for immediate feedback)"""
        session = self.request.SESSION
        session_picks = session.get("random_picker_session", [])

        # Clean old session data (older than 1 hour)
        current_time = datetime.now()
        recent_picks = []

        for pick in session_picks:
            pick_time = datetime.fromisoformat(pick["timestamp"].replace("Z", "+00:00"))
            if (current_time - pick_time.replace(tzinfo=None)).total_seconds() < 3600:
                recent_picks.append(pick)

        session["random_picker_session"] = recent_picks
        return recent_picks

    def reset_daily_history(self):
        """Reset picking history (admin function)"""
        try:
            portal = api.portal.get()
            annotations = IAnnotations(portal)

            today = datetime.now().date().isoformat()
            daily_key = f"picker_history_{today}"

            if daily_key in annotations:
                del annotations[daily_key]

            return json.dumps({"success": True, "message": "History reset for today"})

        except Exception as e:
            logger.error(f"Error resetting history: {e}")
            return json.dumps({"error": "Failed to reset history"})
