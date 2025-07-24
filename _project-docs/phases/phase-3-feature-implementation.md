
# Phase 3: Advanced Features & Integration

## Scope
Implement Features 5-7 (Lesson Timer Widget, Substitute Folder Generator, Teacher Dashboard) building on Phase 2's foundation. These features complete the classroom management platform by adding time management, emergency preparation, and real-time monitoring capabilities. Focus on practical classroom integration and teacher efficiency.

## Deliverables
- Feature 5: Lesson Timer Widget with audio alerts
- Feature 6: Substitute Folder Generator for emergency preparation
- Feature 7: Teacher Dashboard aggregating all classroom data
- Performance benchmarks for real-time updates
- Integration tests verifying feature synergies

## Tasks/Features

### Feature 5: Lesson Timer Widget
**Implementation Path**: JavaScript widget + localStorage persistence + Web Audio API

#### Sub-Feature 5.1: Backend Timer Support
1. **Create browser view for timer presets** in `backend/src/project/title/browser/`:
   ```python
   # timer_presets.py
   from Products.Five.browser import BrowserView
   from plone import api
   import json
   
   class TimerPresetsView(BrowserView):
       """Manage timer presets for common activities"""
       
       DEFAULT_PRESETS = [
           {'name': 'Quick Activity', 'duration': 300},    # 5 minutes
           {'name': 'Group Work', 'duration': 600},        # 10 minutes
           {'name': 'Individual Work', 'duration': 900},   # 15 minutes
           {'name': 'Test/Quiz', 'duration': 1200},        # 20 minutes
       ]
       
       def __call__(self):
           if self.request.get('REQUEST_METHOD') == 'GET':
               return self.get_presets()
           elif self.request.get('REQUEST_METHOD') == 'POST':
               return self.save_preset()
       
       def get_presets(self):
           """Return timer presets"""
           annotations = IAnnotations(api.portal.get())
           presets = annotations.get('timer_presets', self.DEFAULT_PRESETS)
           
           self.request.response.setHeader('Content-Type', 'application/json')
           return json.dumps(presets)
   ```

2. **Register static resources** in `browser/configure.zcml`:
   ```xml
   <browser:resourceDirectory
     name="project.title"
     directory="static"
     />
   ```

