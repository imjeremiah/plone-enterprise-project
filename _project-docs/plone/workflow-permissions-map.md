# Workflow & Permissions Architecture Map: Security & State Management

## Executive Summary

This document maps the **Workflow Engine and Security System** within Plone 6.1.2, detailing state machines, permission models, and access control mechanisms. It covers both **core Plone capabilities** (fully implemented) and **planned educational platform features** (in design/development) for the K-12 Educational Content Platform.

**Document Status**: Core Plone architecture is current and accurate. Educational features are marked with implementation status indicators.

---

## 🔄 Workflow Engine Architecture

### Core Plone Workflow System ✅ Implemented
```
┌──────────────────────────────────────────────────────────────┐
│                PLONE WORKFLOW ARCHITECTURE                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                WORKFLOW LAYER                           │ │
│  │ ┌─────────────────┐  ┌─────────────────┐                │ │
│  │ │ WORKFLOW DEFS   │  │ STATE MACHINES  │                │ │
│  │ │ • States        │  │ • Transitions   │                │ │
│  │ │ • Transitions   │  │ • Guards        │                │ │
│  │ │ • Variables     │  │ • Scripts       │                │ │
│  │ │ • Permissions   │  │ • Worklists     │                │ │
│  │ └─────────────────┘  └─────────────────┘                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                               │
│                              │ Action Execution              │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              WORKFLOW TOOL                              │ │
│  │ ┌─────────────────┐  ┌─────────────────┐                │ │
│  │ │ WORKFLOW MGMT   │  │ HISTORY TRACK   │                │ │
│  │ │ • Registration  │  │ • Audit Trail   │                │ │
│  │ │ • Type Mapping  │  │ • Comments      │                │ │
│  │ │ • Policy Config │  │ • Timestamps    │                │ │
│  │ │ • Chain Config  │  │ • Actor Info    │                │ │
│  │ └─────────────────┘  └─────────────────┘                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                               │
│                              │ Security Integration          │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               SECURITY LAYER                            │ │
│  │ ┌─────────────────┐  ┌─────────────────┐                │ │
│  │ │ ROLE ASSIGNMENT │  │ PERMISSION MAP  │                │ │
│  │ │ • Local Roles   │  │ • State Perms   │                │ │
│  │ │ • Global Roles  │  │ • Action Perms  │                │ │
│  │ │ • Group Roles   │  │ • Guard Perms   │                │ │
│  │ │ • Acquisition   │  │ • Inherit Perms │                │ │
│  │ └─────────────────┘  └─────────────────┘                │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Default Plone Workflow Definitions ✅ Implemented

### Simple Publication Workflow (Active in Project)
```python
# Currently configured as default workflow in project-title/backend
SIMPLE_PUBLICATION_WORKFLOW = {
    'id': 'simple_publication_workflow',
    'title': 'Simple Publication Workflow',
    'description': 'Basic private → published workflow',
    
    'states': {
        'private': {
            'id': 'private',
            'title': 'Private',
            'description': 'Visible only to owner and managers',
            'permissions': {
                'View': ['Manager', 'Owner'],
                'Access contents information': ['Manager', 'Owner'],
                'Modify portal content': ['Manager', 'Owner'],
                'Delete objects': ['Manager', 'Owner'],
            }
        },
        'published': {
            'id': 'published',
            'title': 'Published',
            'description': 'Visible to everyone',
            'permissions': {
                'View': ['Anonymous'],
                'Access contents information': ['Anonymous'],
                'Modify portal content': ['Manager', 'Owner'],
                'Delete objects': ['Manager'],
            }
        }
    },
    
    'transitions': {
        'publish': {
            'id': 'publish',
            'title': 'Publish',
            'new_state_id': 'published',
            'trigger': 'USER',
            'guard': {
                'permissions': ['Review portal content'],
                'roles': ['Manager', 'Reviewer'],
                'expression': 'python:True'
            },
            'actbox_name': 'Publish',
            'actbox_url': '%(content_url)s/content_status_modify?workflow_action=publish'
        },
        'retract': {
            'id': 'retract',
            'title': 'Retract',
            'new_state_id': 'private',
            'trigger': 'USER',
            'guard': {
                'permissions': ['Modify portal content'],
                'roles': ['Manager', 'Owner'],
            }
        }
    },
    
    'variables': {
        'action': {
            'description': 'Previous transition',
            'default_expr': 'transition/getId|nothing',
            'for_status': True,
            'update_always': True
        },
        'actor': {
            'description': 'User performing action',
            'default_expr': 'user/getId',
            'for_status': True,
            'update_always': True
        },
        'comments': {
            'description': 'Comments about action',
            'default_expr': "python:state_change.kwargs.get('comment', '')",
            'for_status': True,
            'update_always': True
        },
        'review_history': {
            'description': 'Workflow history',
            'default_expr': '',
            'for_status': False,
            'update_always': False
        },
        'time': {
            'description': 'Time of action',
            'default_expr': 'state_change/getDateTime',
            'for_status': True,
            'update_always': True
        }
    }
}
```

### Community Workflow ✅ Available (Not Currently Used)
```python
# Complex workflow available in Plone but not configured for educational platform
COMMUNITY_WORKFLOW = {
    'id': 'community_workflow',
    'title': 'Community Workflow',
    'description': 'Collaborative content creation workflow',
    
    'states': {
        'private': {
            'id': 'private',
            'title': 'Private',
            'description': 'Only visible to creator',
            'permissions': {
                'View': ['Manager', 'Owner'],
                'Modify portal content': ['Manager', 'Owner'],
            }
        },
        'pending': {
            'id': 'pending',
            'title': 'Pending Review',
            'description': 'Submitted for review',
            'permissions': {
                'View': ['Manager', 'Reviewer', 'Owner'],
                'Modify portal content': ['Manager', 'Owner'],
            }
        },
        'internally_published': {
            'id': 'internally_published',
            'title': 'Internally Published',
            'description': 'Published to authenticated users',
            'permissions': {
                'View': ['Manager', 'Member'],
                'Modify portal content': ['Manager', 'Editor'],
            }
        },
        'published': {
            'id': 'published',
            'title': 'Published',
            'description': 'Published to everyone',
            'permissions': {
                'View': ['Anonymous'],
                'Modify portal content': ['Manager', 'Editor'],
            }
        },
        'rejected': {
            'id': 'rejected',
            'title': 'Rejected',
            'description': 'Rejected by reviewer',
            'permissions': {
                'View': ['Manager', 'Reviewer', 'Owner'],
                'Modify portal content': ['Manager', 'Owner'],
            }
        }
    },
    
    # ... transitions configuration continues
}
```

---

## 🔐 Security & Permission System ✅ Core Plone Feature

### Standard Plone Permissions (Active in Project)
```python
# Core permissions currently in use
PLONE_PERMISSIONS = {
    # Content permissions
    'View': {
        'id': 'View',
        'title': 'View content',
        'description': 'Access to view content objects',
        'roles': ['Manager', 'Owner', 'Member', 'Anonymous']
    },
    'Access contents information': {
        'id': 'Access contents information',
        'title': 'Access metadata',
        'description': 'Access to object metadata',
        'roles': ['Manager', 'Owner', 'Member', 'Anonymous']
    },
    'Modify portal content': {
        'id': 'Modify portal content',
        'title': 'Edit content',
        'description': 'Modify existing content',
        'roles': ['Manager', 'Owner', 'Editor']
    },
    'Add portal content': {
        'id': 'Add portal content',
        'title': 'Add content',
        'description': 'Create new content',
        'roles': ['Manager', 'Contributor']
    },
    'Delete objects': {
        'id': 'Delete objects',
        'title': 'Delete content',
        'description': 'Remove content objects',
        'roles': ['Manager', 'Owner']
    },
    
    # Workflow permissions
    'Review portal content': {
        'id': 'Review portal content',
        'title': 'Review content',
        'description': 'Review and approve content',
        'roles': ['Manager', 'Reviewer']
    },
    'Request review': {
        'id': 'Request review',
        'title': 'Request review',
        'description': 'Submit content for review',
        'roles': ['Manager', 'Owner', 'Contributor']
    },
    
    # Administration permissions
    'Manage portal': {
        'id': 'Manage portal',
        'title': 'Site administration',
        'description': 'Full site management',
        'roles': ['Manager']
    },
    'Manage users': {
        'id': 'Manage users',
        'title': 'User management',
        'description': 'Create and manage users',
        'roles': ['Manager']
    },
    'Sharing page: Delegate roles': {
        'id': 'Sharing page: Delegate roles',
        'title': 'Delegate permissions',
        'description': 'Grant local roles to users',
        'roles': ['Manager', 'Owner']
    }
}
```

### Standard Plone Roles ✅ Active in Project
```python
# Roles currently available in the platform
PLONE_ROLES = {
    'Anonymous': {
        'title': 'Anonymous User',
        'description': 'Unauthenticated visitor',
        'permissions': [
            'View',
            'Access contents information'
        ]
    },
    'Authenticated': {
        'title': 'Authenticated User', 
        'description': 'Logged-in user base role',
        'permissions': [
            'View',
            'Access contents information'
        ]
    },
    'Member': {
        'title': 'Member',
        'description': 'Regular site member',
        'inherits': ['Authenticated'],
        'permissions': [
            'View',
            'Access contents information',
            'Add portal content'  # In personal folder
        ]
    },
    'Contributor': {
        'title': 'Contributor',
        'description': 'Can create content for review',
        'inherits': ['Member'],
        'permissions': [
            'Add portal content',
            'Request review',
            'Modify portal content'  # Own content only
        ]
    },
    'Editor': {
        'title': 'Editor',
        'description': 'Can edit all content',
        'inherits': ['Contributor'],
        'permissions': [
            'Modify portal content',  # All content
            'Add portal content',
            'Copy or Move'
        ]
    },
    'Reviewer': {
        'title': 'Reviewer',
        'description': 'Can review and publish content',
        'inherits': ['Editor'],
        'permissions': [
            'Review portal content',
            'Access inactive portal content'
        ]
    },
    'Manager': {
        'title': 'Manager',
        'description': 'Site administrator',
        'inherits': ['Reviewer'],
        'permissions': [
            'Manage portal',
            'Manage users',
            'Delete objects',  # All objects
            'Sharing page: Delegate roles'
        ]
    },
    'Owner': {
        'title': 'Owner',
        'description': 'Content owner (local role)',
        'permissions': [
            'View',
            'Modify portal content',  # Own content
            'Delete objects',         # Own content
            'Sharing page: Delegate roles'  # Own content
        ]
    }
}
```

---

## 🏗️ Workflow Tool Implementation ✅ Core Plone

### Workflow Tool (Active in project-title/backend)
```python
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.CMFCore.utils import getToolByName

