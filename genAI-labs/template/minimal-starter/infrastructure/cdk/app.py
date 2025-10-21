#!/usr/bin/env python3
import os
import aws_cdk as cdk
from genai_minimal_starter_stack import GenAIMinimalStarterStack

app = cdk.App()

# Get environment variables
account = os.getenv('CDK_DEFAULT_ACCOUNT')
region = os.getenv('CDK_DEFAULT_REGION', 'us-west-2')
environment = os.getenv('ENVIRONMENT', 'dev')

GenAIMinimalStarterStack(
    app, 
    f"GenAIMinimalStarter-{environment}",
    env=cdk.Environment(account=account, region=region),
    description="EKS cluster for GenAI Minimal Starter template"
)

app.synth()
