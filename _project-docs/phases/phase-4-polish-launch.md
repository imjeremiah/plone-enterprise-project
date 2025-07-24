
# Phase 4: Polish & Production Readiness

## Scope
Perform comprehensive testing, performance optimization, security hardening, and **AWS ECS deployment** (as required by project brief). Create teacher training materials and demonstrate platform value through metrics and documentation. Deliver a production-ready K-12 Classroom Management Platform deployed to AWS that demonstrates modernization from vanilla Plone.

## Deliverables
- Fully tested platform with performance benchmarks
- **AWS ECS deployment (REQUIRED)** with live URL
- Production deployment guide with AWS focus
- Teacher training materials and video tutorials
- Platform comparison (vanilla Plone vs. Classroom Management Platform)
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
- Seating chart drag-drop persistence
- Random picker fairness algorithm
- Hall pass time tracking accuracy
- Timer state persistence
- Substitute folder generation
- Dashboard data aggregation
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
- Complete classroom management workflow
- Touch/drag interactions on tablets
- Timer accuracy and persistence
- Dashboard real-time updates
- Cross-browser compatibility

#### 1.3 Integration Testing (2 hours)
- Full teacher journey from login to dashboard
- Seating chart → random picker integration
- Hall pass alerts on dashboard
- Timer state across page refreshes
- Load testing with 30+ students per class

### Task 2: Performance Optimization (6-8 hours)

#### 2.1 Backend Optimization (3-4 hours)
1. **Catalog optimization for dashboard**:
   ```python
   # backend/src/project/title/optimizations.py
   from plone.memoize import ram
   
   @ram.cache(lambda *args: time() // 30)  # 30-second cache
   def get_dashboard_aggregates():
       """Cache expensive dashboard queries"""
       catalog = api.portal.get_tool('portal_catalog')
       # Optimized aggregation logic
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
   - Batch dashboard updates
   - Minimize hall pass query overhead
   - Optimize seating chart JSON

#### 2.2 Frontend Optimization (3-4 hours)
1. **JavaScript performance**:
   ```javascript
   // Optimize timer updates
   const TimerOptimized = React.memo(({ duration }) => {
     // Use requestAnimationFrame for smooth updates
     const frame = useRef();
     
     const animate = useCallback(() => {
       // Update logic
       frame.current = requestAnimationFrame(animate);
     }, []);
   });
   ```

2. **Bundle optimization**:
   ```bash
   # Analyze bundle size
   cd frontend && pnpm run analyze
   
   # Code split heavy components
   const Dashboard = lazy(() => import('./Dashboard'));
   ```

3. **Asset optimization**:
   - Optimize audio files for timer
   - Compress images for QR codes
   - Minimize CSS for animations

### Task 3: Security Hardening (4-5 hours)

#### 3.1 Security Checklist
- [ ] Update all dependencies: `cd backend && pip list --outdated`
- [ ] Enable security headers in nginx/Apache
- [ ] Configure CSP (Content Security Policy) for inline JS
- [ ] Implement rate limiting for API endpoints (especially picker)
- [ ] Review and restrict CORS settings
- [ ] Secure student data (no PII in QR codes)
- [ ] Enable audit logging for hall passes

#### 3.2 Privacy protection:
```python
# backend/src/project/title/security.py
def anonymize_student_data(data):
    """Remove PII from exported data"""
    # Implementation for FERPA compliance
