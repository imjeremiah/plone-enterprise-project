
# Project Development Rules for K-12 Educational Platform

This document defines the development standards and conventions for our K-12 Educational Content Platform built on Plone 6.1.2. These rules ensure **consistency**, **maintainability**, and **AI-tool compatibility** while respecting Plone's architecture and supporting our educational mission.

## Core Development Principles

1. **Educational Context First**: Every decision should consider teachers in under-resourced schools
2. **Legacy Respect**: Never break core Plone functionality - extend, don't modify
3. **AI-Friendly Code**: Structure for semantic search and automated assistance
4. **Progressive Enhancement**: Basic features work everywhere, advanced features enhance experience

---

## Directory Structure

Our project follows the cookieplone-generated structure with educational-specific organization:

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
│       └── workflows.xml       # Educational workflows
├── content/                    # Content types
│   ├── __init__.py
│   ├── lesson_plan.py          # Lesson plan content type
│   ├── educational_resource.py # Resource content type
│   └── standards_alignment.py  # Standards content type
├── behaviors/                  # Reusable behaviors
│   ├── __init__.py
│   ├── collaborative.py        # Co-teaching behavior
│   ├── standards_aligned.py   # Standards alignment
│   └── google_exportable.py   # Google Classroom export
├── vocabularies/              # Dynamic vocabularies
│   ├── __init__.py
│   ├── grade_levels.py        # K-12 grade levels
│   ├── subjects.py            # Subject areas
│   └── standards.py           # Educational standards
├── api/                       # REST API extensions
│   ├── __init__.py
│   ├── services/              # Custom API endpoints
│   │   ├── google_sync.py     # Google Classroom sync
│   │   └── analytics.py       # Usage analytics
│   └── serializers/           # Content serializers
│       └── lesson_plan.py     # Lesson JSON format
├── browser/                   # Browser views (if needed)
│   └── controlpanel.py        # School settings panel
└── tests/                     # Backend tests
    ├── test_behaviors.py
    ├── test_content_types.py
    └── test_api.py
```

### Frontend Structure (Volto)
```
frontend/packages/volto-project-title/src/
├── index.js                   # Add-on entry point
├── config.js                  # Volto configuration
├── components/                # React components
│   ├── Blocks/               # Custom Volto blocks
│   │   ├── LessonObjective/  # Learning objective block
│   │   ├── StandardsTag/     # Standards alignment block
│   │   └── ResourceAttachment/ # File attachment block
│   ├── Views/                # Content type views
│   │   ├── LessonPlanView.jsx
│   │   └── ResourceView.jsx
│   └── Widgets/              # Form widgets
│       ├── GradeLevelWidget.jsx
│       └── StandardsWidget.jsx
├── actions/                  # Redux actions
│   ├── lessonPlan.js
│   └── googleSync.js
├── reducers/                 # Redux reducers
│   ├── educational.js
│   └── analytics.js
├── theme/                    # Educational theme
│   ├── extras/
│   │   └── educational.less
│   └── globals/
│       └── site.overrides
└── helpers/                  # Utility functions
    ├── educational.js        # Education helpers
    └── standards.js          # Standards utilities
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
- **Classes**: `PascalCase` - e.g., `LessonPlanContent`
- **Interfaces**: `I` prefix - e.g., `IStandardsAligned`
- **Tests**: `test_` prefix - e.g., `test_lesson_workflow.py`

### JavaScript/React (Frontend)
- **Components**: `PascalCase.jsx` - e.g., `LessonPlanView.jsx`
- **Utilities**: `camelCase.js` - e.g., `formatStandards.js`
- **Actions/Reducers**: `camelCase.js` - e.g., `lessonPlanActions.js`
- **Tests**: `.test.js` suffix - e.g., `LessonPlanView.test.js`

### Examples from Current Implementation
```python
# Good: Descriptive and purposeful
lesson_plan.py              # Clear content type
standards_behavior.py       # Specific behavior
google_classroom_api.py     # Integration purpose

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
  # Instead of one large lesson_plan.py:
  lesson_plan_content.py      # Content type definition
  lesson_plan_api.py          # API endpoints
  lesson_plan_workflow.py     # Workflow handlers
  ```

### 2. Function Documentation
Every function must have clear docstrings:
```python
def align_to_standards(lesson_plan, standards):
    """Align a lesson plan to educational standards.
    
    Links the lesson plan to Common Core or state standards,
    enabling filtered searches and curriculum mapping.
    
    Args:
        lesson_plan: ILessonPlan content object
        standards: List of standard identifiers (e.g., ['CCSS.Math.1.OA.1'])
        
    Returns:
        dict: Mapping of standards to lesson objectives
        
    Raises:
        InvalidStandardError: If standard ID is not recognized
    """
```

