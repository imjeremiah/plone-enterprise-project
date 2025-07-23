
# K-12 Educational Platform User Journey

This document outlines the user journeys through our K-12 Educational Content Platform built on Plone 6.1.2. It focuses on the **actual implemented features** and **planned functionality** for teachers in under-resourced U.S. public schools, emphasizing collaborative lesson planning and Google Classroom integration.

## User Personas

### Primary Users
1. **Teachers** - Create, share, and discover lesson plans
2. **Students** - Access assignments and content via Google Classroom
3. **School Administrators** - Manage platform access and monitor usage
4. **District Coordinators** - Oversee multi-school implementations

---

## 1. Teacher Onboarding & Authentication

### Entry Point
Teacher receives invitation email or accesses platform via school portal.

### Current Implementation Status
- ✅ **Basic Plone authentication** via Products.PluggableAuthService
- ✅ **Local user/password login**
- ⏳ **Google OAuth integration** (planned for Google Classroom SSO)
- 📋 **School district SAML/LDAP** (designed, not implemented)

### User Journey Steps
1. Teacher clicks invitation link or navigates to platform URL
2. Lands on Volto React login page (customized for educational branding)
3. Enters credentials or uses "Sign in with Google" (planned)
4. System validates via Plone security framework
5. Redirects to personalized teacher dashboard

### Technical Components
- **Frontend**: Volto login form with educational UI customization
- **Backend**: Plone PAS with planned Google OAuth adapter
- **Security**: CSRF protection, secure session management

### Next Step
→ Teacher Dashboard & Resource Discovery

---

## 2. Teacher Dashboard & Resource Discovery

### Entry Point
Post-login landing on personalized teacher dashboard.

### Current Implementation Status
- ✅ **Basic Volto homepage** with navigation
- ⏳ **Personalized dashboard blocks** (in development)
- 📋 **Subject-specific content recommendations** (designed)
- 💭 **AI-powered lesson suggestions** (conceptual)

### User Journey Steps
1. View dashboard with:
   - Recent lesson plans
   - Shared resources from colleagues
   - Subject-aligned recommendations
2. Browse by:
   - Grade level (K-12)
   - Subject area
   - Teaching standards (Common Core, state standards)
3. Search for specific topics or standards

### Technical Components
- **Frontend**: Custom Volto blocks for dashboard widgets
- **Backend**: Portal Catalog with educational metadata indexes
- **Search**: ZCatalog with custom indexes for:
  - Grade levels
  - Subject areas
  - Standards alignment
  - Resource types

### Next Step
→ Lesson Plan Creation or Viewing

---

## 3. Lesson Plan Creation

### Entry Point
Teacher clicks "Create New Lesson" from dashboard or navigation.

### Current Implementation Status
- ✅ **Basic Dexterity content type** structure
- ⏳ **Lesson Plan content type** with educational fields
- 📋 **Template library** for common lesson formats
- 💭 **AI content generation** assistance

### User Journey Steps
1. Select lesson type/template:
   - Standard lesson plan
   - Project-based learning
   - Assessment/quiz
2. Fill educational metadata:
   - Title, subject, grade level
   - Learning objectives
   - Standards alignment (Common Core picker)
   - Duration/schedule
3. Build content using Volto blocks:
   - Rich text for instructions
   - Media blocks for videos/images
   - Interactive elements (planned)
   - Resource attachments
4. Add differentiation options:
   - Multiple skill levels
   - Accessibility accommodations
   - Language variations

### Technical Components
- **Content Type**: Custom Dexterity type with behaviors:
  - IStandardsAlignment (custom behavior)
  - ICollaborative (sharing/co-editing)
  - IGoogleClassroomExportable
- **Frontend**: Enhanced Volto editor with:
  - Educational block types
  - Standards picker widget
  - Collaborative editing indicators

### Next Step
→ Review & Publishing Workflow

---

## 4. Collaborative Review & Publishing

### Entry Point
Teacher completes lesson draft and initiates review/sharing.

### Current Implementation Status
- ✅ **Basic Plone workflow** (private/published states)
- ⏳ **Collaborative review workflow** (in development)
- 📋 **Peer review system** with comments
- 💭 **Department approval workflows**

### User Journey Steps
1. Save lesson as draft
2. Share with colleagues for feedback:
   - Select specific teachers
   - Share with department/grade team
3. Collaborators can:
   - View and comment
   - Suggest edits
   - Approve/endorse
4. Incorporate feedback
5. Publish to school or district library

### Technical Components
- **Workflow**: Custom DCWorkflow with states:
  - Draft (private to creator)
  - Under Review (shared with selected users)
  - Department Approved
  - Published (school-wide)
  - District Shared (opt-in wider sharing)