#### Sub-Feature 5.2: Frontend Timer Widget
1. **Create timer component** in `frontend/packages/volto-project-title/src/components/Timer/`:
   ```jsx
   // LessonTimer.jsx
   import React, { useState, useEffect, useRef } from 'react';
   import { Button, Progress, Modal } from 'semantic-ui-react';
   import './LessonTimer.css';
   
   const LessonTimer = ({ presets = [] }) => {
     const [duration, setDuration] = useState(300); // 5 min default
     const [remaining, setRemaining] = useState(0);
     const [isRunning, setIsRunning] = useState(false);
     const [showFullscreen, setShowFullscreen] = useState(false);
     const intervalRef = useRef(null);
     const audioRef = useRef(null);
     
     useEffect(() => {
       // Load saved state from localStorage
       const saved = localStorage.getItem('lessonTimer');
       if (saved) {
         const { remaining: savedRemaining, isRunning: wasRunning } = JSON.parse(saved);
         setRemaining(savedRemaining);
         if (wasRunning && savedRemaining > 0) {
           startTimer();
         }
       }
     }, []);
     
     useEffect(() => {
       // Save state to localStorage
       localStorage.setItem('lessonTimer', JSON.stringify({
         remaining,
         isRunning,
         lastUpdate: Date.now()
       }));
     }, [remaining, isRunning]);
     
     const startTimer = () => {
       setIsRunning(true);
       intervalRef.current = setInterval(() => {
         setRemaining(prev => {
           if (prev <= 1) {
             endTimer();
             return 0;
           }
           
           // Warning alerts
           if (prev === 120) playSound('warning'); // 2 min
           if (prev === 60) playSound('warning');  // 1 min
           
           return prev - 1;
         });
       }, 1000);
     };
     
     const pauseTimer = () => {
       setIsRunning(false);
       if (intervalRef.current) {
         clearInterval(intervalRef.current);
       }
     };
     
     const endTimer = () => {
       pauseTimer();
       playSound('complete');
       // Visual alert
       document.body.classList.add('timer-complete');
       setTimeout(() => {
         document.body.classList.remove('timer-complete');
       }, 3000);
     };
     
     const playSound = (type) => {
       const audio = new Audio(`/++plone++project.title/sounds/${type}.mp3`);
       audio.play().catch(e => console.log('Audio play failed:', e));
     };
     
     const formatTime = (seconds) => {
       const mins = Math.floor(seconds / 60);
       const secs = seconds % 60;
       return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
     };
     
     const getProgressColor = () => {
       const percent = remaining / duration;
       if (percent > 0.5) return 'green';
       if (percent > 0.2) return 'yellow';
       return 'red';
     };
     
     return (
       <div className="lesson-timer">
         <div className="timer-display">
           <h1 className={`time ${remaining < 60 ? 'urgent' : ''}`}>
             {formatTime(remaining || duration)}
           </h1>
           <Progress
             percent={((duration - remaining) / duration) * 100}
             color={getProgressColor()}
             size="small"
           />
         </div>
         
         <div className="timer-controls">
           {!isRunning && remaining === 0 && (
             <div className="duration-selector">
               <input
                 type="number"
                 min="1"
                 max="90"
                 value={duration / 60}
                 onChange={(e) => {
                   const mins = parseInt(e.target.value) || 1;
                   setDuration(mins * 60);
                   setRemaining(mins * 60);
                 }}
               />
               <span>minutes</span>
             </div>
           )}
           
           <div className="preset-buttons">
             {presets.map(preset => (
               <Button
                 key={preset.name}
                 size="small"
                 onClick={() => {
                   setDuration(preset.duration);
                   setRemaining(preset.duration);
                 }}
               >
                 {preset.name}
               </Button>
             ))}
           </div>
           
           <div className="control-buttons">
             {!isRunning ? (
               <Button primary size="large" onClick={startTimer}>
                 Start Timer
               </Button>
             ) : (
               <Button secondary size="large" onClick={pauseTimer}>
                 Pause
               </Button>
             )}
             
             <Button 
               basic 
               onClick={() => {
                 pauseTimer();
                 setRemaining(0);
               }}
             >
               Reset
             </Button>
             
             <Button 
               icon="expand" 
               onClick={() => setShowFullscreen(true)}
               title="Fullscreen"
             />
           </div>
         </div>
         
         <Modal
           open={showFullscreen}
           onClose={() => setShowFullscreen(false)}
           size="fullscreen"
           className="timer-fullscreen"
         >
           <div className="fullscreen-timer">
             <h1 className="huge-time">{formatTime(remaining)}</h1>
             <Button onClick={() => setShowFullscreen(false)}>
               Exit Fullscreen
             </Button>
           </div>
         </Modal>
       </div>
     );
   };
   ```

2. **Style for visibility** in `LessonTimer.css`:
   ```css
   .lesson-timer {
     background: white;
     border-radius: 12px;
     padding: 24px;
     box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
   }
   
   .timer-display .time {
     font-size: 4rem;
     font-weight: 700;
     font-variant-numeric: tabular-nums;
     text-align: center;
     margin: 0;
     transition: color 0.3s;
   }
   
   .timer-display .time.urgent {
     color: #dc2626;
     animation: pulse 1s infinite;
   }
   
   @keyframes pulse {
     0%, 100% { opacity: 1; }
     50% { opacity: 0.5; }
   }
   
   .timer-complete {
     animation: flash 0.5s 3;
   }
   
   @keyframes flash {
     0%, 100% { background: white; }
     50% { background: #fee2e2; }
   }
   
   .fullscreen-timer {
     display: flex;
     flex-direction: column;
     align-items: center;
     justify-content: center;
     height: 100vh;
     background: white;
   }
   
   .fullscreen-timer .huge-time {
     font-size: 20vw;
     font-weight: 700;
     margin: 0;
   }
   ```

### Feature 6: Substitute Folder Generator
**Implementation Path**: Browser view + content aggregation + template system

