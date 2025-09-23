#!/usr/bin/env python3
"""
AWS CDK App for GenAI Customer Service Infrastructure
"""

import os
import aws_cdk as cdk
from genai_customer_service_stack import GenaiCustomerServiceStack

app = cdk.App()

# Environment configuration
env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION', 'us-east-1')
)

# Create the main stack
GenaiCustomerServiceStack(
    app,
    "GenaiCustomerServiceStack",
    env=env,
    description="GenAI Customer Service Infrastructure"
)

app.synth()
