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
        # CORS headers - specific origin when using credentials
        self.request.response.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.request.response.setHeader('Access-Control-Allow-Credentials', 'true')
        self.request.response.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.request.response.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept')
        
        if self.request.method == 'OPTIONS':
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


class HallPassReturnView(BrowserView):
    """Mark a hall pass as returned"""
    
    def __call__(self):
        """Mark pass as returned"""
        # CORS headers - specific origin when using credentials
        self.request.response.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.request.response.setHeader('Access-Control-Allow-Credentials', 'true')
        self.request.response.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.request.response.setHeader('Access-Control-Allow-Headers', 'Content-Type')
        
        if self.request.method == 'OPTIONS':
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