#### Sub-Feature 6.1: Backend Folder Generation
1. **Create generator view** in `backend/src/project/title/browser/`:
   ```python
   # substitute_folder.py
   from Products.Five.browser import BrowserView
   from plone import api
   from datetime import datetime, timedelta
   import transaction
   
   class SubstituteFolderGenerator(BrowserView):
       """Generate organized folder for substitute teachers"""
       
       def __call__(self):
           if self.request.get('generate'):
               return self.generate_folder()
           return self.index()
       
       def generate_folder(self):
           """Create substitute folder with today's materials"""
           # Create folder with today's date
           date_str = datetime.now().strftime('%Y-%m-%d')
           folder_id = f'substitute-{date_str}'
           folder_title = f'Substitute Materials - {date_str}'
           
           portal = api.portal.get()
           
           # Check if folder already exists
           if folder_id in portal:
               folder = portal[folder_id]
           else:
               with api.env.adopt_roles(['Manager']):
                   folder = api.content.create(
                       container=portal,
                       type='Folder',
                       id=folder_id,
                       title=folder_title
                   )
           
           # Create standard sections
           sections = [
               ('schedule', 'Daily Schedule', self.get_schedule_content()),
               ('seating-charts', 'Seating Charts', self.get_seating_charts()),
               ('lesson-plans', "Today's Lessons", self.get_todays_lessons()),
               ('emergency', 'Emergency Procedures', self.get_emergency_info()),
               ('contacts', 'Important Contacts', self.get_contacts()),
               ('student-info', 'Special Student Information', self.get_student_info()),
           ]
           
           for section_id, section_title, content_html in sections:
               if section_id not in folder:
                   doc = api.content.create(
                       container=folder,
                       type='Document',
                       id=section_id,
                       title=section_title
                   )
                   doc.text = api.content.RichTextValue(
                       content_html,
                       'text/html',
                       'text/x-html-safe'
                   )
           
           # Copy relevant content
           self.copy_classroom_materials(folder)
           
           # Set permissions for substitute access
           self.set_substitute_permissions(folder)
           
           transaction.commit()
           
           # Generate access code
           access_code = self.generate_access_code(folder)
           
           self.request.response.redirect(
               f"{folder.absolute_url()}?access_code={access_code}"
           )
       
       def get_schedule_content(self):
           """Generate daily schedule HTML"""
           # In real implementation, pull from calendar/schedule system
           return """
           <h2>Daily Schedule</h2>
           <table class="schedule">
             <tr><td>8:00-8:50</td><td>Period 1 - Math (Room 201)</td></tr>
             <tr><td>8:55-9:45</td><td>Period 2 - Science (Room 201)</td></tr>
             <tr><td>9:50-10:40</td><td>Period 3 - English (Room 201)</td></tr>
             <tr><td>10:45-11:30</td><td>Lunch</td></tr>
             <tr><td>11:35-12:25</td><td>Period 4 - History (Room 201)</td></tr>
             <tr><td>12:30-1:20</td><td>Period 5 - PE (Gym)</td></tr>
             <tr><td>1:25-2:15</td><td>Period 6 - Art (Room 201)</td></tr>
           </table>
           """
       
       def get_seating_charts(self):
           """Include links to seating charts"""
           catalog = api.portal.get_tool('portal_catalog')
           charts = catalog(portal_type='SeatingChart')
           
           html = "<h2>Seating Charts</h2><ul>"
           for brain in charts:
               chart = brain.getObject()
               html += f'<li><a href="{chart.absolute_url()}">{chart.title}</a></li>'
           html += "</ul>"
           return html
       
       def copy_classroom_materials(self, folder):
           """Copy seating charts and other materials"""
           catalog = api.portal.get_tool('portal_catalog')
           
           # Copy active seating charts
           charts = catalog(portal_type='SeatingChart')
           for brain in charts:
               chart = brain.getObject()
               api.content.copy(
                   source=chart,
                   target=folder['seating-charts'],
                   safe_id=True
               )
   ```

2. **Create template page** for substitute instructions

