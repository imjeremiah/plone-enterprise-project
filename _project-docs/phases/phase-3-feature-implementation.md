
# Phase 3: Feature Implementation & Integration

## Scope
Implement Features 3/5/6 (Advanced Search, Teacher Dashboard, Google Classroom) building on Phase 2's foundation. These features leverage the standards alignment system and authentication from Phase 2 to create a complete teacher workflow. Focus on practical classroom integration and measurable impact.

## Deliverables
- Feature 3: Advanced search with standards filtering
- Feature 5: Teacher dashboard with analytics
- Feature 6: Google Classroom synchronization
- Performance benchmarks for search and dashboard
- Integration tests verifying feature synergies

## Tasks/Features

### Feature 3: Advanced Search and Filtering 
**Implementation Path**: Enhance catalog indexes + Volto search components + faceted navigation

#### Sub-Feature 3.1: Catalog Indexing
1. **Create custom indexes** in `backend/src/project/title/indexers.py`:
   ```python
   from plone.indexer import indexer
   from plone.dexterity.interfaces import IDexterityContent
   
   @indexer(IDexterityContent)
   def standards_index(obj):
       """Index for standards alignment"""
       adapted = IStandardsAligned(obj, None)
       if adapted:
           return adapted.standards or []
       return []
   
   @indexer(IDexterityContent)
   def grade_level_index(obj):
       """Index for grade levels"""
       # Extract from standards or content
       return getattr(obj, 'grade_levels', [])
   ```

2. **Register indexes** in `backend/src/project/title/profiles/default/catalog.xml`:
   ```xml
   <?xml version="1.0"?>
   <object name="portal_catalog">
     <index name="standards" meta_type="KeywordIndex">
       <indexed_attr value="standards_index"/>
     </index>
     <index name="grade_level" meta_type="KeywordIndex">
       <indexed_attr value="grade_level_index"/>
     </index>
     <index name="subject_area" meta_type="KeywordIndex">
       <indexed_attr value="subject_area"/>
     </index>
   </object>
   ```

3. **Create search endpoint** in `backend/src/project/title/api/search.py`:
   ```python
   from plone.restapi.services import Service
   
   class AdvancedSearch(Service):
       """Enhanced search with facets"""
       
       def reply(self):
           query = self.build_query()
           results = self.context.portal_catalog(query)
           return self.serialize_results(results)
   ```

#### Sub-Feature 3.2: Volto Search Interface 
1. **Create search components** in `frontend/packages/volto-project-title/src/components/Search/`:
   ```jsx
   // AdvancedSearch.jsx
   import React, { useState } from 'react';
   import { SearchWidget } from '@plone/volto/components';
   import { Facets } from './Facets';
   
   export const AdvancedSearch = () => {
     const [filters, setFilters] = useState({
       standards: [],
       grade_level: [],
       subject_area: []
     });
     
     return (
       <div className="advanced-search">
         <SearchWidget />
         <Facets 
           filters={filters} 
           onChange={setFilters}
         />
         <SearchResults filters={filters} />
       </div>
     );
   };
   ```

2. **Create faceted navigation**:
   ```jsx
   // Facets.jsx
   export const Facets = ({ filters, onChange }) => {
     // Standards vocabulary from Phase 2
     const { data: standards } = useVocabulary('project.title.vocabularies.Standards');
     
     return (
       <div className="search-facets">
         <FacetGroup
           title="Standards"
           options={standards}
           selected={filters.standards}
           onChange={(val) => onChange({...filters, standards: val})}
         />
         {/* Grade level and subject facets */}
       </div>
     );
   };
   ```

3. **Mobile-optimized styles** in `frontend/packages/volto-project-title/src/theme/Search.less`:
   ```less
   .advanced-search {
     @media (max-width: 768px) {
       .search-facets {
         // Collapsible facets on mobile
         position: fixed;
         bottom: 0;
         transform: translateY(calc(100% - 60px));
         transition: transform 0.3s;
         
         &.expanded {
           transform: translateY(0);
         }
       }
     }
   }
   ```

#### Sub-Feature 3.3: Performance Optimization 
1. **Add caching** for common searches
2. **Implement pagination** for large result sets
3. **Use lazy loading** for result previews
4. **Index optimization** for frequently searched fields

### Feature 5: Teacher Dashboard/Analytics 
**Implementation Path**: Volto blocks + catalog queries + chart visualization

