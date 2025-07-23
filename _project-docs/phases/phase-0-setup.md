
# Phase 0: Barebones Setup ✅ COMPLETE

## Scope
This phase establishes the foundational setup of the Plone 6.1.2 instance using cookieplone templates, creating a minimal running framework without custom features. It sets up the 'before' state (vanilla cookieplone project) for comparison and establishes the development environment. The output is a basic, functional CMS that isn't fully usable for teachers yet but serves as the starting point.

## Deliverables
- Installed Plone 6.1.2 instance running locally via cookieplone
- Git repository with project structure (not a fork of core Plone)
- Docker-based development environment with docker-compose.yml
- Basic verification completed (standard Plone functionality confirmed)
- Modern development tools configured (uv, pnpm, Make)

## Tasks/Features

### Task 1: Environment and Installation ✅ COMPLETE
1. Install prerequisites (Python 3.12, Node.js 22) per updated tech stack
2. Use cookieplone to generate project structure:
   - Created project-title/ directory structure
   - Backend in backend/ with Plone add-on structure
   - Frontend in frontend/ with Volto configuration
3. Install dependencies using modern tools:
   - `uv` for Python package management
   - `pnpm` for frontend dependencies
4. Start instance using Make commands:
   - `make start-backend` (runs on localhost:8080)
   - `make start-frontend` (Volto on localhost:3000)
5. Verify base functionality (login, content creation working)

### Task 2: Repository Setup ✅ COMPLETE
1. Initialize Git repository in project root
2. Current structure represents the "before" state:
   - Vanilla cookieplone-generated project
   - No educational customizations yet
   - This serves as our baseline for comparison
3. All development will proceed from this foundation
4. Note: We did not fork Plone core as we're building an add-on/customization, not modifying core

## Impacted Files and Directories
- **Directories**: 
  - project-title/ (root project from cookieplone)
  - backend/src/project/title/ (Plone add-on structure)
  - frontend/packages/volto-project-title/ (Volto customization)
  - devops/ (deployment configurations)
- **Files**: 
  - Makefile (development commands)
  - docker-compose.yml (containerization ready)
  - backend/setup.py (Python package configuration)
  - frontend/package.json (Node.js dependencies)
- **Modern Tools**:
  - Using `uv` instead of pip for Python packages
  - Using `pnpm` instead of npm for Node packages
  - Make-based workflow for consistency

**Review Checklist**:
- ✅ Cookieplone project generation successful
- ✅ Backend starts without errors (make start-backend)
- ✅ Frontend connects to backend (make start-frontend)
- ✅ Can create content in vanilla Plone interface
- ✅ Docker environment configured and tested
- ✅ No core Plone files modified (using add-on pattern)

## Rules Adherence
- Following cookieplone conventions for project structure
- Using Plone add-on pattern (no core modifications)
- Respecting ZCA architecture for future extensions
- Docker-ready for cloud deployment

## Key Differences from Original Plan
1. **Used cookieplone** instead of manual Plone installation - provides better structure and best practices
2. **Not forking Plone core** - we're creating an add-on/customization layer
3. **Python 3.12** instead of 3.11 - using latest stable version
4. **Modern tooling** - uv and pnpm for better dependency management
5. **Make commands** - simplified development workflow

## Iteration Notes
This foundation is superior to a raw Plone install as it includes:
- Proper add-on structure for our educational features
- Docker setup ready for AWS deployment
- Modern frontend integration with Volto
- Clear separation between core and customizations

Ready for Phase 1, though legacy analysis will be conceptual since we're starting fresh with modern Plone 6.1.2. 