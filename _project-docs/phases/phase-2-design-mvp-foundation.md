
# Phase 2: Core Classroom Management Features

## Scope
Implement Features 2-4 (Seating Chart Generator, Random Student Picker, Digital Hall Pass) leveraging existing cookieplone structure with Volto frontend and Plone backend. This phase delivers functional classroom management tools that address daily teacher pain points with visual, interactive interfaces.

## Deliverables
- Feature 1: Google SSO ✅ ALREADY COMPLETE
- Feature 2: Seating Chart Generator with drag-drop interface ✅ COMPLETE
- Feature 3: Random Student Picker with fairness algorithm ✅ COMPLETE
- Feature 4: Digital Hall Pass system with QR codes ✅ COMPLETE
- Working MVP demonstrating real-time classroom value

## Tasks/Features

### Task 1: Frontend-Backend Integration Verification ✅ COMPLETE
- Plone backend running on http://localhost:8080
- Volto frontend running on http://localhost:3000
- REST API communication verified
- Frontend Makefile includes `RAZZLE_API_PATH=http://localhost:8080/Plone`

### Feature 1: Google SSO ✅ COMPLETE
- Backend OAuth configuration with pas.plugins.authomatic
- Frontend custom login component with Google button
- Redux integration for authentication flow
- Production-ready with environment variables

### Feature 2: Seating Chart Generator ✅ COMPLETE
**Implementation Path**: Dexterity content type + JSON storage + React drag-drop interface

#### Sub-Feature 2.1: Backend Content Type
1. **Create content type** in `backend/src/project/title/content/`:
   ```python
   # seating_chart.py
   from plone.dexterity.content import Container
   from plone.supermodel import model
   from zope import schema
   import json
   
   class ISeatingChart(model.Schema):
       """Seating chart with drag-drop student positioning"""
       
       title = schema.TextLine(
           title=u"Class Name",
           required=True
       )
       
       grid_data = schema.Text(
           title=u"Seating Grid Data",
           description=u"JSON data storing student positions",
           required=False,
           default=u'{"rows": 5, "cols": 6, "students": {}}'
       )
       
       students = schema.List(
           title=u"Class Roster",
           value_type=schema.TextLine(),
           required=False,
           default=[]
       )
   
   class SeatingChart(Container):
       """Seating chart implementation"""
       
       def get_grid(self):
           """Parse grid data as Python object"""
           return json.loads(self.grid_data or '{}')
       
       def update_position(self, student_id, row, col):
           """Update student position in grid"""
           grid = self.get_grid()
           if 'students' not in grid:
               grid['students'] = {}
           grid['students'][student_id] = {'row': row, 'col': col}
           self.grid_data = json.dumps(grid)
   ```

2. **Register in** `backend/src/project/title/content/configure.zcml`:
   ```xml
   <configure xmlns="http://namespaces.zope.org/zope"
              xmlns:plone="http://namespaces.plone.org/plone">
   
     <plone:content
       portal_type="SeatingChart"
       class=".seating_chart.SeatingChart"
       schema=".seating_chart.ISeatingChart"
       />
   
   </configure>
   ```

3. **Add to profiles** in `backend/src/project/title/profiles/default/types.xml`:
   ```xml
   <?xml version="1.0"?>
   <object name="portal_types">
     <object name="SeatingChart" meta_type="Dexterity FTI"/>
   </object>
   ```

#### Sub-Feature 2.2: Frontend Drag-Drop Interface
1. **Create view component** in `frontend/packages/volto-project-title/src/components/Views/`:
   ```jsx
   // SeatingChartView.jsx
   import React, { useState, useCallback } from 'react';
   import { DndProvider } from 'react-dnd';
   import { HTML5Backend } from 'react-dnd-html5-backend';
   import { TouchBackend } from 'react-dnd-touch-backend';
   import { Container, Button } from 'semantic-ui-react';
   
   const SeatingChartView = ({ content }) => {
     const [grid, setGrid] = useState(JSON.parse(content.grid_data || '{}'));
     const [editMode, setEditMode] = useState(false);
     
     const moveStudent = useCallback((studentId, row, col) => {
       // Update local state
       const newGrid = { ...grid };
       newGrid.students[studentId] = { row, col };
       setGrid(newGrid);
       
       // Save to backend
       fetch(`${content['@id']}/@@update-position`, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ studentId, row, col })
       });
     }, [grid, content]);
     
     const backend = 'ontouchstart' in window ? TouchBackend : HTML5Backend;
     
     return (
       <DndProvider backend={backend}>
         <Container className="seating-chart-view">
           <h1>{content.title}</h1>
           <Button onClick={() => setEditMode(!editMode)}>
             {editMode ? 'Save' : 'Edit Layout'}
           </Button>
           <SeatingGrid 
             grid={grid}
             students={content.students}
             onMove={moveStudent}
             editable={editMode}
           />
         </Container>
       </DndProvider>
     );
   };
   ```

