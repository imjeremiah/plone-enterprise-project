# AWS ECS Deployment Guide
# Classroom Management Platform Production Deployment

This guide provides complete step-by-step instructions for deploying the Classroom Management Platform to AWS ECS with production-ready infrastructure.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Overview](#infrastructure-overview)
3. [Pre-Deployment Setup](#pre-deployment-setup)
4. [AWS Infrastructure Setup](#aws-infrastructure-setup)
5. [Container Registry Setup](#container-registry-setup)
6. [Database and Cache Setup](#database-and-cache-setup)
7. [Load Balancer and Networking](#load-balancer-and-networking)
8. [ECS Cluster and Services](#ecs-cluster-and-services)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [SSL/TLS Configuration](#ssl-tls-configuration)
11. [Deployment Automation](#deployment-automation)
12. [Maintenance and Updates](#maintenance-and-updates)
13. [Cost Optimization](#cost-optimization)
14. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
- AWS CLI v2+ installed and configured
- Docker Desktop
- Node.js 22+ and pnpm 9.1.1
- Python 3.12+ with uv package manager
- Git

### AWS Account Requirements
- AWS Account with appropriate permissions
- AWS CLI configured with access keys
- Domain name registered (or available through Route 53)
- SSL certificate ready (or will use AWS Certificate Manager)

### Estimated Costs (Monthly)
- **Production Environment**: $110-150/month
- **Staging Environment**: $60-80/month
- **Development Environment**: $30-50/month

---

## Infrastructure Overview

### AWS Services Used

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Production Architecture              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐  │
│  │   Route 53  │────▶│     ALB      │────▶│   Target    │  │
│  │     DNS     │     │ Load Balancer│     │   Groups    │  │
│  └─────────────┘     └──────────────┘     └─────────────┘  │
│                              │                             │
│                              ▼                             │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    ECS Cluster                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │  Frontend   │  │   Backend   │  │   Nginx     │    │  │
│  │  │   Service   │  │   Service   │  │   Service   │    │  │
│  │  │  (Volto)    │  │  (Plone)    │  │ (Reverse    │    │  │
│  │  │             │  │             │  │  Proxy)     │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                             │
│                              ▼                             │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐  │
│  │     RDS     │     │ ElastiCache  │     │     S3      │  │
│  │ PostgreSQL  │     │    Redis     │     │   Blob      │  │
│  │  Database   │     │    Cache     │     │  Storage    │  │
│  └─────────────┘     └──────────────┘     └─────────────┘  │
│                                                             │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐  │
│  │ CloudWatch  │     │      IAM     │     │     VPC     │  │
│  │ Monitoring  │     │   Security   │     │  Networking │  │
│  └─────────────┘     └──────────────┘     └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Service Specifications

| Service | Purpose | Instance Type | Scaling |
|---------|---------|---------------|---------|
| Frontend (Volto) | React UI | Fargate 0.5 vCPU, 1GB RAM | 2-5 tasks |
| Backend (Plone) | API & Logic | Fargate 1 vCPU, 2GB RAM | 2-4 tasks |
| Nginx | Reverse Proxy | Fargate 0.25 vCPU, 512MB | 2-3 tasks |
| PostgreSQL | Database | RDS db.t3.small | Single AZ (Multi-AZ for HA) |
| Redis | Cache | ElastiCache t3.micro | Single node (cluster for HA) |

---

## Pre-Deployment Setup

### 1. Environment Variables Configuration

Create a `.env.production` file:

```bash
# Domain and URLs
DOMAIN_NAME=classroom.yourdomain.com
PUBLIC_URL=https://classroom.yourdomain.com
CORS_ORIGINS=https://classroom.yourdomain.com

# Database Configuration
DB_NAME=classroom_production
DB_USER=classroom_admin
DB_PASSWORD=your-super-secure-password-here

# Redis Configuration  
REDIS_PASSWORD=your-redis-password-here

# Security Configuration
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-secret

# Monitoring (Optional)
BACKEND_SENTRY_DSN=your-backend-sentry-dsn
FRONTEND_SENTRY_DSN=your-frontend-sentry-dsn

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
ECR_REGISTRY=123456789012.dkr.ecr.us-east-1.amazonaws.com

# Application Configuration
ENVIRONMENT=production
VERSION=v1.0.0
PLONE_SITE_ID=Plone
```

### 2. Domain and SSL Preparation

#### Option A: Using Route 53 and ACM (Recommended)
```bash
# Request SSL certificate
aws acm request-certificate \
  --domain-name classroom.yourdomain.com \
  --subject-alternative-names "*.classroom.yourdomain.com" \
  --validation-method DNS \
  --region us-east-1
```

#### Option B: Existing Domain
- Ensure your domain's DNS can be pointed to AWS
- Have SSL certificate ready or use AWS Certificate Manager

---

## AWS Infrastructure Setup

### 1. Create VPC and Networking

```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=classroom-vpc}]'

# Store VPC ID
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=classroom-vpc" \
  --query 'Vpcs[0].VpcId' --output text)

# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=classroom-igw}]'

IGW_ID=$(aws ec2 describe-internet-gateways \
  --filters "Name=tag:Name,Values=classroom-igw" \
  --query 'InternetGateways[0].InternetGatewayId' --output text)

# Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID

# Create Public Subnets (for Load Balancer)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=classroom-public-1}]'

aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=classroom-public-2}]'

# Create Private Subnets (for ECS tasks)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.10.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=classroom-private-1}]'

aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=classroom-private-2}]'

# Create Database Subnets
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.20.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=classroom-db-1}]'

aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.21.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=classroom-db-2}]'
```

### 2. Create Security Groups

```bash
# Application Load Balancer Security Group
aws ec2 create-security-group \
  --group-name classroom-alb-sg \
  --description "Security group for ALB" \
  --vpc-id $VPC_ID

ALB_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=classroom-alb-sg" \
  --query 'SecurityGroups[0].GroupId' --output text)

# Allow HTTP and HTTPS traffic
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# ECS Tasks Security Group
aws ec2 create-security-group \
  --group-name classroom-ecs-sg \
  --description "Security group for ECS tasks" \
  --vpc-id $VPC_ID

ECS_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=classroom-ecs-sg" \
  --query 'SecurityGroups[0].GroupId' --output text)

# Allow traffic from ALB
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG_ID \
  --protocol tcp \
  --port 3000 \
  --source-group $ALB_SG_ID

aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG_ID \
  --protocol tcp \
  --port 8080 \
  --source-group $ALB_SG_ID

# Database Security Group
aws ec2 create-security-group \
  --group-name classroom-db-sg \
  --description "Security group for RDS and ElastiCache" \
  --vpc-id $VPC_ID

DB_SG_ID=$(aws ec2 describe-security-group \
  --filters "Name=group-name,Values=classroom-db-sg" \
  --query 'SecurityGroups[0].GroupId' --output text)

# Allow database access from ECS
aws ec2 authorize-security-group-ingress \
  --group-id $DB_SG_ID \
  --protocol tcp \
  --port 5432 \
  --source-group $ECS_SG_ID

aws ec2 authorize-security-group-ingress \
  --group-id $DB_SG_ID \
  --protocol tcp \
  --port 6379 \
  --source-group $ECS_SG_ID
```

### 3. Set up NAT Gateway (for private subnet internet access)

```bash
# Allocate Elastic IP for NAT Gateway
aws ec2 allocate-address --domain vpc

EIP_ALLOCATION_ID=$(aws ec2 describe-addresses \
  --query 'Addresses[?Domain==`vpc`]|[-1].AllocationId' --output text)

# Get public subnet ID
PUBLIC_SUBNET_ID=$(aws ec2 describe-subnets \
  --filters "Name=tag:Name,Values=classroom-public-1" \
  --query 'Subnets[0].SubnetId' --output text)

# Create NAT Gateway
aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_ID \
  --allocation-id $EIP_ALLOCATION_ID \
  --tag-specifications 'ResourceType=nat-gateway,Tags=[{Key=Name,Value=classroom-nat}]'
```

---

## Container Registry Setup

### 1. Create ECR Repositories

```bash
# Create repository for backend
aws ecr create-repository \
  --repository-name classroom-backend \
  --image-scanning-configuration scanOnPush=true

# Create repository for frontend  
aws ecr create-repository \
  --repository-name classroom-frontend \
  --image-scanning-configuration scanOnPush=true

# Create repository for nginx
aws ecr create-repository \
  --repository-name classroom-nginx \
  --image-scanning-configuration scanOnPush=true
```

### 2. Build and Push Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

# Build and push backend
cd backend
docker build -f Dockerfile.prod -t classroom-backend:$VERSION .
docker tag classroom-backend:$VERSION $ECR_REGISTRY/classroom-backend:$VERSION
docker tag classroom-backend:$VERSION $ECR_REGISTRY/classroom-backend:latest
docker push $ECR_REGISTRY/classroom-backend:$VERSION
docker push $ECR_REGISTRY/classroom-backend:latest

# Build and push frontend
cd ../frontend
docker build -f Dockerfile.prod -t classroom-frontend:$VERSION .
docker tag classroom-frontend:$VERSION $ECR_REGISTRY/classroom-frontend:$VERSION
docker tag classroom-frontend:$VERSION $ECR_REGISTRY/classroom-frontend:latest
docker push $ECR_REGISTRY/classroom-frontend:$VERSION
docker push $ECR_REGISTRY/classroom-frontend:latest

# Build and push nginx (using custom nginx config)
cd ../docker/nginx
docker build -f Dockerfile -t classroom-nginx:$VERSION .
docker tag classroom-nginx:$VERSION $ECR_REGISTRY/classroom-nginx:$VERSION
docker tag classroom-nginx:$VERSION $ECR_REGISTRY/classroom-nginx:latest
docker push $ECR_REGISTRY/classroom-nginx:$VERSION
docker push $ECR_REGISTRY/classroom-nginx:latest
```

---

## Database and Cache Setup

### 1. Create RDS PostgreSQL Database

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name classroom-db-subnet-group \
  --db-subnet-group-description "Subnet group for classroom database" \
  --subnet-ids $(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=classroom-db-*" \
    --query 'Subnets[].SubnetId' --output text)

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier classroom-db-prod \
  --db-instance-class db.t3.small \
  --engine postgres \
  --engine-version 16.1 \
  --master-username $DB_USER \
  --master-user-password $DB_PASSWORD \
  --allocated-storage 20 \
  --max-allocated-storage 100 \
  --storage-type gp2 \
  --vpc-security-group-ids $DB_SG_ID \
  --db-subnet-group-name classroom-db-subnet-group \
  --backup-retention-period 7 \
  --storage-encrypted \
  --deletion-protection \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --tags Key=Environment,Value=production Key=Application,Value=classroom
```

### 2. Create ElastiCache Redis Cluster

```bash
# Create cache subnet group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name classroom-cache-subnet-group \
  --cache-subnet-group-description "Subnet group for classroom cache" \
  --subnet-ids $(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=classroom-db-*" \
    --query 'Subnets[].SubnetId' --output text)

# Create Redis cache cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id classroom-redis-prod \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --security-group-ids $DB_SG_ID \
  --cache-subnet-group-name classroom-cache-subnet-group \
  --auth-token $REDIS_PASSWORD \
  --transit-encryption-enabled \
  --at-rest-encryption-enabled \
  --tags Key=Environment,Value=production Key=Application,Value=classroom
```

### 3. Create S3 Bucket for Blob Storage

```bash
# Create S3 bucket for blob storage
aws s3 mb s3://classroom-blobs-prod-$AWS_ACCOUNT_ID

# Configure bucket encryption
aws s3api put-bucket-encryption \
  --bucket classroom-blobs-prod-$AWS_ACCOUNT_ID \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Configure bucket versioning
aws s3api put-bucket-versioning \
  --bucket classroom-blobs-prod-$AWS_ACCOUNT_ID \
  --versioning-configuration Status=Enabled

# Configure bucket policy (restrict access to ECS tasks)
aws s3api put-bucket-policy \
  --bucket classroom-blobs-prod-$AWS_ACCOUNT_ID \
  --policy file://s3-bucket-policy.json
```

---

## Load Balancer and Networking

### 1. Create Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name classroom-alb-prod \
  --subnets $(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=classroom-public-*" \
    --query 'Subnets[].SubnetId' --output text) \
  --security-groups $ALB_SG_ID \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Environment,Value=production Key=Application,Value=classroom

# Get ALB ARN
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names classroom-alb-prod \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# Create target groups for frontend
aws elbv2 create-target-group \
  --name classroom-frontend-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-enabled \
  --health-check-path "/" \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

# Create target groups for backend
aws elbv2 create-target-group \
  --name classroom-backend-tg \
  --protocol HTTP \
  --port 8080 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-enabled \
  --health-check-path "/Plone/@@security-middleware" \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 10 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3
```

### 2. Configure ALB Listeners and Rules

```bash
# Get target group ARNs
FRONTEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names classroom-frontend-tg \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

BACKEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names classroom-backend-tg \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

# Create HTTPS listener (if SSL certificate is available)
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$SSL_CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN

# Create HTTP listener (redirect to HTTPS)
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig='{
    "Protocol": "HTTPS",
    "Port": "443",
    "StatusCode": "HTTP_301"
  }'

# Create rule for backend API traffic
HTTPS_LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --query 'Listeners[?Port==`443`].ListenerArn' --output text)

aws elbv2 create-rule \
  --listener-arn $HTTPS_LISTENER_ARN \
  --priority 100 \
  --conditions Field=path-pattern,Values="/Plone/*","/++api++/*" \
  --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN
```

---

## ECS Cluster and Services

### 1. Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name classroom-cluster-prod \
  --capacity-providers FARGATE \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
  --tags key=Environment,value=production key=Application,value=classroom
```

### 2. Create IAM Roles

```bash
# Create ECS task execution role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document file://ecs-task-execution-role.json

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create ECS task role for application permissions
aws iam create-role \
  --role-name classroomTaskRole \
  --assume-role-policy-document file://ecs-task-role.json

aws iam attach-role-policy \
  --role-name classroomTaskRole \
  --policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/classroom-s3-access
```

### 3. Create Task Definitions

#### Backend Task Definition

```json
{
  "family": "classroom-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/classroomTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/classroom-backend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "DB_HOST", "value": "classroom-db-prod.cluster-xyz.us-east-1.rds.amazonaws.com"},
        {"name": "DB_PORT", "value": "5432"},
        {"name": "DB_NAME", "value": "classroom_production"},
        {"name": "DB_USER", "value": "classroom_admin"},
        {"name": "REDIS_HOST", "value": "classroom-redis-prod.cache.amazonaws.com"},
        {"name": "PLONE_SITE_ID", "value": "Plone"}
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:ssm:us-east-1:123456789012:parameter/classroom/db-password"
        },
        {
          "name": "REDIS_PASSWORD", 
          "valueFrom": "arn:aws:ssm:us-east-1:123456789012:parameter/classroom/redis-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/classroom-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/Plone/@@security-middleware || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 120
      }
    }
  ]
}
```

#### Frontend Task Definition

```json
{
  "family": "classroom-frontend",
  "networkMode": "awsvpc", 
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/classroom-frontend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "NODE_ENV", "value": "production"},
        {"name": "BACKEND_HOST", "value": "classroom-backend"},
        {"name": "PUBLIC_URL", "value": "https://classroom.yourdomain.com"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/classroom-frontend",
          "awslogs-region": "us-east-1", 
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### 4. Create ECS Services

```bash
# Register task definitions
aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json

# Create backend service
aws ecs create-service \
  --cluster classroom-cluster-prod \
  --service-name classroom-backend-service \
  --task-definition classroom-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[$(aws ec2 describe-subnets \
      --filters "Name=tag:Name,Values=classroom-private-*" \
      --query 'Subnets[].SubnetId' --output text | tr '\t' ',')],
    securityGroups=[$ECS_SG_ID],
    assignPublicIp=DISABLED
  }" \
  --load-balancers targetGroupArn=$BACKEND_TG_ARN,containerName=backend,containerPort=8080 \
  --enable-execute-command

# Create frontend service  
aws ecs create-service \
  --cluster classroom-cluster-prod \
  --service-name classroom-frontend-service \
  --task-definition classroom-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[$(aws ec2 describe-subnets \
      --filters "Name=tag:Name,Values=classroom-private-*" \
      --query 'Subnets[].SubnetId' --output text | tr '\t' ',')],
    securityGroups=[$ECS_SG_ID],
    assignPublicIp=DISABLED
  }" \
  --load-balancers targetGroupArn=$FRONTEND_TG_ARN,containerName=frontend,containerPort=3000 \
  --enable-execute-command
```

---

## Monitoring and Logging

### 1. Create CloudWatch Log Groups

```bash
# Create log groups
aws logs create-log-group --log-group-name /ecs/classroom-backend
aws logs create-log-group --log-group-name /ecs/classroom-frontend
aws logs create-log-group --log-group-name /aws/ecs/classroom-cluster

# Set retention period
aws logs put-retention-policy \
  --log-group-name /ecs/classroom-backend \
  --retention-in-days 30

aws logs put-retention-policy \
  --log-group-name /ecs/classroom-frontend \
  --retention-in-days 30
```

### 2. Create CloudWatch Dashboard

```bash
# Create dashboard configuration
cat > dashboard-config.json << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", "ServiceName", "classroom-backend-service"],
          [".", "MemoryUtilization", ".", "."],
          ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "app/classroom-alb-prod"],
          [".", "RequestCount", ".", "."]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Classroom Management Platform Metrics"
      }
    }
  ]
}
EOF

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "Classroom-Management-Production" \
  --dashboard-body file://dashboard-config.json
```

### 3. Create CloudWatch Alarms

```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "Classroom-Backend-High-CPU" \
  --alarm-description "Backend CPU utilization is too high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:$AWS_ACCOUNT_ID:classroom-alerts

# Database connection alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "Classroom-DB-Connections" \
  --alarm-description "Database connection count is high" \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 15 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=DBInstanceIdentifier,Value=classroom-db-prod
```

---

## SSL/TLS Configuration

### 1. Configure HTTPS Redirection

The ALB listener configuration above already handles HTTPS redirection. Ensure your ACM certificate is validated and attached.

### 2. Update DNS Records

```bash
# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names classroom-alb-prod \
  --query 'LoadBalancers[0].DNSName' --output text)

# Create Route 53 record (if using Route 53)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "classroom.yourdomain.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'$ALB_DNS'"}]
      }
    }]
  }'
