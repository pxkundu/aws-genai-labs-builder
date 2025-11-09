"""Utilities for interacting with Amazon Bedrock (Claude) for log analytics."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import boto3

BEDROCK_REGION = os.getenv("BEDROCK_REGION", os.getenv("AWS_REGION", "us-east-1"))
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")


def get_bedrock_client() -> boto3.client:
    return boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def analyze_logs(prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
    client = get_bedrock_client()
    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "temperature": 0.4,
                "messages": [
                    {"role": "system", "content": context.get("system_prompt", "You are an SRE assistant.")},
                    {"role": "user", "content": prompt},
                ],
            }
        ),
    )
    payload = response["body"].read().decode("utf-8")
    return json.loads(payload)