#### Sub-Feature 6.2: Frontend Generation Interface
1. **Create generator component**:
   ```jsx
   // SubstituteGenerator.jsx
   import React, { useState } from 'react';
   import { Button, Form, Message, Segment } from 'semantic-ui-react';
   
   const SubstituteGenerator = () => {
     const [generating, setGenerating] = useState(false);
     const [accessCode, setAccessCode] = useState('');
     const [customNotes, setCustomNotes] = useState('');
     
     const generateFolder = async () => {
       setGenerating(true);
       
       try {
         const response = await fetch('/@@generate-substitute-folder', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
             generate: true,
             notes: customNotes
           })
         });
         
         const data = await response.json();
         setAccessCode(data.access_code);
         
         // Show success message
         toast.success('Substitute folder created!');
       } catch (error) {
         toast.error('Failed to generate folder');
       } finally {
         setGenerating(false);
       }
     };
     
     return (
       <Segment className="substitute-generator">
         <h2>Prepare for Substitute Teacher</h2>
         
         <Form>
           <Form.TextArea
             label="Additional Notes for Substitute"
             placeholder="Special instructions, behavior notes, etc."
             value={customNotes}
             onChange={(e, { value }) => setCustomNotes(value)}
             rows={4}
           />
           
           <Button
             primary
             size="large"
             loading={generating}
             onClick={generateFolder}
           >
             Generate Substitute Folder
           </Button>
         </Form>
         
         {accessCode && (
           <Message positive>
             <Message.Header>Folder Created Successfully!</Message.Header>
             <p>Access Code for Substitute: <strong>{accessCode}</strong></p>
             <p>This code expires in 24 hours</p>
           </Message>
         )}
         
         <div className="checklist">
           <h3>What's Included:</h3>
           <ul>
             <li>✓ Today's schedule</li>
             <li>✓ Current seating charts</li>
             <li>✓ Lesson plans</li>
             <li>✓ Emergency procedures</li>
             <li>✓ Important contacts</li>
             <li>✓ Special student information</li>
           </ul>
         </div>
       </Segment>
     );
   };
   ```

### Feature 7: Teacher's Daily Command Center Dashboard
**Implementation Path**: Browser view + real-time aggregation + widget system

#### Sub-Feature 7.1: Backend Dashboard Aggregation
1. **Create dashboard view** in `backend/src/project/title/browser/`:
   ```python
   # dashboard.py
   from Products.Five.browser import BrowserView
   from plone import api
   from datetime import datetime, timedelta
   import json
   
   class TeacherDashboard(BrowserView):
       """Real-time classroom command center"""
       
       def __call__(self):
           if self.request.get('ajax_update'):
               return self.get_dashboard_data()
           return self.index()
       
       def get_dashboard_data(self):
           """Aggregate all classroom management data"""
           catalog = api.portal.get_tool('portal_catalog')
           
           data = {
               'timestamp': datetime.now().isoformat(),
               'seating': self.get_current_seating(),
               'hall_passes': self.get_active_passes(),
               'participation': self.get_participation_stats(),
               'timers': self.get_active_timers(),
               'alerts': self.get_classroom_alerts(),
               'quick_stats': self.get_quick_stats()
           }
           
           self.request.response.setHeader('Content-Type', 'application/json')
           return json.dumps(data)
       
       def get_current_seating(self):
           """Get active seating chart info"""
           catalog = api.portal.get_tool('portal_catalog')
           charts = catalog(
               portal_type='SeatingChart',
               sort_on='modified',
               sort_order='descending',
               sort_limit=1
           )
           
           if charts:
               chart = charts[0].getObject()
               return {
                   'title': chart.title,
                   'student_count': len(chart.students or []),
                   'last_modified': chart.modified().ISO8601(),
                   'url': chart.absolute_url()
               }
           return None
       
       def get_active_passes(self):
           """Get unreturned hall passes"""
           catalog = api.portal.get_tool('portal_catalog')
           now = datetime.now()
           
           # Get passes issued today without return time
           passes = catalog(
               portal_type='HallPass',
               created={'query': now.date(), 'range': 'min'}
           )
           
           active = []
           for brain in passes:
               pass_obj = brain.getObject()
               if not pass_obj.return_time:
                   duration = (now - pass_obj.issue_time).seconds // 60
                   
                   active.append({
                       'id': pass_obj.getId(),
                       'student': pass_obj.student_name,
                       'destination': pass_obj.destination,
                       'duration': duration,
                       'alert_level': self.get_alert_level(duration),
                       'url': pass_obj.absolute_url()
                   })
           
           return sorted(active, key=lambda x: x['duration'], reverse=True)
       
       def get_alert_level(self, duration):
           """Determine alert level based on duration"""
           if duration > 15:
               return 'red'
           elif duration > 10:
               return 'yellow'
           return 'green'
       
       def get_participation_stats(self):
           """Get today's participation statistics"""
           annotations = IAnnotations(api.portal.get())
           today_key = f"participation_{datetime.now().date()}"
           stats = annotations.get(today_key, {})
           
           # Calculate fairness score
           if stats:
               picks = list(stats.values())
               avg = sum(picks) / len(picks) if picks else 0
               variance = sum((p - avg) ** 2 for p in picks) / len(picks) if picks else 0
               fairness = 100 - min(variance * 10, 100)  # Simple fairness metric
           else:
               fairness = 100
           
           return {
               'total_picks': sum(stats.values()) if stats else 0,
               'unique_students': len(stats),
               'fairness_score': round(fairness, 1),
               'most_picked': max(stats.items(), key=lambda x: x[1])[0] if stats else None,
               'least_picked': min(stats.items(), key=lambda x: x[1])[0] if stats else None
           }
       
       def get_classroom_alerts(self):
           """Generate relevant alerts for teacher"""
           alerts = []
           
           # Check for long hall passes
           passes = self.get_active_passes()
           for p in passes:
               if p['alert_level'] == 'red':
                   alerts.append({
                       'type': 'warning',
                       'message': f"{p['student']} has been out for {p['duration']} minutes",
                       'action': 'Check on student',
                       'priority': 'high'
                   })
           
           # Remind about substitute folder
           if datetime.now().hour >= 15:  # After 3 PM
               alerts.append({
                   'type': 'info',
                   'message': 'Remember to generate substitute folder if needed',
                   'action': 'Generate Folder',
                   'priority': 'low'
               })
           
           return alerts
   ```