```

---

## Deployment Automation

### 1. Create Deployment Scripts

Create `deploy.sh`:

```bash
#!/bin/bash
set -euo pipefail

# Production deployment script
VERSION=${1:-latest}
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "🚀 Deploying Classroom Management Platform v$VERSION"

# Build and push images
echo "Building and pushing container images..."
./scripts/build-and-push.sh $VERSION

# Update task definitions
echo "Updating ECS task definitions..."
aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json

# Update services
echo "Updating ECS services..."
aws ecs update-service \
  --cluster classroom-cluster-prod \
  --service classroom-backend-service \
  --task-definition classroom-backend

aws ecs update-service \
  --cluster classroom-cluster-prod \
  --service classroom-frontend-service \
  --task-definition classroom-frontend

# Wait for deployment
echo "Waiting for deployment to complete..."
aws ecs wait services-stable \
  --cluster classroom-cluster-prod \
  --services classroom-backend-service classroom-frontend-service

echo "✅ Deployment completed successfully!"
```

### 2. Create CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy-production.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  AWS_REGION: us-east-1
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
        
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2
      
    - name: Build and push images
      run: |
        VERSION=${GITHUB_REF#refs/tags/}
        if [[ $VERSION == refs/heads/main ]]; then
          VERSION=latest
        fi
        ./scripts/build-and-push.sh $VERSION
        
    - name: Deploy to ECS
      run: |
        ./scripts/deploy.sh $VERSION
```

