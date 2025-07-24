
# Project Development Rules for K-12 Classroom Management Platform

This document defines the development standards and conventions for our K-12 Classroom Management Platform built on Plone 6.1.2. These rules ensure **consistency**, **maintainability**, and **AI-tool compatibility** while respecting Plone's architecture and supporting teachers' daily classroom operations.

## Core Development Principles

1. **Classroom Operations First**: Every decision should consider real-time classroom needs
2. **Legacy Respect**: Never break core Plone functionality - extend, don't modify
3. **AI-Friendly Code**: Structure for semantic search and automated assistance
4. **Progressive Enhancement**: Basic features work everywhere, advanced features enhance experience

---

## Directory Structure

Our project follows the cookieplone-generated structure with classroom management organization:

### Project Root Structure
```
project-title/
├── backend/                    # Plone backend (Python/Zope)
├── frontend/                   # Volto frontend (React)
├── devops/                     # Deployment configurations
├── docs/                       # Project documentation
├── Makefile                    # Development commands
├── docker-compose.yml          # Local development
└── pyproject.toml             # Python project config
```

### Backend Structure (Plone Add-on)
```
backend/src/project/title/
├── __init__.py                 # Package initialization
├── configure.zcml              # Zope configuration
├── profiles/                   # GenericSetup profiles
│   └── default/
│       ├── metadata.xml
│       ├── types.xml           # Content type definitions
│       └── workflows.xml       # Management workflows
├── content/                    # Content types
│   ├── __init__.py
│   ├── seating_chart.py        # Seating chart content type
│   ├── hall_pass.py            # Digital hall pass type
│   └── substitute_folder.py    # Substitute materials
├── behaviors/                  # Reusable behaviors
│   ├── __init__.py
│   ├── timer_enabled.py        # Add timers to content
│   ├── qr_enabled.py           # QR code generation
│   └── trackable.py            # Usage tracking behavior
├── vocabularies/              # Dynamic vocabularies
│   ├── __init__.py
│   ├── classroom_locations.py  # Destinations for passes
│   ├── student_roster.py       # Student lists
│   └── timer_presets.py        # Common timer durations
├── api/                       # REST API extensions
│   ├── __init__.py
│   ├── services/              # Custom API endpoints
│   │   ├── dashboard_data.py  # Real-time dashboard
│   │   └── picker_service.py  # Fair selection algorithm
│   └── serializers/           # Content serializers
│       └── seating_chart.py   # Grid JSON format
├── browser/                   # Browser views
│   ├── views/
│   │   ├── dashboard.py       # Teacher command center
│   │   ├── random_picker.py   # Student selection
│   │   └── timer_widget.py    # Lesson timer
│   ├── static/               # JavaScript/CSS
│   │   ├── seating-chart.js  # Drag-drop logic
│   │   ├── picker-wheel.js    # Animation
│   │   └── timer.js          # Timer functionality
│   └── templates/            # Page templates
└── tests/                     # Backend tests
    ├── test_seating_chart.py
    ├── test_hall_pass.py
    └── test_dashboard.py
```

### Frontend Structure (Volto)
```
frontend/packages/volto-project-title/src/
├── index.js                   # Add-on entry point
├── config.js                  # Volto configuration
├── components/                # React components
│   ├── Blocks/               # Custom Volto blocks
│   │   ├── TimerBlock/       # Timer widget block
│   │   ├── SeatingGrid/      # Seating chart block
│   │   └── HallPassStatus/   # Active passes block
│   ├── Views/                # Content type views
│   │   ├── SeatingChartView.jsx
│   │   └── DashboardView.jsx
│   └── Widgets/              # Form widgets
│       ├── StudentPickerWidget.jsx
│       └── QRDisplayWidget.jsx
├── actions/                  # Redux actions
│   ├── classroom.js
│   └── timer.js
├── reducers/                 # Redux reducers
│   ├── management.js
│   └── realtime.js
├── theme/                    # Classroom theme
│   ├── extras/
│   │   └── classroom.less
│   └── globals/
│       └── site.overrides
└── helpers/                  # Utility functions
    ├── fairness.js           # Picker algorithm
    └── qrGenerator.js        # QR utilities
```

