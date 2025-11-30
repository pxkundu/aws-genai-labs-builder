# Module 2: AI Content Studio

## Learning Objectives

By the end of this module, you will be able to:

- Build script-to-video workflows using Amazon Bedrock
- Generate storyboards and scripts with GenAI
- Synthesize voiceovers with Amazon Polly
- Process and render videos with MediaConvert
- Orchestrate content creation workflows with Step Functions
- Manage AI templates for content teams

## Prerequisites

- Completed Module 1: Environment & Content Pipeline Setup
- S3 buckets configured for raw, processed, and generated content
- MediaConvert endpoint configured
- Access to Amazon Bedrock with Claude models
- Access to Amazon Polly
- Access to AWS Step Functions

## Duration

**Estimated Time**: 120 minutes

## Step 1: Set Up Bedrock Script Generation

### 1.1 Create Script Generation Lambda

```python
# lambda/script_generator.py
import json
import boto3
import os

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    """
    Generate script from brief using Bedrock
    """
    brief = event.get('brief', '')
    style = event.get('style', 'professional')
    duration = event.get('duration', '60')  # seconds
    
    prompt = f"""Create a video script based on the following brief:

Brief: {brief}
Style: {style}
Duration: {duration} seconds

The script should include:
1. Scene descriptions
2. Dialogue/narration
3. Visual cues
4. Timing information

Format the output as JSON with the following structure:
{{
  "title": "Script title",
  "scenes": [
    {{
      "scene_number": 1,
      "description": "Scene description",
      "dialogue": "Dialogue or narration",
      "visual_cues": ["cue1", "cue2"],
      "duration_seconds": 10
    }}
  ],
  "total_duration": {duration}
}}
"""
    
    # Call Bedrock
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 4000,
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
    )
    
    result = json.loads(response['body'].read())
    script_content = result['content'][0]['text']
    
    # Parse JSON from response
    script_json = json.loads(script_content)
    
    return {
        'statusCode': 200,
        'script': script_json,
        'raw_response': script_content
    }
```

### 1.2 Deploy Script Generator Lambda

```bash
# Create deployment package
cd lambda
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

### 1.3 Test Script Generation

```python
# test_script_generation.py
import boto3
import json

lambda_client = boto3.client('lambda')

test_event = {
    'brief': 'A 60-second promotional video for a new streaming service highlighting original content, exclusive shows, and family-friendly entertainment.',
    'style': 'energetic and modern',
    'duration': '60'
}

response = lambda_client.invoke(
    FunctionName='media-script-generator',
    Payload=json.dumps(test_event)
)

result = json.loads(response['Payload'].read())
print(json.dumps(result['script'], indent=2))
```

## Step 2: Implement Storyboard Generation

### 2.1 Create Storyboard Generator

```python
# lambda/storyboard_generator.py
import json
import boto3
import os

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    """
    Generate storyboard from script
    """
    script = event.get('script', {})
    
    prompt = f"""Create a detailed storyboard from this video script:

{json.dumps(script, indent=2)}

For each scene, provide:
1. Visual description
2. Camera angles and movements
3. Lighting and mood
4. Props and set requirements
5. Character positions

Format as JSON:
{{
  "storyboard": [
    {{
      "scene_number": 1,
      "visual_description": "...",
      "camera_angle": "...",
      "lighting": "...",
      "props": ["..."],
      "characters": ["..."]
    }}
  ]
}}
"""
    
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 4000,
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
    )
    
    result = json.loads(response['body'].read())
    storyboard_content = result['content'][0]['text']
    storyboard_json = json.loads(storyboard_content)
    
    return {
        'statusCode': 200,
        'storyboard': storyboard_json
    }
```

## Step 3: Set Up Polly Voiceover Synthesis

### 3.1 Create Voiceover Lambda

```python
# lambda/voiceover_synthesizer.py
import json
import boto3
import os

