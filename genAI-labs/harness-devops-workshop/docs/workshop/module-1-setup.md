# Module 1: Harness Platform Setup

## Overview

In this module, you'll set up your Harness account, configure organizations, projects, connectors, and install the Harness Delegate. This foundation is essential for all subsequent modules.

**Duration**: 60 minutes  
**Difficulty**: Beginner

## Learning Objectives

By the end of this module, you will:
- Understand Harness platform architecture
- Create and configure Harness organizations and projects
- Set up AWS and Git connectors
- Configure secrets management
- Install and verify Harness Delegate

## Prerequisites

- Harness account (sign up at [app.harness.io](https://app.harness.io))
- AWS account with appropriate permissions
- GitHub or GitLab account
- Basic understanding of cloud services

## Step 1: Create Harness Account

### 1.1 Sign Up for Harness

1. Navigate to [app.harness.io](https://app.harness.io)
2. Click **"Sign Up"** or **"Start Free Trial"**
3. Enter your email address and create a password
4. Verify your email address
5. Complete the onboarding wizard

### 1.2 Choose Account Type

- **Free Tier**: Perfect for learning and small projects
- **Enterprise**: Full features for production use

For this workshop, the **Free Tier** is sufficient.

## Step 2: Create Organization

### 2.1 Create New Organization

1. In Harness, click on your account name (top right)
2. Select **"Organizations"**
3. Click **"New Organization"**
4. Enter organization details:
   - **Name**: `harness-workshop`
   - **Description**: `Workshop organization for learning Harness DevOps`
5. Click **"Save"**

### 2.2 Organization Settings

1. Navigate to **Organization Settings**
2. Review available settings:
   - **General**: Name, description
   - **Security**: SAML, OAuth
   - **Audit Trail**: Activity logs

## Step 3: Create Project

### 3.1 Create New Project

1. In your organization, click **"Projects"**
2. Click **"New Project"**
3. Enter project details:
   - **Name**: `devops-workshop`
   - **Description**: `Enterprise DevOps project with Harness`
   - **Color**: Choose a color for identification
4. Click **"Save"**

### 3.2 Project Modules

Enable the following modules for this project:
- ✅ **CI** (Continuous Integration)
- ✅ **CD** (Continuous Delivery)
- ✅ **FF** (Feature Flags) - Optional
- ✅ **CCM** (Cloud Cost Management) - Optional
- ✅ **STO** (Security Testing Orchestration) - Optional

## Step 4: Configure AWS Connector

### 4.1 Create AWS Connector

1. In your project, navigate to **"Connectors"**
2. Click **"New Connector"**
3. Select **"AWS"**
4. Choose authentication method:
   - **AWS Access Key**: For quick setup
   - **IAM Role**: Recommended for production
   - **IRSA (IAM Role for Service Account)**: For Kubernetes

### 4.2 Configure Access Key Method

1. Select **"AWS Access Key"**
2. Enter connector details:
   - **Name**: `aws-workshop-connector`
   - **Description**: `AWS connector for workshop`
3. Enter AWS credentials:
   - **Access Key ID**: Your AWS access key
   - **Secret Access Key**: Your AWS secret key
4. Select **"Region"**: `us-east-1` (or your preferred region)
5. Click **"Save and Continue"**
6. Test the connection
7. Click **"Finish"**

### 4.3 Configure IAM Role Method (Recommended)

1. Select **"IAM Role"**
2. Enter connector details:
   - **Name**: `aws-workshop-connector-iam`
   - **Description**: `AWS connector using IAM role`
3. Follow the instructions to:
   - Create IAM role in AWS
   - Configure trust relationship
   - Attach required policies
4. Enter the **IAM Role ARN**
5. Select **"Region"**
6. Click **"Save and Continue"**
7. Test the connection
8. Click **"Finish"**

### 4.4 Required IAM Policies

The IAM role/user needs the following permissions:
- `AmazonEC2FullAccess`
- `AmazonECS_FullAccess`
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonS3FullAccess`
- `CloudWatchFullAccess`
- `IAMReadOnlyAccess`

## Step 5: Configure Git Connector

### 5.1 Create GitHub Connector

1. Navigate to **"Connectors"**
2. Click **"New Connector"**
3. Select **"GitHub"**
4. Choose authentication:
   - **HTTPS**: Username and password/token
   - **SSH**: SSH key authentication

### 5.2 Configure HTTPS Method

1. Select **"HTTPS"**
2. Enter connector details:
   - **Name**: `github-workshop-connector`
   - **Description**: `GitHub connector for workshop`
3. Enter GitHub credentials:
   - **Username**: Your GitHub username
   - **Personal Access Token**: Generate in GitHub Settings
4. Select **"Repository"**: Choose specific repo or all repos
5. Click **"Save and Continue"**
6. Test the connection
7. Click **"Finish"**

### 5.3 Generate GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings
2. Click **"Personal access tokens"** → **"Tokens (classic)"**
3. Click **"Generate new token"**
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
5. Generate and copy the token
6. Save securely (you won't see it again)

## Step 6: Configure Secrets Management

### 6.1 Create Secret for AWS Credentials

1. Navigate to **"Secrets"** → **"Secrets"**
2. Click **"New Secret"**
3. Select **"Secret Text"**
4. Enter secret details:
   - **Name**: `aws-access-key-id`
   - **Value**: Your AWS access key ID
   - **Secret Manager**: Harness built-in secret manager
5. Click **"Save"**

### 6.2 Create Secret for AWS Secret Key

1. Click **"New Secret"**
2. Select **"Secret Text"**
3. Enter secret details:
   - **Name**: `aws-secret-access-key`
   - **Value**: Your AWS secret access key
   - **Secret Manager**: Harness built-in secret manager
5. Click **"Save"**

### 6.3 Create SSH Key Secret (Optional)

1. Click **"New Secret"**
2. Select **"SSH Key"**
3. Enter key details:
   - **Name**: `github-ssh-key`
   - **SSH Key File**: Paste your private SSH key
4. Click **"Save"**

## Step 7: Install Harness Delegate

### 7.1 Create Delegate

1. Navigate to **"Project Setup"** → **"Delegates"**
2. Click **"New Delegate"**
3. Select **"Kubernetes"** or **"Docker"** based on your setup
4. For this workshop, we'll use **"Docker"** (simpler)

### 7.2 Docker Delegate Installation

1. Select **"Docker"**
2. Enter delegate details:
   - **Name**: `workshop-delegate`
   - **Description**: `Delegate for workshop`
3. Copy the installation command provided
4. Run the command on your local machine or EC2 instance:

```bash
docker run --cpus=1 --memory=2g \
  -e DELEGATE_NAME=workshop-delegate \
  -e NEXT_GEN=true \
  -e DELEGATE_TYPE=DOCKER \
  -e ACCOUNT_ID=<YOUR_ACCOUNT_ID> \
  -e DELEGATE_TOKEN=<YOUR_DELEGATE_TOKEN> \
  -e MANAGER_HOST_AND_PORT=https://app.harness.io \
  -e POLL_FOR_TASKS=true \
  -e HELM_DESIRED_VERSION= \
  -e WATCHER_STORAGE_URL=https://app.harness.io/public/free/free-tier-watcher \
  -e WATCHER_CHECK_LOCATION=watcherci.txt \
  -e DELEGATE_STORAGE_URL=https://app.harness.io/public/free/free-tier-delegate \
  -e DELEGATE_CHECK_LOCATION=delegateci.txt \
  -e DEPLOY_MODE=KUBERNETES \
  -e PROXY_HOST= \
  -e PROXY_PORT= \
  -e PROXY_SCHEME= \
  -e PROXY_USER= \
  -e PROXY_PASSWORD= \
  -e NO_PROXY= \
  -e PROXY_MANAGER=true \
  -e INIT_SCRIPT= \
  harness/delegate:latest
```

### 7.3 Verify Delegate

1. Wait 2-3 minutes for delegate to register
2. Navigate to **"Delegates"** in Harness
3. Verify delegate status shows **"Connected"** (green)
4. Click on delegate name to see details
5. Verify it can connect to AWS

### 7.4 Delegate on AWS ECS (Alternative)

If you prefer to run delegate on AWS ECS:

1. Use the provided Terraform script in `infrastructure/delegate/`
2. Or follow the ECS delegate installation guide in Harness docs

## Step 8: Configure Environments

### 8.1 Create Development Environment

1. Navigate to **"Environments"**
2. Click **"New Environment"**
3. Enter environment details:
   - **Name**: `development`
   - **Type**: `Non-Production`
   - **Description**: `Development environment`
4. Click **"Save"**

### 8.2 Create Production Environment

1. Click **"New Environment"**
2. Enter environment details:
   - **Name**: `production`
   - **Type**: `Production`
   - **Description**: `Production environment`
3. Click **"Save"**

## Step 9: Verify Setup

### 9.1 Checklist

Verify all components are configured:

- [ ] Organization created
- [ ] Project created with required modules
- [ ] AWS connector configured and tested
- [ ] Git connector configured and tested
- [ ] Secrets created for credentials
- [ ] Delegate installed and connected
- [ ] Environments created

### 9.2 Test Connections

1. **Test AWS Connector**:
   - Navigate to connector
   - Click **"Test"**
   - Verify connection successful

2. **Test Git Connector**:
   - Navigate to connector
   - Click **"Test"**
   - Verify connection successful

3. **Test Delegate**:
   - Navigate to Delegates
   - Verify status is "Connected"
   - Check delegate logs for any errors

## Troubleshooting

### Delegate Not Connecting

**Issue**: Delegate shows as disconnected

**Solutions**:
- Check network connectivity
- Verify delegate token is correct
- Check firewall rules
- Review delegate logs: `docker logs <container-id>`

### Connector Test Failing

**Issue**: AWS or Git connector test fails

**Solutions**:
- Verify credentials are correct
- Check IAM permissions for AWS
- Verify GitHub token has correct scopes
- Check network connectivity

### Secrets Not Accessible

**Issue**: Secrets cannot be referenced in pipelines

**Solutions**:
- Verify secret is in same project/organization
- Check secret manager configuration
- Verify user has permissions to access secrets

## Next Steps

Congratulations! You've completed Module 1. You now have:
- ✅ Harness account configured
- ✅ Organization and project set up
- ✅ Connectors configured
- ✅ Delegate installed
- ✅ Environments created

**Proceed to [Module 2: Application Development](./module-2-application.md)** to build your application! 🚀

## Additional Resources

- [Harness Getting Started Guide](https://docs.harness.io/article/getting-started-with-harness)
- [Harness Delegate Installation](https://docs.harness.io/article/harness-delegate-overview)
- [Harness Connectors](https://docs.harness.io/article/cat8z3dk0s-connectors)
- [Harness Secrets Management](https://docs.harness.io/article/security/secrets-management/secrets-overview)

