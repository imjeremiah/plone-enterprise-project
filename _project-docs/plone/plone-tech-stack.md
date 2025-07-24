# Plone 6 Technology Stack: K-12 Classroom Management Platform Implementation

## Overview

This document details the **actual technology stack** powering our K-12 Classroom Management Platform, built on Plone 6.1.2. Rather than cataloging all possible Plone technologies, this focuses on what's **currently implemented** and **planned for implementation** in our classroom management platform for K-12 teachers.

---

## 🏗️ Project Architecture Layers

```
┌──────────────────────────────────────────────────────────────┐
│         K-12 CLASSROOM MANAGEMENT PLATFORM TECH STACK        │
├──────────────────────────────────────────────────────────────┤
│  Frontend Layer     │  Development Tools                     │
│  ├─ Volto (React)   │  ├─ uv (Python packages)               │
│  └─ pnpm workspace  │  ├─ Make (task automation)             │
│                     │  └─ Docker Compose                     │
├──────────────────────────────────────────────────────────────┤
│                Backend Layer                                 │
│  ├─ Plone 6.1.2     │  ├─ plone.restapi 9.8.5                │
│  ├─ Zope 5.11       │  ├─ Custom package: project.title      │
│  └─ Python 3.12     │  └─ Cookieplone structure              │
├──────────────────────────────────────────────────────────────┤
│               Database & Storage                             │
│  ├─ ZODB 6.2        │  ├─ PostgreSQL 14 (Docker)             │
│  ├─ RelStorage      │  ├─ Varnish cache                      │
│  └─ File Storage    │  └─ Blob storage                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🐍 Backend Technology Stack (Current Implementation)

### Core Runtime Environment

#### **Python Foundation**
```python
# Actual Runtime Configuration
Python 3.12 (Project standard)
├─ CPython Implementation
├─ uv (Modern package management - NOT pip/buildout)
├─ pyproject.toml (PEP 621 project configuration)
└─ WSGI via Waitress server

# Package Management Approach
├─ uv for dependency resolution
├─ requirements-mxdev.txt for constraints
├─ No buildout configuration
└─ Direct package installation
```

**Current Status**: ✅ Fully implemented with Python 3.12 and uv package manager

**Classroom Platform Context**: Simplified dependency management allows school IT staff to deploy updates without complex buildout knowledge.

#### **Zope Application Server**
```python
# Implemented Zope Stack
Zope 5.11 (via Plone 6.1.2)
├─ WSGI Support (modern deployment)
├─ ZPublisher (Request/Response handling)
├─ ZODB 6.2 (Object persistence)
└─ Acquisition (Attribute inheritance)

# Core Packages in Use
├─ zope.interface (Interface definitions)
├─ zope.component (Component architecture)
├─ zope.schema (Content schemas)
├─ AccessControl 7.2 (Security)
└─ Products.CMFCore (Content management)

# ZCML Configuration
├─ Minimal ZCML usage in project.title
├─ Standard Plone registrations
└─ No complex customizations yet
```

**Implementation Notes**: 
- Using standard Plone ZCML patterns
- Custom package (`project.title`) has minimal configuration
- Planning to add classroom-specific components in Phase 2

### Database Layer

#### **ZODB (Primary Database)**
```python
# Current Database Setup
ZODB 6.2
├─ File Storage (Data.fs) for development
├─ PostgreSQL via RelStorage in Docker
├─ 3.2MB current database size
└─ Standard ZODB configuration

# Planned Classroom Features
├─ Seating chart persistence
├─ Hall pass tracking
├─ Timer state storage
└─ Dashboard cache data
```

**Performance Baseline**: 
- Startup: ~15 seconds
- Memory: ~180MB base usage
- Response time: <200ms for API calls

### Content Management Core

#### **Plone CMS Implementation**
```python
# Core Package Versions
Products.CMFPlone 6.1.2
├─ plone.app.contenttypes 3.1.3 (Content types)
├─ plone.dexterity (Content framework)
├─ plone.restapi 9.8.5 (REST API)
├─ plone.volto 4.3.1 (Frontend bridge)
└─ plone.api (Developer API)

# Current Content Configuration
├─ Standard Plone content types only
├─ No custom content types yet
├─ Basic workflow (private/published)
└─ Default security settings

# Planned Classroom Content Types (Phase 2-3)
├─ SeatingChart (drag-drop grid storage)
├─ HallPass (QR code tracking)
├─ SubstituteFolder (auto-generated)
├─ TimerPreset (reusable timers)
└─ ClassroomDashboard (aggregated view)
```

### Security & Authentication

#### **Current Security Setup**
```python
# Implemented Security
AccessControl 7.2
├─ Basic Plone authentication
├─ Standard role-based permissions
├─ CSRF protection enabled
└─ Admin user configured

# Implemented Features
├─ Google OAuth integration (SSO) ✅
├─ Teacher/Admin roles
└─ School-based permissions

# Planned Security Enhancements (Phase 3)
├─ Substitute teacher access
├─ Student privacy protections
├─ Hall pass audit logging
└─ Dashboard access controls
```

### REST API Layer

#### **plone.restapi Implementation**
```python
# Current API Configuration
plone.restapi 9.8.5
├─ Standard CRUD operations
├─ Basic authentication
├─ JSON serialization
└─ Custom serializers started