polly = boto3.client('polly', region_name=os.environ['AWS_REGION'])
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Synthesize voiceover from script dialogue
    """
    script = event.get('script', {})
    voice_id = event.get('voice_id', 'Joanna')  # Default voice
    output_bucket = os.environ['OUTPUT_BUCKET']
    
    audio_files = []
    
    for scene in script.get('scenes', []):
        dialogue = scene.get('dialogue', '')
        if not dialogue:
            continue
        
        scene_num = scene.get('scene_number', 0)
        
        # Synthesize speech
        response = polly.synthesize_speech(
            Text=dialogue,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine='neural'  # Use neural engine for better quality
        )
        
        # Save to S3
        audio_key = f'voiceovers/scene_{scene_num:03d}.mp3'
        s3.put_object(
            Bucket=output_bucket,
            Key=audio_key,
            Body=response['AudioStream'].read(),
            ContentType='audio/mpeg'
        )
        
        audio_files.append({
            'scene_number': scene_num,
            's3_key': audio_key,
            'duration': scene.get('duration_seconds', 0)
        })
    
    return {
        'statusCode': 200,
        'audio_files': audio_files
    }
```

### 3.2 Test Voiceover Generation

```bash
# Test with sample script
aws lambda invoke \
  --function-name media-voiceover-synthesizer \
  --payload '{
    "script": {
      "scenes": [
        {
          "scene_number": 1,
          "dialogue": "Welcome to our streaming service. Discover original content like never before.",
          "duration_seconds": 5
        }
      ]
    },
    "voice_id": "Joanna"
  }' \
  response.json

cat response.json
```

## Step 4: Configure MediaConvert for Video Rendering

### 4.1 Create MediaConvert Job Template

```python
# scripts/create_mediaconvert_template.py
import boto3
import json

mediaconvert = boto3.client('mediaconvert', region_name='us-east-1')

# Get MediaConvert endpoint
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
                        'SegmentLength': 10,
                        'SegmentModifier': '$dt$'
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
                                    'RateControlMode': 'QVBR',
                                    'QualityTuningLevel': 'SINGLE_PASS_HQ'
                                }
                            }
                        },
                        'AudioDescriptions': [
                            {
                                'CodecSettings': {
                                    'Codec': 'AAC',
                                    'AacSettings': {
                                        'Bitrate': 192000,
                                        'CodecProfile': 'LC',
                                        'SampleRate': 48000
                                    }
                                }
                            }
                        ],
                        'ContainerSettings': {
                            'Container': 'M3U8'
                        }
                    }
                ]
            },
            {
                'Name': 'MP4',
                'OutputGroupSettings': {
                    'Type': 'FILE_GROUP_SETTINGS',
                    'FileGroupSettings': {
                        'Destination': 's3://media-dev-processed/mp4/'
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
                            'Container': 'MP4'
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

### 4.2 Create MediaConvert Job Lambda

```python
# lambda/mediaconvert_processor.py
import json
import boto3
import os
from datetime import datetime

mediaconvert = boto3.client('mediaconvert', region_name=os.environ['AWS_REGION'])
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Create MediaConvert job for video rendering
    """
    # Get MediaConvert endpoint
    endpoint_response = mediaconvert.describe_endpoints()
    endpoint = endpoint_response['Endpoints'][0]['Url']
    mediaconvert = boto3.client('mediaconvert', endpoint_url=endpoint, region_name=os.environ['AWS_REGION'])
    
    input_video = event.get('input_video_s3_path')
    output_prefix = event.get('output_prefix', f'jobs/{datetime.now().strftime("%Y%m%d-%H%M%S")}')
    template_name = event.get('template_name', 'ai-content-studio-template')
    
    job_settings = {
        'Role': os.environ['MEDIACONVERT_ROLE_ARN'],
        'Settings': {
            'Inputs': [
                {
                    'FileInput': input_video,
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
                            'Destination': f's3://{os.environ["OUTPUT_BUCKET"]}/{output_prefix}/hls/',
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
    
    response = mediaconvert.create_job(**job_settings)
    
    return {
        'statusCode': 200,
        'job_id': response['Job']['Id'],
        'job_arn': response['Job']['Arn'],
        'status': response['Job']['Status']
    }
```

## Step 5: Orchestrate Workflow with Step Functions

### 5.1 Create Step Functions State Machine

```json
{
  "Comment": "AI Content Studio Workflow",
  "StartAt": "GenerateScript",
  "States": {
    "GenerateScript": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "media-script-generator",
        "Payload": {
          "brief.$": "$.brief",
          "style.$": "$.style",
          "duration.$": "$.duration"
        }
      },
      "ResultPath": "$.script_result",
      "Next": "GenerateStoryboard"
    },
    "GenerateStoryboard": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "media-storyboard-generator",
        "Payload": {
          "script.$": "$.script_result.Payload.script"
        }
      },
      "ResultPath": "$.storyboard_result",
      "Next": "SynthesizeVoiceover"
    },
    "SynthesizeVoiceover": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "media-voiceover-synthesizer",
        "Payload": {
          "script.$": "$.script_result.Payload.script",
          "voice_id.$": "$.voice_id"
        }
      },
      "ResultPath": "$.voiceover_result",
      "Next": "ProcessVideo"
    },
    "ProcessVideo": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "media-mediaconvert-processor",
        "Payload": {
          "input_video_s3_path.$": "$.input_video",
          "output_prefix.$": "$.output_prefix",
          "audio_files.$": "$.voiceover_result.Payload.audio_files"
        }
      },
      "ResultPath": "$.video_result",
      "End": true
    }
  }
}
```

### 5.2 Deploy State Machine

```bash
# Create state machine
aws stepfunctions create-state-machine \
  --name ai-content-studio-workflow \
  --definition file://workflows/content-studio-state-machine.json \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/StepFunctionsExecutionRole