---

## Maintenance and Updates

### 1. Backup Procedures

```bash
# Create backup script
cat > backup-database.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="classroom-backup-$DATE"

# Create RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier classroom-db-prod \
  --db-snapshot-identifier $BACKUP_NAME

# Wait for completion
aws rds wait db-snapshot-completed \
  --db-snapshot-identifier $BACKUP_NAME

echo "Database backup completed: $BACKUP_NAME"
EOF

chmod +x backup-database.sh
```

### 2. Update Procedures

```bash
# Rolling update script
cat > rolling-update.sh << 'EOF'
#!/bin/bash
NEW_VERSION=$1

# Update backend with zero downtime
aws ecs update-service \
  --cluster classroom-cluster-prod \
  --service classroom-backend-service \
  --task-definition classroom-backend:$NEW_VERSION \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100"

# Wait for backend deployment
aws ecs wait services-stable \
  --cluster classroom-cluster-prod \
  --services classroom-backend-service

# Update frontend
aws ecs update-service \
  --cluster classroom-cluster-prod \
  --service classroom-frontend-service \
  --task-definition classroom-frontend:$NEW_VERSION \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100"

echo "Rolling update completed"
EOF
```

### 3. Health Monitoring

```bash
# Health check script
cat > health-check.sh << 'EOF'
#!/bin/bash
DOMAIN="https://classroom.yourdomain.com"

# Check frontend
if curl -f "$DOMAIN/" > /dev/null 2>&1; then
  echo "✅ Frontend is healthy"
else
  echo "❌ Frontend health check failed"
  exit 1
fi

# Check backend API
if curl -f "$DOMAIN/Plone/@@security-middleware" > /dev/null 2>&1; then
  echo "✅ Backend API is healthy"
else
  echo "❌ Backend API health check failed"
  exit 1
fi

echo "🎉 All services are healthy"
EOF
```

