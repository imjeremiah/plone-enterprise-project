# Classroom Management Platform - Deployment Documentation

This directory contains complete documentation and tools for deploying the Classroom Management Platform in various environments.

## 📁 Documentation Structure

```
docs/deployment/
├── README.md                     # This overview file
├── aws-deployment-guide.md       # Complete AWS ECS deployment guide
├── cloudformation-template.yaml  # Infrastructure as Code template
├── docker-deployment.md          # Docker containerization guide
├── local-development.md          # Local development setup
└── monitoring-guide.md           # Monitoring and maintenance
```

## 🚀 Quick Start Deployment Options

### Option 1: Docker Compose (Recommended for Testing)

```bash
# Clone and setup
git clone <repository>
cd project-title

# Configure environment
cp .env.example .env.production
# Edit .env.production with your settings

# Build and deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Access at http://localhost
```

**Time to Deploy:** 10-15 minutes  
**Suitable for:** Development, testing, small-scale production

### Option 2: AWS ECS (Recommended for Production)

```bash
# Prerequisites: AWS CLI configured, domain ready

# Deploy infrastructure
aws cloudformation create-stack \
  --stack-name classroom-infrastructure \
  --template-body file://cloudformation-template.yaml \
  --parameters ParameterKey=Environment,ParameterValue=production \
               ParameterKey=DomainName,ParameterValue=classroom.yourdomain.com \
               ParameterKey=CertificateArn,ParameterValue=arn:aws:acm:... \
  --capabilities CAPABILITY_IAM

# Deploy application
./scripts/deploy-to-aws.sh production
```

**Time to Deploy:** 45-60 minutes  
**Suitable for:** Production, staging, scalable deployments

## 🔧 Deployment Guides

### [AWS ECS Deployment Guide](aws-deployment-guide.md)
Complete step-by-step guide for production AWS deployment including:
- Infrastructure setup (VPC, RDS, ALB, ECS)
- Container registry and image building
- Monitoring and logging with CloudWatch
- SSL/TLS configuration
- Cost optimization strategies
- Troubleshooting guide

**Best for:** Production environments requiring scalability and reliability

### [Docker Deployment Guide](docker-deployment.md)
Comprehensive Docker containerization including:
- Multi-stage production Dockerfiles
- Docker Compose for full stack
- Container security hardening
- Volume management and persistence
- Local development with Docker

**Best for:** Development, testing, or single-server deployments

### [CloudFormation Template](cloudformation-template.yaml)
Infrastructure as Code template providing:
- Complete AWS infrastructure provisioning
- Environment-specific configurations (dev/staging/prod)
- Security groups and IAM roles
- Database and caching setup
- Load balancer and auto-scaling configuration

**Best for:** Automated, repeatable AWS deployments

## 📊 Deployment Comparison

| Feature | Docker Compose | AWS ECS | Kubernetes |
|---------|---------------|---------|------------|
| **Complexity** | Low | Medium | High |
| **Setup Time** | 10-15 min | 45-60 min | 2-4 hours |
| **Scalability** | Limited | High | Very High |
| **Cost (Monthly)** | $0-20 | $110-150 | $200-400 |
| **High Availability** | No | Yes | Yes |
| **Auto Scaling** | No | Yes | Yes |
| **Managed Services** | No | Yes | Partial |
| **Best For** | Development | Production | Enterprise |

## 🛠️ Prerequisites by Deployment Type

### Docker Compose Requirements
- Docker Desktop or Docker Engine 20+
- Docker Compose v2+
- 4GB RAM minimum, 8GB recommended
- Domain name (for production use)

### AWS ECS Requirements
- AWS Account with appropriate permissions
- AWS CLI v2+ configured
- Domain name with DNS control
- SSL certificate (AWS ACM recommended)
- Estimated budget: $110-150/month for production

### Common Requirements
- Git
- Node.js 22+ and pnpm 9.1.1 (for frontend builds)
- Python 3.12+ with uv (for backend builds)

## 🔐 Security Considerations