# Test execution
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
```

## Step 6: Create Content Studio API

### 6.1 API Gateway Integration

```python
# lambda/api_handler.py
import json
import boto3

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    """
    API handler for content studio requests
    """
    body = json.loads(event.get('body', '{}'))
    
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

## Step 7: Test Complete Workflow

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

cat script_output.json
```

### 7.2 Test Complete Pipeline

```bash
# Start full workflow
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:ai-content-studio-workflow \
  --input file://test-input.json

# Check execution status
aws stepfunctions describe-execution \
  --execution-arn <execution-arn>
```

## Best Practices

### Script Generation
- Use specific, detailed briefs for better results
- Include brand voice guidelines in prompts
- Validate script structure before proceeding
- Store scripts in DynamoDB for reuse

### Voiceover Synthesis
- Use neural voices for better quality
- Match voice characteristics to content style
- Test different voices for A/B testing
- Cache frequently used voiceovers

### MediaConvert
- Use job templates for consistency
- Monitor job costs and optimize settings
- Implement retry logic for failed jobs
- Store job metadata for tracking

### Workflow Orchestration
- Add error handling and retries
- Implement parallel processing where possible
- Add notifications for job completion
- Log all workflow steps for debugging

## Troubleshooting

### Common Issues

**Bedrock Access Denied**
- Verify model access in Bedrock console
- Check IAM permissions for Lambda role

**Polly Synthesis Fails**
- Verify voice ID is available in your region
- Check S3 bucket permissions for output

**MediaConvert Job Fails**
- Verify input file exists and is accessible
- Check IAM role has MediaConvert permissions
- Review job settings for compatibility

**Step Functions Timeout**
- Increase Lambda timeout values
- Add wait states for long-running jobs
- Monitor execution duration

## Next Steps

- **Module 3**: Implement content discovery and search
- **Enhancements**: Add image generation with Bedrock
- **Integration**: Connect to existing CMS or MAM systems
- **Optimization**: Implement caching for frequently used content

---

**Ready for Module 3? Continue with [Content Discovery & Search](./module-3-discovery.md)!**