# API Endpoints (Functional)
GET    /api/               # API root
GET    /api/@search       # Content search
GET    /api/@types        # Type information
GET    /api/@workflow     # Workflow states

# Planned Classroom API Endpoints
GET    /api/@dashboard     # Real-time classroom data
POST   /api/@seating       # Update student positions
POST   /api/@picker        # Fair selection algorithm
POST   /api/@hallpass      # Issue/return passes
GET    /api/@timer         # Timer state management
POST   /api/@substitute    # Generate sub folder
```

---

## ⚛️ Frontend Technology Stack (Current Implementation)

### Modern Frontend (Volto)

#### **React Ecosystem**
```javascript
// Current Volto Setup
@plone/volto (via pnpm workspace)
├─ React 18+ (via Volto)
├─ Redux (State management)
├─ Minimal customization
└─ volto-project-title addon

// Package Management
pnpm 9.1.1
├─ Workspace configuration
├─ Shared dependencies
├─ Efficient disk usage
└─ Fast installation

// Current Frontend Features
├─ Basic Volto configuration
├─ Language settings (English)
├─ Google SSO integration ✅
└─ Standard Volto theme
```

**Development Status**:
- ✅ Basic Volto installation complete
- ✅ Google SSO authentication working
- ⏳ Custom classroom UI components planned
- ⏳ Interactive JavaScript widgets planned

#### **Planned Frontend Technologies (Phase 2-3)**
```javascript
// Classroom Management Components
├─ Seating chart drag-drop interface
├─ Random picker animation wheel
├─ Timer widget with audio alerts
├─ QR code display components
└─ Real-time dashboard updates

// Interactive Features
├─ Touch-optimized for tablets
├─ Offline timer functionality
├─ WebSocket considerations
└─ Progressive Web App features
```

---

## 🗄️ Database & Storage Technologies

### Current Implementation

#### **Development Database**
```python
# Local Development
ZODB File Storage
├─ Data.fs (3.2MB current)
├─ Standard blob storage
├─ No external databases yet
└─ Simple backup strategy

# Docker Stack Database
PostgreSQL 14
├─ Via docker-compose.yml
├─ RelStorage configuration
├─ Persistent volumes
└─ Ready for production
```

#### **Caching Layer**
```yaml
# Current Cache Setup (Docker)
Varnish 7.6
├─ HTTP acceleration
├─ Static asset caching
├─ Configured for Plone
└─ Purging support
```

---

## 🚀 Development & Deployment Stack

### Development Environment

#### **Current Build Tools**
```bash
# Primary Development Tools
make                    # Task automation
├─ make install        # Full setup
├─ make backend-start  # Run Plone
├─ make frontend-start # Run Volto
├─ make test          # Run tests
└─ make format        # Code formatting

# Python Environment
uv                     # Package manager
├─ Fast dependency resolution
├─ No virtual env needed
├─ requirements-mxdev.txt
└─ Direct from pyproject.toml

# Frontend Build
pnpm 9.1.1            # Node package manager
├─ Workspace support
├─ Volto development
├─ Fast installation
└─ Disk efficient
```

#### **Container Stack**
```yaml
# docker-compose.yml Services
traefik      # Reverse proxy with SSL
frontend     # Volto on port 3000  
backend      # Plone on port 8080
db           # PostgreSQL 14
varnish      # Cache layer
purger       # Cache invalidation
```

### Version Control & CI/CD

#### **Current Implementation**
```yaml
# Repository Structure
Git with Cookieplone conventions
├─ backend/          # Plone application
├─ frontend/         # Volto application
├─ devops/          # Infrastructure
└─ _project-docs/   # Documentation

# Planned CI/CD (Phase 4)
GitHub Actions
├─ Automated testing
├─ Docker image builds
├─ Deployment pipelines
└─ Security scanning
```

---

## 🧪 Testing & Quality Assurance

### Current Testing Setup

#### **Backend Testing**
```python
# Test Framework
pytest with pytest-plone
├─ Unit tests (minimal)
├─ Integration test setup
├─ plone.app.testing layers
└─ Test fixtures ready

# Quality Tools
├─ Ruff (linting/formatting)
├─ pyroma (package checks)
├─ zpretty (ZCML formatting)
└─ check-python-versions

# Current Test Coverage
├─ ✅ Basic setup tests
├─ ✅ Google SSO tests
├─ ⏳ Feature tests planned
├─ ⏳ API tests planned
└─ ⏳ Performance tests planned
```

#### **Frontend Testing**
```javascript
// Current Setup
Jest (via Volto)
├─ Component testing ready
├─ No custom tests yet
└─ Standard Volto tests pass

// Planned Testing (Phase 3)
├─ JavaScript widget tests
├─ Drag-drop interaction tests
├─ Timer accuracy tests
└─ Cross-browser testing
```

---

## 📦 Package Dependencies

### Core Dependencies (Actual)

#### **Backend Packages**
```toml
# From pyproject.toml
[project.dependencies]
Products.CMFPlone = "6.1.2"
plone.api = "*"
plone.restapi = "*"
plone.volto = "*"

