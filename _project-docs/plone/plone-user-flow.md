
# K-12 Classroom Management Platform User Journey

This document outlines the user journeys through our K-12 Classroom Management Platform built on Plone 6.1.2. It focuses on the **actual implemented features** and **planned functionality** for teachers managing their daily classroom operations, emphasizing real-time control and efficiency.

## User Personas

### Primary Users
1. **Teachers** - Manage classroom operations, track students, control timing
2. **Substitute Teachers** - Access pre-prepared materials and classroom info
3. **School Administrators** - Monitor platform usage and manage access
4. **Students** - Limited interaction via hall passes and displays

---

## 1. Teacher Authentication & Dashboard Access

### Entry Point
Teacher accesses platform via school portal or direct URL.

### Current Implementation Status
- ✅ **Basic Plone authentication** via Products.PluggableAuthService
- ✅ **Google OAuth integration** for single sign-on
- ⏳ **Remember device** functionality planned
- 📋 **Biometric login** for tablets (future)

### User Journey Steps
1. Teacher navigates to platform URL
2. Clicks "Sign in with Google" (primary method)
3. Authenticates via school Google account
4. System validates teacher role and permissions
5. Redirects to personalized classroom dashboard

### Technical Components
- **Frontend**: Volto login with Google SSO button
- **Backend**: OAuth adapter integrated with Plone PAS
- **Security**: Session management, device recognition

### Next Step
→ Classroom Dashboard Command Center

---

## 2. Classroom Dashboard - Command Center

### Entry Point
Post-login landing on real-time classroom dashboard.

### Current Implementation Status
- ✅ **Google SSO** authentication complete
- ⏳ **Dashboard aggregation view** in development
- 📋 **Real-time widget updates** designed
- 💭 **Multi-classroom support** conceptual

### User Journey Steps
1. View dashboard with real-time status:
   - Active timers and countdowns
   - Current hall passes
   - Today's seating arrangement
   - Participation statistics
   - Alerts and notifications
2. Quick access to all tools:
   - Start timer (one click)
   - Pick student (one click)
   - Issue pass (two clicks)
   - View/edit seating chart

### Technical Components
- **Frontend**: Custom Volto dashboard blocks
- **Backend**: Browser view aggregating data
- **Updates**: AJAX polling every 30 seconds
- **Caching**: Minimize database queries

### Next Step
→ Any classroom management feature

---

## 3. Seating Chart Management

### Entry Point
Teacher clicks "Seating Chart" from dashboard or navigation.

### Current Implementation Status
- 📋 **Dexterity content type** designed
- 📋 **Drag-drop interface** planned
- 💭 **Multiple arrangements** per class
- 💭 **Integration with picker** planned

### User Journey Steps
1. View current seating arrangement grid
2. Drag students to rearrange seats:
   - Visual feedback during drag
   - Snap-to-grid positioning
   - Automatic save
3. Optional features:
   - Create multiple arrangements (test mode, groups)
   - Print seating chart
   - Share with substitute
   - Random shuffle option

### Technical Components
- **Content Type**: SeatingChart with JSON grid storage
- **Frontend**: React drag-drop library
- **Backend**: Auto-save via plone.restapi
- **Storage**: Grid data in ZODB

### Next Step
→ Use with Random Picker or return to Dashboard

---

## 4. Random Student Selection

### Entry Point
Teacher clicks "Pick Student" from dashboard or toolbar.

### Current Implementation Status
- 📋 **Browser view** designed
- 📋 **Fairness algorithm** planned
- 💭 **Visual spinner** animation
- 💭 **History tracking** for equity

### User Journey Steps
1. Click "Pick Student" button
2. Visual spinner animation begins
3. Student selected with fairness weighting:
   - Recently picked students less likely
   - All students guaranteed participation
   - Visual celebration on selection
4. Options after selection:
   - Pick another
   - View participation history
   - Reset fairness tracking

### Technical Components
- **View**: Browser view with AJAX endpoint
- **Algorithm**: Weighted random with history
- **Frontend**: CSS animations, sound effects
- **Storage**: Participation history in session

### Integration
- Pulls student list from active seating chart
- Updates participation metrics on dashboard

---

## 5. Digital Hall Pass System

### Entry Point
Teacher clicks "Issue Pass" or student requests pass.

### Current Implementation Status
- 📋 **Content type** designed
- 📋 **QR code generation** planned
- 💭 **Time tracking** system
- 💭 **Alert system** for long passes

### User Journey Steps
1. Quick issue flow:
   - Select student (or scan ID)
   - Choose destination (bathroom, office, nurse)
   - Pass auto-generates with QR code
2. Active monitoring:
   - Dashboard shows all active passes
   - Time elapsed displays
   - Color coding: green → yellow → red
3. Pass return:
   - Student/staff scans QR to return
   - Or teacher marks returned
   - Duration logged for patterns

