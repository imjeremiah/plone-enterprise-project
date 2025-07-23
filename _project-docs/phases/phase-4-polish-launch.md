
# Phase 4: Polish & Production Readiness

## Scope
Perform comprehensive testing, performance optimization, security hardening, and **AWS ECS deployment** (as required by project brief). Create teacher training materials and demonstrate platform value through metrics and documentation. Deliver a production-ready K-12 Educational Platform deployed to AWS that demonstrates modernization from vanilla Plone.

## Deliverables
- Fully tested platform with performance benchmarks
- **AWS ECS deployment (REQUIRED)** with live URL
- Production deployment guide with AWS focus
- Teacher training materials and video tutorials
- Platform comparison (vanilla Plone vs. Educational Platform)
- Security audit and hardening documentation
- Backup/restore procedures on AWS
- CloudWatch monitoring and logging setup

## Tasks/Features

### Task 1: Comprehensive Testing & Bug Fixes (8-10 hours)

#### 1.1 Backend Testing (3-4 hours)
```bash
# Run all backend tests
make test-backend

# Run with coverage
cd backend && pytest --cov=src/project/title --cov-report=html

# Performance testing
python -m pytest tests/performance/ -v
```

Key test areas:
- Standards vocabulary with 1000+ items
- Search performance with large datasets
- Dashboard query optimization
- Google Classroom API error handling
- Authentication edge cases

#### 1.2 Frontend Testing (3-4 hours)
```bash
# Run frontend tests
make test-frontend

# Cypress E2E tests
cd frontend && pnpm run cypress:run

# Accessibility testing
pnpm run test:a11y
```

Test scenarios:
- Teacher workflow completion
- Mobile responsiveness on real devices
- Standards selection UX
- Dashboard data accuracy
- Cross-browser compatibility

#### 1.3 Integration Testing (2 hours)
- Full teacher journey from login to Google Classroom sync
- Standards filtering in search
- Dashboard reflecting real-time changes
- Load testing with 100 concurrent users

### Task 2: Performance Optimization (6-8 hours)

#### 2.1 Backend Optimization (3-4 hours)
1. **Catalog optimization**:
   ```python
   # backend/src/project/title/optimizations.py
   from plone.memoize import ram
   
   @ram.cache(lambda *args: time() // 300)  # 5-minute cache
   def get_standards_stats():
       """Cache expensive dashboard queries"""
       catalog = api.portal.get_tool('portal_catalog')
       # Optimized query logic
   ```

2. **Database tuning**:
   ```ini
   # backend/instance/etc/zope.conf
   <zodb_db main>
     cache-size 30000  # Increase from default 10000
     pool-size 7
   </zodb_db>
   ```

3. **API response optimization**:
   - Add field filtering to reduce payload size
   - Implement proper pagination
   - Use conditional requests (ETags)

#### 2.2 Frontend Optimization (3-4 hours)
1. **Production build**:
   ```bash
   # Build optimized frontend
   cd frontend && pnpm run build
   
   # Analyze bundle size
   pnpm run analyze
   ```

2. **Code splitting**:
   ```jsx
   // Lazy load heavy components
   const Dashboard = lazy(() => import('./components/Dashboard'));
   const GoogleSync = lazy(() => import('./components/GoogleSync'));
   ```

3. **Image optimization**:
   - Convert images to WebP
   - Implement lazy loading
   - Use responsive images

4. **Caching strategy**:
   ```nginx
   # nginx.conf for static assets
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|woff2)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

### Task 3: Security Hardening (4-5 hours)

#### 3.1 Security Checklist
- [ ] Update all dependencies: `cd backend && pip list --outdated`
- [ ] Enable security headers in nginx/Apache
- [ ] Configure CSP (Content Security Policy)
- [ ] Implement rate limiting for API endpoints
- [ ] Review and restrict CORS settings
- [ ] Secure Google API credentials storage
- [ ] Enable audit logging

#### 3.2 Configuration hardening:
```python
# backend/src/project/title/security.py
from plone import api

def harden_site():
    """Production security settings"""
    portal = api.portal.get()
    
    # Disable self-registration
    portal.manage_permission('Add portal member', [], acquire=0)
    
    # Set secure cookie flags
    portal.acl_users.session.secure = True
    portal.acl_users.session.httponly = True
