#!/usr/bin/env python3
"""
AWS CDK App for Claude Code Workshop
Main entry point for CDK deployment
"""

import aws_cdk as cdk
from claude_code_stack import ClaudeCodeStack


app = cdk.App()

# Create Claude Code Workshop Stack
ClaudeCodeStack(
    app,
    "ClaudeCodeWorkshopStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account") or None,
        region=app.node.try_get_context("region") or "us-east-1"
    ),
    description="Claude Code on AWS Workshop Infrastructure"
)

app.synth()