class WorkflowTool(Folder):
    """Portal workflow management tool - Core Plone implementation"""
    
    id = 'portal_workflow'
    meta_type = 'CMF Workflow Tool'
    
    def __init__(self):
        self._workflows = {}
        self._default_workflow = ('simple_publication_workflow',)
        
    def getWorkflowFor(self, obj):
        """Get workflow definition for object"""
        if hasattr(obj, 'portal_type'):
            chain = self.getChainFor(obj.portal_type)
            if chain:
                return self._workflows.get(chain[0])
        return None
        
    def doActionFor(self, obj, action, comment='', **kw):
        """Execute workflow action on object"""
        workflow = self.getWorkflowFor(obj)
        if workflow is None:
            raise WorkflowException('No workflow found')
            
        # Check guards
        if not self._checkGuards(obj, workflow, action):
            raise Unauthorized('Action not allowed')
            
        # Execute transition
        old_state = self.getInfoFor(obj, 'review_state')
        workflow.doActionFor(obj, action, comment=comment, **kw)
        new_state = self.getInfoFor(obj, 'review_state')
        
        # Update security
        if old_state != new_state:
            self._updateRoleMappingsFor(obj)
            
        # Fire events
        self._fireTransitionEvent(obj, action, old_state, new_state)
        
    # ... additional implementation details