2. **Create grid component** with drag-drop:
   ```jsx
   // SeatingGrid.jsx
   const SeatingGrid = ({ grid, students, onMove, editable }) => {
     const { rows = 5, cols = 6 } = grid;
     
     return (
       <div className="seating-grid" style={{
         display: 'grid',
         gridTemplateColumns: `repeat(${cols}, 1fr)`,
         gap: '10px',
         padding: '20px'
       }}>
         {Array.from({ length: rows * cols }, (_, index) => {
           const row = Math.floor(index / cols);
           const col = index % cols;
           return (
             <DeskSlot
               key={`${row}-${col}`}
               row={row}
               col={col}
               student={findStudentAt(grid.students, row, col)}
               onDrop={onMove}
               editable={editable}
             />
           );
         })}
       </div>
     );
   };
   ```

3. **Style for classroom feel** in `frontend/packages/volto-project-title/src/theme/SeatingChart.less`:
   ```less
   .seating-chart-view {
     .seating-grid {
       max-width: 800px;
       margin: 0 auto;
       
       .desk-slot {
         aspect-ratio: 1;
         border: 2px dashed #e5e7eb;
         border-radius: 8px;
         display: flex;
         align-items: center;
         justify-content: center;
         background: white;
         transition: all 0.2s;
         
         &.occupied {
           background: #dbeafe;
           border-color: #3b82f6;
         }
         
         &.drag-over {
           background: #ede9fe;
           transform: scale(1.05);
         }
       }
     }
   }
   ```

### Feature 3: Random Student Picker ✅ COMPLETE
**Implementation Path**: Browser view + AJAX endpoint + visual spinner animation

#### Sub-Feature 3.1: Backend Fair Selection Algorithm
1. **Create browser view** in `backend/src/project/title/browser/`:
   ```python
   # random_picker.py
   from Products.Five.browser import BrowserView
   from plone import api
   import json
   import random
   from datetime import datetime
   
   class RandomStudentPicker(BrowserView):
       """Fair random student selection with history tracking"""
       
       def __call__(self):
           if self.request.get('REQUEST_METHOD') == 'POST':
               return self.pick_student()
           return self.render()
       
       def get_students(self):
           """Get student list from context (seating chart or folder)"""
           if hasattr(self.context, 'students'):
               return self.context.students
           # Fallback to catalog search
           return self.get_students_from_catalog()
       
       def pick_student(self):
           """Select student with fairness weighting"""
           students = self.get_students()
           history = self.get_pick_history()
           
           # Weight selection by least recently picked
           weights = []
           for student in students:
               last_picked = history.get(student, 0)
               # Higher weight for students picked less recently
               weight = datetime.now().timestamp() - last_picked
               weights.append(weight)
           
           # Weighted random selection
           if students and weights:
               selected = random.choices(students, weights=weights)[0]
               
               # Update history
               history[selected] = datetime.now().timestamp()
               self.save_pick_history(history)
               
               self.request.response.setHeader('Content-Type', 'application/json')
               return json.dumps({
                   'selected': selected,
                   'timestamp': datetime.now().isoformat(),
                   'fairness_score': self.calculate_fairness(history)
               })
       
       def get_pick_history(self):
           """Retrieve picking history from annotations"""
           annotations = IAnnotations(self.context)
           return annotations.get('pick_history', {})
       
       def save_pick_history(self, history):
           """Save picking history to annotations"""
           annotations = IAnnotations(self.context)
           annotations['pick_history'] = history
   ```

2. **Register view** in `browser/configure.zcml`:
   ```xml
   <browser:page
     name="random-picker"
     for="*"
     class=".random_picker.RandomStudentPicker"
     template="random_picker.pt"
     permission="zope2.View"
     />
   ```

