# Module 4: Harness CI Pipeline

## Overview

In this module, you'll create a comprehensive Continuous Integration pipeline in Harness that builds, tests, and scans your application code before publishing artifacts to Amazon ECR.

**Duration**: 120 minutes  
**Difficulty**: Intermediate

## Learning Objectives

By the end of this module, you will:
- Create a CI pipeline in Harness
- Configure build steps for Docker images
- Set up automated testing
- Integrate security scanning
- Publish artifacts to Amazon ECR
- Configure pipeline triggers

## Prerequisites

- Completed Module 1 (Harness Setup)
- Completed Module 2 (Application Development)
- Completed Module 3 (Infrastructure)
- AWS ECR repository created
- Harness Delegate connected

## Step 1: Create CI Pipeline

### 1.1 Navigate to CI Module

1. In Harness, navigate to your project
2. Click on **"CI"** module
3. Click **"Pipelines"**
4. Click **"New Pipeline"**

### 1.2 Pipeline Configuration

1. Enter pipeline details:
   - **Name**: `workshop-ci-pipeline`
   - **Description**: `CI pipeline for building and testing application`
2. Select **"Inline"** pipeline type
3. Click **"Start"**

## Step 2: Configure Pipeline Stages

### 2.1 Add Build Stage

1. Click **"Add Stage"**
2. Select **"Build"**
3. Enter stage name: `build-and-test`
4. Click **"Set Up Stage"**

### 2.2 Configure Build Infrastructure

1. Under **"Infrastructure"**, select:
   - **Type**: `Kubernetes` or `Cloud` (based on your setup)
   - **Namespace**: `default` (or your namespace)
   - **Connector**: Select your Kubernetes/Cloud connector
2. Click **"Apply"**

## Step 3: Add Build Steps

### 3.1 Checkout Code Step

1. Click **"Add Step"**
2. Select **"Checkout"**
3. Configure:
   - **Name**: `checkout-code`
   - **Connector**: Select your Git connector
   - **Repository**: Your repository
   - **Branch**: `<+trigger.branch>` or `main`
4. Click **"Apply Changes"**

### 3.2 Build Backend Image

1. Click **"Add Step"**
2. Select **"Build and Push an image"**
3. Configure:
   - **Name**: `build-backend-image`
   - **Connector**: Select your AWS connector
   - **Registry**: `ECR`
   - **Region**: `us-east-1` (or your region)
   - **Image**: `<+pipeline.registry>/backend:<+pipeline.imageTag>`
   - **Dockerfile**: `backend/Dockerfile`
   - **Context**: `backend/`
4. Click **"Apply Changes"**

### 3.3 Build Frontend Image

1. Click **"Add Step"**
2. Select **"Build and Push an image"**
3. Configure:
   - **Name**: `build-frontend-image`
   - **Connector**: Select your AWS connector
   - **Registry**: `ECR`
   - **Region**: `us-east-1`
   - **Image**: `<+pipeline.registry>/frontend:<+pipeline.imageTag>`
   - **Dockerfile**: `frontend/Dockerfile`
   - **Context**: `frontend/`
4. Click **"Apply Changes"**

## Step 4: Add Test Steps

### 4.1 Run Backend Tests

1. Click **"Add Step"**
2. Select **"Run"**
3. Configure:
   - **Name**: `run-backend-tests`
   - **Image**: `python:3.11-slim`
   - **Command**: 
     ```bash
     cd backend
     pip install -r requirements.txt
     pytest tests/ -v --cov=app --cov-report=xml
     ```
   - **Output Variables**: (optional) Test coverage metrics
4. Click **"Apply Changes"**

### 4.2 Run Frontend Tests

1. Click **"Add Step"**
2. Select **"Run"**
3. Configure:
   - **Name**: `run-frontend-tests`
   - **Image**: `node:18-alpine`
   - **Command**:
     ```bash
     cd frontend
     npm ci
     npm test -- --coverage --watchAll=false
     ```
4. Click **"Apply Changes"**

## Step 5: Add Security Scanning

### 5.1 Container Image Scanning

1. Click **"Add Step"**
2. Select **"Security"** → **"Security Tests"**
3. Configure:
   - **Name**: `scan-backend-image`
   - **Tool**: `Snyk` or `OWASP`
   - **Target**: `Image`
   - **Image**: `<+pipeline.registry>/backend:<+pipeline.imageTag>`
   - **Fail on Severity**: `High`
4. Click **"Apply Changes"**

### 5.2 Code Quality Scanning

1. Click **"Add Step"**
2. Select **"Security"** → **"SonarQube"** (if configured)
3. Configure:
   - **Name**: `sonarqube-scan`
   - **Connector**: SonarQube connector
   - **Project Key**: Your project key
   - **Source Code**: Repository root
4. Click **"Apply Changes"**

## Step 6: Configure Pipeline Variables

### 6.1 Add Pipeline Variables

1. Click on **"Variables"** tab
2. Add variables:
   - **registry**: `123456789012.dkr.ecr.us-east-1.amazonaws.com`
   - **imageTag**: `<+trigger.tag>` or `<+pipeline.sequenceId>`
   - **awsRegion**: `us-east-1`