[project.optional-dependencies.test]
plone.app.testing = "*"
pytest = "*"
pytest-plone = ">=0.5.0"
```

#### **Frontend Dependencies**
```json
// From package.json
{
  "dependencies": {
    "@plone/volto": "workspace:*",
    "@plone/registry": "workspace:*",
    "volto-project-title": "workspace:*"
  },
  "devDependencies": {
    "mrs-developer": "^2.2.0"
  }
}
```

---

## 🎯 Classroom Management Features (Technology Mapping)

### Phase 2: Core Features
| Feature | Technologies | Status |
|---------|-------------|--------|
| ✅ Google SSO | OAuth2, pas.plugins.oauth | ✅ Complete |
| Seating Chart | Dexterity, Drag-drop JS, JSON storage | ⏳ Planned |
| Random Picker | Browser view, Fairness algorithm, CSS animations | ⏳ Planned |

### Phase 3: Advanced Features
| Feature | Technologies | Status |
|---------|-------------|--------|
| Hall Pass | QR codes, Python qrcode library, Time tracking | 📋 Designed |
| Timer Widget | JavaScript, Web Audio API, localStorage | 📋 Designed |
| Sub Folder | plone.api, Content aggregation, Templates | 📋 Designed |

### Phase 4: Integration
| Feature | Technologies | Status |
|---------|-------------|--------|
| Dashboard | Browser view, AJAX polling, Chart.js | 💭 Conceptual |
| Real-time Updates | plone.restapi, Caching, WebSockets | 💭 Conceptual |
| Mobile PWA | Service Workers, Offline support | 💭 Conceptual |

---

## 🔧 Development Workflow

### Current Development Commands
```bash
# Daily Development
make install                # Initial setup
make backend-start         # Start Plone (port 8080)
make frontend-start        # Start Volto (port 3000)
make test                  # Run all tests

# Code Quality
make format               # Format Python code
make lint                # Check code quality

# Docker Development  
make stack-start         # Full stack with database
make stack-stop          # Stop all services
```

### Technology Decisions & Rationale

#### **Why These Technologies?**

1. **uv over pip/buildout**: Faster, simpler dependency management suitable for school IT departments
2. **pnpm over npm/yarn**: Better monorepo support, disk efficiency for limited school hardware
3. **PostgreSQL over MySQL**: Better ZODB RelStorage support, enterprise reliability
4. **Make over complex scripts**: Universal, simple, well-documented automation
5. **Docker Compose**: Easy local development, mirrors production architecture

#### **Technology Constraints**

- **School Infrastructure**: Must work on older hardware, limited bandwidth
- **IT Expertise**: Deployable by school IT staff, not just developers
- **Security Requirements**: FERPA compliance, student data protection
- **Accessibility**: Touch-friendly for tablets, works on school networks

---

## 📊 Performance Benchmarks

### Current Metrics (Phase 1)
| Metric | Current | Target (Phase 4) |
|--------|---------|------------------|
| Page Load | 2.5-4.2s | <2s |
| API Response | <200ms | <150ms |
| Dashboard Refresh | N/A | <200ms |
| Drag-drop Response | N/A | <50ms |
| Timer Accuracy | N/A | ±100ms |

---

## 🔐 Security Stack

### Current Implementation
- Standard Plone security model
- CSRF protection enabled
- Google OAuth SSO ✅
- Teacher role-based access

### Planned Security Stack (Phase 2-3)
```python
# Authentication
├─ Google OAuth 2.0 (SSO) ✅
├─ JWT tokens for API
├─ Session management
└─ Substitute teacher access

# Authorization  
├─ Teacher/Sub/Admin roles
├─ Feature-based permissions
├─ Dashboard access controls
└─ API rate limiting

# Privacy
├─ No PII in QR codes
├─ Anonymized picker data
├─ Secure timer states
└─ Audit logging
```

---

## 📝 Summary

This technology stack represents the **actual implementation** of our K-12 Classroom Management Platform, not just Plone's theoretical capabilities.

### **What We Have Now**
- ✅ Plone 6.1.2 with modern Python 3.12
- ✅ Basic Volto React frontend
- ✅ Docker-based development environment
- ✅ Cookieplone project structure
- ✅ RESTful API foundation
- ✅ Google SSO authentication

### **What We're Building**
- 🚧 Interactive classroom management tools
- 🚧 Real-time dashboard aggregation
- 🚧 Touch-optimized tablet interface
- 🚧 Offline-capable timer functionality
- 🚧 Fair participation tracking

### **Technology Philosophy**
- **Real-time over batch**: Instant classroom updates
- **Simple over complex**: Teachers can understand the tools
- **Touch-first**: Designed for classroom tablets
- **Privacy-first**: Protect student information
- **Performance matters**: Sub-second interactions

This stack provides enterprise reliability while focusing on the specific needs of daily classroom management, teacher workflows, and school infrastructure constraints.

*Technical specifications based on actual project implementation as of Phase 1 completion.* 