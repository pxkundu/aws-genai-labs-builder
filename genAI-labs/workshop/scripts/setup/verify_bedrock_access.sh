#!/bin/bash
# Verify Amazon Bedrock access and Claude model availability

set -e

echo "🔍 Verifying Amazon Bedrock Access..."

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured"
    exit 1
fi

# Get AWS region
REGION=${AWS_REGION:-us-east-1}
echo "📍 AWS Region: $REGION"

# List Claude models
echo "📋 Checking Claude model availability..."
MODELS=$(aws bedrock list-foundation-models \
    --region $REGION \
    --query 'modelSummaries[?contains(modelId, `claude`)].{Name:modelName,ID:modelId}' \
    --output table)

if [ -z "$MODELS" ]; then
    echo "⚠️  No Claude models found. You may need to:"
    echo "   1. Request access to Claude models in Bedrock console"
    echo "   2. Check if Bedrock is available in your region"
    echo "   3. Verify IAM permissions"
    exit 1
else
    echo "✅ Available Claude models:"
    echo "$MODELS"
fi

# Test Bedrock access
echo "🧪 Testing Bedrock access..."
python3 << EOF
import boto3
import json
import os

bedrock = boto3.client('bedrock-runtime', region_name='$REGION')
model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'

try:
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 10,
            'messages': [{
                'role': 'user',
                'content': 'Say hello'
            }]
        })
    )
    result = json.loads(response['body'].read())
    print("✅ Bedrock access successful!")
    print(f"Response: {result['content'][0]['text']}")
except Exception as e:
    print(f"❌ Bedrock access failed: {str(e)}")
    exit(1)
EOF

echo ""
echo "✅ Bedrock access verified successfully!"