- **Permissions**: Granular control via Plone security
- **Collaboration**: Working copy support for concurrent editing

### Next Step
→ Google Classroom Integration

---

## 5. Google Classroom Export & Assignment

### Entry Point
Teacher selects "Export to Google Classroom" from published lesson.

### Current Implementation Status
- 📋 **Google Classroom API integration** (designed, not implemented)
- 📋 **Assignment creation automation**
- 💭 **Two-way sync for grades/submissions**

### Planned Journey Steps
1. Click "Export to Google Classroom"
2. Select target classroom(s)
3. Configure assignment options:
   - Due date
   - Point value
   - Student instructions
4. System converts lesson to Google format:
   - Creates assignment
   - Attaches resources
   - Sets up submission requirements
5. Students receive notification in Google Classroom

### Technical Components
- **Integration**: Custom Plone adapter for Google APIs
- **Content Transform**: Lesson → Google Assignment converter
- **Sync Service**: Background task for status updates

### Next Step
→ Student Access & Engagement

---

## 6. Student Experience

### Entry Point
Student accesses assignment via Google Classroom.

### Current Implementation Status
- 💭 **Direct student access** (conceptual)
- 📋 **View-only lesson access** via public links
- 💭 **Interactive elements** for student engagement

### Planned Journey Steps
1. Student clicks assignment in Google Classroom
2. Views lesson content in simplified interface:
   - Clear instructions
   - Resources/materials
   - Interactive elements (quizzes, activities)
3. Completes work in Google Docs/Slides
4. Submits via Google Classroom
5. Teacher receives notification

### Technical Components
- **Public Views**: Restricted Volto views for students
- **Tracking**: Anonymous usage analytics
- **Integration**: Google Classroom submission API

### Next Step
→ Analytics & Improvement

---

## 7. Analytics & Continuous Improvement

### Entry Point
Teacher reviews lesson effectiveness and student engagement.

### Current Implementation Status
- 💭 **Analytics dashboard** (conceptual)
- 💭 **Lesson effectiveness metrics**
- 💭 **Standards mastery tracking**

### Planned Features
1. View lesson analytics:
   - Usage by other teachers
   - Student engagement metrics
   - Standards mastery data
2. Collect feedback:
   - Peer ratings
   - Student performance correlation
3. Iterate and improve:
   - Create new versions
   - Build on successful patterns

### Technical Components
- **Analytics**: Custom Plone views with data aggregation
- **Reporting**: Integration with school data systems
- **Versioning**: Plone's built-in version control

---

## 8. Administrative Workflows

### Entry Point
School/district administrators access management interface.

### Current Implementation Status
- ✅ **Basic Plone user/group management**
- ⏳ **School-specific roles and permissions**
- 📋 **Bulk user import from SIS**
- 💭 **Usage reporting and compliance**

### Administrator Journey
1. Manage users:
   - Bulk import teachers
   - Set up departments/grade teams
   - Configure permissions
2. Monitor platform:
   - Usage statistics
   - Content quality metrics
   - Standards coverage reports
3. Configure integrations:
   - Google Workspace settings
   - District systems connections

### Technical Components
- **Control Panels**: Custom Plone control panels
- **Import Tools**: CSV/API user provisioning
- **Reports**: Scheduled email reports via Content Rules

---

## Journey Interconnections

The platform creates a **virtuous cycle** of content creation and improvement:

1. **Discovery → Creation**: Teachers find gaps and create new content
2. **Sharing → Collaboration**: Peer review improves quality
3. **Usage → Analytics**: Data drives continuous improvement
4. **Standards → Alignment**: Ensures curriculum coverage

## Technical Architecture Supporting User Journeys

```
┌─────────────────────────────────────────────────────────┐
│                   USER INTERACTIONS                     │
├─────────────────────────────────────────────────────────┤
│  Teachers         │  Students        │  Admins          │
│  ├─ Create        │  ├─ Access       │  ├─ Manage       │
│  ├─ Share         │  ├─ Submit       │  ├─ Monitor      │
│  └─ Discover      │  └─ Learn        │  └─ Report       │
├─────────────────────────────────────────────────────────┤
│                   PLATFORM LAYER                        │
├─────────────────────────────────────────────────────────┤
│  Volto React      │  Plone Backend   │  Integrations    │
│  ├─ Custom UI     │  ├─ Workflows    │  ├─ Google API   │
│  ├─ Ed Blocks     │  ├─ Security     │  ├─ LMS          │ 
│  └─ Dashboards    │  └─ Content      │  └─ Analytics    │
└─────────────────────────────────────────────────────────┘
```

This user journey emphasizes the **educational mission** while leveraging Plone's enterprise capabilities for security, workflow, and content management. 