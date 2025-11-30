# AI Content Studio Setup Guide

## Overview

This guide provides detailed instructions for setting up and configuring the AI Content Studio for media and entertainment applications. The Content Studio enables script-to-video workflows using Amazon Bedrock for script generation, Amazon Polly for voiceover synthesis, and AWS Elemental MediaConvert for video rendering.

## Architecture

The AI Content Studio consists of:

1. **Script Generation**: Bedrock-powered script creation from briefs
2. **Storyboard Generation**: Visual planning with AI assistance
3. **Voiceover Synthesis**: Polly neural voices for narration
4. **Video Processing**: MediaConvert for rendering and encoding
5. **Workflow Orchestration**: Step Functions for end-to-end automation
6. **API Layer**: Lambda functions and API Gateway for content creation requests

## Prerequisites

- AWS Account with required services enabled
- Bedrock model access configured (Claude 3.5 Sonnet)
- MediaConvert endpoint configured
- S3 buckets for raw, processed, and generated content
- IAM roles with appropriate permissions

## Step 1: Deploy Infrastructure

### 1.1 Create S3 Buckets

```bash
# Create buckets for content storage
aws s3 mb s3://media-dev-raw --region us-east-1
aws s3 mb s3://media-dev-processed --region us-east-1
aws s3 mb s3://media-dev-generated --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket media-dev-raw \
  --versioning-configuration Status=Enabled

# Set up lifecycle policies
aws s3api put-bucket-lifecycle-configuration \
  --bucket media-dev-raw \
  --lifecycle-configuration file://config/s3-lifecycle.json
```

### 1.2 Configure MediaConvert

```bash
# Get MediaConvert endpoint
aws mediaconvert describe-endpoints --region us-east-1

# Create IAM role for MediaConvert
aws iam create-role \
  --role-name MediaConvertServiceRole \
  --assume-role-policy-document file://config/mediaconvert-trust-policy.json

# Attach MediaConvert permissions
aws iam attach-role-policy \
  --role-name MediaConvertServiceRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### 1.3 Create DynamoDB Tables

```bash
# Content metadata table
aws dynamodb create-table \
  --table-name media-content-metadata \
  --attribute-definitions \
    AttributeName=content_id,AttributeType=S \
  --key-schema \
    AttributeName=content_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Script templates table
aws dynamodb create-table \
  --table-name media-script-templates \
  --attribute-definitions \
    AttributeName=template_id,AttributeType=S \
  --key-schema \
    AttributeName=template_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

## Step 2: Deploy Lambda Functions

### 2.1 Script Generator Lambda

```bash
# Package Lambda function
cd lambda/script_generator
zip -r script_generator.zip script_generator.py

# Create Lambda function
aws lambda create-function \
  --function-name media-script-generator \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler script_generator.lambda_handler \
  --zip-file fileb://script_generator.zip \
  --timeout 60 \
  --memory-size 512 \
  --environment Variables="{AWS_REGION=us-east-1}"

# Grant Bedrock permissions
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### 2.2 Storyboard Generator Lambda

```bash
# Package and deploy
cd lambda/storyboard_generator
zip -r storyboard_generator.zip storyboard_generator.py

aws lambda create-function \
  --function-name media-storyboard-generator \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler storyboard_generator.lambda_handler \
  --zip-file fileb://storyboard_generator.zip \
  --timeout 60 \
  --memory-size 512
```

### 2.3 Voiceover Synthesizer Lambda

```bash
# Package and deploy
cd lambda/voiceover_synthesizer
zip -r voiceover_synthesizer.zip voiceover_synthesizer.py

aws lambda create-function \
  --function-name media-voiceover-synthesizer \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler voiceover_synthesizer.lambda_handler \
  --zip-file fileb://voiceover_synthesizer.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{OUTPUT_BUCKET=media-dev-processed}"

# Grant Polly and S3 permissions
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonPollyFullAccess
```

### 2.4 MediaConvert Processor Lambda

```bash
# Package and deploy
cd lambda/mediaconvert_processor
zip -r mediaconvert_processor.zip mediaconvert_processor.py

