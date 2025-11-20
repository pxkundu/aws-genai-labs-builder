# Harness Pipeline Configurations

This directory contains Harness pipeline configurations in YAML format that can be imported into your Harness project.

## Pipeline Files

### CI Pipeline (`ci-pipeline.yaml`)

The Continuous Integration pipeline includes:
- Code checkout
- Docker image builds for backend and frontend
- Unit and integration tests
- Security scanning
- Artifact publishing to Amazon ECR

**Usage:**
1. Import into Harness via UI or CLI
2. Configure connectors and variables
3. Set up triggers for automatic execution

### CD Pipeline (`cd-pipeline.yaml`)

The Continuous Delivery pipeline includes:
- Deployment to development environment
- Deployment to production environment
- Blue/Green and Canary deployment strategies
- Rollback capabilities

**Usage:**
1. Import into Harness via UI or CLI
2. Configure services and environments
3. Set up infrastructure definitions
4. Configure approval gates

## Importing Pipelines

### Via Harness UI

1. Navigate to your project
2. Go to **Pipelines**
3. Click **Import Pipeline**
4. Select **YAML**
5. Paste the pipeline YAML content
6. Configure variables and connectors

### Via Harness CLI

```bash
harness pipeline import --file harness/pipelines/ci-pipeline.yaml
harness pipeline import --file harness/pipelines/cd-pipeline.yaml
```

## Configuration

### Required Connectors

- **AWS Connector**: For ECR and ECS access
- **Git Connector**: For source code access
- **Kubernetes/Cloud Connector**: For delegate infrastructure

### Required Variables

- `registry`: ECR registry URL (e.g., `123456789012.dkr.ecr.us-east-1.amazonaws.com`)
- `imageTag`: Docker image tag (e.g., `v1.0.0` or `<+pipeline.sequenceId>`)
- `awsRegion`: AWS region (e.g., `us-east-1`)

### Required Services

- Backend service definition in Harness
- Frontend service definition in Harness
- ECS infrastructure definitions

## Customization

You can customize these pipelines by:
- Adding additional test steps
- Integrating more security scanners
- Adding deployment strategies
- Configuring notifications
- Adding approval gates

## Next Steps

1. Review pipeline configurations
2. Import into Harness
3. Configure connectors and variables
4. Set up triggers
5. Test pipeline execution