### Documentation Structure
```
docs/
├── teacher-guide/           # End-user documentation
├── developer/               # Technical documentation
├── api/                     # API reference
└── deployment/              # Deployment guides
```

---

## File Naming Conventions

### Python (Backend)
- **Files**: `snake_case.py` - descriptive, purposeful names
- **Classes**: `PascalCase` - e.g., `SeatingChartContent`
- **Interfaces**: `I` prefix - e.g., `ITimerEnabled`
- **Tests**: `test_` prefix - e.g., `test_hall_pass_tracking.py`

### JavaScript/React (Frontend)
- **Components**: `PascalCase.jsx` - e.g., `RandomPicker.jsx`
- **Utilities**: `camelCase.js` - e.g., `calculateFairness.js`
- **Actions/Reducers**: `camelCase.js` - e.g., `timerActions.js`
- **Tests**: `.test.js` suffix - e.g., `SeatingChart.test.js`

### Examples from Current Implementation
```python
# Good: Descriptive and purposeful
seating_chart.py            # Clear content type
hall_pass_tracker.py        # Specific functionality
dashboard_aggregator.py     # Data aggregation purpose

# Bad: Too generic or unclear
utils.py                    # What utilities?
helper.py                   # Helper for what?
data.py                     # What kind of data?
```

---

## Code Organization Rules

### 1. File Size Limits
- **Maximum 500 lines** per file for AI readability
- Split large files by concern:
  ```python
  # Instead of one large dashboard.py:
  dashboard_view.py           # View logic
  dashboard_data.py           # Data aggregation
  dashboard_widgets.py        # Widget components
  ```

### 2. Function Documentation
Every function must have clear docstrings:
```python
def select_random_student(roster, history=None):
    """Select a student using fairness algorithm.
    
    Ensures equitable participation by weighting selection
    based on recent participation history.
    
    Args:
        roster: List of student IDs in the class
        history: Dict mapping student_id to last_selected timestamp
        
    Returns:
        dict: Selected student info with timestamp
        
    Raises:
        EmptyRosterError: If no students available
    """
```

### 3. Component Structure
React components follow consistent patterns:
```jsx
// SeatingChartView.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { Container } from 'semantic-ui-react';

/**
 * Interactive seating chart with drag-drop student positioning.
 * Supports real-time updates and integrates with random picker.
 */
const SeatingChartView = ({ content, isEditable }) => {
  // Component logic here
};

SeatingChartView.propTypes = {
  content: PropTypes.shape({
    title: PropTypes.string.isRequired,
    grid_data: PropTypes.object,
    students: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
  isEditable: PropTypes.bool,
};

export default SeatingChartView;
```

### 4. Configuration Management
Use clear configuration patterns:
```python
# config.py
CLASSROOM_CONFIG = {
    'max_hall_pass_duration': 15,  # minutes
    'timer_warning_threshold': 2,   # minutes
    'picker_animation_duration': 3,  # seconds
    'dashboard_refresh_interval': 30,  # seconds
}
```

---

## Integration Patterns

### 1. Behavior Registration
```xml
<!-- configure.zcml -->
<plone:behavior
    title="Timer Enabled"
    description="Add timer functionality to content"
    provides=".behaviors.timer_enabled.ITimerEnabled"
    factory=".behaviors.timer_enabled.TimerEnabled"
    for="plone.dexterity.interfaces.IDexterityContent"
    />
```

### 2. API Endpoint Registration
```python
# api/services/dashboard_data.py
@implementer(IPublishTraverse)
@adapter(IFolder, IRequest)
class DashboardDataService(Service):
    """Provide real-time classroom data."""
    
    def reply(self):
        """Aggregate classroom status data."""
        # Implementation
```

