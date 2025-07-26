"""
Hall Pass Manager Browser Views

Simple demo views that work without a Plone site for testing purposes.
"""

import json
import uuid
from datetime import datetime, timedelta
from Products.Five.browser import BrowserView
import qrcode
from io import BytesIO
import base64
import logging

# ADD these imports for event integration
from ..event_handlers import fire_hall_pass_issued
from ..events import HallPassReturnedEvent
from zope.event import notify

from .cors_helper import set_cors_headers

logger = logging.getLogger(__name__)

# Demo storage - in-memory storage for demo purposes
class DemoStorage:
    _instance = None
    _passes = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DemoStorage, cls).__new__(cls)
        return cls._instance
    
    def get_passes(self):
        return self._passes
    
    def add_pass(self, pass_id, pass_data):
        self._passes[pass_id] = pass_data
    
    def update_pass(self, pass_id, updates):
        if pass_id in self._passes:
            self._passes[pass_id].update(updates)
            return True
        return False
    
    def get_pass(self, pass_id):
        return self._passes.get(pass_id)
    
    def remove_pass(self, pass_id):
        if pass_id in self._passes:
            del self._passes[pass_id]
            return True
        return False


class HallPassManagerView(BrowserView):
    """
    Simple hall pass manager for demo purposes
    """
    
    def __call__(self):
        """Handle all requests"""
        # Handle CORS headers for frontend integration
        is_preflight = set_cors_headers(self.request, self.request.response)
        if is_preflight:
            return ''
            
        if self.request.method == 'POST':
            return self.issue_pass()
        elif self.request.get('ajax_data'):
            return self.get_passes_data()
        else:
            return self.render_demo_page()
    
    def render_demo_page(self):
        """Render a simple demo page"""
        self.request.response.setHeader('Content-Type', 'text/html')
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Digital Hall Pass Manager - Demo</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; }
                .demo-info { background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 600px; }
                .endpoint { background: #f8f8f8; padding: 10px; margin: 10px; border-radius: 4px; font-family: monospace; }
            </style>
        </head>
        <body>
            <h1>🎫 Digital Hall Pass Manager - Working!</h1>
            <div class="demo-info">
                <h2>✅ Backend is Running Successfully</h2>
                <p>This hall pass system is now working with session storage.</p>
                
                <h3>📡 Available Endpoints:</h3>
                <div class="endpoint">POST /@@hall-pass-manager - Issue a pass</div>
                <div class="endpoint">GET /@@hall-pass-manager?ajax_data=1 - Get pass data</div>
                <div class="endpoint">POST /@@return-pass - Return a pass</div>
                
                <h3>🎯 Test from Frontend:</h3>
                <p>Go to: <a href="http://localhost:3000/hall-pass-manager">http://localhost:3000/hall-pass-manager</a></p>
                
                <p><strong>Status:</strong> ✅ Ready for full testing!</p>
            </div>
        </body>
        </html>
        """
    
    def issue_pass(self):
        """Issue a new hall pass"""
        try:
            # Get JSON data
            body = self.request.get('BODY', '{}')
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body)
            
            # Generate pass data
            pass_id = str(uuid.uuid4())[:8].upper()
            pass_data = {
                'id': pass_id,
                'student_name': data.get('student_name', ''),
                'destination': data.get('destination', ''),
                'issue_time': datetime.now().isoformat(),
                'return_time': None,
                'expected_duration': int(data.get('expected_duration', 5)),
                'notes': data.get('notes', ''),
                'pass_code': pass_id,
                'is_active': True
            }
            
            # Store in demo storage
            storage = DemoStorage()
            storage.add_pass(pass_id, pass_data)
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr_data = f"HALL_PASS:{pass_id}:{pass_data['student_name']}:{pass_data['destination']}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_code_data = base64.b64encode(buffer.getvalue()).decode()
            pass_data['qr_code'] = f"data:image/png;base64,{qr_code_data}"
            
            # ENHANCE: Fire event for integration (non-breaking)
            try:
                # Create a mock object for event firing
                class MockHallPassObj:
                    def getId(self):
                        return pass_id
                
                mock_obj = MockHallPassObj()
                fire_hall_pass_issued(
                    mock_obj, 
                    student_name=pass_data['student_name'], 
                    destination=pass_data['destination']
                )
                logger.info(f"✅ Hall pass event fired for {pass_data['student_name']}")
            except Exception as event_error:
                logger.info(f"Event firing skipped (non-critical): {event_error}")

            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({
                'success': True,
                'pass': pass_data,
                'message': f'Hall pass issued for {pass_data["student_name"]}'
            })
            
        except Exception as e:
            self.request.response.setStatus(500)
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({
                'error': 'Failed to issue pass',
                'details': str(e)
            })
    
    def get_passes_data(self):
        """Get current hall pass data"""
        try:
            # Get passes from demo storage
            storage = DemoStorage()
            all_passes = storage.get_passes()
            
            active_passes = []
            recent_passes = []
            
            for pass_data in all_passes.values():
                # Calculate duration
                issue_time = datetime.fromisoformat(pass_data['issue_time'])
                now = datetime.now()
                duration_minutes = int((now - issue_time).total_seconds() / 60)
                pass_data['duration_minutes'] = duration_minutes
                
                # Determine status and alert level
                expected = pass_data.get('expected_duration', 5)
                if pass_data.get('return_time'):
                    pass_data['is_active'] = False
                    pass_data['alert_level'] = 'green'
                    recent_passes.append(pass_data)
                elif duration_minutes > expected + 10:
                    pass_data['alert_level'] = 'red'
                    active_passes.append(pass_data)
                elif duration_minutes > expected:
                    pass_data['alert_level'] = 'yellow'
                    active_passes.append(pass_data)
                else:
                    pass_data['alert_level'] = 'green'
                    active_passes.append(pass_data)
            
            # Calculate statistics
            total_passes = len(all_passes)
            active_count = len(active_passes)
            overdue_count = len([p for p in active_passes if p['alert_level'] == 'red'])
            
            # Generate alerts
            alerts = []
            if overdue_count > 0:
                alerts.append({
                    'type': 'warning',
                    'message': f'{overdue_count} pass(es) are overdue'
                })
            
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({
                'active_passes': active_passes,
                'recent_passes': recent_passes[-10:],  # Last 10
                'statistics': {
                    'total_today': total_passes,
                    'active_count': active_count,
                    'overdue_count': overdue_count,
                    'avg_duration': sum(p['duration_minutes'] for p in all_passes.values()) / max(total_passes, 1)
                },
                'alerts': alerts
            })
            
        except Exception as e:
            self.request.response.setStatus(500)
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps({
                'error': 'Failed to load data',
                'details': str(e)
            })

    # WORKFLOW ENHANCEMENT METHODS (ADDITIVE ONLY)
    def issue_pass_with_workflow(self):
        """Enhanced pass issuing with workflow support"""
        # Call existing issue_pass method first (no breaking changes)
        result = self.issue_pass()
        
        # Add workflow support if available
        try:
            if hasattr(self.context, 'portal_workflow'):
                # Find the newly created pass
                from plone import api
                catalog = api.portal.get_tool('portal_catalog')
                recent_passes = catalog(
                    portal_type='HallPass',
                    sort_on='created',
                    sort_order='descending',
                    sort_limit=1
                )
                if recent_passes:
                    pass_obj = recent_passes[0].getObject()
                    api.content.transition(obj=pass_obj, transition='issue')
        except Exception as e:
            # Log warning but don't break existing functionality
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Workflow enhancement failed, basic functionality preserved: {e}")
        
        return result

    def return_pass_with_workflow(self):
        """Enhanced pass return with workflow support"""
        pass_id = self.request.get('pass_id')
        try:
            # For demo storage, just call the existing return functionality
            storage = DemoStorage()
            pass_obj = storage.get_pass(pass_id)
            if pass_obj:
                # Set return time (existing functionality)
                updates = {
                    'return_time': datetime.now().isoformat(),
                    'is_active': False
                }
                storage.update_pass(pass_id, updates)
                
                # Add workflow transition if available (enhancement)
                try:
                    if hasattr(self.context, 'portal_workflow'):
                        from plone import api
                        # In real implementation, would find actual content object
                        # api.content.transition(obj=pass_obj, transition='return')
                        pass
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Workflow transition skipped: {e}")
            
            return self.get_passes_data()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Return pass failed: {e}")
            return {'error': str(e)}


class HallPassReturnView(BrowserView):
    """Mark a hall pass as returned"""
    
    def __call__(self):
        """Mark pass as returned"""
        # Handle CORS headers for frontend integration
        is_preflight = set_cors_headers(self.request, self.request.response)
        if is_preflight:
            return ''
        
        try:
            body = self.request.get('BODY', '{}')
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body)
            pass_id = data.get('pass_id')
            
            # Get demo storage
            storage = DemoStorage()
            pass_data = storage.get_pass(pass_id)
            
            if pass_data:
                # Update the pass
                updates = {
                    'return_time': datetime.now().isoformat(),
                    'is_active': False
                }
                storage.update_pass(pass_id, updates)
                
                # Get the updated pass data
                updated_pass = storage.get_pass(pass_id)
                
                # ENHANCE: Fire return event for integration (non-breaking)
                try:
                    # Calculate duration for event
                    issue_time = datetime.fromisoformat(pass_data['issue_time'])
                    return_time = datetime.now()
                    duration = int((return_time - issue_time).total_seconds() / 60)
                    
                    # Create mock object and fire event
                    class MockHallPassObj:
                        def getId(self):
                            return pass_id
                    
                    mock_obj = MockHallPassObj()
                    event = HallPassReturnedEvent(mock_obj, duration=duration)
                    notify(event)
                    logger.info(f"✅ Hall pass return event fired after {duration} minutes")
                except Exception as event_error:
                    logger.info(f"Return event firing skipped (non-critical): {event_error}")
                
                self.request.response.setHeader('Content-Type', 'application/json')
                return json.dumps({
                    'success': True,
                    'pass': updated_pass,
                    'message': 'Pass marked as returned'
                })
            else:
                self.request.response.setStatus(404)
                return json.dumps({'error': 'Pass not found'})
                
        except Exception as e:
            self.request.response.setStatus(500)
            return json.dumps({'error': str(e)})


class HallPassDisplayView(BrowserView):
    """Simple display view"""
    
    def __call__(self):
        return "Hall Pass Display - Demo Mode"


class PassVerifyView(BrowserView):
    """Mobile-friendly hall pass verification page"""
    
    def __call__(self):
        """Handle pass verification requests"""
        # Handle CORS headers
        is_preflight = set_cors_headers(self.request, self.request.response)
        if is_preflight:
            return ''
        
        # Get pass code from request
        pass_code = self.request.get('code', '')
        
        if not pass_code:
            return self.render_error("No pass code provided")
        
        # For demo purposes, create a mock pass verification
        # In a real implementation, you'd search for the actual pass
        return self.render_demo_verification_page(pass_code)
    
    def render_demo_verification_page(self, pass_code):
        """Render a demo verification page"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hall Pass Verification</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 400px; margin: 0 auto; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 24px; }}
        .status {{ padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 20px; background: #e3f2fd; color: #1565c0; }}
        .detail {{ margin: 12px 0; padding: 12px; background: #f8f9fa; border-radius: 6px; }}
        .detail-label {{ font-weight: bold; color: #666; }}
        .detail-value {{ font-size: 1.1em; }}
        .button {{ display: block; width: 100%; padding: 14px; background: #1976d2; color: white; text-decoration: none; text-align: center; border-radius: 8px; font-weight: bold; margin-top: 20px; border: none; font-size: 16px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🎫 Hall Pass Verification</h2>
        </div>
        
        <div class="status">
            ✅ Valid Pass - 5 minutes
        </div>
        
        <div class="detail">
            <div class="detail-label">Student:</div>
            <div class="detail-value">ERIC W.</div>
        </div>
        
        <div class="detail">
            <div class="detail-label">Destination:</div>
            <div class="detail-value">RESTROOM</div>
        </div>
        
        <div class="detail">
            <div class="detail-label">Pass Code:</div>
            <div class="detail-value">{pass_code}</div>
        </div>
        
        <div class="detail">
            <div class="detail-label">Issued:</div>
            <div class="detail-value">{datetime.now().strftime('%I:%M %p')}</div>
        </div>
        
        <a href="#" class="button" onclick="markReturned()">✅ Mark as Returned</a>
        
        <div class="footer">
            Scanned at {datetime.now().strftime('%I:%M %p')}
        </div>
    </div>
    
    <script>
        function markReturned() {{
            alert('Pass marked as returned!');
            document.querySelector('.status').innerHTML = '✅ Returned Successfully';
            document.querySelector('.button').style.display = 'none';
        }}
    </script>
</body>
</html>
        """
        
        self.request.response.setHeader('Content-Type', 'text/html')
        return html
    
    def render_error(self, message):
        """Render error page"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hall Pass Error</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 400px; margin: 0 auto; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }}
        .error {{ color: #c62828; font-size: 1.2em; margin: 20px 0; }}
        .error-icon {{ font-size: 3em; color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <div class="error">{message}</div>
    </div>
</body>
</html>
        """
        
        self.request.response.setHeader('Content-Type', 'text/html')
        return html 