### Technical Components
- **Content Type**: HallPass with timestamp fields
- **QR Library**: Python qrcode for generation
- **Frontend**: Real-time pass monitor widget
- **Alerts**: Progressive time-based warnings

### Next Step
→ Monitor on dashboard or issue another pass

---

## 6. Lesson Timer Management

### Entry Point
Teacher clicks "Start Timer" from dashboard or lesson plan.

### Current Implementation Status
- 📋 **JavaScript widget** designed
- 📋 **Audio alerts** planned
- 💭 **Multiple timers** support
- 💭 **Full-screen mode** for class viewing

### User Journey Steps
1. Quick timer start:
   - Click preset (5, 10, 15, 20 min)
   - Or enter custom duration
   - Timer starts immediately
2. During countdown:
   - Large visual display
   - Color transitions (green → yellow → red)
   - Audio warnings at 2 min, 1 min, 0
   - Pause/resume capability
3. Timer completion:
   - Visual and audio alert
   - Option to add time
   - Quick restart same duration

### Technical Components
- **Frontend**: JavaScript timer with localStorage
- **Audio**: Web Audio API for alerts
- **Display**: Full-screen capable
- **Sync**: Persists across page refreshes

### Next Step
→ Return to activity or start another timer

---

## 7. Substitute Folder Generation

### Entry Point
Teacher clicks "Prepare Substitute Folder" from dashboard.

### Current Implementation Status
- 📋 **Folder generation view** designed
- 📋 **Content aggregation** planned
- 💭 **Template system** for common items
- 💭 **Emergency quick-generate** option

### User Journey Steps
1. One-click generation:
   - System creates dated folder
   - Auto-populates with:
     - Today's schedule
     - Current seating charts
     - Class rosters
     - Emergency procedures
     - Special student notes
2. Teacher customization:
   - Add specific lesson plans
   - Include behavior notes
   - Special instructions
3. Access control:
   - Generate substitute access code
   - Time-limited permissions
   - Read-only access

### Technical Components
- **View**: Browser view using plone.api
- **Aggregation**: Collect relevant content
- **Templates**: Pre-configured sections
- **Permissions**: Temporary access grants

### Next Step
→ Share access code or return to dashboard

---

## 8. Teacher's Daily Command Center

### Entry Point
Persistent dashboard view throughout the day.

### Current Implementation Status
- 📋 **Aggregation view** designed
- 📋 **Widget system** planned
- 💭 **Customizable layout** future
- 💭 **Multi-device sync** future

### Continuous Monitoring
1. Real-time status widgets:
   - Active timers countdown
   - Hall pass locations/duration
   - Next period preparation
   - Student participation equity
   - Important alerts

2. Quick actions always available:
   - Start/stop timers
   - Issue/return passes
   - Pick students
   - Switch class periods

3. End-of-day summary:
   - Participation statistics
   - Hall pass patterns
   - Timer usage
   - Generate reports

### Technical Components
- **View**: Master dashboard view
- **Updates**: AJAX polling for freshness
- **Layout**: Responsive grid system
- **Performance**: Efficient data queries

---

## Substitute Teacher Journey

### Entry Point
Substitute receives access code from regular teacher or admin.

### Special Workflow
1. Access substitute folder:
   - Enter provided code
   - View read-only materials
   - See classroom layout
   - Access emergency info

2. Limited feature access:
   - View seating chart (no edit)
   - Use timers
   - Issue hall passes
   - Cannot modify core settings

3. End-of-day handoff:
   - Auto-generated summary
   - Hall pass log
   - Any incidents noted

---

## Journey Interconnections

The platform creates an **integrated classroom management ecosystem**:

1. **Dashboard → Features**: Central command for all tools
2. **Seating → Picker**: Integrated student data
3. **Timer → Dashboard**: Real-time status updates
4. **Passes → Alerts**: Automatic monitoring

## Technical Architecture Supporting User Journeys

```
┌─────────────────────────────────────────────────────────┐
│                   USER INTERACTIONS                     │
├─────────────────────────────────────────────────────────┤
│  Teachers         │  Substitutes     │  Admins          │
│  ├─ Monitor       │  ├─ Access       │  ├─ Manage       │
│  ├─ Control       │  ├─ View         │  ├─ Configure    │
│  └─ Track         │  └─ Use Basic    │  └─ Report       │
├─────────────────────────────────────────────────────────┤
│                   PLATFORM LAYER                        │
├─────────────────────────────────────────────────────────┤
│  Volto React      │  Plone Backend   │  Features        │
│  ├─ Dashboard     │  ├─ Content Types│  ├─ Timers       │
│  ├─ Widgets       │  ├─ Views        │  ├─ Passes       │ 
│  └─ Real-time     │  └─ API          │  └─ Picker       │
└─────────────────────────────────────────────────────────┘
```

This user journey emphasizes **real-time classroom control** while leveraging Plone's enterprise capabilities for security, persistence, and reliability. 