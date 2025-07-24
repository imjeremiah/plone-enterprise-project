# Educational Content Platform Modernization Project

## Introduction

In the professional software development world, developers often inherit massive, complex legacy codebases rather than building from scratch. This project adapts the enterprise legacy modernization scenario by selecting Plone CMS—a mature, open-source content management system with over 1.1 million lines of code originally rooted in older Python versions (2.7/3.6)—and evolving it into a specialized Classroom Management Platform for a new target market: K-12 teachers.

Using Plone 6.1 as the base (evolving from its legacy foundations while incorporating modernizations like Python 3.12), we'll leverage AI-assisted tools such as Cursor for code exploration, generation, and debugging to understand, preserve, and enhance the system's core business logic (e.g., content workflows, user management, and integrations). This results in a relaunch-ready application that demonstrates the ability to transform legacy systems for contemporary needs, directly translating to enterprise value by unlocking embedded business logic for streamlined classroom operations.

## Core Challenge

Modernize Plone CMS (1.1M+ lines) by identifying K-12 teachers as the target user segment, then use AI-assisted development to create a relaunch-ready Classroom Management Platform. This preserves Plone's core business logic (e.g., hierarchical content storage in ZODB, permissions, and workflows) while delivering a modern user experience and architecture, including API-first design and cloud deployment.

**Success means:** Shipping a working, containerized application deployed to AWS, with a before/after demonstration quantifying improvements (e.g., reduced classroom management time by 40%), showcasing deep legacy understanding and AI-driven transformation.

## Project Pathway

**Legacy Codebase:** Plone CMS (1.1M lines, using version 6.1 as the evolutionary base from Python 2.7/3.6 roots, justified by its retention of legacy patterns while enabling modern extensions).

**Why This System:** Plone contains years of web application patterns, user management systems, content workflows, and integration logic that represent typical enterprise Python deployments, making it ideal for adaptation to classroom management needs like seating arrangements, student tracking, and daily operations.

**Modernization Opportunities:**
- Python 3.12 migration with async/await patterns (implemented via local setup and feature code).
- Modern container deployment with Docker (local testing and AWS integration).
- API-first architecture replacing monolithic structure (using plone.restapi for headless features).
- Modern frontend frameworks replacing server-side templates (customizing Volto for responsive, React-based UI).

## Target User Selection

Based on the pathway, the target user segment is K-12 teachers (grades 6-12) in U.S. public schools, particularly in under-resourced districts, who need efficient tools for daily classroom management and operations.

### Examples of Target Users (Adapted):
- **Plone → Classroom Management Platform:** Teachers needing real-time classroom tools for seating charts, student participation tracking, and substitute preparation.

### Target User Requirements:
- Represents a legitimate market opportunity: Teachers spend 5+ hours weekly on classroom management tasks; 90% lack integrated digital tools for daily operations, relying on paper-based systems that don't scale.
- Highlights specific pain points solved by modern technology: Manual seating charts (solved by drag-drop interface), unfair participation patterns (solved by random picker with tracking), substitute chaos (solved by automated folder generation), and lack of real-time visibility (solved by dashboard).
- Narrow enough for 7 days (focus on daily classroom operations) but broad enough for meaningful modernization (demonstrates value for 3.7M+ U.S. teachers via quantifiable time savings).

## Grading Criteria

The project will target the highest scores by adhering to the criteria, with specific strategies:

### 1. Legacy System Understanding (Target: 18-20 points)
Demonstrates deep comprehension of Plone's original codebase through architecture mapping (e.g., ZODB flows, ZCA components) via AI-assisted exploration, identifying critical logic like content types and browser views to preserve in features.

### 2. Six New Features Implementation (Target: 50 points - 10 points each)
Add exactly 6 meaningful features that enhance Plone for teachers, each functional, value-adding, and integrated via ZCA/Volto without breaking core functionality.

**Feature Requirements:** Each integrates with existing code (e.g., REST API, browser views) and is tested for completeness.

