"""
Substitute Materials Generator Browser View (New Implementation)

Generates JSON-based substitute materials without creating content objects
to avoid permission issues with folder creation in Plone root.
"""

from Products.Five.browser import BrowserView
from plone import api
from datetime import datetime, timedelta
import json
import secrets
import string
import logging

logger = logging.getLogger(__name__)


class SubstituteMaterialsView(BrowserView):
    """Generate substitute materials as JSON response"""

    def __call__(self):
        """Handle requests"""
        logger.info("🚀 NEW SUBSTITUTE MATERIALS VIEW CALLED!")

        # Handle CORS headers
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

        try:
            # Parse request data
            body = self.request.get("BODY", "{}")
            if isinstance(body, bytes):
                body = body.decode("utf-8")
            data = json.loads(body) if body != "{}" else {}

            custom_notes = data.get("notes", "").strip()

            # Generate access code
            access_code = "".join(
                secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8)
            )

            # Get current date
            date_str = datetime.now().strftime("%Y-%m-%d")

            # Create sections data
            sections_data = {
                "Daily Schedule": self.get_schedule_content(),
                "Seating Charts": self.get_seating_charts_content(),
                "Today's Lessons": self.get_lessons_content(),
                "Emergency Procedures": self.get_emergency_content(),
                "Important Contacts": self.get_contacts_content(),
                "Student Information": self.get_student_info_content(custom_notes),
            }

            # Prepare response
            response_data = {
                "success": True,
                "access_code": access_code,
                "document_title": f"Substitute Materials - {date_str}",
                "sections_data": sections_data,
                "custom_notes": custom_notes,
                "generated_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
                "expiry_time": (datetime.now() + timedelta(hours=24)).isoformat(),
                "message": f"Substitute materials generated successfully for {date_str}",
                "sections_created": list(sections_data.keys()),
            }

            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps(response_data)

        except Exception as e:
            logger.error(f"Error in new substitute materials view: {e}")
            self.request.response.setStatus(500)
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to generate substitute materials",
                    "details": str(e),
                }
            )

    def get_schedule_content(self):
        """Generate daily schedule HTML"""
        current_time = datetime.now()
        day_name = current_time.strftime("%A")

        return f"""
        <div class="substitute-schedule">
            <h2>Daily Schedule - {day_name}</h2>
            <p><strong>Date:</strong> {current_time.strftime('%B %d, %Y')}</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Time</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Activity</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Location</th>
                        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">8:00-8:50</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Period 1 - Math</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 201</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Chapter 7 review worksheets</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">8:55-9:45</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Period 2 - Science</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 201</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Lab safety review - no experiments</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">9:50-10:40</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Period 3 - English</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 201</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Silent reading & comprehension</td>
                    </tr>
                    <tr style="background-color: #fff3cd;">
                        <td style="border: 1px solid #ddd; padding: 8px;">10:45-11:30</td>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Lunch Break</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Cafeteria</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Duty-free lunch</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">11:35-12:25</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Period 4 - History</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 201</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Chapter 12 reading assignment</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">12:30-1:20</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Period 5 - PE</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Gymnasium</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Indoor activities only</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">1:25-2:15</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Period 6 - Art</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Art Room</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Watercolor project continuation</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """

    def get_seating_charts_content(self):
        """Get seating charts information"""
        catalog = api.portal.get_tool("portal_catalog")
        charts = catalog(portal_type="SeatingChart")

        if not charts:
            return """
            <div class="seating-charts">
                <h2>Current Seating Charts</h2>
                <p><em>No digital seating charts available. Check for printed charts posted in the classroom.</em></p>
            </div>
            """

        html = "<div class='seating-charts'><h2>Current Seating Charts</h2><ul>"
        for brain in charts:
            chart = brain.getObject()
            html += f"<li><strong>{chart.title}</strong> - {len(getattr(chart, 'students', []))} students</li>"
        html += "</ul></div>"
        return html

    def get_lessons_content(self):
        """Get lesson plans and backup activities"""
        return """
        <div class="lessons">
            <h2>Today's Lesson Plans & Activities</h2>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>📚 Backup Activities (if no specific plans available)</h3>
                <ol>
                    <li><strong>Silent Reading</strong> - Have students read from textbook or library books</li>
                    <li><strong>Review Worksheets</strong> - Use materials from teacher's desk filing system</li>
                    <li><strong>Educational Video</strong> - Check computer bookmarks for approved content</li>
                    <li><strong>Study Hall</strong> - Students work on homework or catch-up assignments</li>
                </ol>
            </div>
            
            <div style="background-color: #d4edda; padding: 15px; border-radius: 5px;">
                <h4>✅ Teaching Reminders</h4>
                <ul>
                    <li>Take attendance at start of each period</li>
                    <li>Follow the schedule closely</li>
                    <li>Keep students engaged but avoid new material</li>
                    <li>Report behavioral issues to office immediately</li>
                </ul>
            </div>
        </div>
        """

    def get_emergency_content(self):
        """Get emergency procedures"""
        return """
        <div class="emergency-procedures">
            <h2>🚨 Emergency Procedures</h2>
            
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>🔥 Fire Drill</h3>
                <ol>
                    <li>Stop instruction immediately when alarm sounds</li>
                    <li>Have students line up quickly and quietly</li>
                    <li>Take attendance clipboard by door</li>
                    <li>Exit through designated route (see posted map)</li>
                    <li>Report to assembly point and take attendance</li>
                    <li>Report missing students to fire warden</li>
                </ol>
            </div>
            
            <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px;">
                <h3>🔒 Lockdown Procedure</h3>
                <ol>
                    <li>Lock classroom door immediately</li>
                    <li>Turn off lights and move away from windows</li>
                    <li>Keep students quiet and calm</li>
                    <li>Do not open door for anyone</li>
                    <li>Wait for official all-clear from administration</li>
                </ol>
            </div>
            
            <p><strong>Emergency Contacts:</strong> Main Office (Ext. 100), Nurse (Ext. 120), Security (Ext. 150)</p>
        </div>
        """

    def get_contacts_content(self):
        """Get important contacts"""
        return """
        <div class="contacts">
            <h2>📞 Important Contacts</h2>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>Main Office</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Extension 100</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">General assistance, emergencies</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>Principal</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Extension 101</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Serious issues, parent calls</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>School Nurse</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Extension 120</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Medical issues, medications</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>IT Support</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Extension 200</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">Computer, projector problems</td>
                </tr>
            </table>
        </div>
        """

    def get_student_info_content(self, custom_notes=""):
        """Get student information with custom notes"""
        content = """
        <div class="student-info">
            <h2>👥 Student Information</h2>
        """

        if custom_notes:
            content += f"""
            <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>📝 Special Instructions from Regular Teacher</h3>
                <p style="white-space: pre-wrap;">{custom_notes}</p>
            </div>
            """

        content += """
            <div style="background-color: #e2e3e5; padding: 15px; border-radius: 5px;">
                <h4>General Guidelines</h4>
                <ul>
                    <li>Students raise hands before speaking</li>
                    <li>One bathroom pass at a time</li>
                    <li>Cell phones should be put away during instruction</li>
                    <li>Stay in assigned seats unless directed otherwise</li>
                    <li>Contact office for any behavioral concerns</li>
                </ul>
            </div>
        </div>
        """

        return content