---

## Cost Optimization

### 1. Production Cost Breakdown (Monthly)

| Service | Configuration | Cost |
|---------|---------------|------|
| ECS Fargate | 2 backend + 2 frontend tasks | $35-45 |
| RDS PostgreSQL | db.t3.small | $25-35 |
| ElastiCache Redis | cache.t3.micro | $15-20 |
| Application Load Balancer | 1 ALB | $20-25 |
| Data Transfer | Moderate usage | $10-15 |
| CloudWatch | Logs + metrics | $5-10 |
| **Total** | | **$110-150** |

### 2. Cost Optimization Strategies

#### Use Spot Instances for Development
```bash
# Development cluster with Spot instances
aws ecs put-cluster-capacity-providers \
  --cluster classroom-cluster-dev \
  --capacity-providers FARGATE_SPOT \
  --default-capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1
```

#### Implement Auto Scaling
```bash
# Create auto scaling target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/classroom-cluster-prod/classroom-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --policy-name classroom-backend-cpu-scaling \
  --service-namespace ecs \
  --resource-id service/classroom-cluster-prod/classroom-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 60.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }'
```

#### Schedule Development Environment
```bash
# Stop development environment at night
aws events put-rule \
  --name "classroom-dev-stop" \
  --schedule-expression "cron(0 22 ? * MON-FRI *)" \
  --description "Stop development environment at 10 PM"

aws events put-targets \
  --rule classroom-dev-stop \
  --targets "Id=1,Arn=arn:aws:ecs:us-east-1:$AWS_ACCOUNT_ID:cluster/classroom-cluster-dev,RoleArn=arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsEventsRole,EcsParameters={TaskDefinitionArn=arn:aws:ecs:us-east-1:$AWS_ACCOUNT_ID:task-definition/stop-services,LaunchType=FARGATE}"
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. ECS Tasks Failing to Start

**Symptoms:** Tasks keep stopping with EXIT_CODE 1

**Solutions:**
```bash
# Check logs
aws logs get-log-events \
  --log-group-name /ecs/classroom-backend \
  --log-stream-name $(aws logs describe-log-streams \
    --log-group-name /ecs/classroom-backend \
    --order-by LastEventTime \
    --descending \
    --max-items 1 \
    --query 'logStreams[0].logStreamName' --output text)

