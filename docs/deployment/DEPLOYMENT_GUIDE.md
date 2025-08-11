# Deployment Guide

## Overview

This guide covers deploying AbSequenceAlign in various environments, from local development to production cloud deployments.

## Prerequisites

- Docker and Docker Compose
- Git
- Access to container registry (for production)
- Domain name and SSL certificates (for production)

## Local Development Deployment

### Quick Start
```bash
# Clone the repository
git clone https://github.com/maquino1985/AbSequenceAlign.git
cd AbSequenceAlign

# Start development environment
make dev
```

### Manual Setup
```bash
# Start backend
cd app/backend
conda env create -f environment.yml
conda activate AbSequenceAlign
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd app/frontend
npm install
npm run dev
```

## Docker Deployment

### Development with Docker
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production with Docker
```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Environment Configuration

Create a `.env` file based on `env.example`:

```bash
# Copy example environment file
cp env.example .env

# Edit environment variables
nano .env
```

Key environment variables:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/absequencealign

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]

# External Services
ANARCI_PATH=/usr/local/bin/anarci
HMMER_PATH=/usr/local/bin/hmmer
```

## Cloud Deployment

### AWS ECS/Fargate

#### 1. Build and Push Images
```bash
# Build production images
docker build -t absequencealign-backend:latest -f app/backend/Dockerfile .
docker build -t absequencealign-frontend:latest -f app/frontend/Dockerfile .

# Tag for ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker tag absequencealign-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/absequencealign-backend:latest
docker tag absequencealign-frontend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/absequencealign-frontend:latest

# Push to ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/absequencealign-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/absequencealign-frontend:latest
```

#### 2. Create ECS Task Definition
```json
{
  "family": "absequencealign",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/absequencealign-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:password@your-rds-endpoint:5432/absequencealign"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/absequencealign",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    },
    {
      "name": "frontend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/absequencealign-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/absequencealign",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

#### 1. Build and Deploy
```bash
# Set project
gcloud config set project your-project-id

# Build and deploy backend
cd app/backend
gcloud run deploy absequencealign-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://user:password@your-sql-instance:5432/absequencealign

# Build and deploy frontend
cd ../frontend
gcloud run deploy absequencealign-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Kubernetes Deployment

#### 1. Create Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: absequencealign
```

#### 2. Deploy Backend
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: absequencealign-backend
  namespace: absequencealign
spec:
  replicas: 3
  selector:
    matchLabels:
      app: absequencealign-backend
  template:
    metadata:
      labels:
        app: absequencealign-backend
    spec:
      containers:
      - name: backend
        image: absequencealign-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: absequencealign-backend-service
  namespace: absequencealign
spec:
  selector:
    app: absequencealign-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

#### 3. Deploy Frontend
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: absequencealign-frontend
  namespace: absequencealign
spec:
  replicas: 2
  selector:
    matchLabels:
      app: absequencealign-frontend
  template:
    metadata:
      labels:
        app: absequencealign-frontend
    spec:
      containers:
      - name: frontend
        image: absequencealign-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: absequencealign-frontend-service
  namespace: absequencealign
spec:
  selector:
    app: absequencealign-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

## Database Setup

### PostgreSQL Setup

#### Local Development
```bash
# Using Docker
docker run --name postgres-absequencealign \
  -e POSTGRES_DB=absequencealign \
  -e POSTGRES_USER=absequencealign \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

#### Production Database
```bash
# Run migrations
cd app/backend
alembic upgrade head

# Seed initial data (if needed)
python -m backend.database.seed_data
```

## Monitoring and Logging

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'absequencealign-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Grafana Dashboard
Import the provided Grafana dashboard configuration for monitoring:
- CPU and memory usage
- Request rates and response times
- Error rates
- Database connection metrics

### Log Aggregation
```bash
# Using ELK Stack
# Elasticsearch configuration
# Logstash pipeline
# Kibana dashboard setup
```

## Security Considerations

### SSL/TLS Configuration
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    location / {
        proxy_pass http://frontend:80;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
    }
}
```

### Environment Security
```bash
# Use secrets management
# AWS Secrets Manager
# Google Secret Manager
# Kubernetes Secrets
# HashiCorp Vault
```

## Performance Optimization

### Frontend Optimization
```bash
# Build optimization
npm run build

# Enable compression
# Configure CDN
# Implement caching strategies
```

### Backend Optimization
```bash
# Database indexing
# Query optimization
# Caching with Redis
# Load balancing
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
docker exec -it postgres-absequencealign psql -U absequencealign -d absequencealign

# Check logs
docker-compose logs backend
```

#### Frontend Build Issues
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install

# Check build logs
npm run build
```

#### Docker Issues
```bash
# Clean up Docker resources
docker system prune -a

# Rebuild images
docker-compose build --no-cache
```

### Health Checks
```bash
# Backend health check
curl http://localhost:8000/health

# Frontend health check
curl http://localhost:3000
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
pg_dump -h localhost -U absequencealign -d absequencealign > backup.sql

# Restore backup
psql -h localhost -U absequencealign -d absequencealign < backup.sql
```

### Application Backup
```bash
# Backup configuration files
tar -czf config-backup.tar.gz .env docker-compose*.yml

# Backup data directory
tar -czf data-backup.tar.gz data/
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Load balancer configuration
# Auto-scaling policies
```

### Vertical Scaling
```bash
# Increase resource limits
# Optimize application performance
# Database optimization
```