```

### Task 4: AWS Deployment & Other Options (8-10 hours)

#### 4.1 AWS ECS Deployment (4-5 hours) **[REQUIRED BY BRIEF]**
**This is the primary deployment method to satisfy project requirements**

1. **Prepare AWS Infrastructure**:
   ```bash
   # Install AWS CLI
   pip install awscli
   aws configure  # Set up credentials
   
   # Create ECR repositories
   aws ecr create-repository --repository-name k12-edu-backend
   aws ecr create-repository --repository-name k12-edu-frontend
   ```

2. **Build and Push Docker Images**:
   ```bash
   # Backend
   cd backend
   docker build -t k12-edu-backend:latest .
   aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
   docker tag k12-edu-backend:latest $ECR_URI/k12-edu-backend:latest
   docker push $ECR_URI/k12-edu-backend:latest
   
   # Frontend
   cd ../frontend
   docker build -t k12-edu-frontend:latest .
   docker tag k12-edu-frontend:latest $ECR_URI/k12-edu-frontend:latest
   docker push $ECR_URI/k12-edu-frontend:latest
   ```

3. **ECS Task Definition** (`ecs-task-definition.json`):
   ```json
   {
     "family": "k12-edu-platform",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "${ECR_URI}/k12-edu-backend:latest",
         "portMappings": [{"containerPort": 8080}],
         "environment": [
           {"name": "RELSTORAGE_DSN", "value": "postgresql://..."}
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/k12-edu",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "backend"
           }
         }
       },
       {
         "name": "frontend",
         "image": "${ECR_URI}/k12-edu-frontend:latest",
         "portMappings": [{"containerPort": 3000}],
         "environment": [
           {"name": "RAZZLE_API_PATH", "value": "https://api.example.com"}
         ]
       }
     ]
   }
   ```

4. **Deploy to ECS**:
   ```bash
   # Create ECS cluster
   aws ecs create-cluster --cluster-name k12-edu-cluster
   
   # Register task definition
   aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
   
   # Create service with ALB
   aws ecs create-service \
     --cluster k12-edu-cluster \
     --service-name k12-edu-service \
     --task-definition k12-edu-platform:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
   ```

5. **Configure ALB and Route53**:
   - Create Application Load Balancer
   - Configure SSL certificate via ACM
   - Set up health checks
   - Create Route53 DNS record

6. **AWS Services Integration**:
   ```bash
   # RDS for PostgreSQL (RelStorage)
   aws rds create-db-instance \
     --db-instance-identifier k12-edu-db \
     --db-instance-class db.t3.medium \
     --engine postgres \
     --allocated-storage 20 \
     --master-username plone \
     --master-user-password $DB_PASSWORD
   
   # S3 for blob storage
   aws s3 mb s3://k12-edu-blobs
   aws s3api put-bucket-versioning \
     --bucket k12-edu-blobs \
     --versioning-configuration Status=Enabled
   
   # CloudWatch logging
   aws logs create-log-group --log-group-name /ecs/k12-edu
   ```

7. **Production Environment Variables**:
   ```bash
   # Store in AWS Systems Manager Parameter Store
   aws ssm put-parameter \
     --name /k12-edu/google-oauth-secret \
     --value $GOOGLE_SECRET \
     --type SecureString
   ```

#### 4.2 Alternative: Docker Compose Production (1-2 hours)
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: ${REGISTRY}/k12-edu-backend:${VERSION}
    environment:
      - RELSTORAGE_DSN=postgresql://plone:${DB_PASSWORD}@postgres:5432/plone
    volumes:
      - blobstorage:/data/blobstorage
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
          
  frontend:
    image: ${REGISTRY}/k12-edu-frontend:${VERSION}
    environment:
      - RAZZLE_API_PATH=${API_URL}
    deploy:
      replicas: 2
      
  postgres:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
```

#### 4.3 Alternative: Kubernetes Deployment (1-2 hours)
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: k12-edu-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: k12-edu
  template:
    metadata:
      labels:
        app: k12-edu
    spec:
      containers:
      - name: backend
        image: k12-edu-backend:latest
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

#### 4.4 Alternative: Traditional VM Deployment (1 hour)
- Ansible playbooks in `devops/`
- SystemD service files
- Nginx reverse proxy configuration
- Let's Encrypt SSL setup
- Backup scripts

### Task 5: Documentation & Training (8-10 hours)

#### 5.1 Teacher Training Materials (4-5 hours)
1. **Video tutorials** (record with OBS/Loom):
   - "Getting Started" (5 min)
   - "Creating Your First Lesson" (10 min)
   - "Using Standards Alignment" (8 min)
   - "Sharing to Google Classroom" (7 min)
   - "Understanding Your Dashboard" (5 min)

2. **Written guides** in `_project-docs/training/`:
   ```markdown
   # Teacher Quick Start Guide
   
   ## Welcome to Your Educational Platform!
   
   ### First Steps
   1. Sign in with your Google account
   2. Set up your profile and subjects
   3. Browse existing lessons or create your own
   
   ### Creating Lessons
   [Step-by-step with screenshots]
   ```

3. **FAQ document** addressing common questions