#### Sub-Feature 5.1: Dashboard Block Type 
1. **Create block** in `frontend/packages/volto-project-title/src/components/Blocks/Dashboard/`:
   ```jsx
   // DashboardBlock.jsx
   import React from 'react';
   import { Block } from '@plone/volto/components';
   import { StandardsCoverage } from './StandardsCoverage';
   import { RecentActivity } from './RecentActivity';
   import { ClassroomSync } from './ClassroomSync';
   
   export const DashboardBlock = ({ data }) => {
     return (
       <div className="dashboard-block">
         <div className="dashboard-grid">
           <StandardsCoverage />
           <RecentActivity />
           <ClassroomSync />
           <PopularLessons />
         </div>
       </div>
     );
   };
   ```

2. **Register block** in `frontend/packages/volto-project-title/src/config.js`:
   ```jsx
   export default function applyConfig(config) {
     config.blocks.blocksConfig.teacherDashboard = {
       id: 'teacherDashboard',
       title: 'Teacher Dashboard',
       icon: chartIcon,
       group: 'common',
       view: DashboardBlock,
       edit: DashboardBlockEdit,
       restricted: false,
       sidebarTab: 1,
     };
     return config;
   }
   ```

#### Sub-Feature 5.2: Analytics Components
1. **Standards coverage chart**:
   ```jsx
   // StandardsCoverage.jsx
   import { PieChart, Pie, Cell } from 'recharts';
   
   export const StandardsCoverage = () => {
     const { data } = useQuery('/@@standards-analytics');
     
     return (
       <div className="analytics-card">
         <h3>Standards Coverage</h3>
         <PieChart width={300} height={200}>
           <Pie data={data} dataKey="count">
             {data.map((entry, index) => (
               <Cell key={index} fill={COLORS[index % COLORS.length]} />
             ))}
           </Pie>
         </PieChart>
         <div className="coverage-details">
           {data.map(standard => (
             <div key={standard.id}>
               {standard.name}: {standard.percentage}%
             </div>
           ))}
         </div>
       </div>
     );
   };
   ```

2. **Backend analytics endpoint** in `backend/src/project/title/api/analytics.py`:
   ```python
   from plone.restapi.services import Service
   from collections import Counter
   
   class StandardsAnalytics(Service):
       """Analyze standards coverage"""
       
       def reply(self):
           catalog = self.context.portal_catalog
           lessons = catalog(portal_type='Lesson')
           
           standards_count = Counter()
           for brain in lessons:
               obj = brain.getObject()
               standards = getattr(obj, 'standards', [])
               standards_count.update(standards)
           
           return self.format_analytics(standards_count)
   ```

#### Sub-Feature 5.3: Real-time Updates
1. **WebSocket integration** for live updates
2. **Efficient catalog queries** with caching
3. **Progressive loading** for better UX

### Feature 6: Google Classroom Integration 
**Implementation Path**: Google API client + content sync + OAuth from Phase 2

#### Sub-Feature 6.1: Google API Setup 
1. **Install dependencies** in `backend/requirements.txt`:
   ```
   google-api-python-client==2.100.0
   google-auth-httplib2==0.1.1
   google-auth-oauthlib==1.1.0
   ```

2. **Create service wrapper** in `backend/src/project/title/integrations/google_classroom.py`:
   ```python
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build
   
   class GoogleClassroomService:
       """Wrapper for Google Classroom API"""
       
       def __init__(self, user):
           self.credentials = self.get_user_credentials(user)
           self.service = build('classroom', 'v1', 
                               credentials=self.credentials)
       
       def list_courses(self):
           """Get teacher's courses"""
           results = self.service.courses().list(
               teacherId='me'
           ).execute()
           return results.get('courses', [])
       
       def create_assignment(self, course_id, lesson):
           """Push lesson as assignment"""
           assignment = {
               'title': lesson.title,
               'description': lesson.description,
               'materials': self.convert_materials(lesson),
               'workType': 'ASSIGNMENT',
               'state': 'DRAFT'
           }
           return self.service.courses().courseWork().create(
               courseId=course_id,
               body=assignment
           ).execute()
   ```

#### Sub-Feature 6.2: Content Sync Interface 
1. **Create sync action** in `frontend/packages/volto-project-title/src/components/GoogleSync/`:
   ```jsx
   // SyncToClassroom.jsx
   import React, { useState } from 'react';
   import { useSelector } from 'react-redux';
   
   export const SyncToClassroom = ({ content }) => {
     const [selectedCourse, setSelectedCourse] = useState(null);
     const [syncing, setSyncing] = useState(false);
     const courses = useSelector(state => state.googleClassroom.courses);
     
     const handleSync = async () => {
       setSyncing(true);
       try {
         await syncToClassroom({
           content_uid: content.UID,
           course_id: selectedCourse,
           include_standards: true
         });
         toast.success('Synced to Google Classroom!');
       } catch (error) {
         toast.error('Sync failed: ' + error.message);
       }
       setSyncing(false);
     };
     
     return (
       <div className="sync-to-classroom">
         <h3>Share to Google Classroom</h3>
         <CourseSelector 
           courses={courses}
           value={selectedCourse}
           onChange={setSelectedCourse}
         />
         <SyncOptions />
         <Button 
           primary 
           loading={syncing}
           disabled={!selectedCourse}
           onClick={handleSync}
         >
           Share as Assignment
         </Button>
       </div>
     );
   };
   ```

