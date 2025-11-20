# Deployment Guide

This guide provides step-by-step instructions for deploying the Harness DevOps workshop application.

## Prerequisites

Before deploying, ensure you have:

- ✅ Harness account set up (Module 1)
- ✅ Application code ready (Module 2)
- ✅ AWS infrastructure provisioned (Module 3)
- ✅ CI pipeline configured (Module 4)
- ✅ CD pipeline configured (Module 5)

## Quick Deployment

### Option 1: Automated Deployment via Harness

1. **Trigger CI Pipeline**:
   ```bash
   # Push code to trigger CI pipeline
   git push origin main
   ```

2. **Monitor CI Pipeline**:
   - Navigate to Harness CI pipeline
   - Monitor build progress
   - Verify tests pass
   - Confirm images pushed to ECR

3. **Trigger CD Pipeline**:
   - CI pipeline completion triggers CD pipeline
   - Or manually run CD pipeline with image tag

4. **Verify Deployment**:
   - Check ECS service status
   - Test application endpoints
   - Review deployment logs

### Option 2: Manual Deployment

1. **Build and Push Images**:
   ```bash
   # Backend
   cd backend
   docker build -t backend:latest .
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/harness-workshop-dev-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/harness-workshop-dev-backend:latest

   # Frontend
   cd frontend
   docker build -t frontend:latest .
   docker tag frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/harness-workshop-dev-frontend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/harness-workshop-dev-frontend:latest
   ```

2. **Deploy via ECS**:
   ```bash
   # Update ECS service with new image
   aws ecs update-service \
     --cluster harness-workshop-dev-cluster \
     --service workshop-backend-service \
     --force-new-deployment
   ```

## Deployment Strategies

### Development Environment

- **Strategy**: Rolling Deployment
- **Batch Size**: 50%
- **Health Checks**: Enabled
- **Rollback**: Automatic on failure

### Production Environment

- **Strategy**: Canary Deployment
- **Phases**: 10% → 25% → 50% → 100%
- **Verification**: Between each phase
- **Approval**: Required before full rollout

## Verification Steps

### 1. Health Check

```bash
# Backend health check
curl http://<alb-dns>/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0"
}
```

### 2. Service Verification

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster harness-workshop-dev-cluster \
  --services workshop-backend-service

# Check running tasks
aws ecs list-tasks \
  --cluster harness-workshop-dev-cluster \
  --service-name workshop-backend-service
```

### 3. Application Testing

```bash
# Test API endpoints
curl http://<alb-dns>/api/users
curl -X POST http://<alb-dns>/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'
```

## Rollback Procedures

### Automatic Rollback

If deployment fails, Harness automatically rolls back to previous version.

### Manual Rollback

1. **Via Harness UI**:
   - Navigate to pipeline execution
   - Click "Rollback"
   - Select previous successful deployment

2. **Via AWS CLI**:
   ```bash
   # Get previous task definition
   aws ecs describe-task-definition \
     --task-definition workshop-backend-service:previous

   # Update service with previous task definition
   aws ecs update-service \
     --cluster harness-workshop-dev-cluster \
     --service workshop-backend-service \
     --task-definition workshop-backend-service:previous
   ```

## Monitoring

### CloudWatch Logs

```bash
# View backend logs
aws logs tail /ecs/harness-workshop-dev/backend --follow

# View frontend logs
aws logs tail /ecs/harness-workshop-dev/frontend --follow
```

### CloudWatch Metrics

- ECS service metrics
- ALB target group metrics
- Application custom metrics

### Harness Analytics

- Pipeline execution metrics
- Deployment success rates
- Rollback frequency

## Troubleshooting

### Deployment Stuck

1. Check ECS service events
2. Review task definition
3. Verify health checks
4. Check CloudWatch logs

### Health Check Failures

1. Verify application is listening on correct port
2. Check security group rules
3. Review health check endpoint
4. Check application logs

### Image Pull Errors

1. Verify ECR repository exists
2. Check IAM permissions
3. Verify image tag exists
4. Check ECR authentication

## Best Practices

1. **Always test in development first**
2. **Use canary deployments for production**
3. **Monitor deployments closely**
4. **Have rollback plan ready**
5. **Document deployment procedures**
6. **Use infrastructure as code**
7. **Automate as much as possible**

## Next Steps

After successful deployment:

1. Set up monitoring and alerting
2. Configure auto-scaling
3. Implement backup strategies
4. Plan disaster recovery
5. Document runbooks