```

### Task 4: AWS Deployment (8-10 hours) **[REQUIRED BY BRIEF]**

#### 4.1 AWS ECS Deployment (5-6 hours) **PRIMARY DEPLOYMENT**

1. **Prepare Docker images**:
   ```dockerfile
   # backend/Dockerfile.prod
   FROM python:3.12-slim
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       libjpeg-dev \
       libpng-dev \
       libxml2-dev \
       libxslt-dev
   
   # Copy and install backend
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   RUN pip install gunicorn
   
   CMD ["gunicorn", "-b", "0.0.0.0:8080", "wsgi:application"]
   ```

2. **Build and push to ECR**:
   ```bash
   # Create repositories
   aws ecr create-repository --repository-name classroom-backend
   aws ecr create-repository --repository-name classroom-frontend
   
   # Build and push
   docker build -t classroom-backend:latest -f Dockerfile.prod .
   aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
   docker tag classroom-backend:latest $ECR_URI/classroom-backend:latest
   docker push $ECR_URI/classroom-backend:latest
   ```

3. **ECS Task Definition**:
   ```json
   {
     "family": "classroom-management",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "${ECR_URI}/classroom-backend:latest",
         "portMappings": [{"containerPort": 8080}],
         "environment": [
           {"name": "RELSTORAGE_DSN", "value": "${RDS_CONNECTION}"},
           {"name": "GOOGLE_CLIENT_ID", "value": "${GOOGLE_CLIENT_ID}"}
         ],
         "secrets": [
           {
             "name": "GOOGLE_CLIENT_SECRET",
             "valueFrom": "arn:aws:ssm:region:account:parameter/classroom/google-secret"
           }
         ]
       }
     ]
   }
   ```

4. **Infrastructure setup**:
   ```bash
   # RDS for PostgreSQL
   aws rds create-db-instance \
     --db-instance-identifier classroom-db \
     --db-instance-class db.t3.small \
     --engine postgres \
     --allocated-storage 20
   
   # ALB for load balancing
   aws elbv2 create-load-balancer \
     --name classroom-alb \
     --subnets subnet-xxx subnet-yyy
   
   # S3 for blob storage
   aws s3 mb s3://classroom-blobs
   ```

5. **Deploy service**:
   ```bash
   aws ecs create-service \
     --cluster classroom-cluster \
     --service-name classroom-service \
     --task-definition classroom-management:1 \
     --desired-count 2 \
     --launch-type FARGATE
   ```

### Task 5: Documentation & Training (8-10 hours)

#### 5.1 Teacher Training Materials (4-5 hours)
1. **Video tutorials** (record with Loom):
   - "Getting Started with Classroom Management" (5 min)
   - "Setting Up Your Seating Chart" (3 min)
   - "Using the Random Student Picker" (3 min)
   - "Managing Digital Hall Passes" (4 min)
   - "Timer Tools for Activities" (3 min)
   - "Preparing for a Substitute" (5 min)
   - "Your Daily Dashboard" (5 min)

2. **Quick reference guide**:
   ```markdown
   # Teacher's Quick Reference
   
   ## Daily Classroom Tasks
   
   ### Start of Class
   1. Open Dashboard - see everything at a glance
   2. Check seating chart - drag to rearrange
   3. Start warm-up timer - visible to all
   
   ### During Class
   - Pick students fairly - automatic tracking
   - Issue hall passes - digital accountability
   - Monitor who's out - real-time alerts
   
   ### End of Day
   - Generate sub folder - one click prep
   - Review participation - ensure equity
   ```

#### 5.2 Platform Comparison (2-3 hours)
**Before (Manual Methods)**:
- Paper seating charts
- Mental note participation
- Kitchen timer on desk
- Clipboard hall passes
- 90-minute sub prep

**After (Classroom Management Platform)**:
- Interactive seating charts
- Fair picker with history
- Visible countdown timers
- Digital pass tracking
- 5-minute sub prep

Metrics to highlight:
- 70% reduction in transition time
- 100% participation tracking
- 80% less time on admin tasks
- 95% teacher satisfaction

#### 5.3 Technical Documentation (2 hours)
1. **AWS Deployment Guide**:
   - Prerequisites and AWS setup
   - Step-by-step deployment
   - Monitoring with CloudWatch
   - Backup procedures

2. **Operational Manual**:
   - Daily monitoring checklist
   - Common troubleshooting
   - Performance tuning
   - Update procedures

### Task 6: Production Readiness Checklist (2-3 hours)

#### 6.1 Pre-Launch Verification
- [ ] All tests passing (100% feature coverage)
- [ ] Performance targets met:
  - [ ] Dashboard load < 1 second
  - [ ] Drag-drop response < 50ms
  - [ ] Timer accuracy ±100ms
- [ ] Security scan completed
- [ ] **AWS deployment live**:
  - [ ] ECS tasks healthy
  - [ ] ALB routing correctly
  - [ ] RDS connected
  - [ ] S3 permissions set
- [ ] Teacher guides reviewed
- [ ] FERPA compliance verified

#### 6.2 Launch Plan
1. **Pilot with 2-3 teachers** (1 week)
2. **Gather feedback** on real classroom use
3. **Full school launch** with support
4. **Monitor CloudWatch** for issues

## Monitoring & Analytics

### CloudWatch Dashboard
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", {"stat": "Average"}],
          ["AWS/ApplicationELB", "TargetResponseTime"],
          ["AWS/RDS", "DatabaseConnections"]
        ]
      }
    },
    {
      "type": "log",
      "properties": {
        "query": "fields @timestamp, @message | filter @message like /ERROR/"
      }
    }
  ]
}
```

### Key Metrics to Track
- Active users per hour
- Average dashboard load time
- Hall passes per day
- Timer usage patterns
- Substitute folder generations

## Cost Optimization

### AWS Cost Breakdown (Monthly Estimate)
- ECS Fargate (2 tasks): ~$50
- RDS PostgreSQL: ~$30
- ALB: ~$20
- S3 & Data Transfer: ~$10
- **Total**: ~$110/month

### Cost Optimization Strategies
1. Use Fargate Spot for non-critical tasks
2. Enable RDS auto-pause for dev/test
3. Implement CloudFront for static assets
4. Use S3 lifecycle policies

## Review Checklist
- [ ] All 7 features working correctly
- [ ] Touch-optimized for tablets
- [ ] Real-time updates performing well
- [ ] Teacher documentation clear
- [ ] AWS deployment stable
- [ ] Monitoring operational
- [ ] Backup tested
- [ ] Security hardened

## Time Estimates
- Task 1 (Testing): 8-10 hours
- Task 2 (Optimization): 6-8 hours
- Task 3 (Security): 4-5 hours
- Task 4 (AWS Deployment): 8-10 hours
- Task 5 (Documentation): 8-10 hours
- Task 6 (Checklist): 2-3 hours
- **Total**: 36-46 hours (5-6 days)

## Success Metrics
- Dashboard load time < 1 second
- 99.9% uptime on AWS
- Zero security vulnerabilities
- 95% teacher task success rate
- < 5 support tickets per 100 users

## Iteration Notes
This phase delivers a production-ready Classroom Management Platform on AWS ECS. The cloud deployment demonstrates modernization from legacy on-premise systems to scalable cloud architecture. The focus on real-time classroom tools shows how Plone can be transformed for specialized vertical markets.

**Key Achievement**: Transforming Plone from a general CMS to a focused classroom management solution, deployed on modern cloud infrastructure, solving real teacher pain points with 70%+ efficiency gains. 