### 3. Component Structure
React components follow consistent patterns:
```jsx
// LessonPlanView.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { Container } from 'semantic-ui-react';

/**
 * Displays a lesson plan with educational metadata.
 * Supports teacher view with edit capabilities and
 * student view with simplified interface.
 */
const LessonPlanView = ({ content, isTeacher }) => {
  // Component logic here
};

LessonPlanView.propTypes = {
  content: PropTypes.shape({
    title: PropTypes.string.isRequired,
    grade_level: PropTypes.string,
    standards: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
  isTeacher: PropTypes.bool,
};

export default LessonPlanView;
```

### 4. Configuration Management
Use clear configuration patterns:
```python
# config.py
EDUCATIONAL_CONFIG = {
    'grade_levels': ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'google_sync_interval': 300,  # 5 minutes
}
```

---

## Integration Patterns

### 1. Behavior Registration
```xml
<!-- configure.zcml -->
<plone:behavior
    title="Standards Aligned"
    description="Add educational standards alignment to content"
    provides=".behaviors.standards_aligned.IStandardsAligned"
    factory=".behaviors.standards_aligned.StandardsAligned"
    for="plone.dexterity.interfaces.IDexterityContent"
    />
```

### 2. API Endpoint Registration
```python
# api/services/google_sync.py
@implementer(IPublishTraverse)
@adapter(ILessonPlan, IRequest)
class GoogleSyncService(Service):
    """Sync lesson plans with Google Classroom."""
    
    def reply(self):
        """Export lesson to Google Classroom format."""
        # Implementation
```

### 3. Redux Integration
```javascript
// actions/lessonPlan.js
export const SAVE_LESSON = 'SAVE_LESSON';

export function saveLesson(lessonData) {
  return {
    type: SAVE_LESSON,
    request: {
      op: 'post',
      path: '/lessons',
      data: lessonData,
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
# test_lesson_plan.py
class TestLessonPlanContent(unittest.TestCase):
    """Test lesson plan content type."""
    
    def test_lesson_plan_creation(self):
        """Test creating a lesson plan with required fields."""
        
    def test_standards_alignment_behavior(self):
        """Test adding standards alignment to lesson plan."""
```

### 3. Coverage Requirements
- Minimum 80% code coverage
- 100% coverage for critical paths (auth, permissions)
- Document why uncovered code is acceptable

---

## Performance Guidelines

### 1. Query Optimization
```python
# Good: Use catalog for searches
catalog = api.portal.get_tool('portal_catalog')
results = catalog(
    portal_type='LessonPlan',
    grade_level='5',
    sort_on='modified',
    sort_limit=10,
)

# Bad: Loading all objects
lessons = [obj for obj in folder.objectValues() 
           if obj.portal_type == 'LessonPlan']
```

### 2. Caching Strategy
```python
# Use plone.memoize for expensive operations
from plone.memoize import ram

@ram.cache(lambda method, grade: f'standards-{grade}')
def get_standards_for_grade(grade):
    """Cache standards by grade level."""
    # Expensive computation
```

### 3. Asset Optimization
- Images: Max 1MB, use responsive formats
- JavaScript: Bundle and minify
- CSS: Use CSS-in-JS or CSS Modules

---

## Security Rules

### 1. Permission Checks
Always verify permissions in code:
```python
from plone import api

def share_lesson(lesson_id, teacher_emails):
    """Share lesson with other teachers."""
    if not api.user.has_permission('Modify portal content', obj=lesson):
        raise Unauthorized("Cannot share lesson")
```

### 2. Input Validation
```python
from zope.schema import ValidationError

def validate_grade_level(value):
    """Validate grade level is K-12."""
    valid_grades = ['K'] + [str(i) for i in range(1, 13)]
    if value not in valid_grades:
        raise ValidationError(f"Invalid grade: {value}")
```

### 3. Data Privacy
- Never log student PII
- Anonymize analytics data
- Follow COPPA/FERPA requirements

---

## Common Pitfalls to Avoid

1. **Modifying Core Plone**: Always extend through add-ons
2. **Ignoring Permissions**: Every action needs permission checks
3. **Dense Code**: Break complex logic into readable functions
4. **Missing Tests**: No feature without tests
5. **Poor Names**: Be specific and descriptive
6. **Large Files**: Keep under 500 lines
7. **No Documentation**: Every public API needs docs
8. **Synchronous External Calls**: Use async for Google API
9. **Hardcoded Values**: Use configuration
10. **Ignoring Mobile**: Test on actual devices

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
- [ ] Considers mobile users
- [ ] Maintains backwards compatibility

### 3. Deployment Preparation
- Use Docker for consistency
- Environment-specific configs
- Health check endpoints
- Monitoring integration

---

This ruleset ensures our K-12 Educational Platform maintains high quality while serving teachers effectively. When in doubt, prioritize teacher needs and code clarity. 