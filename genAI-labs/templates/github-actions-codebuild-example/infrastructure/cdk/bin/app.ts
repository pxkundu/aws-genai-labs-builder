#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { CodeBuildStack } from '../lib/codebuild-stack';

const app = new cdk.App();

// Get environment from context or default to 'development'
const environment = app.node.tryGetContext('environment') || 'development';

// Create the CodeBuild stack
new CodeBuildStack(app, `GitHubActionsCodeBuild-${environment}`, {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
  tags: {
    Environment: environment,
    Project: 'GitHubActionsCodeBuild',
    ManagedBy: 'CDK',
  },
});

// Add validation
app.node.addValidation({
  validate: () => {
    const errors: string[] = [];
    
    if (!process.env.CDK_DEFAULT_ACCOUNT) {
      errors.push('CDK_DEFAULT_ACCOUNT environment variable is required');
    }
    
    return errors;
  },
});