aws lambda create-function \
  --function-name media-mediaconvert-processor \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler mediaconvert_processor.lambda_handler \
  --zip-file fileb://mediaconvert_processor.zip \
  --timeout 300 \
  --memory-size 256 \
  --environment Variables="{
    AWS_REGION=us-east-1,
    OUTPUT_BUCKET=media-dev-processed,
    MEDIACONVERT_ROLE_ARN=arn:aws:iam::ACCOUNT_ID:role/MediaConvertServiceRole
  }"
```

## Step 3: Create Step Functions Workflow

### 3.1 Define State Machine

```bash
# Create state machine
aws stepfunctions create-state-machine \
  --name ai-content-studio-workflow \
  --definition file://workflows/content-studio-state-machine.json \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/StepFunctionsExecutionRole

# Grant Step Functions permissions
aws iam attach-role-policy \
  --role-name StepFunctionsExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess
```

### 3.2 Test Workflow

```bash
# Start execution
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:ai-content-studio-workflow \
  --input '{
    "brief": "A 60-second promotional video for a new streaming service",
    "style": "energetic and modern",
    "duration": "60",
    "voice_id": "Joanna",
    "input_video": "s3://media-dev-raw/source-video.mp4",
    "output_prefix": "content-studio/output-001"
  }'

# Check execution status
aws stepfunctions describe-execution \
  --execution-arn <execution-arn>
```

## Step 4: Set Up API Gateway

### 4.1 Create API

```bash
# Create HTTP API
aws apigatewayv2 create-api \
  --name media-content-studio-api \
  --protocol-type HTTP \
  --cors-configuration AllowOrigins="*",AllowMethods="GET,POST,OPTIONS",AllowHeaders="content-type"

# Get API ID
API_ID=$(aws apigatewayv2 get-apis --query "Items[?Name=='media-content-studio-api'].ApiId" --output text)

# Create integration
aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:us-east-1:ACCOUNT_ID:function:media-content-studio-api-handler \
  --payload-format-version "2.0"

# Create route
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "POST /generate-content" \
  --target "integrations/$INTEGRATION_ID"
```

### 4.2 API Handler Lambda

```python
# lambda/api_handler.py
import json
import boto3
import os

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    """
    API handler for content studio requests
    """
    body = json.loads(event.get('body', '{}'))
    
    # Validate input
    required_fields = ['brief', 'style', 'duration']
    if not all(field in body for field in required_fields):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields'})
        }
    
    # Start Step Functions execution
    response = stepfunctions.start_execution(
        stateMachineArn=os.environ['STATE_MACHINE_ARN'],
        input=json.dumps(body)
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'execution_arn': response['executionArn'],
            'start_date': response['startDate'].isoformat()
        })
    }
```

## Step 5: Configure Polly Voices

### 5.1 List Available Voices

```bash
# List neural voices
aws polly describe-voices \
  --engine neural \
  --region us-east-1 \
  --query 'Voices[?Engine==`neural`].[Name,LanguageName,Gender]' \
  --output table
```

### 5.2 Test Voice Synthesis

```python
# test_polly.py
import boto3

polly = boto3.client('polly', region_name='us-east-1')

response = polly.synthesize_speech(
    Text='Welcome to our streaming service. Discover original content like never before.',
    OutputFormat='mp3',
    VoiceId='Joanna',
    Engine='neural'
)

# Save audio
with open('test_voiceover.mp3', 'wb') as f:
    f.write(response['AudioStream'].read())

print("Voiceover saved to test_voiceover.mp3")
```

## Step 6: Create MediaConvert Job Templates

### 6.1 Create Job Template

```python
# scripts/create_mediaconvert_template.py
import boto3
import json

mediaconvert = boto3.client('mediaconvert', region_name='us-east-1')

# Get endpoint
response = mediaconvert.describe_endpoints()
endpoint = response['Endpoints'][0]['Url']
mediaconvert = boto3.client('mediaconvert', endpoint_url=endpoint, region_name='us-east-1')

