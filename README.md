# K-12 Classroom Management Platform

> **Transforming Plone CMS into a modern classroom command center for K-12 teachers**

A specialized platform built on Plone 6.1.2 that modernizes classroom management through real-time digital tools, helping teachers save 40+ minutes daily on administrative tasks while improving student engagement and classroom organization.

## 🎯 Project Vision

This project demonstrates **enterprise legacy modernization** by evolving Plone CMS (1.1M+ lines of mature Python code) into a specialized K-12 Classroom Management Platform. We preserve Plone's robust content management, security, and workflow capabilities while adding modern, touch-optimized tools for daily classroom operations.

### Target Users: K-12 Teachers (Grades 6-12)
- **Primary Users**: Public school teachers needing efficient classroom management tools
- **Pain Points Solved**: Manual seating charts, unfair participation patterns, substitute preparation chaos, lack of real-time classroom visibility
- **Value Proposition**: Reduce administrative time by 45+ minutes daily while improving classroom equity and organization

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│         K-12 CLASSROOM MANAGEMENT PLATFORM                   │
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

## ✨ Core Features

### 🔐 Authentication & Access
- **Google SSO Integration** - Single sign-on with school Google accounts
- **Role-based Permissions** - Teacher, substitute, and admin access levels

### 📱 Interactive Classroom Tools
- **Seating Chart Generator** - Drag-drop interface for optimal classroom layouts
- **Random Student Picker** - Fair participation with equity tracking
- **Digital Hall Pass System** - QR code tracking for student movement
- **Lesson Timer Widget** - Audio alerts for activity management
- **Substitute Folder Generator** - Automated daily materials compilation
- **Teacher Dashboard** - Real-time classroom command center

### 🔄 Feature Integration
All tools work together seamlessly:
- Seating charts feed into random picker student lists
- Hall pass data appears on dashboard for real-time monitoring
- Timer coordinates with all classroom activities
- Dashboard aggregates data from all features for comprehensive oversight

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 22+ 
- Docker & Docker Compose
- Make

### Development Setup

```bash
# Clone and enter project
git clone <repository-url>
cd k12-classroom-platform

# Install dependencies and start services
make install          # Install all dependencies
make backend-start    # Start Plone backend (port 8080)
make frontend-start   # Start Volto frontend (port 3000)

# Or start full Docker stack
make stack-start      # Complete environment with database
```

### Access Points
- **Frontend**: http://localhost:3000 (Volto React app)
- **Backend**: http://localhost:8080 (Plone admin interface)
- **API**: http://localhost:8080/api (REST API)

## 🛠️ Development Workflow

### Daily Development Commands
```bash
make install                # Initial setup
make backend-start         # Start Plone (port 8080)
make frontend-start        # Start Volto (port 3000)
make test                  # Run all tests
make format               # Format Python code
make lint                 # Check code quality
```

### Docker Development
```bash
make stack-start         # Full stack with database
make stack-stop          # Stop all services
```

## 📁 Project Structure

```
project-title/
├── backend/                    # Plone backend (Python/Zope)
│   └── src/project/title/     # Custom classroom package
│       ├── content/           # Seating charts, hall passes
│       ├── browser/           # Dashboard, picker views
│       ├── api/              # REST API extensions
│       └── tests/            # Backend tests
├── frontend/                   # Volto frontend (React)
│   └── packages/volto-project-title/
│       ├── components/        # Classroom UI components
│       ├── actions/          # Redux state management
│       └── theme/            # Classroom styling
├── devops/                     # Deployment configurations
├── docs/                       # Project documentation
├── Makefile                   # Development commands
└── docker-compose.yml         # Local development stack
```

## 📝 Development Conventions

### Code Standards
- **File Size Limit**: Maximum 500 lines per file for AI readability
- **Naming**: `snake_case.py` for Python, `PascalCase.jsx` for React components
- **Documentation**: Every function needs clear docstrings with purpose and parameters
- **Testing**: Minimum 80% code coverage, 100% for critical paths

### Architecture Principles
1. **Classroom Operations First** - Every decision considers real-time classroom needs
2. **Legacy Respect** - Never break core Plone functionality, only extend
3. **AI-Friendly Code** - Structured for semantic search and automated assistance
4. **Progressive Enhancement** - Basic features work everywhere, advanced features enhance experience

### Performance Standards
- Page load: <2 seconds
- API response: <150ms
- Dashboard refresh: <200ms
- Drag-drop response: <50ms
- Timer accuracy: ±100ms

## 🧪 Testing

```bash
# Backend tests
make test-backend          # Python/Plone tests
pytest backend/tests/      # Run specific tests

# Frontend tests  
make test-frontend         # React/JavaScript tests
cd frontend && pnpm test   # Run Jest tests

# Full test suite
make test                  # All tests
```

## 🔒 Security & Privacy

- **FERPA Compliance** - Follows educational privacy requirements
- **Role-based Access** - Teachers, substitutes, and admins have appropriate permissions
- **Data Protection** - No PII in QR codes, anonymized participation tracking
- **Input Validation** - All user inputs validated and sanitized

## 📊 Current Implementation Status

### ✅ Completed (Phase 1)
- Plone 6.1.2 backend with Python 3.12
- Basic Volto React frontend  
- Docker-based development environment
- Google SSO authentication
- RESTful API foundation
- Cookieplone project structure

### 🚧 In Development (Phase 2-3)
- Interactive classroom management tools
- Real-time dashboard aggregation
- Touch-optimized tablet interface
- Fair participation tracking algorithms

### 💭 Planned (Phase 4)
- Offline-capable timer functionality
- WebSocket real-time updates
- Progressive Web App features
- Production deployment on AWS

## 🎓 Educational Impact

This platform demonstrates how mature enterprise systems can be transformed for specialized markets:

- **Legacy Preservation**: Maintains Plone's 20+ years of content management expertise
- **Modern Enhancement**: Adds React-based UI and API-first architecture
- **Market Specialization**: Focuses on K-12 classroom operations vs. general CMS
- **Measurable Value**: Quantifiable time savings and improved classroom equity

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/classroom-timer`)
3. **Follow** our development conventions (see above)
4. **Add** tests for new functionality
5. **Submit** a pull request with clear description

## 📚 Documentation

- **Teacher Guide**: `/docs/teacher-guide/` - End-user documentation
- **Developer Guide**: `/docs/developer/` - Technical implementation details
- **API Reference**: `/docs/api/` - REST API documentation
- **Deployment Guide**: `/docs/deployment/` - Production deployment instructions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Plone Community** - For 20+ years of robust CMS development
- **Cookieplone** - For modern project scaffolding
- **K-12 Educators** - For defining real classroom management needs
- **AI Development Tools** - For accelerating legacy system understanding

---

**Built with ❤️ for teachers who shape the future**

*Transforming enterprise legacy systems for modern educational needs* 