```

---

## 🎯 Educational Platform Workflows 📋 Planned Features

### Teacher Content Workflow 📋 Designed (Not Implemented)
```python
# PLANNED FEATURE: Specialized workflow for educational content
# Status: Design phase - not yet implemented in project-title/backend
TEACHER_CONTENT_WORKFLOW = {
    'id': 'teacher_content_workflow',
    'title': 'Teacher Content Workflow',
    'description': 'Workflow for educational content creation',
    'implementation_status': 'PLANNED - Phase 3',
    
    'states': {
        'draft': {
            'id': 'draft',
            'title': 'Draft',
            'description': 'Content being developed',
            'permissions': {
                'View': ['Manager', 'Owner', 'TeacherRole'],  # TeacherRole to be created
                'Modify portal content': ['Manager', 'Owner'],
                'Standards Alignment Access': ['Manager', 'Owner', 'StandardsEditor']  # Custom permission
            }
        },
        'peer_review': {
            'id': 'peer_review',
            'title': 'Peer Review',
            'description': 'Under review by teaching peers',
            'permissions': {
                'View': ['Manager', 'TeacherRole', 'Owner'],
                'Add Comments': ['Manager', 'TeacherRole'],  # Custom permission
                'Review Content': ['Manager', 'DepartmentHead'],
                'Standards Alignment Access': ['Manager', 'StandardsEditor']
            }
        },
        'curriculum_approved': {
            'id': 'curriculum_approved',
            'title': 'Curriculum Approved',
            'description': 'Approved by curriculum committee',
            'permissions': {
                'View': ['Manager', 'TeacherRole', 'Student'],
                'Modify portal content': ['Manager', 'CurriculumCommittee'],
                'Google Classroom Sync': ['Manager', 'Owner']  # Integration permission
            }
        },
        'published': {
            'id': 'published',
            'title': 'Published',
            'description': 'Available for student access',
            'permissions': {
                'View': ['Anonymous'],  # Public access
                'Standards Alignment Access': ['TeacherRole'],
                'Analytics Access': ['Manager', 'Owner', 'Principal']  # Custom permission
            }
        },
        'archived': {
            'id': 'archived',
            'title': 'Archived',
            'description': 'Archived lesson content',
            'permissions': {
                'View': ['Manager', 'Owner'],
                'Restore Content': ['Manager', 'Owner']  # Custom permission
            }
        }
    },
    
    'transitions': {
        'submit_for_peer_review': {
            'id': 'submit_for_peer_review',
            'title': 'Submit for Peer Review',
            'new_state_id': 'peer_review',
            'guard': {
                'roles': ['Owner', 'TeacherRole'],
                'expression': 'python:object.standards_aligned() and object.has_objectives()'
            }
        },
        # ... additional transitions
    }
}
```

### Educational Roles 📋 Planned (Phase 2-3)
```python
# PLANNED FEATURES: Teacher-specific roles for educational platform
# Status: To be implemented when user management features are built
EDUCATIONAL_ROLES = {
    'TeacherRole': {
        'title': 'Teacher',
        'description': 'K-12 educator with content creation rights',
        'implementation_status': 'PLANNED - Phase 2',
        'inherits': ['Member'],
        'permissions': [
            'Add portal content',
            'Modify portal content',  # Own content
            'Standards Alignment Access',  # Custom permission
            'Analytics Access',  # Custom permission
            'Peer Review Access'  # Custom permission
        ]
    },
    'DepartmentHead': {
        'title': 'Department Head',
        'description': 'Department leadership role',
        'implementation_status': 'PLANNED - Phase 3',
        'inherits': ['TeacherRole'],
        'permissions': [
            'Review Content',
            'Department Analytics Access',
            'Curriculum Standards Management'
        ]
    },
    'CurriculumCommittee': {
        'title': 'Curriculum Committee',
        'description': 'Curriculum approval authority',
        'implementation_status': 'PLANNED - Phase 3',
        'inherits': ['DepartmentHead'],
        'permissions': [
            'Approve Curriculum',
            'Standards Alignment Management',
            'District Analytics Access'
        ]
    },
    'StandardsEditor': {
        'title': 'Standards Editor',
        'description': 'Educational standards specialist',
        'implementation_status': 'PLANNED - Phase 3',
        'inherits': ['TeacherRole'],
        'permissions': [
            'Standards Alignment Management',
            'Standards Vocabulary Management',
            'Cross-curriculum Analytics'
        ]
    },
    'Student': {
        'title': 'Student',
        'description': 'Student access to published content',
        'implementation_status': 'PLANNED - Phase 4',
        'inherits': ['Member'],
        'permissions': [
            'View',  # Published content only
            'Student Progress Tracking'
        ]
    }
}
```

---

## 🔒 Security Policy Implementation

### Core Plone Security ✅ Active
```python
# Standard Plone security implementation currently in use
class PloneSecurityPolicy:
    """Core Plone security policy - Active in project"""
    
    def checkPermission(self, permission, object, context):
        """Standard permission checking"""
        user = getSecurityManager().getUser()
        
        # Basic permission check
        if not user.has_permission(permission, object):
            return False
            
        return True