### Production Security Checklist
- [ ] SSL/TLS certificates configured
- [ ] Security headers enabled
- [ ] CORS properly configured
- [ ] Database encryption at rest
- [ ] Secrets managed securely (AWS Secrets Manager/Parameter Store)
- [ ] Network isolation (VPC, security groups)
- [ ] Regular security updates
- [ ] Audit logging enabled

### FERPA Compliance Features
- [ ] Student PII protection implemented
- [ ] Data anonymization for exports
- [ ] Secure QR code generation (no PII)
- [ ] Audit trails for all student data access
- [ ] Configurable data retention policies

## 📈 Performance Targets

### Production Performance Goals
- **Dashboard Load Time:** < 1 second
- **API Response Time:** < 200ms (95th percentile)
- **Uptime:** 99.9%
- **Concurrent Users:** 100+ per classroom
- **Database Queries:** < 100ms average

### Optimization Features
- **Caching:** Redis for session and data caching
- **CDN:** CloudFront for static assets (AWS deployment)
- **Database:** Optimized PostgreSQL with read replicas
- **Auto Scaling:** CPU and memory-based scaling
- **Performance Monitoring:** CloudWatch dashboards and alerts

## 🔍 Monitoring and Maintenance

### Included Monitoring
- **Application Metrics:** Response times, error rates, throughput
- **Infrastructure Metrics:** CPU, memory, disk, network
- **Database Metrics:** Connection counts, query performance
- **Security Metrics:** Failed logins, rate limiting triggers
- **Business Metrics:** Hall passes issued, participation tracking

### Maintenance Tasks
- **Daily:** Health check verification, log review
- **Weekly:** Performance metric review, capacity planning
- **Monthly:** Security patch updates, cost optimization review
- **Quarterly:** Disaster recovery testing, documentation updates

## 🆘 Support and Troubleshooting

### Common Issues and Solutions

#### 1. Container Startup Failures
```bash
# Check container logs
docker logs classroom-backend
docker logs classroom-frontend

# Verify database connectivity
docker exec -it classroom-backend curl http://localhost:8080/health
```

#### 2. Database Connection Issues
```bash
# Test database connection
docker exec -it classroom-postgres psql -U classroom_user -d classroom_db -c "SELECT version();"

# Check network connectivity
docker network ls
docker network inspect project-title_classroom-network
```

#### 3. Load Balancer Health Check Failures
```bash
# AWS ECS: Check target group health
aws elbv2 describe-target-health --target-group-arn $TARGET_GROUP_ARN

# Verify health check endpoints
curl -f http://your-backend/Plone/@@security-middleware
curl -f http://your-frontend/
```

### Getting Help
1. **Documentation:** Check specific deployment guides
2. **Logs:** Review application and infrastructure logs
3. **Health Checks:** Verify all health check endpoints
4. **Community:** Check project issues and discussions
5. **Support:** Contact the development team

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] SSL certificates ready
- [ ] Domain DNS configured
- [ ] Database passwords generated
- [ ] AWS permissions verified (for AWS deployment)

### During Deployment
- [ ] Infrastructure provisioned successfully
- [ ] Containers built and pushed to registry
- [ ] Database initialized and migrated
- [ ] Load balancer health checks passing
- [ ] SSL/TLS certificates applied

### Post-Deployment
- [ ] Application accessible via domain
- [ ] All features tested end-to-end
- [ ] Monitoring dashboards configured
- [ ] Backup procedures tested
- [ ] Documentation updated
- [ ] Team trained on operations

## 🎯 Next Steps

After successful deployment:

1. **Configure OAuth:** Set up Google OAuth for teacher authentication
2. **Import Data:** Import existing student rosters and classroom data
3. **User Training:** Provide training materials to teachers
4. **Monitor Usage:** Review monitoring dashboards regularly
5. **Plan Updates:** Establish update and maintenance procedures

---

**Need Help?** Choose the appropriate deployment guide above and follow the step-by-step instructions. Each guide includes troubleshooting sections for common issues. 