#### Sub-Feature 3.2: Frontend Spinner Animation
1. **Create picker component** in `frontend/packages/volto-project-title/src/components/`:
   ```jsx
   // RandomPicker.jsx
   import React, { useState } from 'react';
   import { Button, Modal } from 'semantic-ui-react';
   import './RandomPicker.css';
   
   const RandomPicker = ({ students = [] }) => {
     const [isSpinning, setIsSpinning] = useState(false);
     const [selected, setSelected] = useState(null);
     const [showModal, setShowModal] = useState(false);
     
     const spin = async () => {
       setIsSpinning(true);
       setSelected(null);
       
       // Visual spinning for 3 seconds
       setTimeout(async () => {
         const response = await fetch('@@random-picker', {
           method: 'POST'
         });
         const data = await response.json();
         
         setSelected(data.selected);
         setIsSpinning(false);
         setShowModal(true);
         
         // Play sound effect
         const audio = new Audio('/++plone++project.title/sounds/ding.mp3');
         audio.play();
       }, 3000);
     };
     
     return (
       <div className="random-picker">
         <div className={`picker-wheel ${isSpinning ? 'spinning' : ''}`}>
           <div className="wheel-content">
             {students.map((student, i) => (
               <div 
                 key={student}
                 className="student-slice"
                 style={{
                   transform: `rotate(${(360 / students.length) * i}deg)`
                 }}
               >
                 {student}
               </div>
             ))}
           </div>
           <div className="pointer">▼</div>
         </div>
         
         <Button 
           primary 
           size="large"
           onClick={spin}
           disabled={isSpinning}
         >
           {isSpinning ? 'Spinning...' : 'Pick a Student'}
         </Button>
         
         <Modal open={showModal} onClose={() => setShowModal(false)}>
           <Modal.Header>Selected Student</Modal.Header>
           <Modal.Content>
             <h2>{selected}</h2>
           </Modal.Content>
         </Modal>
       </div>
     );
   };
   ```

2. **Add CSS animations**:
   ```css
   /* RandomPicker.css */
   .picker-wheel {
     width: 300px;
     height: 300px;
     border-radius: 50%;
     position: relative;
     margin: 20px auto;
     background: linear-gradient(45deg, #7c3aed, #8b5cf6);
   }
   
   .picker-wheel.spinning {
     animation: spin 3s cubic-bezier(0.17, 0.67, 0.83, 0.67);
   }
   
   @keyframes spin {
     0% { transform: rotate(0deg); }
     100% { transform: rotate(720deg + var(--final-rotation)); }
   }
   ```

### Feature 4: Digital Hall Pass System ✅ COMPLETE
**Implementation Path**: Dexterity type + QR code generation + time tracking

#### Sub-Feature 4.1: Backend Hall Pass Type
1. **Create content type** in `backend/src/project/title/content/`:
   ```python
   # hall_pass.py
   from plone.dexterity.content import Item
   from plone.supermodel import model
   from zope import schema
   from datetime import datetime
   import qrcode
   import io
   import base64
   
   class IHallPass(model.Schema):
       """Digital hall pass with QR tracking"""
       
       student_name = schema.TextLine(
           title=u"Student Name",
           required=True
       )
       
       destination = schema.Choice(
           title=u"Destination",
           values=[u'Restroom', u'Office', u'Nurse', u'Library', u'Other'],
           required=True
       )
       
       issue_time = schema.Datetime(
           title=u"Issue Time",
           required=True,
           defaultFactory=datetime.now
       )
       
       return_time = schema.Datetime(
           title=u"Return Time",
           required=False
       )
       
       pass_code = schema.TextLine(
           title=u"Pass Code",
           description=u"Unique code for QR",
           required=False
       )
   
   class HallPass(Item):
       """Hall pass implementation"""
       
       def generate_qr_code(self):
           """Generate QR code for this pass"""
           # Create pass data (no PII in QR)
           pass_data = {
               'id': self.getId(),
               'code': self.pass_code,
               'issued': self.issue_time.isoformat()
           }
           
           # Generate QR
           qr = qrcode.QRCode(version=1, box_size=10, border=4)
           qr.add_data(str(pass_data))
           qr.make(fit=True)
           
           # Create image
           img = qr.make_image(fill_color="black", back_color="white")
           
           # Convert to base64
           buffer = io.BytesIO()
           img.save(buffer, format='PNG')
           img_str = base64.b64encode(buffer.getvalue()).decode()
           
           return f"data:image/png;base64,{img_str}"
   ```

2. **Add QR code dependency** to `backend/requirements.txt`:
   ```
   qrcode[pil]==7.4.2
   ```

