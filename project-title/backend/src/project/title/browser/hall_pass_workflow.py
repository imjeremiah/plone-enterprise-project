"""
Hall Pass Workflow Support - ADDITIVE ONLY

This module adds workflow support without breaking existing functionality.
All existing hall pass features continue to work unchanged.
"""

from Products.Five.browser import BrowserView
from plone import api
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class HallPassWorkflowSupport(BrowserView):
    """Add workflow capabilities to existing hall pass system"""

    def __call__(self):
        """Handle AJAX requests for workflow state"""
        # Set CORS headers for frontend integration
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

        # Return workflow state as JSON
        workflow_state = self.get_workflow_state()

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(
            {
                "workflow_state": workflow_state,
                "context_type": getattr(self.context, "portal_type", "Unknown"),
                "supports_workflow": self.supports_workflow(),
            }
        )

    def supports_workflow(self):
        """Check if context supports workflow"""
        try:
            # Check if this is a real Plone content object
            return hasattr(self.context, "portal_workflow") and hasattr(
                self.context, "portal_type"
            )
        except:
            return False

    def transition_to_issued(self):
        """Safely transition hall pass to issued state"""
        try:
            # Only transition if workflow is available
            if self.supports_workflow():
                api.content.transition(obj=self.context, transition="issue")
                # Set issue time if not already set (backward compatibility)
                if not getattr(self.context, "issue_time", None):
                    self.context.issue_time = datetime.now()

            return self.context.absolute_url()
        except Exception as e:
            logger.warning(
                f"Workflow transition failed, continuing with basic functionality: {e}"
            )
            return self.context.absolute_url()

    def transition_to_returned(self):
        """Safely transition hall pass to returned state"""
        try:
            if self.supports_workflow():
                api.content.transition(obj=self.context, transition="return")
                # Set return time
                self.context.return_time = datetime.now()
            else:
                # Fallback to manual return time setting
                self.context.return_time = datetime.now()

            return self.context.absolute_url()
        except Exception as e:
            logger.warning(f"Workflow transition failed, using manual return: {e}")
            self.context.return_time = datetime.now()
            return self.context.absolute_url()

    def get_workflow_state(self):
        """Get current workflow state with fallback"""
        try:
            if self.supports_workflow():
                return api.content.get_state(obj=self.context)
        except:
            pass

        # For demo objects or any context, use request parameters to determine state
        request_id = self.request.get("REQUEST_URL", "").split("/")[-2]

        # Import demo storage to check pass data
        try:
            from .hall_pass_views import DemoStorage

            storage = DemoStorage()
            pass_data = storage.get_pass(request_id)

            if pass_data:
                if pass_data.get("return_time"):
                    return "returned"
                elif pass_data.get("issue_time"):
                    return "issued"
                else:
                    return "draft"
        except:
            pass

        # Final fallback logic
        if getattr(self.context, "return_time", None):
            return "returned"
        elif getattr(self.context, "issue_time", None):
            return "issued"
        else:
            return "draft"

    def get_workflow_history(self):
        """Get workflow history with fallback"""
        try:
            if self.supports_workflow():
                workflow_tool = api.portal.get_tool("portal_workflow")
                return workflow_tool.getHistoryOf("hall_pass_workflow", self.context)
        except:
            pass

        return []