template = {
    'Name': 'ai-content-studio-template',
    'Description': 'Template for AI-generated content rendering',
    'Settings': {
        'Inputs': [
            {
                'VideoSelector': {},
                'AudioSelectors': {
                    'Audio Selector 1': {
                        'DefaultSelection': 'DEFAULT'
                    }
                }
            }
        ],
        'OutputGroups': [
            {
                'Name': 'HLS',
                'OutputGroupSettings': {
                    'Type': 'HLS_GROUP_SETTINGS',
                    'HlsGroupSettings': {
                        'Destination': 's3://media-dev-processed/hls/',
                        'SegmentLength': 10
                    }
                },
                'Outputs': [
                    {
                        'VideoDescription': {
                            'CodecSettings': {
                                'Codec': 'H_264',
                                'H264Settings': {
                                    'Bitrate': 5000000,
                                    'MaxBitrate': 6000000,
                                    'RateControlMode': 'QVBR'
                                }
                            }
                        },
                        'AudioDescriptions': [
                            {
                                'CodecSettings': {
                                    'Codec': 'AAC',
                                    'AacSettings': {
                                        'Bitrate': 192000
                                    }
                                }
                            }
                        ],
                        'ContainerSettings': {
                            'Container': 'M3U8'
                        }
                    }
                ]
            }
        ]
    }
}

response = mediaconvert.create_job_template(**template)
print(f"Template created: {response['JobTemplate']['Arn']}")
```

## Step 7: Testing and Validation

### 7.1 Test Script Generation

```bash
# Test script generation
aws lambda invoke \
  --function-name media-script-generator \
  --payload '{
    "brief": "A 30-second ad for a new movie release",
    "style": "cinematic",
    "duration": "30"
  }' \
  script_output.json

cat script_output.json | jq '.script'
```

### 7.2 Test Voiceover Synthesis

```bash
# Test voiceover
aws lambda invoke \
  --function-name media-voiceover-synthesizer \
  --payload '{
    "script": {
      "scenes": [
        {
          "scene_number": 1,
          "dialogue": "Welcome to our streaming service.",
          "duration_seconds": 5
        }
      ]
    },
    "voice_id": "Joanna"
  }' \
  voiceover_output.json
```

### 7.3 Test Complete Workflow

```bash
# Test via API
curl -X POST https://$API_ID.execute-api.us-east-1.amazonaws.com/generate-content \
  -H "Content-Type: application/json" \
  -d '{
    "brief": "A 60-second promotional video",
    "style": "energetic",
    "duration": "60",
    "voice_id": "Joanna"
  }'
```

## Best Practices

### Script Generation
- Use detailed, specific briefs for better results
- Include brand voice guidelines in prompts
- Validate script structure before proceeding
- Store scripts in DynamoDB for reuse and versioning

### Voiceover Synthesis
- Use neural voices for better quality
- Match voice characteristics to content style
- Cache frequently used voiceovers in S3
- Test different voices for A/B testing

### MediaConvert
- Use job templates for consistency
- Monitor job costs and optimize settings
- Implement retry logic for failed jobs
- Store job metadata for tracking and analytics

### Workflow Orchestration
- Add error handling and retries
- Implement parallel processing where possible
- Add notifications for job completion
- Log all workflow steps for debugging

### Cost Optimization
- Use appropriate MediaConvert presets
- Cache generated content in S3
- Implement request throttling
- Monitor Bedrock and MediaConvert usage

## Troubleshooting

### Common Issues

**Bedrock Access Denied**
- Verify model access in Bedrock console
- Check IAM permissions for Lambda role
- Ensure correct region configuration

**Polly Synthesis Fails**
- Verify voice ID is available in your region
- Check S3 bucket permissions for output
- Verify neural engine is available

**MediaConvert Job Fails**
- Verify input file exists and is accessible
- Check IAM role has MediaConvert permissions
- Review job settings for compatibility
- Check MediaConvert service quotas

**Step Functions Timeout**
- Increase Lambda timeout values
- Add wait states for long-running jobs
- Monitor execution duration
- Consider using Express Workflows for faster execution

**API Gateway Errors**
- Check Lambda function permissions
- Verify CORS configuration
- Review API Gateway logs
- Check request size limits

## Next Steps

- **Content Discovery**: Implement semantic and visual search
- **Content Generation**: Add automated marketing content creation
- **Audience Intelligence**: Build analytics and insights
- **Optimization**: Fine-tune prompts and workflows based on usage

---

For more information, see the [Content Studio Workshop Module](../workshop/module-2-content-studio.md).