### 3. Redux Integration
```javascript
// actions/classroom.js
export const UPDATE_SEATING = 'UPDATE_SEATING';

export function updateSeating(studentId, position) {
  return {
    type: UPDATE_SEATING,
    request: {
      op: 'patch',
      path: '/seating-chart',
      data: { studentId, position },
    },
  };
}
```

---

## Testing Standards

### 1. Test Organization
- Unit tests next to code being tested
- Integration tests in dedicated folders
- E2E tests in cypress/tests/

### 2. Test Naming
```python
# test_seating_chart.py
class TestSeatingChartContent(unittest.TestCase):
    """Test seating chart functionality."""
    
    def test_drag_drop_student_position(self):
        """Test updating student position via drag-drop."""
        
    def test_grid_data_persistence(self):
        """Test that seating arrangements persist."""
```

### 3. Coverage Requirements
- Minimum 80% code coverage
- 100% coverage for critical paths (timers, tracking)
- Document why uncovered code is acceptable

---

## Performance Guidelines

### 1. Query Optimization
```python
# Good: Use catalog for dashboard aggregation
catalog = api.portal.get_tool('portal_catalog')
active_passes = catalog(
    portal_type='HallPass',
    review_state='active',
    sort_on='created',
    sort_limit=10,
)

# Bad: Loading all objects
passes = [obj for obj in folder.objectValues() 
          if obj.portal_type == 'HallPass' and obj.is_active]
```

### 2. Caching Strategy
```python
# Use plone.memoize for dashboard data
from plone.memoize import ram

@ram.cache(lambda method, classroom_id: f'dashboard-{classroom_id}')
def get_dashboard_data(classroom_id):
    """Cache dashboard data for performance."""
    # Expensive aggregation
```

### 3. Real-time Updates
- Use AJAX polling for dashboard (30s intervals)
- WebSocket consideration for future
- Optimize payload size for mobile

---

## Security Rules

### 1. Permission Checks
Always verify permissions in code:
```python
from plone import api

def issue_hall_pass(student_id):
    """Issue digital hall pass."""
    if not api.user.has_permission('Manage classroom', obj=self.context):
        raise Unauthorized("Only teachers can issue passes")
```

### 2. Input Validation
```python
from zope.schema import ValidationError

def validate_timer_duration(value):
    """Validate timer duration is reasonable."""
    if value < 1 or value > 90:
        raise ValidationError(f"Invalid duration: {value} minutes")
```

### 3. Data Privacy
- Never log student PII in QR codes
- Anonymize participation data
- Follow FERPA requirements

---

## Common Pitfalls to Avoid

1. **Modifying Core Plone**: Always extend through add-ons
2. **Ignoring Permissions**: Every action needs permission checks
3. **Dense Code**: Break complex logic into readable functions
4. **Missing Tests**: No feature without tests
5. **Poor Names**: Be specific and descriptive
6. **Large Files**: Keep under 500 lines
7. **No Documentation**: Every public API needs docs
8. **Synchronous Long Operations**: Use async for dashboard updates
9. **Hardcoded Values**: Use configuration
10. **Ignoring Touch Devices**: Test on tablets

---

## Development Workflow

### 1. Local Development
```bash
# Start with Make commands
make start-backend
make start-frontend

# Run tests before committing
make test-backend
make test-frontend
```

### 2. Code Review Checklist
- [ ] Follows naming conventions
- [ ] Includes appropriate tests
- [ ] Has clear documentation
- [ ] Respects file size limits
- [ ] Handles errors gracefully
- [ ] Considers tablet/mobile users
- [ ] Maintains real-time performance

### 3. Deployment Preparation
- Use Docker for consistency
- Environment-specific configs
- Health check endpoints
- Monitoring integration

---

This ruleset ensures our K-12 Classroom Management Platform maintains high quality while helping teachers manage their classrooms effectively. When in doubt, prioritize real-time performance and teacher usability. 