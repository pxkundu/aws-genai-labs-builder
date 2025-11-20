# Quick Start Guide

This guide will help you get started with the Harness DevOps Workshop quickly.

## Prerequisites Checklist

- [ ] Harness account (sign up at [app.harness.io](https://app.harness.io))
- [ ] AWS account with admin access
- [ ] GitHub/GitLab account
- [ ] Docker installed
- [ ] Terraform >= 1.5 installed
- [ ] AWS CLI configured
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed

## 5-Minute Setup

### 1. Clone and Navigate

```bash
cd genAI-labs/harness-devops-workshop
```

### 2. Set up Harness Account

1. Go to [app.harness.io](https://app.harness.io) and sign up
2. Create organization: `harness-workshop`
3. Create project: `devops-workshop`
4. Enable CI and CD modules

### 3. Install Delegate

```bash
./scripts/setup-delegate.sh
# Follow prompts to enter Account ID and Delegate Token
```

### 4. Configure Connectors

In Harness UI:
1. **AWS Connector**: Add AWS credentials
2. **Git Connector**: Add GitHub/GitLab credentials

### 5. Deploy Infrastructure

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform apply
```

### 6. Import Pipelines

1. In Harness, go to Pipelines
2. Import `harness/pipelines/ci-pipeline.yaml`
3. Import `harness/pipelines/cd-pipeline.yaml`
4. Configure variables and connectors

## Next Steps

1. **Follow Module 1**: [Harness Platform Setup](./docs/workshop/module-1-setup.md)
2. **Follow Module 2**: [Application Development](./docs/workshop/module-2-application.md)
3. **Follow Module 3**: [Infrastructure as Code](./docs/workshop/module-3-infrastructure.md)
4. **Follow Module 4**: [CI Pipeline](./docs/workshop/module-4-ci-pipeline.md)
5. **Follow Module 5**: [CD Pipeline](./docs/workshop/module-5-cd-pipeline.md)

## Common Commands

### Build and Test Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
pytest tests/ -v

# Frontend
cd frontend
npm install
npm test
```

### Docker Compose

```bash
docker-compose up --build
```

### Infrastructure

```bash
# Deploy
./scripts/deploy-infrastructure.sh

# Destroy
./scripts/destroy-infrastructure.sh
```

## Getting Help

- **Workshop Documentation**: [docs/workshop/](./docs/workshop/)
- **Architecture**: [architecture.md](./architecture.md)
- **Deployment Guide**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Harness Docs**: [docs.harness.io](https://docs.harness.io/)

## Workshop Timeline

| Module | Time | Status |
|--------|------|--------|
| Module 1: Setup | 60 min | ⬜ |
| Module 2: Application | 90 min | ⬜ |
| Module 3: Infrastructure | 90 min | ⬜ |
| Module 4: CI Pipeline | 120 min | ⬜ |
| Module 5: CD Pipeline | 120 min | ⬜ |
| Module 6: Advanced | 90 min | ⬜ |
| Module 7: Monitoring | 60 min | ⬜ |

**Total**: ~8.5 hours

## Success Criteria

You'll know you're successful when:
- ✅ Application builds and tests pass
- ✅ Images are pushed to ECR
- ✅ Application deploys to ECS
- ✅ Health checks pass
- ✅ You can access the application via ALB

## Ready to Start?

Begin with [Module 1: Harness Platform Setup](./docs/workshop/module-1-setup.md) 🚀