2. **Add to content actions** in toolbar or sidebar

#### Sub-Feature 6.3: Permissions & Security 
1. **Scope management** - only request needed permissions:
   ```python
   SCOPES = [
       'https://www.googleapis.com/auth/classroom.courses.readonly',
       'https://www.googleapis.com/auth/classroom.coursework.students'
   ]
   ```

2. **Token storage** - secure OAuth tokens:
   ```python
   from plone.app.users.browser.interfaces import IUserData
   
   class IGoogleTokens(IUserData):
       """Store Google OAuth tokens"""
       
       google_access_token = schema.TextLine(
           title="Access Token",
           required=False
       )
       
       google_refresh_token = schema.TextLine(
           title="Refresh Token", 
           required=False
       )
   ```

3. **Permission checks** - verify teacher has access to course

#### Sub-Feature 6.4: Standards Metadata 
1. **Include standards** in assignment metadata
2. **Map to Google's** rubric/grading features
3. **Sync grade level** and subject information

### Task 1: Integration Testing & Performance 

1. **Feature integration tests** in `backend/tests/test_integrations.py`:
   ```python
   def test_search_with_standards_filter(self):
       """Test that search properly filters by standards"""
       self.create_lesson_with_standards(['CCSS.Math.5.NF.1'])
       results = self.search({'standards': 'CCSS.Math.5.NF.1'})
       self.assertEqual(len(results), 1)
   
   def test_dashboard_standards_count(self):
       """Test dashboard correctly counts standards"""
       # Create lessons with various standards
       analytics = self.get_analytics()
       self.assertIn('CCSS.Math.5.NF.1', analytics)
   ```

2. **Performance benchmarks**:
   - Search response time < 200ms for 10k items
   - Dashboard load time < 1s
   - Google sync < 5s per assignment

3. **Load testing** with realistic data volumes

## Impacted Files and Directories
- **Backend Structure**:
  - `backend/src/project/title/indexers.py` - Catalog indexes
  - `backend/src/project/title/api/` - REST endpoints
  - `backend/src/project/title/integrations/` - Google Classroom
  - `backend/profiles/default/catalog.xml` - Index registration
  
- **Frontend Structure**:
  - `frontend/packages/volto-project-title/src/components/Search/` - Search UI
  - `frontend/packages/volto-project-title/src/components/Blocks/Dashboard/` - Analytics
  - `frontend/packages/volto-project-title/src/components/GoogleSync/` - Classroom sync
  - `frontend/packages/volto-project-title/src/actions/` - API actions

## Review Checklist
- [ ] Search returns relevant results with standards filter
- [ ] Dashboard loads quickly with real data
- [ ] Google Classroom sync preserves all metadata
- [ ] Mobile experience remains smooth
- [ ] No performance degradation from Phase 2
- [ ] All existing tests still pass
- [ ] New integration tests pass
- [ ] Security review for Google integration

## Rules Adherence
- ZCA patterns for all extensions
- No core Plone modifications
- Responsive design maintained
- Progressive enhancement approach
- AI-friendly code organization

## Time Estimates
- Feature 3 (Search): 6-8 hours
- Feature 5 (Dashboard): 5-7 hours  
- Feature 6 (Google Classroom): 8-10 hours
- Integration Testing: 3-4 hours
- **Total**: 22-29 hours (3-4 days)

## Risk Mitigation
1. **Search Performance**: Start with simple queries, optimize iteratively
2. **Dashboard Queries**: Cache expensive calculations, use async loading
3. **Google API Limits**: Implement rate limiting and quota monitoring
4. **OAuth Complexity**: Thoroughly test token refresh flow
5. **Data Privacy**: Clear data handling documentation for schools

## Dependencies on Phase 2
- Standards vocabulary (Feature 2) used in search and sync
- OAuth setup (Feature 1) extended for Google APIs
- Mobile patterns (Feature 4) applied to new components

## Iteration Notes
These features complete the core platform functionality. Phase 4 will focus on polish, performance optimization, and production readiness. The tight integration between features (standards in search/dashboard/sync) demonstrates the platform's coherent design. 