# Check task definition
aws ecs describe-tasks \
  --cluster classroom-cluster-prod \
  --tasks $(aws ecs list-tasks \
    --cluster classroom-cluster-prod \
    --service-name classroom-backend-service \
    --query 'taskArns[0]' --output text)
```

#### 2. Database Connection Issues

**Symptoms:** Backend can't connect to PostgreSQL

**Check Security Groups:**
```bash
# Verify ECS security group has access to DB
aws ec2 describe-security-groups \
  --group-ids $DB_SG_ID \
  --query 'SecurityGroups[0].IpPermissions'
```

**Check Database Status:**
```bash
aws rds describe-db-instances \
  --db-instance-identifier classroom-db-prod \
  --query 'DBInstances[0].DBInstanceStatus'
```

#### 3. Load Balancer Health Check Failures

**Symptoms:** Target group shows unhealthy targets

**Check Target Health:**
```bash
aws elbv2 describe-target-health \
  --target-group-arn $BACKEND_TG_ARN
```

**Verify Health Check Configuration:**
```bash
aws elbv2 describe-target-groups \
  --target-group-arns $BACKEND_TG_ARN \
  --query 'TargetGroups[0].HealthCheckPath'
```

#### 4. SSL Certificate Issues

**Check Certificate Status:**
```bash
aws acm describe-certificate \
  --certificate-arn $SSL_CERT_ARN \
  --query 'Certificate.Status'
