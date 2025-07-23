
# Educational Content Platform User Journey

This document outlines the user journey for K-12 teachers (target users: grades 6-12 in U.S. public schools, under-resourced districts) through the modernized Plone-based Educational Content Platform, derived exclusively from project-overview.md. It segments the journey into phases focused on collaborative lesson planning and Google Classroom integration. The 6 features are integrated, with synergies highlighted (e.g., Standards Alignment enhances search, dashboard, and Google metadata; Google SSO streamlines access). The journey preserves Plone's core logic (e.g., workflows, permissions) while emphasizing modernizations (Python 3.12, API-first, Volto UI, Docker/AWS deployment).

## 1. Onboarding and Authentication
- **Entry Point**: Teacher accesses the platform via browser or mobile device.
- **Incorporated Features**:
  - Feature 1: Modern authentication (OAuth/2FA/SSO with Google) for secure login, preserving Plone's acl_users.
- **Synergies**: Google SSO streamlines access to all features, connecting to later integrations (Feature 6).
- **Journey Steps**: Teacher logs in using Google credentials; system verifies and grants role-based access (e.g., teacher permissions for lesson creation).
- **Next Segment**: Proceeds to dashboard for overview.

## 2. Dashboard and Overview
- **Entry Point**: Post-login, teacher views personalized dashboard.
- **Incorporated Features**:
  - Feature 5: Dashboard/analytics (Volto blocks showing engagement metrics, standards coverage analysis via portal_catalog).
  - Feature 4: Mobile-responsive design (Volto customizations for device-friendly UX).
- **Synergies**: Dashboard displays standards coverage (from Feature 2), optimized for mobile lesson planning; connects to search (Feature 3) for quick queries.
- **Journey Steps**: View metrics (e.g., lesson engagement); navigate via responsive Volto interface.
- **Next Segment**: Moves to content creation or search for lessons.

## 3. Content Discovery and Search
- **Entry Point**: Teacher searches for existing lessons or resources.
- **Incorporated Features**:
  - Feature 3: Advanced search and filtering (enhanced Portal Catalog with standards-based faceted search).
  - Feature 2: Standards Alignment System (educational standards taxonomy using plone.app.vocabularies for Common Core tagging).
- **Synergies**: Standards Alignment enhances search filtering (e.g., query by Common Core tags); mobile optimizations (Feature 4) ensure tablet-friendly results; feeds into dashboard analytics (Feature 5).
- **Journey Steps**: Enter query with standards filters; browse faceted results; select lesson for viewing/editing.
- **Next Segment**: Proceeds to lesson creation or editing.

## 4. Lesson Creation and Editing
- **Entry Point**: Teacher creates or edits a lesson plan.
- **Incorporated Features**:
  - Feature 2: Standards Alignment (tagging with Common Core/state standards for compliance tracking).
  - Feature 4: Mobile-responsive design (Volto customizations for tablet-optimized planning).
- **Synergies**: Standards tagging integrates with search (Feature 3) and dashboard (Feature 5); mobile UX supports on-the-go editing.
- **Journey Steps**: Add new content type (e.g., lesson); apply standards tags; edit in responsive Volto interface.
- **Next Segment**: Applies workflow for collaboration/review.

## 5. Collaboration and Workflow
- **Entry Point**: Teacher shares or reviews lesson plans.
- **Incorporated Features**:
  - Feature 6: Integration with third-party services (Google Classroom sync using API client, extending content types with standards metadata).
  - Feature 2: Standards Alignment (compliance tracking during collaboration).
- **Synergies**: Standards metadata enriches Google sync (Feature 6); workflow preserves Plone permissions, connecting to auth (Feature 1) for secure sharing.
- **Journey Steps**: Assign workflow state (e.g., review); collaborate via extended content types; sync to Google Classroom with metadata.
- **Next Segment**: Analyzes outcomes in dashboard.

## 6. Analytics and Integration Sync
- **Entry Point**: Teacher reviews lesson performance or syncs with external tools.
- **Incorporated Features**:
  - Feature 5: Dashboard/analytics (standards coverage analysis).
  - Feature 6: Google Classroom integration (sync assignments with metadata).
- **Synergies**: Dashboard shows metrics enhanced by standards (Feature 2) and search data (Feature 3); Google sync leverages metadata for compliance.
- **Journey Steps**: View analytics (e.g., engagement, coverage); initiate sync to Google Classroom.
- **Next Segment**: Cycles back to search or creation for iterations.

## 7. Logout and Session End
- **Entry Point**: Teacher logs out.
- **Incorporated Features**:
  - Feature 1: Modern authentication (secure session management).
- **Synergies**: Ensures all features (e.g., syncs, analytics) persist via Plone's core logic (ZODB/workflows).
- **Journey Steps**: Logout; system secures session.

This journey is cyclical, centered on lesson planning workflows. Features interconnect synergistically (e.g., Standards Alignment as cornerstone enhancing search, dashboard, and integration), supporting target user needs without breaking core Plone functionality. 