#### Sub-Feature 4.2: Frontend Pass Management
1. **Create pass issuing interface**:
   ```jsx
   // HallPassManager.jsx
   import React, { useState, useEffect } from 'react';
   import { Form, Button, Card, Label } from 'semantic-ui-react';
   
   const HallPassManager = () => {
     const [activePasses, setActivePasses] = useState([]);
     const [newPass, setNewPass] = useState({
       student_name: '',
       destination: 'Restroom'
     });
     
     useEffect(() => {
       // Poll for active passes
       const interval = setInterval(fetchActivePasses, 30000);
       return () => clearInterval(interval);
     }, []);
     
     const issuePass = async () => {
       const response = await fetch('/++api++/hall-pass', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(newPass)
       });
       
       if (response.ok) {
         const pass = await response.json();
         setActivePasses([...activePasses, pass]);
         setNewPass({ student_name: '', destination: 'Restroom' });
       }
     };
     
     const returnPass = async (passId) => {
       await fetch(`/++api++/hall-pass/${passId}/return`, {
         method: 'PATCH'
       });
       fetchActivePasses();
     };
     
     return (
       <div className="hall-pass-manager">
         <Form onSubmit={issuePass}>
           <Form.Input
             label="Student Name"
             value={newPass.student_name}
             onChange={(e, { value }) => 
               setNewPass({ ...newPass, student_name: value })
             }
           />
           <Form.Select
             label="Destination"
             value={newPass.destination}
             options={destinations}
             onChange={(e, { value }) => 
               setNewPass({ ...newPass, destination: value })
             }
           />
           <Button primary type="submit">Issue Pass</Button>
         </Form>
         
         <div className="active-passes">
           <h3>Active Passes</h3>
           {activePasses.map(pass => (
             <PassCard 
               key={pass.id}
               pass={pass}
               onReturn={() => returnPass(pass.id)}
             />
           ))}
         </div>
       </div>
     );
   };
   ```

2. **Create pass display card**:
   ```jsx
   // PassCard.jsx
   const PassCard = ({ pass, onReturn }) => {
     const duration = getTimeDifference(pass.issue_time);
     const alertLevel = duration > 10 ? 'red' : duration > 5 ? 'yellow' : 'green';
     
     return (
       <Card color={alertLevel}>
         <Card.Content>
           <Card.Header>{pass.student_name}</Card.Header>
           <Card.Meta>{pass.destination}</Card.Meta>
           <Card.Description>
             <Label color={alertLevel}>
               {duration} minutes
             </Label>
           </Card.Description>
         </Card.Content>
         <Card.Content extra>
           <Button onClick={onReturn}>Mark Returned</Button>
           <img src={pass.qr_code} alt="Pass QR" width="50" />
         </Card.Content>
       </Card>
     );
   };
   ```

### Task 2: Integration Testing ✅ COMPLETE
1. **Test feature interactions**:
   - Seating chart loads student list for picker ✅ COMPLETE
   - Hall passes show on dashboard (ready for Phase 3)
   - All features work on tablets ✅ COMPLETE
2. **Performance benchmarks**:
   - Drag-drop response < 50ms ✅ COMPLETE
   - Picker animation smooth ✅ COMPLETE
   - Pass generation < 1s ✅ COMPLETE

## Impacted Files and Directories
- **Backend Structure**:
  - `backend/src/project/title/content/` - Content types
  - `backend/src/project/title/browser/` - Views and endpoints
  - `backend/requirements.txt` - Python dependencies
  
- **Frontend Structure**:
  - `frontend/packages/volto-project-title/src/components/` - UI components
  - `frontend/packages/volto-project-title/src/theme/` - Styles

## Review Checklist
- [x] Google SSO continues to work ✅
- [x] Seating chart drag-drop works on tablets ✅
- [x] Random picker shows fairness in selection ✅
- [x] Hall passes track time accurately ✅
- [x] All features follow UI/theme rules ✅
- [x] Performance targets met ✅
- [x] No core Plone functionality broken ✅

## Rules Adherence
- Using Plone add-on patterns (no core modifications)
- Following ZCA principles for browser views
- Progressive enhancement for JavaScript
- File naming follows project rules
- Components under 500 lines

## Time Estimates
- Feature 2 (Seating Chart): 6-8 hours ✅ COMPLETE
- Feature 3 (Random Picker): 4-5 hours ✅ COMPLETE
- Feature 4 (Hall Pass): 5-6 hours ✅ COMPLETE
- Integration Testing: 2-3 hours ✅ COMPLETE
- **Phase 2**: FULLY COMPLETE ✅

## Risk Mitigation
1. **Drag-drop complexity**: Start with basic grid, enhance iteratively
2. **Fairness algorithm**: Test with various class sizes
3. **QR generation**: Handle library installation issues
4. **Real-time updates**: Use polling first, WebSockets later

## Iteration Notes
These features provide immediate classroom value. Phase 3 will add Features 5-7 (Timer, Sub Folder, Dashboard) to complete the platform. Focus on touch-friendly interfaces since teachers use tablets. 