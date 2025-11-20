# Module 6: Advanced Features

## Overview

In this module, you'll explore advanced Harness features including Feature Flags, GitOps, Cost Management, and Security Policies.

**Duration**: 90 minutes  
**Difficulty**: Advanced

## Learning Objectives

By the end of this module, you will:
- Implement Feature Flags for gradual rollouts
- Set up GitOps workflows
- Configure Cost Management
- Implement Security Policies
- Set up Pipeline Templates
- Use Harness API and CLI

## Prerequisites

- Completed Modules 1-5
- Understanding of basic Harness concepts
- Access to Harness advanced features

## Step 1: Feature Flags

### 1.1 Create Feature Flag

1. Navigate to **"Feature Flags"** module
2. Click **"New Feature Flag"**
3. Configure:
   - **Name**: `new-ui-feature`
   - **Identifier**: `new_ui_feature`
   - **Type**: `Boolean`
4. Click **"Create"**

### 1.2 Configure Targeting Rules

1. Set up targeting:
   - **Default Rule**: `false` (disabled)
   - **Targeting Rules**: Enable for specific users/environments
2. Configure percentage rollout:
   - Start with 10% of users
   - Gradually increase to 100%

### 1.3 Integrate in Application

```python
# Backend integration
from harness import FeatureFlagClient

client = FeatureFlagClient(api_key="your-api-key")
if client.is_enabled("new_ui_feature", user_id):
    # New feature code
    pass
```

## Step 2: GitOps

### 2.1 Set up GitOps Repository

1. Create GitOps repository structure:
   ```
   gitops/
   ├── environments/
   │   ├── dev/
   │   │   ├── backend.yaml
   │   │   └── frontend.yaml
   │   └── prod/
   │       ├── backend.yaml
   │       └── frontend.yaml
   └── applications/
       └── workshop-app.yaml
   ```

### 2.2 Configure GitOps in Harness

1. Navigate to **"GitOps"** module
2. Add GitOps repository
3. Configure sync policies
4. Set up auto-sync

## Step 3: Cost Management

### 3.1 Enable Cost Management

1. Navigate to **"Cloud Cost Management"**
2. Connect AWS account
3. Configure cost visibility
4. Set up budgets and alerts

### 3.2 Create Cost Budgets

1. Create budget for ECS services
2. Set up alerts at 50%, 80%, 100%
3. Configure notifications

## Step 4: Security Policies

### 4.1 Create Security Policy

1. Navigate to **"Security"** → **"Policies"**
2. Create new policy:
   - **Name**: `workshop-security-policy`
   - **Rules**: 
     - Require security scans
     - Block high-severity vulnerabilities
     - Require approvals for production

### 4.2 Apply Policy to Pipelines

1. Attach policy to pipelines
2. Configure enforcement
3. Test policy violations

## Step 5: Pipeline Templates

### 5.1 Create Template

1. Navigate to **"Templates"**
2. Create pipeline template
3. Define template variables
4. Save template

### 5.2 Use Template

1. Create new pipeline from template
2. Fill in template variables
3. Customize as needed

## Next Steps

Congratulations! You've completed Module 6. Explore more advanced features in Harness documentation.

**Proceed to [Module 7: Monitoring and Optimization](./module-7-monitoring.md)**! 🚀