```

### Educational Security Policy 💭 Conceptual
```python
# CONCEPTUAL: Future security enhancements for educational features
class EducationalSecurityPolicy:
    """Security policy for educational content - NOT YET IMPLEMENTED"""
    
    def checkPermission(self, permission, object, context):
        """Check permission with educational context"""
        # Base Plone check first
        if not super().checkPermission(permission, object, context):
            return False
            
        # Educational-specific checks (FUTURE)
        if permission == 'Standards Alignment Access':
            return self._checkStandardsAccess(user, object)
        elif permission == 'Analytics Access':
            return self._checkAnalyticsAccess(user, object)
        elif permission == 'Google Classroom Sync':
            return self._checkGoogleSyncAccess(user, object)
            
        return True
```

---

## 📊 Workflow Integration Examples

### Current Integration ✅ Active
```python
# Catalog integration with workflow - Currently active
@adapter(IContentish, IActionSucceededEvent)
def track_workflow_transitions(obj, event):
    """Track workflow transitions - Core Plone feature in use"""
    
    # Reindex on state change
    catalog = getToolByName(obj, 'portal_catalog')
    catalog.reindexObject(obj, idxs=['review_state', 'modified'])
```

### Standards Alignment Integration 📋 Planned
```python
# PLANNED FEATURE: Standards alignment workflow integration
class StandardsWorkflowIntegration:
    """Integrate standards alignment with workflow - NOT YET IMPLEMENTED"""
    
    def pre_transition_check(self, action):
        """Check standards requirements before transition"""
        # To be implemented when standards alignment feature is built
        pass
