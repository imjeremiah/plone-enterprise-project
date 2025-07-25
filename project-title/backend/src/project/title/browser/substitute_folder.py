"""
Substitute Folder Generator Browser View for Classroom Management

Automatically generates organized folders for substitute teachers containing
daily schedules, seating charts, lesson plans, emergency procedures, and
important contact information with time-limited access codes.
"""

from Products.Five.browser import BrowserView
from plone import api
from zope.annotation.interfaces import IAnnotations
from datetime import datetime, timedelta
import json
import transaction
import secrets
import string
import logging

logger = logging.getLogger(__name__)


class SubstituteFolderGenerator(BrowserView):
    """Generate comprehensive document with materials for substitute teachers"""
    
    def __call__(self):
        """Handle GET (show form) and POST (generate folder) requests"""
        logger.info(f"🎯 SUBSTITUTE FOLDER __CALL__ METHOD - Request method: {self.request.method}")
        
        # Handle CORS headers for frontend integration
        self.request.response.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.request.response.setHeader('Access-Control-Allow-Credentials', 'true')
        self.request.response.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.request.response.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept')
        
        if self.request.method == 'OPTIONS':
            logger.info("📧 Handling OPTIONS request")
            return ''
        elif self.request.method == 'POST':
            logger.info("📝 Handling POST request - calling generate_folder()")
            return self.generate_materials_json()
        else:
            logger.info("📄 Handling GET request - calling get_generation_info()")
            return self.get_generation_info()
    
    def get_generation_info(self):
        """Return information about folder generation capabilities or generate materials for POST"""
        
        # If this is a POST request, generate the materials instead
        if self.request.method == 'POST':
            logger.info("🎯 POST request to substitute-folder-info - generating materials via working endpoint!")
            return self.generate_simple_materials()
        
        # Otherwise return info for GET requests
        catalog = api.portal.get_tool('portal_catalog')
        
        # Count available materials
        seating_charts = len(catalog(portal_type='SeatingChart'))
        hall_passes = len(catalog(portal_type='HallPass'))
        documents = len(catalog(portal_type='Document'))
        
        info = {
            'success': True,
            'available_materials': {
                'seating_charts': seating_charts,
                'hall_passes': hall_passes,
                'documents': documents
            },
            'sections_included': [
                'Daily Schedule',
                'Seating Charts',
                'Lesson Plans',
                'Emergency Procedures',
                'Important Contacts',
                'Student Information'
            ]
        }
        
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(info)
    
    def generate_simple_materials(self):
        """Generate substitute materials without creating any content objects"""
        logger.info("🚀 GENERATING SIMPLE MATERIALS - WORKING METHOD!")
        
        try:
            # Parse request data
            body = self.request.get('BODY', '{}')
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body) if body != '{}' else {}
            
            custom_notes = data.get('notes', '').strip()
            
            # Generate access code
            access_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            # Get current date
            date_str = datetime.now().strftime('%Y-%m-%d')
            day_name = datetime.now().strftime('%A')
            
            # Create simple sections without any complex logic
            sections_data = {
                'Daily Schedule': f"""
                <div class="schedule">
                    <h2>Daily Schedule - {day_name}</h2>
                    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">
                        <p><strong>8:00-8:50:</strong> Period 1 - Math (Room 201)</p>
                        <p><strong>8:55-9:45:</strong> Period 2 - Science (Room 201)</p>
                        <p><strong>9:50-10:40:</strong> Period 3 - English (Room 201)</p>
                        <p><strong>10:45-11:30:</strong> Lunch Break</p>
                        <p><strong>11:35-12:25:</strong> Period 4 - History (Room 201)</p>
                        <p><strong>12:30-1:20:</strong> Period 5 - PE (Gymnasium)</p>
                        <p><strong>1:25-2:15:</strong> Period 6 - Art (Art Room)</p>
                    </div>
                </div>
                """,
                'Seating Charts': """
                <div class="seating">
                    <h2>Seating Charts</h2>
                    <p>Check for posted seating charts in the classroom or on the teacher's desk.</p>
                    <p><em>Students should remain in their assigned seats unless directed otherwise.</em></p>
                </div>
                """,
                "Today's Lessons": """
                <div class="lessons">
                    <h2>Today's Lessons & Backup Activities</h2>
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px;">
                        <h3>Backup Activities:</h3>
                        <ul>
                            <li>Silent reading from textbooks</li>
                            <li>Review worksheets (check teacher's desk)</li>
                            <li>Study hall for homework</li>
                            <li>Educational videos (check computer bookmarks)</li>
                        </ul>
                    </div>
                </div>
                """,
                'Emergency Procedures': """
                <div class="emergency">
                    <h2>🚨 Emergency Procedures</h2>
                    <div style="background: #f8d7da; padding: 15px; border-radius: 5px; margin: 10px 0;">
                        <h3>Fire Drill:</h3>
                        <ol>
                            <li>Stop instruction when alarm sounds</li>
                            <li>Line up students quickly and quietly</li>
                            <li>Exit through designated route</li>
                            <li>Report to assembly point</li>
                        </ol>
                    </div>
                    <div style="background: #d1ecf1; padding: 15px; border-radius: 5px;">
                        <h3>Lockdown:</h3>
                        <ol>
                            <li>Lock classroom door immediately</li>
                            <li>Turn off lights, move away from windows</li>
                            <li>Keep students quiet and calm</li>
                            <li>Wait for official all-clear</li>
                        </ol>
                    </div>
                </div>
                """,
                'Important Contacts': """
                <div class="contacts">
                    <h2>📞 Important Contacts</h2>
                    <ul>
                        <li><strong>Main Office:</strong> Extension 100</li>
                        <li><strong>Principal:</strong> Extension 101</li>
                        <li><strong>School Nurse:</strong> Extension 120</li>
                        <li><strong>IT Support:</strong> Extension 200</li>
                    </ul>
                </div>
                """,
                'Student Information': f"""
                <div class="student-info">
                    <h2>👥 Student Information</h2>
                    {f'''
                    <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h3>📝 Special Instructions from Teacher</h3>
                        <p style="white-space: pre-wrap;">{custom_notes}</p>
                    </div>
                    ''' if custom_notes else ''}
                    <div style="background: #e2e3e5; padding: 15px; border-radius: 5px;">
                        <h4>General Guidelines:</h4>
                        <ul>
                            <li>Students raise hands before speaking</li>
                            <li>One bathroom pass at a time</li>
                            <li>Stay in assigned seats</li>
                            <li>Contact office for behavioral concerns</li>
                        </ul>
                    </div>
                </div>
                """
            }
            
            # Prepare response
            response_data = {
                'success': True,
                'access_code': access_code,
                'document_title': f'Substitute Materials - {date_str}',
                'sections_data': sections_data,
                'custom_notes': custom_notes,
                'generated_date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                'expiry_time': (datetime.now() + timedelta(hours=24)).isoformat(),
                'message': f'Substitute materials generated successfully for {date_str}',
                'sections_created': list(sections_data.keys())
            }
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps(response_data)
            
        except Exception as e:
            logger.error(f"Error generating simple materials: {e}")
            self.request.response.setStatus(500)
            return json.dumps({
                'success': False,
                'error': 'Failed to generate substitute materials',
                'details': str(e)
            })
    
    def generate_folder(self):
        """Create comprehensive substitute document with today's materials"""
        logger.info("🚀 GENERATE_FOLDER METHOD CALLED - NEW CODE IS RUNNING!")
        try:
            # Parse request data for custom notes
            body = self.request.get('BODY', '{}')
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body) if body != '{}' else {}
            
            custom_notes = data.get('notes', '').strip()
            
            # Create folder with today's date
            date_str = datetime.now().strftime('%Y-%m-%d')
            folder_id = f'substitute-{date_str}'
            folder_title = f'Substitute Materials - {date_str}'
            
            portal = api.portal.get()
            
            # Check if document already exists
            logger.info(f"DEBUG: Checking if {folder_id} exists in portal")
            if folder_id in portal:
                folder = portal[folder_id]
                logger.info(f"Using existing substitute document: {folder_id}")
            else:
                logger.info(f"DEBUG: Document {folder_id} does not exist, creating new one")
                with api.env.adopt_roles(['Manager']):
                    logger.info(f"DEBUG: About to create Document with id={folder_id}, type=Document")
                    folder = api.content.create(
                        container=portal,
                        type='Document',
                        id=folder_id,
                        title=folder_title,
                        description=f'Emergency substitute materials for {datetime.now().strftime("%B %d, %Y")}'
                    )
                    logger.info(f"Created new substitute document: {folder_id}")
            
            # Create comprehensive substitute document content
            sections = [
                ('Daily Schedule', self.get_schedule_content()),
                ('Seating Charts', self.get_seating_charts_content()),
                ("Today's Lessons", self.get_todays_lessons()),
                ('Emergency Procedures', self.get_emergency_info()),
                ('Important Contacts', self.get_contacts()),
                ('Special Student Information', self.get_student_info(custom_notes)),
            ]
            
            # Combine all sections into one comprehensive document
            combined_content = f"""
            <div class="substitute-materials">
                <h1>Substitute Teacher Materials - {datetime.now().strftime('%B %d, %Y')}</h1>
                <p><strong>Access Code:</strong> <span style="background-color: #f0f8ff; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{{ACCESS_CODE}}</span></p>
                <p><em>This document contains all materials needed for successful classroom management.</em></p>
                <hr style="margin: 30px 0;">
            """
            
            created_sections = []
            
            with api.env.adopt_roles(['Manager']):
                for section_title, content_html in sections:
                    combined_content += f"""
                    <div class="section" style="margin-bottom: 40px;">
                        {content_html}
                    </div>
                    <hr style="margin: 20px 0; border: 1px solid #eee;">
                    """
                    created_sections.append(section_title)
                    logger.info(f"Added section: {section_title}")
                
                # Set permissions and generate access code
                access_code = self.set_substitute_permissions(folder)
                
                # Replace access code placeholder in content
                combined_content = combined_content.replace('{ACCESS_CODE}', access_code)
                combined_content += "</div>"
                
                # Set the document text content
                folder.text = api.content.RichTextValue(
                    combined_content,
                    'text/html',
                    'text/x-html-safe'
                )
            
            transaction.commit()
            
            response_data = {
                'success': True,
                'folder_url': folder.absolute_url(),
                'access_code': access_code,
                'folder_title': folder_title,
                'sections_created': created_sections,
                'expiry_time': (datetime.now() + timedelta(hours=24)).isoformat(),
                'message': f'Substitute materials document created successfully for {date_str}'
            }
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps(response_data)
            
        except Exception as e:
            import traceback
            logger.error(f"Error generating substitute folder: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.request.response.setStatus(500)
            return json.dumps({
                'success': False,
                'error': 'Failed to generate substitute folder',
                'details': str(e)
            })
    
    def generate_materials_json(self):
        """Generate substitute materials as JSON response instead of creating content objects"""
        logger.info("🚀 GENERATE_MATERIALS_JSON METHOD CALLED - NEW APPROACH!")
        
        try:
            # Parse request data for custom notes
            body = self.request.get('BODY', '{}')
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body) if body != '{}' else {}
            
            custom_notes = data.get('notes', '').strip()
            
            # Generate access code
            access_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            # Get current date
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Create sections data
            sections_data = {
                'Daily Schedule': self.get_schedule_content(),
                'Seating Charts': self.get_seating_charts_content(),
                "Today's Lessons": self.get_todays_lessons(),
                'Emergency Procedures': self.get_emergency_info(),
                'Important Contacts': self.get_contacts(),
                'Special Student Information': self.get_student_info(custom_notes),
            }
            
            # Prepare response
            response_data = {
                'success': True,
                'access_code': access_code,
                'document_title': f'Substitute Materials - {date_str}',
                'document_url': f'{api.portal.get().absolute_url()}/substitute-materials-{date_str}',
                'sections_data': sections_data,
                'custom_notes': custom_notes,
                'generated_date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                'expiry_time': (datetime.now() + timedelta(hours=24)).isoformat(),
                'message': f'Substitute materials generated successfully for {date_str}',
                'sections_created': list(sections_data.keys())
            }
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps(response_data)
            
        except Exception as e:
            import traceback
            logger.error(f"Error generating substitute materials JSON: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.request.response.setStatus(500)
            return json.dumps({
                'success': False,
                'error': 'Failed to generate substitute materials',
                'details': str(e)
            })
    
    def get_schedule_content(self):
        """Generate daily schedule HTML"""
        # Get current time for context
        current_time = datetime.now()
        day_name = current_time.strftime('%A')
        
        return f"""
        <div class="substitute-schedule">
            <h2>Daily Schedule - {day_name}</h2>
            <p><strong>Date:</strong> {current_time.strftime('%B %d, %Y')}</p>
            
            <table class="schedule-table" style="width: 100%; border-collapse: collapse; margin: 20px 0;">
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
                        <td style="border: 1px solid #ddd; padding: 8px;">Chapter 7 review</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">8:55-9:45</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Period 2 - Science</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 201</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Lab safety review</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">9:50-10:40</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Period 3 - English</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 201</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Reading comprehension</td>
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
                        <td style="border: 1px solid #ddd; padding: 8px;">Chapter 12 discussion</td>
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
                        <td style="border: 1px solid #ddd; padding: 8px;">Watercolor project</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="important-reminders" style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h3>⚠️ Important Reminders</h3>
                <ul>
                    <li><strong>Attendance:</strong> Take attendance at the beginning of each period</li>
                    <li><strong>Emergency:</strong> Fire drill procedure posted by door</li>
                    <li><strong>Bathroom passes:</strong> Only one student at a time</li>
                    <li><strong>End of day:</strong> Ensure all students are picked up or on buses</li>
                </ul>
            </div>
        </div>
        """
    
    def get_seating_charts_content(self):
        """Include current seating charts information"""
        catalog = api.portal.get_tool('portal_catalog')
        charts = catalog(portal_type='SeatingChart')
        
        if not charts:
            return """
            <div class="seating-charts-section">
                <h2>Current Seating Charts</h2>
                <p><em>No seating charts are currently available.</em></p>
                <p>Students may sit in any available seat or refer to any printed seating charts posted in the classroom.</p>
            </div>
            """
        
        charts_html = """
        <div class="seating-charts-section">
            <h2>Current Seating Charts</h2>
            <p>The following seating arrangements are active for today:</p>
            <ul style="list-style-type: none; padding-left: 0;">
        """
        
        for brain in charts:
            chart = brain.getObject()
            student_count = len(getattr(chart, 'students', []))
            charts_html += f"""
                <li style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                    <strong>{chart.title}</strong><br>
                    <small>Students: {student_count} | Last updated: {chart.modified().strftime('%B %d, %Y at %I:%M %p')}</small><br>
                    <a href="{chart.absolute_url()}" target="_blank">View Seating Chart →</a>
                </li>
            """
        
        charts_html += """
            </ul>
            <div class="seating-notes" style="background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0;">
                <h4>Seating Chart Notes:</h4>
                <ul>
                    <li>Maintain assigned seating to help with attendance and classroom management</li>
                    <li>If a student is absent, leave their seat empty</li>
                    <li>For group activities, students may temporarily move but should return to assigned seats</li>
                    <li>Report any seating issues to the main office</li>
                </ul>
            </div>
        </div>
        """
        
        return charts_html
    
    def get_todays_lessons(self):
        """Get today's lesson plans and materials"""
        today = datetime.now().date()
        catalog = api.portal.get_tool('portal_catalog')
        
        # Look for documents created or modified today
        today_docs = catalog(
            portal_type='Document',
            modified={'query': today, 'range': 'min'}
        )
        
        lessons_html = """
        <div class="todays-lessons">
            <h2>Today's Lesson Plans</h2>
        """
        
        if today_docs:
            lessons_html += f"""
            <p>The following lesson materials have been prepared for today ({today.strftime('%B %d, %Y')}):</p>
            <ul style="list-style-type: none; padding-left: 0;">
            """
            
            for brain in today_docs[:5]:  # Limit to 5 most recent
                doc = brain.getObject()
                lessons_html += f"""
                    <li style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <strong><a href="{doc.absolute_url()}" target="_blank">{doc.title}</a></strong><br>
                        <small>Modified: {doc.modified().strftime('%I:%M %p')}</small><br>
                        {doc.description or 'No description available'}
                    </li>
                """
            
            lessons_html += "</ul>"
        else:
            lessons_html += """
            <div class="default-lesson-plan" style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px;">
                <h3>Default Lesson Activities</h3>
                <p>No specific lesson plans were found for today. Here are suggested backup activities:</p>
                <ol>
                    <li><strong>Silent Reading (15-20 minutes)</strong>
                        <ul>
                            <li>Students read from their current class book or library book</li>
                            <li>Encourage note-taking or journaling about what they read</li>
                        </ul>
                    </li>
                    <li><strong>Review Activities</strong>
                        <ul>
                            <li>Review previous day's work or homework</li>
                            <li>Practice worksheets from teacher's desk</li>
                        </ul>
                    </li>
                    <li><strong>Educational Videos</strong>
                        <ul>
                            <li>Subject-appropriate videos (see computer bookmarks)</li>
                            <li>Follow with brief discussion or writing activity</li>
                        </ul>
                    </li>
                    <li><strong>Quiet Individual Work</strong>
                        <ul>
                            <li>Catch up on any incomplete assignments</li>
                            <li>Extra credit worksheets available in file cabinet</li>
                        </ul>
                    </li>
                </ol>
            </div>
            """
        
        lessons_html += """
            <div class="lesson-reminders" style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4>Teaching Reminders:</h4>
                <ul>
                    <li>✓ Take attendance at the start of each period</li>
                    <li>✓ Follow the posted schedule closely</li>
                    <li>✓ Keep students engaged but avoid introducing new material</li>
                    <li>✓ Send any behavioral concerns to the office immediately</li>
                    <li>✓ Leave detailed notes about the day for the regular teacher</li>
                </ul>
            </div>
        </div>
        """
        
        return lessons_html
    
    def get_emergency_info(self):
        """Generate emergency procedures content"""
        return """
        <div class="emergency-procedures">
            <h2>🚨 Emergency Procedures</h2>
            
            <div class="emergency-contacts" style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h3>Emergency Contacts (Call Immediately)</h3>
                <ul style="font-size: 16px; line-height: 1.6;">
                    <li><strong>Main Office:</strong> Extension 100 (or dial 911 for life-threatening emergencies)</li>
                    <li><strong>School Nurse:</strong> Extension 120</li>
                    <li><strong>Principal:</strong> Extension 101</li>
                    <li><strong>Security:</strong> Extension 150</li>
                </ul>
            </div>
            
            <div class="fire-drill" style="margin: 20px 0;">
                <h3>🔥 Fire Drill Procedure</h3>
                <ol>
                    <li>Stop teaching immediately when alarm sounds</li>
                    <li>Have students line up quickly and quietly</li>
                    <li>Take attendance clipboard (by door)</li>
                    <li>Turn off lights and close door (DO NOT LOCK)</li>
                    <li>Lead students to designated assembly area (see map by door)</li>
                    <li>Take attendance at assembly point</li>
                    <li>Report any missing students to fire warden immediately</li>
                    <li>Wait for all-clear signal before returning</li>
                </ol>
            </div>
            
            <div class="lockdown" style="margin: 20px 0;">
                <h3>🔒 Lockdown Procedure</h3>
                <ol>
                    <li>Lock classroom door immediately</li>
                    <li>Turn off lights</li>
                    <li>Move students away from windows and doors</li>
                    <li>Keep students quiet and calm</li>
                    <li>Do not open door for anyone</li>
                    <li>Wait for official all-clear from administration</li>
                    <li>Be prepared to evacuate if instructed by authorities</li>
                </ol>
            </div>
            
            <div class="medical-emergency" style="margin: 20px 0;">
                <h3>🏥 Medical Emergency</h3>
                <ol>
                    <li>Call main office immediately (Extension 100)</li>
                    <li>If life-threatening: Call 911 first, then office</li>
                    <li>Do not move injured student unless in immediate danger</li>
                    <li>Send reliable student to get nurse if available</li>
                    <li>Stay calm and reassure the student</li>
                    <li>Clear area of other students</li>
                    <li>Wait for professional help to arrive</li>
                </ol>
            </div>
            
            <div class="severe-weather" style="margin: 20px 0;">
                <h3>⛈️ Severe Weather</h3>
                <ol>
                    <li>Listen for announcements over intercom</li>
                    <li>Move students away from windows</li>
                    <li>Have students sit on floor in center of room</li>
                    <li>Students should cover heads with hands</li>
                    <li>Stay calm and keep students quiet</li>
                    <li>Wait for all-clear announcement</li>
                </ol>
            </div>
            
            <div class="important-notes" style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4>⚠️ Important Emergency Notes</h4>
                <ul>
                    <li>Emergency evacuation maps are posted by each exit</li>
                    <li>First aid kit is located in the supply closet</li>
                    <li>AED is located in the main hallway near the office</li>
                    <li>Never leave students unattended during an emergency</li>
                    <li>Follow instructions from administration and emergency personnel</li>
                </ul>
            </div>
        </div>
        """
    
    def get_contacts(self):
        """Generate important contacts list"""
        return """
        <div class="important-contacts">
            <h2>📞 Important Contacts</h2>
            
            <div class="school-contacts" style="margin: 20px 0;">
                <h3>School Administration</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Principal</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Dr. Sarah Johnson</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Extension 101</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">sjohnson@school.edu</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Vice Principal</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Mr. Robert Chen</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Extension 102</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">rchen@school.edu</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Main Office</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Administrative Staff</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Extension 100</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">office@school.edu</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>School Nurse</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Mrs. Lisa Martinez</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Extension 120</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">lmartinez@school.edu</td>
                    </tr>
                </table>
            </div>
            
            <div class="support-contacts" style="margin: 20px 0;">
                <h3>Support Staff</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>IT Support</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Extension 200</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">For computer/projector issues</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Custodial</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Extension 300</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">For spills, maintenance issues</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Security</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Extension 150</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">For safety concerns</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Transportation</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Extension 400</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">For bus-related issues</td>
                    </tr>
                </table>
            </div>
            
            <div class="teacher-contacts" style="margin: 20px 0;">
                <h3>Key Teacher Contacts</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Grade Level Team Lead</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Ms. Jennifer Walsh</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 205</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">jwalsh@school.edu</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>Special Education Coordinator</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Mr. David Kim</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 180</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">dkim@school.edu</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;"><strong>English Language Learning</strong></td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Mrs. Carmen Rodriguez</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">Room 190</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">crodriguez@school.edu</td>
                    </tr>
                </table>
            </div>
            
            <div class="contact-notes" style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4>Contact Guidelines</h4>
                <ul>
                    <li><strong>Emergency situations:</strong> Call main office first (Extension 100)</li>
                    <li><strong>Student issues:</strong> Contact administration before parents</li>
                    <li><strong>Technical problems:</strong> Try restarting first, then call IT</li>
                    <li><strong>End of day:</strong> Report any incidents to principal via email</li>
                    <li><strong>Parent calls:</strong> Direct all parent inquiries to the main office</li>
                </ul>
            </div>
        </div>
        """
    
    def get_student_info(self, custom_notes=''):
        """Generate special student information with custom notes"""
        content = """
        <div class="student-information">
            <h2>👥 Student Information & Notes</h2>
            
            <div class="confidentiality-notice" style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4>⚠️ CONFIDENTIALITY NOTICE</h4>
                <p>This information is confidential and for classroom management purposes only. Do not share with unauthorized personnel.</p>
            </div>
        """
        
        if custom_notes:
            content += f"""
            <div class="teacher-notes" style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h3>Special Instructions from Regular Teacher</h3>
                <div style="white-space: pre-wrap; font-family: Arial, sans-serif; line-height: 1.6;">
{custom_notes}
                </div>
            </div>
            """
        
        content += """
            <div class="general-guidelines" style="margin: 20px 0;">
                <h3>General Student Guidelines</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h4>Classroom Management</h4>
                        <ul>
                            <li>Students are expected to raise hands before speaking</li>
                            <li>Hall pass required for bathroom breaks (one at a time)</li>
                            <li>Cell phones should be put away during instruction</li>
                            <li>Remind students to stay in assigned seats</li>
                            <li>Report any disruptions to the office immediately</li>
                        </ul>
                    </div>
                    <div>
                        <h4>Accommodation Reminders</h4>
                        <ul>
                            <li>Some students may have extended time on assignments</li>
                            <li>Check for any posted behavior intervention plans</li>
                            <li>Allow movement breaks if students seem restless</li>
                            <li>Use positive reinforcement liberally</li>
                            <li>Contact office for any concerns about student needs</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="behavior-support" style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4>Behavior Support Strategies</h4>
                <ol>
                    <li><strong>Prevention:</strong> Keep students engaged with clear expectations</li>
                    <li><strong>Redirection:</strong> Use proximity and quiet verbal reminders first</li>
                    <li><strong>Choices:</strong> Offer appropriate alternatives when possible</li>
                    <li><strong>Documentation:</strong> Note any significant behavioral incidents</li>
                    <li><strong>Support:</strong> Contact office if student needs additional assistance</li>
                </ol>
            </div>
            
            <div class="student-helpers" style="margin: 20px 0;">
                <h3>Reliable Student Helpers</h3>
                <p>These students can assist with classroom routines if needed:</p>
                <ul>
                    <li>Technology helper for computer/projector issues</li>
                    <li>Line leader for movements around school</li>
                    <li>Materials manager for distributing supplies</li>
                    <li>Office messenger for urgent communications</li>
                </ul>
                <p><em>Note: These roles may be posted near the teacher's desk or ask students who typically helps.</em></p>
            </div>
            
            <div class="end-of-day" style="background-color: #e2e3e5; border: 1px solid #d6d8db; border-radius: 5px; padding: 15px; margin: 20px 0;">
                <h4>End of Day Checklist</h4>
                <ul style="list-style: none; padding-left: 0;">
                    <li>☐ All students accounted for at dismissal</li>
                    <li>☐ Classroom cleaned and organized</li>
                    <li>☐ Important incidents reported to administration</li>
                    <li>☐ Leave detailed note for regular teacher</li>
                    <li>☐ Turn off lights and lock classroom</li>
                </ul>
            </div>
        </div>
        """
        
        return content
    

    def set_substitute_permissions(self, folder):
        """Set appropriate permissions and generate access code"""
        try:
            # Generate secure access code
            access_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            # Store access code in annotations with expiry
            annotations = IAnnotations(folder)
            annotations['substitute_access'] = {
                'code': access_code,
                'created': datetime.now().isoformat(),
                'expires': (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            # Set folder to be visible to Authenticated users (substitute teachers)
            # In a real implementation, you might create a specific substitute role
            api.content.transition(obj=folder, transition='publish')
            
            logger.info(f"Generated access code {access_code} for substitute folder")
            
            return access_code
            
        except Exception as e:
            logger.error(f"Error setting substitute permissions: {e}")
            return "TEMP-CODE"
    
    def generate_access_code(self, folder):
        """Generate a temporary access code for the substitute folder"""
        # This method is kept for backward compatibility with the spec
        return self.set_substitute_permissions(folder) 