**Specific Features (Tied to Brief Examples):**
- Modern authentication (OAuth/SSO with Google): Secure login preserving Plone's acl_users.
- Seating Chart Generator: Dexterity type with drag-drop JavaScript for visual classroom layout.
- Random Student Picker: Widget ensuring equitable participation with history tracking.
- Substitute Folder Generator: Automated action compiling daily materials for seamless transitions.
- Lesson Timer Widget: JavaScript timer for activity management and instructional pacing.
- Digital Hall Pass: QR code system for student movement tracking and safety compliance.
- Teacher Dashboard: Command center aggregating all tools with real-time classroom status.

**Scoring Strategy:** Aim for "Excellent" by quantifying value (e.g., "Reduces daily admin time by 45 minutes") and ensuring integration (e.g., unit tests via bin/test).

**Feature Integration Synergy:**
- **Dashboard** displays data from all other features in unified view
- **Google SSO** provides single sign-on across all tools
- **Seating Chart** feeds into Random Picker for location-aware selection
- **Hall Pass** data shows on Dashboard for real-time monitoring
- **Timer Widget** integrates with lesson planning workflows
- **Substitute Folder** pulls from all features for comprehensive handoff

### 3. Technical Implementation Quality (Target: 17-20 points)
Code follows best practices (e.g., PEP 8, proper browser view registration), with efficient catalog queries, security (e.g., OAuth), and Docker/AWS deployment for performance. Quantify: E.g., "Dashboard loads in <1 second with 30 students."

### 4. AI Utilization Documentation (Target: 9-10 points)
Comprehensive logging in ai-usage.md, with 50+ prompts/techniques categorized by phase, innovative uses (e.g., AI-generated QR code logic), and methodology (iterative prompting for Plone pattern compliance).

## 7-Day Project Timeline

### Days 1-2: Legacy System Mastery
- Complete checklist.md setup for local Plone 6.1 instance.
- Analyze architecture using AI-assisted exploration (e.g., Cursor prompts for browser views, Dexterity types).
- Define teacher segment needs/pain points (e.g., time wasted on attendance/seating).
- Map core logic (e.g., content types, view patterns) to preserve.
- Reproduce base functionality (test core features "as is").

### Days 3-4: Modernization Design & Foundation
- Design architecture: Browser views and Dexterity types, preserving logic while adding features.
- Implement deployment pipeline: Dockerize locally, deploy to AWS ECS (free tier) for relaunch-ready app.
- Create base Dexterity types for classroom data.
- Begin core features (e.g., seating chart foundation).

### Days 5-6: Feature Implementation & Integration
- Implement/test 6 features (3 per day), ensuring no breakage via modular patterns and bin/test:
  - Seating Chart with drag-drop interface
  - Random Student Picker with participation tracking
  - Substitute Folder Generator with smart organization
  - Lesson Timer with activity management
  - Digital Hall Pass with QR codes
  - Teacher Dashboard aggregating all data
- Optimize/perform tests for quantified improvements (e.g., setup time reduction benchmarks).
- Update ai-usage.md with prompts (e.g., for code gen/debugging).

### Day 7: Polish & Launch Preparation
- Final testing/bug fixes for production-ready quality.
- Create deployment docs (e.g., Docker/AWS guide) and teacher training materials.
- Prepare before/after demo: Side-by-side videos showing paper vs. digital workflows with time savings.
- Finalize ai-usage.md and overall methodology (e.g., how AI enabled rapid feature development).

## Final Thoughts

This project bridges academic concepts with professional reality by evolving Plone 6.1 into a Classroom Management Platform, preserving its legacy strengths (e.g., robust permissions, content management) for teachers' daily operational needs. The Teacher Dashboard serves as the integration point, creating synergy across all features - displaying real-time seating charts, tracking participation equity, monitoring hall passes, and providing quick access to all classroom tools.

By focusing on classroom management as the core theme, we create a cohesive platform where each feature enhances the others, demonstrating deep understanding of Plone's component architecture. The combination of Docker/AWS deployment and AI-assisted development shows the ability to transform complex enterprise systems competitively for specialized markets.

Success here proves we can take an enterprise codebase, understand its architectural value, and relaunch it for new opportunities like educational operations, directly relevant to career growth. **Remember:** The goal is to evolve Plone's embedded value for teachers, using modern tools and solving real daily pain points. All decisions (e.g., visual tools, time-saving automation) ensure a thorough, high-scoring outcome within 7 days.