
# Phase 1: Platform Analysis & Feature Planning

## Scope
Analyze modern Plone 6.1.2 architecture for extension points and conduct conceptual legacy analysis to understand evolution from older Plone versions. Map integration points for the 7 classroom management features and identify teacher workflow gaps. This phase provides the "understanding" required by the grading rubric while planning practical implementation.

## Deliverables
- Conceptual legacy comparison (Plone 2.x/3.x vs 6.1.2)
- Feature integration map showing where each of 7 features plugs into Plone
- Teacher workflow gap analysis for classroom management with vanilla Plone
- Technical approach documentation for risk-free implementation
- AI usage documentation for architecture exploration

## Tasks/Features

### Task 1: Conceptual Legacy Analysis
1. Research Plone 2.7/3.x architecture patterns (via documentation/articles)
2. Document key differences:
   - Python 2.7 → Python 3.12 migration benefits
   - Zope 2 → Zope 5 improvements  
   - Classic UI → Volto React frontend
   - Archetypes → Dexterity content types
3. Create comparison showing how modern Plone addresses legacy limitations
4. Frame our project as "leveraging evolved Plone" rather than migrating
5. Document in `_project-docs/plone/legacy-evolution-analysis.md`

### Task 2: Feature Integration Mapping
1. For each of the 7 features, identify:
   - Integration points in Plone architecture
   - Required components (behaviors, viewlets, utilities, browser views)
   - Risk assessment (what could break)
   - Implementation approach
2. Create feature matrix:
   ```
   Feature 1: Google SSO → pas.plugins.authomatic ✅ COMPLETE
   Feature 2: Seating Chart → Dexterity type + JSON field + drag-drop JS
   Feature 3: Random Picker → Browser view + AJAX + fairness algorithm
   Feature 4: Digital Hall Pass → Dexterity type + QR generation + time tracking
   Feature 5: Timer Widget → JavaScript + localStorage + Web Audio API
   Feature 6: Sub Folder → Browser view + plone.api + content aggregation
   Feature 7: Dashboard → Browser view + catalog queries + real-time updates
   ```
3. Document in `_project-docs/project/feature-integration-map.md`

### Task 3: Teacher Workflow Analysis
1. Map current vanilla Plone workflow for classroom management
2. Identify pain points for teachers:
   - No integrated classroom tools
   - Paper-based seating charts
   - Manual participation tracking
   - No timer management
   - Cumbersome substitute preparation
3. Document how each feature addresses specific pain points:
   - Seating Chart: Eliminates paper charts, enables drag-drop arrangements
   - Random Picker: Ensures fair participation, tracks history
   - Hall Pass: Digital accountability, time tracking
   - Timer: Visible to all students, audio alerts
   - Sub Folder: One-click preparation when sick
   - Dashboard: Real-time classroom awareness
4. Create before/after workflow comparison
5. Save as `_project-docs/project/teacher-workflow-gaps.md`

### Task 4: Technical Approach & Risk Mitigation
1. Document implementation strategy:
   - Use Plone add-on pattern (no core modifications)
   - Leverage ZCA for clean integration
   - Progressive enhancement for JavaScript features
   - Test each feature in isolation
   - Maintain upgrade path
2. Create testing checklist for each feature:
   - Unit tests for Python components
   - JavaScript tests for interactive features
   - Integration tests for feature interactions
   - Performance tests for real-time updates
3. Plan rollback strategy if features cause issues
4. Document in `_project-docs/project/implementation-strategy.md`

## Impacted Files and Directories
- **New Documentation**: 
  - `_project-docs/plone/legacy-evolution-analysis.md`
  - `_project-docs/project/feature-integration-map.md` ✅ UPDATED
  - `_project-docs/project/teacher-workflow-gaps.md` ✅ UPDATED
  - `_project-docs/project/implementation-strategy.md` ✅ UPDATED
- **Existing Docs** (reference only):
  - Review all files in `_project-docs`
  - No modifications to existing architecture docs

**Review Checklist**:
- ✅ Legacy analysis provides context without actual migration
- ✅ All 7 features have clear integration points mapped
- ✅ Teacher pain points documented with solutions
- ✅ Technical risks identified and mitigated
- ✅ Ready to start feature implementation

## Rules Adherence
- No core Plone modifications (add-on pattern only)
- Follow ZCA principles for integrations
- Follow file naming conventions from plone-project-rules.md
- Maintain clear separation of concerns
- Document all architectural decisions

## Key Insights for Grading
This phase satisfies the "Legacy System Understanding" criterion by:
1. Demonstrating knowledge of Plone's evolution
2. Understanding core architecture and extension points
3. Identifying business logic to preserve (workflows, permissions, content management)
4. Planning modernization without breaking core functionality

## Iteration Notes
This analysis phase should take maximum 1 day. The real value comes from feature implementation (Phases 2-3), which is 50% of the grade. Move quickly through analysis to maximize development time. 