```

### Analytics Integration 💭 Conceptual
```python
# CONCEPTUAL: Analytics tracking for educational workflows
@adapter(IContentish, IActionSucceededEvent)
def track_educational_analytics(obj, event):
    """Track workflow transitions for educational analytics - FUTURE FEATURE"""
    
    # Will integrate with analytics system when built
    pass
```

---

## 📋 Summary

### **Core Plone Workflow & Security** ✅ Active
- **🔄 DCWorkflow Engine**: Fully functional state machine system
- **🛡️ Permission System**: Fine-grained access control active
- **📊 Audit Trail**: Complete history tracking enabled
- **🎯 Role-based Security**: Standard Plone roles configured
- **🔧 Extensible Framework**: Ready for custom workflows

### **Educational Platform Features** 📋 Planned
- **👩‍🏫 Teacher Workflows**: Lesson approval processes (Phase 3)
- **📚 Standards Integration**: Alignment requirements (Phase 2)
- **👥 Peer Review System**: Collaborative feedback (Phase 3)
- **📊 Analytics Tracking**: Performance monitoring (Phase 4)
- **🔒 Student Safety**: Age-appropriate access (Phase 4)

### **Implementation Roadmap**
1. **Phase 1** ✅: Basic Plone workflow (Complete)
2. **Phase 2** ⏳: Teacher roles and permissions
3. **Phase 3** 📋: Educational workflows and peer review
4. **Phase 4** 💭: Student access and analytics

This architecture provides the **foundation** for implementing sophisticated educational workflows while leveraging Plone's **proven security model** for the K-12 Educational Content Platform. 