### 6.2 Configure Runtime Inputs

1. Mark variables as **"Runtime Input"** if needed
2. This allows values to be provided at runtime

## Step 7: Configure Pipeline Triggers

### 7.1 Create Git Trigger

1. Click **"Triggers"** tab
2. Click **"New Trigger"**
3. Select **"Git"**
4. Configure:
   - **Name**: `git-trigger`
   - **Source**: Your Git connector
   - **Repository**: Your repository
   - **Branch**: `main` or `develop`
   - **Event**: `Push` or `Pull Request`
5. Click **"Continue"**
6. Configure pipeline inputs:
   - **imageTag**: `<+trigger.tag>` or `<+trigger.branch>`
7. Click **"Create Trigger"**

### 7.2 Test Trigger

1. Make a commit to your repository
2. Push to the configured branch
3. Verify trigger fires in Harness
4. Monitor pipeline execution

## Step 8: Add Conditional Steps

### 8.1 Conditional Test Execution

1. Select a test step
2. Click **"Advanced"**
3. Add condition:
   - **Condition**: `<+stage.variables.runTests> == "true"`
4. This allows conditional execution based on variables

### 8.2 Parallel Execution

1. Select multiple steps
2. Click **"Run in Parallel"**
3. Steps will execute simultaneously

## Step 9: Add Notifications

### 9.1 Configure Notifications

1. Click **"Notifications"** tab
2. Add notification rules:
   - **Event**: `Pipeline Success` or `Pipeline Failure`
   - **Method**: `Email`, `Slack`, or `PagerDuty`
   - **Recipients**: Your email or channel
3. Click **"Save"**

## Step 10: Pipeline YAML (Alternative Method)

### 10.1 View Pipeline YAML

1. Click **"YAML"** tab
2. View the generated YAML
3. You can edit directly in YAML mode

### 10.2 Sample CI Pipeline YAML

```yaml
pipeline:
  name: workshop-ci-pipeline
  identifier: workshop_ci_pipeline
  projectIdentifier: devops-workshop
  orgIdentifier: harness-workshop
  tags: {}
  stages:
    - stage:
        name: build-and-test
        identifier: build_and_test
        type: CI
        spec:
          cloneCodebase: true
          infrastructure:
            type: KubernetesDirect
            spec:
              connectorRef: <+input>
              namespace: default
          execution:
            steps:
              - step:
                  type: Run
                  name: checkout-code
                  identifier: checkout_code
                  spec:
                    connectorRef: github-workshop-connector
                    repo: <+input>
                    branch: <+input>
              - step:
                  type: BuildAndPushECR
                  name: build-backend-image
                  identifier: build_backend_image
                  spec:
                    connectorRef: aws-workshop-connector
                    region: us-east-1
                    image: <+pipeline.variables.registry>/backend:<+pipeline.variables.imageTag>
                    dockerfile: backend/Dockerfile
                    context: backend/
              - step:
                  type: Run
                  name: run-backend-tests
                  identifier: run_backend_tests
                  spec:
                    shell: Sh
                    command: |
                      cd backend
                      pip install -r requirements.txt
                      pytest tests/ -v --cov=app
              - step:
                  type: BuildAndPushECR
                  name: build-frontend-image
                  identifier: build_frontend_image
                  spec:
                    connectorRef: aws-workshop-connector
                    region: us-east-1
                    image: <+pipeline.variables.registry>/frontend:<+pipeline.variables.imageTag>
                    dockerfile: frontend/Dockerfile
                    context: frontend/
              - step:
                  type: Run
                  name: run-frontend-tests
                  identifier: run_frontend_tests
                  spec:
                    shell: Sh
                    command: |
                      cd frontend
                      npm ci
                      npm test -- --watchAll=false
          variables: []
        description: ""
  properties:
    ci:
      codebase:
        connectorRef: github-workshop-connector
        repoName: <+input>
        build: <+input>
```

## Step 11: Test Pipeline

### 11.1 Run Pipeline Manually

1. Click **"Run"** button
2. Provide required inputs:
   - Branch: `main`
   - Image tag: `latest` or version number
3. Click **"Run Pipeline"**
4. Monitor execution in real-time

### 11.2 Verify Results

1. Check build logs for each step
2. Verify images pushed to ECR
3. Review test results
4. Check security scan reports

## Troubleshooting

### Build Failures
- Check Dockerfile syntax
- Verify build context paths
- Check ECR permissions
- Review delegate logs

### Test Failures
- Verify test dependencies installed
- Check test data and fixtures
- Review test output logs

### Security Scan Issues
- Verify scanner credentials
- Check image availability
- Review scan configuration

## Next Steps

Congratulations! You've completed Module 4. You now have:
- ✅ CI pipeline configured
- ✅ Automated builds and tests
- ✅ Security scanning integrated
- ✅ Artifacts published to ECR
- ✅ Pipeline triggers set up

**Proceed to [Module 5: Harness CD Pipeline](./module-5-cd-pipeline.md)** to implement Continuous Delivery! 🚀