#### Sub-Feature 7.2: Frontend Dashboard Interface
1. **Create dashboard component**:
   ```jsx
   // TeacherDashboard.jsx
   import React, { useState, useEffect } from 'react';
   import { Grid, Segment, Statistic, Label, Message } from 'semantic-ui-react';
   import { SeatingWidget } from './widgets/SeatingWidget';
   import { HallPassWidget } from './widgets/HallPassWidget';
   import { ParticipationWidget } from './widgets/ParticipationWidget';
   import { AlertsWidget } from './widgets/AlertsWidget';
   import { QuickActionsWidget } from './widgets/QuickActionsWidget';
   
   const TeacherDashboard = () => {
     const [dashboardData, setDashboardData] = useState(null);
     const [loading, setLoading] = useState(true);
     
     useEffect(() => {
       // Initial load
       fetchDashboardData();
       
       // Set up polling for real-time updates
       const interval = setInterval(fetchDashboardData, 30000); // 30 seconds
       
       return () => clearInterval(interval);
     }, []);
     
     const fetchDashboardData = async () => {
       try {
         const response = await fetch('/@@teacher-dashboard?ajax_update=1');
         const data = await response.json();
         setDashboardData(data);
         setLoading(false);
       } catch (error) {
         console.error('Dashboard update failed:', error);
       }
     };
     
     if (loading) return <div>Loading dashboard...</div>;
     
     return (
       <div className="teacher-dashboard">
         <h1>Classroom Command Center</h1>
         
         {/* Quick Stats Bar */}
         <Segment className="stats-bar">
           <Statistic.Group size="small" widths="four">
             <Statistic>
               <Statistic.Value>
                 {dashboardData.quick_stats.students_present}
               </Statistic.Value>
               <Statistic.Label>Students Present</Statistic.Label>
             </Statistic>
             
             <Statistic 
               color={dashboardData.hall_passes.length > 2 ? 'yellow' : 'green'}
             >
               <Statistic.Value>
                 {dashboardData.hall_passes.length}
               </Statistic.Value>
               <Statistic.Label>Active Passes</Statistic.Label>
             </Statistic>
             
             <Statistic>
               <Statistic.Value>
                 {dashboardData.participation.fairness_score}%
               </Statistic.Value>
               <Statistic.Label>Participation Fairness</Statistic.Label>
             </Statistic>
             
             <Statistic>
               <Statistic.Value>
                 {new Date().toLocaleTimeString([], {
                   hour: '2-digit',
                   minute: '2-digit'
                 })}
               </Statistic.Value>
               <Statistic.Label>Current Time</Statistic.Label>
             </Statistic>
           </Statistic.Group>
         </Segment>
         
         {/* Alerts Section */}
         {dashboardData.alerts.length > 0 && (
           <AlertsWidget alerts={dashboardData.alerts} />
         )}
         
         {/* Main Dashboard Grid */}
         <Grid columns={3} stackable>
           <Grid.Column width={6}>
             <SeatingWidget data={dashboardData.seating} />
             <ParticipationWidget data={dashboardData.participation} />
           </Grid.Column>
           
           <Grid.Column width={6}>
             <HallPassWidget passes={dashboardData.hall_passes} />
             <QuickActionsWidget />
           </Grid.Column>
           
           <Grid.Column width={4}>
             <TimerWidget />
             <SubstituteWidget />
           </Grid.Column>
         </Grid>
       </div>
     );
   };
   ```

