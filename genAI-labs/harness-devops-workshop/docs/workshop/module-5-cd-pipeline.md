# Module 5: Harness CD Pipeline

## Overview

In this module, you'll create a Continuous Delivery pipeline in Harness that deploys your application to AWS ECS using advanced deployment strategies like Blue/Green and Canary.

**Duration**: 120 minutes  
**Difficulty**: Advanced

## Learning Objectives

By the end of this module, you will:
- Create a CD pipeline in Harness
- Configure service definitions
- Set up environment configurations
- Implement deployment strategies (Blue/Green, Canary, Rolling)
- Configure approval gates
- Set up rollback strategies

## Prerequisites

- Completed Module 4 (CI Pipeline)
- ECS cluster and services created
- ECR repositories with images
- Harness Delegate connected

## Step 1: Create Service Definitions

### 1.1 Create Backend Service

1. Navigate to **"Services"** in Harness
2. Click **"New Service"**
3. Enter service details:
   - **Name**: `workshop-backend-service`
   - **Type**: `ECS`
4. Click **"Save"**

### 1.2 Configure Service Definition

1. In service configuration, select **"Service Definition"**
2. Configure ECS service:
   - **Task Definition**: Create new or use existing
   - **Container Specifications**:
     - **Image**: `<+artifact.image>`
     - **Port**: `5000`
     - **CPU**: `256`
     - **Memory**: `512`
   - **Environment Variables**:
     - `FLASK_ENV`: `production`
     - `APP_VERSION`: `<+artifact.tag>`

### 1.3 Create Frontend Service

Repeat steps 1.1-1.2 for frontend service:
- **Name**: `workshop-frontend-service`
- **Port**: `80`
- **CPU**: `256`
- **Memory**: `256`

## Step 2: Configure Environments

### 2.1 Update Development Environment

1. Navigate to **"Environments"** → **"development"**
2. Add infrastructure:
   - **Type**: `ECS`
   - **Connector**: AWS connector
   - **Cluster**: Your ECS cluster name
   - **Region**: `us-east-1`
3. Save infrastructure definition

### 2.2 Update Production Environment

1. Navigate to **"Environments"** → **"production"**
2. Add infrastructure (same as development)
3. Configure overrides for production:
   - Higher CPU/Memory
   - More task count
   - Production-specific environment variables

## Step 3: Create CD Pipeline

### 3.1 Create New Pipeline

1. Navigate to **"CD"** module
2. Click **"Pipelines"** → **"New Pipeline"**
3. Enter pipeline details:
   - **Name**: `workshop-cd-pipeline`
   - **Description**: `CD pipeline for deploying to ECS`
4. Click **"Start"**

### 3.2 Add Deployment Stage

1. Click **"Add Stage"**
2. Select **"Deploy"**
3. Enter stage name: `deploy-to-development`
4. Click **"Set Up Stage"**

## Step 4: Configure Deployment Stage

### 4.1 Select Service

1. Under **"Service"**, select `workshop-backend-service`
2. Configure artifact source:
   - **Primary Artifact**: ECR
   - **Image Path**: `<registry>/backend`
   - **Tag**: `<+pipeline.variables.imageTag>`

### 4.2 Select Environment

1. Under **"Environment"**, select `development`
2. Select infrastructure definition
3. Configure environment variables if needed

### 4.3 Configure Execution

1. Under **"Execution"**, add deployment steps:
   - **Deploy Step**: ECS Rolling Deploy
   - Configure:
     - **Skip Steady State Check**: `false`
     - **Timeout**: `10m`

## Step 5: Implement Deployment Strategies

### 5.1 Rolling Deployment

1. In deployment step, select **"Rolling"**
2. Configure:
   - **Batch Size**: `50%`
   - **Batch Count**: `2`
   - **Health Check**: Enabled

### 5.2 Blue/Green Deployment

1. Add new stage: `deploy-to-production`
2. Select **"Blue/Green"** strategy
3. Configure:
   - **Target Group 1**: Production target group
   - **Target Group 2**: Green target group
   - **Traffic Shift**: Gradual (0% → 100%)

### 5.3 Canary Deployment

1. For production, select **"Canary"** strategy
2. Configure canary phases:
   - **Phase 1**: 10% traffic, 5 minutes
   - **Phase 2**: 25% traffic, 5 minutes
   - **Phase 3**: 50% traffic, 5 minutes
   - **Phase 4**: 100% traffic
3. Set up verification steps between phases

## Step 6: Add Approval Gates

### 6.1 Manual Approval

1. Add **"Approval"** step before production deployment
2. Configure:
   - **Approval Type**: `Manual`
   - **Approvers**: Select users/groups
   - **Message**: `Approve deployment to production?`

### 6.2 JIRA Approval (Optional)

1. Add **"JIRA Approval"** step
2. Configure JIRA connector
3. Set up approval workflow

## Step 7: Configure Rollback

### 7.1 Automatic Rollback

1. In stage settings, enable **"Rollback"**
2. Configure rollback steps:
   - **Rollback Type**: `Previous Version`
   - **Rollback Condition**: On failure

### 7.2 Manual Rollback

1. Add rollback step
2. Configure:
   - **Rollback Strategy**: `Previous Successful Deployment`
   - **Timeout**: `10m`

## Step 8: Add Verification Steps

### 8.1 Health Check Verification

1. Add **"Verification"** step after deployment
2. Configure:
   - **Type**: `Health Check`
   - **Endpoint**: `/api/health`
   - **Expected Status**: `200`
   - **Timeout**: `5m`

### 8.2 Custom Verification

1. Add **"Shell Script"** verification
2. Run custom checks:
   ```bash
   # Verify service is responding
   curl -f http://<service-url>/api/health
   # Run smoke tests
   npm run smoke-tests
   ```

## Step 9: Connect CI to CD

### 9.1 Pipeline Chaining

1. In CI pipeline, add **"Harness Approval"** step
2. Configure to trigger CD pipeline:
   - **Pipeline**: `workshop-cd-pipeline`
   - **Inputs**: Pass image tag and registry

### 9.2 Artifact Promotion

1. Configure artifact promotion in CI pipeline
2. After successful build, promote to CD pipeline
3. Pass artifact details as pipeline variables

## Step 10: Test Pipeline

### 10.1 Run Pipeline

1. Click **"Run"** on CD pipeline
2. Provide inputs:
   - **Image Tag**: From CI pipeline
   - **Registry**: ECR registry URL
3. Monitor deployment progress

### 10.2 Verify Deployment

1. Check ECS service status
2. Verify tasks are running
3. Test application endpoints
4. Review deployment logs

## Troubleshooting

### Deployment Failures
- Check ECS service logs
- Verify task definition
- Check IAM permissions
- Review health check configuration

### Rollback Issues
- Verify previous version exists
- Check rollback permissions
- Review rollback logs

### Approval Issues
- Verify approver permissions
- Check notification settings
- Review approval logs

## Next Steps

Congratulations! You've completed Module 5. You now have:
- ✅ CD pipeline configured
- ✅ Multiple deployment strategies implemented
- ✅ Approval gates configured
- ✅ Rollback strategies set up
- ✅ CI/CD pipeline integration complete

**Proceed to [Module 6: Advanced Features](./module-6-advanced.md)** to explore advanced Harness capabilities! 🚀