```

#### 5. High Costs

**Monitor Usage:**
```bash
# Check Fargate usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=classroom-backend-service \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average
```

### Emergency Procedures

#### 1. Rollback Deployment

```bash
# Get previous task definition revision
PREVIOUS_REVISION=$(aws ecs describe-services \
  --cluster classroom-cluster-prod \
  --services classroom-backend-service \
  --query 'services[0].taskDefinition' --output text | sed 's/:.*/:/' | awk -F: '{print $2-1}')

# Rollback to previous version
aws ecs update-service \
  --cluster classroom-cluster-prod \
  --service classroom-backend-service \
  --task-definition classroom-backend:$PREVIOUS_REVISION
```

#### 2. Scale Up for High Traffic

```bash
# Quickly scale up services
aws ecs update-service \
  --cluster classroom-cluster-prod \
  --service classroom-backend-service \
  --desired-count 4

aws ecs update-service \
  --cluster classroom-cluster-prod \
  --service classroom-frontend-service \
  --desired-count 4
```

#### 3. Emergency Database Restore

```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier classroom-db-prod \
  --snapshot-type manual

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier classroom-db-prod-restored \
  --db-snapshot-identifier classroom-backup-20240115_143000
```

---

## Summary

This deployment guide provides a complete AWS ECS production setup for the Classroom Management Platform with:

- **High Availability**: Multi-AZ deployment with auto-scaling
- **Security**: VPC isolation, encrypted storage, HTTPS-only access
- **Monitoring**: CloudWatch dashboards, alarms, and logging
- **Cost Optimization**: Resource limits and scaling policies
- **Maintainability**: Automated deployments and backup procedures

**Expected Monthly Costs:**
- Production: $110-150
- Staging: $60-80
- Development: $30-50

**Performance Targets:**
- Dashboard load time: <1 second
- 99.9% uptime
- Auto-scaling based on CPU/memory usage
- Zero-downtime deployments

The platform is now ready for production use with enterprise-grade reliability and security suitable for K-12 educational environments. 