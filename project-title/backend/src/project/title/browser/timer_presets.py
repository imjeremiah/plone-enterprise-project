"""
Timer Presets Browser View for Classroom Management

Handles timer presets for common classroom activities like group work,
individual activities, and assessments.
"""

from Products.Five.browser import BrowserView
from plone import api
from zope.annotation.interfaces import IAnnotations
import json
import logging

logger = logging.getLogger(__name__)


class TimerPresetsView(BrowserView):
    """Manage timer presets for common classroom activities"""

    # Default presets for common classroom activities
    DEFAULT_PRESETS = [
        {
            "name": "Quick Activity",
            "duration": 300,
            "description": "5 minutes for warm-ups or quick tasks",
        },
        {
            "name": "Group Work",
            "duration": 600,
            "description": "10 minutes for small group collaboration",
        },
        {
            "name": "Individual Work",
            "duration": 900,
            "description": "15 minutes for independent practice",
        },
        {
            "name": "Test/Quiz",
            "duration": 1200,
            "description": "20 minutes for assessments",
        },
        {
            "name": "Presentation",
            "duration": 1800,
            "description": "30 minutes for student presentations",
        },
        {
            "name": "Reading Time",
            "duration": 2400,
            "description": "40 minutes for sustained reading",
        },
    ]

    def __call__(self):
        """Handle GET (retrieve presets) and POST (save preset) requests"""
        # Handle CORS headers for frontend integration
        self.request.response.setHeader(
            "Access-Control-Allow-Origin", "http://localhost:3000"
        )
        self.request.response.setHeader("Access-Control-Allow-Credentials", "true")
        self.request.response.setHeader(
            "Access-Control-Allow-Methods", "GET, POST, OPTIONS"
        )
        self.request.response.setHeader(
            "Access-Control-Allow-Headers", "Content-Type, Accept"
        )

        if self.request.method == "OPTIONS":
            return ""
        elif self.request.method == "GET":
            return self.get_presets()
        elif self.request.method == "POST":
            return self.save_preset()
        else:
            self.request.response.setStatus(405)
            return json.dumps({"error": "Method not allowed"})

    def get_presets(self):
        """Return timer presets for frontend consumption"""
        try:
            portal = api.portal.get()
            annotations = IAnnotations(portal)

            # Get custom presets or use defaults
            presets = annotations.get("timer_presets", self.DEFAULT_PRESETS.copy())

            # Ensure all presets have required fields
            for preset in presets:
                if "description" not in preset:
                    preset["description"] = (
                        f"{preset['duration'] // 60} minute activity"
                    )

            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps(
                {"success": True, "presets": presets, "count": len(presets)}
            )

        except Exception as e:
            logger.error(f"Error getting timer presets: {e}")
            self.request.response.setStatus(500)
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to retrieve timer presets",
                    "details": str(e),
                }
            )

    def save_preset(self):
        """Save a new custom timer preset"""
        try:
            # Parse request data
            body = self.request.get("BODY", "{}")
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            data = json.loads(body)

            # Validate required fields
            name = data.get("name", "").strip()
            duration = data.get("duration", 0)
            description = data.get("description", "").strip()

            if not name:
                raise ValueError("Preset name is required")
            if not isinstance(duration, int) or duration <= 0:
                raise ValueError("Duration must be a positive integer (seconds)")
            if duration > 7200:  # 2 hours max
                raise ValueError("Duration cannot exceed 2 hours")

            # Get current presets
            portal = api.portal.get()
            annotations = IAnnotations(portal)
            presets = annotations.get("timer_presets", self.DEFAULT_PRESETS.copy())

            # Create new preset
            new_preset = {
                "name": name,
                "duration": duration,
                "description": description or f"{duration // 60} minute activity",
                "custom": True,  # Mark as user-created
            }

            # Check for duplicate names and replace if exists
            preset_names = [p["name"] for p in presets]
            if name in preset_names:
                # Update existing preset
                for i, preset in enumerate(presets):
                    if preset["name"] == name:
                        presets[i] = new_preset
                        break
            else:
                # Add new preset
                presets.append(new_preset)

            # Save updated presets
            annotations["timer_presets"] = presets

            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps(
                {
                    "success": True,
                    "message": f'Timer preset "{name}" saved successfully',
                    "preset": new_preset,
                    "total_presets": len(presets),
                }
            )

        except ValueError as e:
            self.request.response.setStatus(400)
            return json.dumps(
                {"success": False, "error": "Invalid preset data", "details": str(e)}
            )
        except Exception as e:
            logger.error(f"Error saving timer preset: {e}")
            self.request.response.setStatus(500)
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to save timer preset",
                    "details": str(e),
                }
            )

    def delete_preset(self):
        """Delete a custom timer preset"""
        try:
            body = self.request.get("BODY", "{}")
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            data = json.loads(body)

            preset_name = data.get("name", "").strip()
            if not preset_name:
                raise ValueError("Preset name is required")

            portal = api.portal.get()
            annotations = IAnnotations(portal)
            presets = annotations.get("timer_presets", self.DEFAULT_PRESETS.copy())

            # Find and remove preset (only custom ones)
            updated_presets = []
            deleted = False

            for preset in presets:
                if preset["name"] == preset_name and preset.get("custom", False):
                    deleted = True
                else:
                    updated_presets.append(preset)

            if not deleted:
                raise ValueError("Preset not found or cannot be deleted")

            annotations["timer_presets"] = updated_presets

            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps(
                {
                    "success": True,
                    "message": f'Timer preset "{preset_name}" deleted successfully',
                    "total_presets": len(updated_presets),
                }
            )

        except Exception as e:
            logger.error(f"Error deleting timer preset: {e}")
            self.request.response.setStatus(500)
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to delete timer preset",
                    "details": str(e),
                }
            )

    def get_timer_sounds(self):
        """Return available timer sound options"""
        sounds = {
            "warning": {
                "name": "Warning Chime",
                "file": "warning.mp3",
                "description": "Gentle chime for 2-minute and 1-minute warnings",
            },
            "complete": {
                "name": "Completion Bell",
                "file": "complete.mp3",
                "description": "Clear bell sound when timer finishes",
            },
            "urgent": {
                "name": "Urgent Alert",
                "file": "urgent.mp3",
                "description": "Attention-getting sound for immediate action",
            },
        }

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({"success": True, "sounds": sounds})