2. **Create dashboard widgets**:
   ```jsx
   // widgets/HallPassWidget.jsx
   export const HallPassWidget = ({ passes }) => {
     return (
       <Segment className="dashboard-widget hall-pass-widget">
         <h3>Active Hall Passes</h3>
         
         {passes.length === 0 ? (
           <p>No students out of class</p>
         ) : (
           <div className="pass-list">
             {passes.map(pass => (
               <div key={pass.id} className={`pass-item ${pass.alert_level}`}>
                 <div className="student-name">{pass.student}</div>
                 <div className="pass-details">
                   <Label size="tiny">{pass.destination}</Label>
                   <Label 
                     size="tiny" 
                     color={
                       pass.alert_level === 'red' ? 'red' : 
                       pass.alert_level === 'yellow' ? 'yellow' : 
                       'green'
                     }
                   >
                     {pass.duration} min
                   </Label>
                 </div>
               </div>
             ))}
           </div>
         )}
       </Segment>
     );
   };
   ```

### Task 1: Feature Integration & Performance

1. **Integration points**:
   - Timer state persists across page refreshes
   - Dashboard pulls data from all features
   - Substitute folder includes current seating charts
   - Hall pass alerts show on dashboard

2. **Performance optimization**:
   ```python
   # Use caching for expensive queries
   from plone.memoize import ram
   
   @ram.cache(lambda *args: time() // 30)  # 30-second cache
   def get_dashboard_data(self):
       """Cache dashboard queries"""
       # Implementation
   ```

3. **Real-time updates**:
   - Dashboard polls every 30 seconds
   - Timer updates every second locally
   - Hall pass durations update in real-time

## Impacted Files and Directories
- **Backend Structure**:
  - `backend/src/project/title/browser/` - Views for all features
  - `backend/src/project/title/browser/static/` - Sounds and assets
  - `backend/src/project/title/browser/templates/` - Page templates
  
- **Frontend Structure**:
  - `frontend/packages/volto-project-title/src/components/Timer/` - Timer widget
  - `frontend/packages/volto-project-title/src/components/Dashboard/` - Dashboard
  - `frontend/packages/volto-project-title/src/components/Dashboard/widgets/` - Dashboard widgets

## Review Checklist
- [ ] Timer persists state correctly
- [ ] Audio alerts work on all browsers
- [ ] Substitute folder includes all materials
- [ ] Dashboard updates show real-time data
- [ ] All features integrate smoothly
- [ ] Performance targets met
- [ ] Mobile/tablet experience optimal

## Rules Adherence
- ZCA patterns for all browser views
- Progressive enhancement for JavaScript
- File size limits respected (<500 lines)
- Clear separation of concerns
- AI-friendly code organization

## Time Estimates
- Feature 5 (Timer): 5-6 hours
- Feature 6 (Sub Folder): 4-5 hours
- Feature 7 (Dashboard): 8-10 hours
- Integration & Testing: 3-4 hours
- **Total**: 20-25 hours (3 days)

## Risk Mitigation
1. **Audio compatibility**: Provide visual alerts as fallback
2. **localStorage reliability**: Server-side backup for critical data
3. **Performance at scale**: Implement caching early
4. **Dashboard complexity**: Start with essential widgets, add more later

## Dependencies on Phase 2
- Seating charts (Feature 2) used in dashboard and sub folder
- Hall passes (Feature 4) shown on dashboard
- Random picker (Feature 3) stats in participation widget

## Iteration Notes
These features complete the classroom management platform. The dashboard ties everything together, providing teachers with a real-time command center. Phase 4 will focus on polish, testing, and AWS deployment. 