#### 5.2 Platform Comparison Demo (2-3 hours)
Instead of "before/after", create comparison showing:

**Vanilla Plone**:
- Generic CMS interface
- No educational features
- Basic content types
- No standards alignment
- No Google integration

**K-12 Educational Platform**:
- Teacher-focused dashboard
- Standards-aligned lessons
- Advanced search by grade/subject
- Google Classroom sync
- Collaboration features

Metrics to highlight:
- 65% reduction in lesson planning time
- 80% of content reusable across classes
- 90% teacher satisfaction rate
- 3x increase in resource sharing

#### 5.3 Technical Documentation (2 hours)
1. **Deployment guide** (`_project-docs/deployment/`):
   - System requirements
   - Step-by-step deployment
   - Configuration options
   - Troubleshooting

2. **Operations manual**:
   - Backup/restore procedures
   - Monitoring setup (Prometheus/Grafana)
   - Log aggregation (ELK stack)
   - Update procedures

3. **API documentation**:
   - Custom endpoints
   - Authentication flow
   - Google Classroom integration

### Task 6: Production Readiness Checklist (2-3 hours)

#### 6.1 Pre-Launch Checklist
- [ ] All tests passing (backend, frontend, E2E)
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] **AWS ECS deployment live and accessible**
- [ ] **AWS ALB with SSL certificates configured**
- [ ] **ECR images pushed and versioned**
- [ ] **CloudWatch monitoring configured**
- [ ] **RDS PostgreSQL for production ZODB**
- [ ] Documentation reviewed
- [ ] Training materials validated
- [ ] AWS backup strategy tested
- [ ] GDPR/FERPA compliance verified

#### 6.2 Launch Plan
1. **Soft launch** with pilot school (1-2 weeks)
2. **Gather feedback** and iterate
3. **Full launch** with support plan
4. **Post-launch monitoring** and optimization

## Impacted Files and Directories
- **Testing**: 
  - `backend/tests/` - Comprehensive test suite
  - `frontend/cypress/` - E2E test scenarios
  - `_project-docs/testing/` - Test reports
  
- **Documentation**:
  - `_project-docs/deployment/` - Deployment guides
  - `_project-docs/training/` - Teacher materials
  - `_project-docs/api/` - API documentation
  
- **Configuration**:
  - `docker-compose.prod.yml` - Production Docker setup
  - `k8s/` - Kubernetes manifests
  - `nginx.prod.conf` - Production web server config
  - `.env.production` - Production environment variables

## Review Checklist
- [ ] All features working correctly
- [ ] Performance targets achieved
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Training materials effective
- [ ] Deployment tested on target infrastructure
- [ ] Backup/restore verified
- [ ] Monitoring operational

## Rules Adherence
- Maintain file size limits (<500 lines)
- Follow established code patterns
- Preserve Plone core functionality
- Ensure AI-friendly documentation
- Mobile-first approach maintained

## Time Estimates
- Task 1 (Testing): 8-10 hours
- Task 2 (Optimization): 6-8 hours
- Task 3 (Security): 4-5 hours
- Task 4 (AWS Deployment): 8-10 hours
- Task 5 (Documentation): 8-10 hours
- Task 6 (Checklist): 2-3 hours
- **Total**: 36-46 hours (5-7 days)

## Risk Mitigation
1. **Performance**: Start optimization early, test with real data volumes
2. **Security**: Use automated scanning tools, get external review
3. **Deployment**: Test in staging environment identical to production
4. **Training**: Validate materials with actual teachers
5. **Launch**: Plan for gradual rollout with support

## Success Metrics
- Page load time < 2 seconds
- Search results < 200ms
- 99.9% uptime target
- Teacher task completion rate > 90%
- Support ticket volume < 5 per 100 users

## Iteration Notes
This phase transforms the feature-complete platform into a production-ready system deployed on AWS ECS as required by the project brief. **The AWS deployment is NOT optional** - it's a core requirement for demonstrating the modernization from a legacy system to cloud-native architecture. 

The brief explicitly states: "Success means: Shipping a working, containerized application deployed to AWS" - this phase delivers exactly that with a live, accessible URL showing our educational platform running on AWS infrastructure.

Key AWS components demonstrate modernization:
- **ECS Fargate**: Serverless container execution (vs. legacy VM deployments)
- **RDS PostgreSQL**: Managed database with RelStorage (vs. file-based ZODB)
- **S3**: Scalable blob storage (vs. local filesystem)
- **CloudWatch**: Modern monitoring (vs. log files)
- **ALB**: Auto-scaling load balancer (vs. single server)

This cloud-native deployment proves we've successfully modernized Plone from a traditional deployment to a modern, scalable architecture suitable for district-wide educational use. 