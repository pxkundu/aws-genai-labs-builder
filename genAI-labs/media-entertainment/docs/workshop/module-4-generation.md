# Module 4: Automated Content Generation

## Learning Objectives

By the end of this module, you will be able to:

- Generate marketing copy and social media content with Bedrock
- Create platform-specific content optimized for different channels
- Implement brand voice consistency across content
- Build content generation templates and workflows
- Automate multi-platform content distribution
- Track and optimize content performance

## Prerequisites

- Completed Module 3: Content Discovery & Search
- Access to Amazon Bedrock (Claude models)
- Access to Amazon Comprehend
- DynamoDB table for content storage
- Basic understanding of social media platforms

## Duration

**Estimated Time**: 90 minutes

## Step 1: Set Up Content Generation Service

### 1.1 Create Content Generator Lambda

```python
# lambda/content_generator.py
import json
import boto3
import os
from datetime import datetime

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Generate content for various platforms using Bedrock
    """
    content_type = event.get('content_type')  # social_post, blog, email, ad_copy
    platform = event.get('platform')  # twitter, instagram, facebook, linkedin, tiktok
    topic = event.get('topic', '')
    brand_voice = event.get('brand_voice', 'professional and friendly')
    tone = event.get('tone', 'neutral')
    length = event.get('length', 'medium')  # short, medium, long
    
    # Load platform-specific guidelines
    platform_guidelines = get_platform_guidelines(platform, content_type)
    
    prompt = f"""Generate {content_type} content for {platform} platform.

Topic: {topic}
Brand Voice: {brand_voice}
Tone: {tone}
Length: {length}

Platform Guidelines:
{platform_guidelines}

Requirements:
- Engaging and authentic
- Platform-optimized format
- Include relevant hashtags (if applicable)
- Call-to-action (if applicable)
- Comply with platform character limits

Generate the content in JSON format:
{{
  "content": "Generated content text",
  "hashtags": ["hashtag1", "hashtag2"],
  "call_to_action": "CTA text",
  "metadata": {{
    "word_count": 0,
    "character_count": 0,
    "estimated_engagement": "high/medium/low"
  }}
}}
"""
    
    # Call Bedrock
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 2000,
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
    )
    
    result = json.loads(response['body'].read())
    generated_text = result['content'][0]['text']
    
    # Parse JSON from response
    try:
        content_data = json.loads(generated_text)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        content_data = {
            'content': generated_text,
            'hashtags': [],
            'call_to_action': '',
            'metadata': {}
        }
    
    # Store in DynamoDB
    table = dynamodb.Table('generated-content')
    content_id = f"{content_type}-{platform}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    table.put_item(
        Item={
            'content_id': content_id,
            'content_type': content_type,
            'platform': platform,
            'topic': topic,
            'generated_content': content_data,
            'status': 'draft',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'brand_voice': brand_voice,
                'tone': tone,
                'length': length
            }
        }
    )
    
    return {
        'statusCode': 200,
        'content_id': content_id,
        'content': content_data
    }

def get_platform_guidelines(platform, content_type):
    """Get platform-specific content guidelines"""
    guidelines = {
        'twitter': {
            'social_post': 'Max 280 characters. Use concise language. Include 1-2 relevant hashtags. Thread for longer content.',
            'ad_copy': 'Max 280 characters. Clear value proposition. Strong CTA. Use Twitter Cards for rich media.'
        },
        'instagram': {
            'social_post': 'Max 2,200 characters for caption. Use 5-10 relevant hashtags. Include emojis. First line is critical (visible without "more").',
            'ad_copy': 'Visual-first. Compelling caption under 125 characters for preview. Include branded hashtags.'
        },
        'facebook': {
            'social_post': 'Optimal length 40-80 characters for engagement. Include questions to encourage comments. Use 1-2 hashtags.',
            'ad_copy': 'Headline max 40 characters. Primary text max 125 characters. Clear CTA button text.'
        },
        'linkedin': {
            'social_post': 'Professional tone. Optimal length 150-300 characters. Use 3-5 hashtags. Include industry insights.',
            'ad_copy': 'B2B focused. Value-driven messaging. Professional CTA. Include company credentials.'
        },
        'tiktok': {
            'social_post': 'Trending and authentic. Use popular hashtags (3-5). Keep it fun and engaging. Short sentences.',
            'ad_copy': 'Native to platform. Trend-aware. Include trending sounds/music references. Authentic voice.'
        }
    }
    
    return guidelines.get(platform, {}).get(content_type, 'Follow platform best practices.')
```

### 1.2 Deploy Content Generator

```bash
# Create deployment package
cd lambda
zip -r content_generator.zip content_generator.py

# Create Lambda function
aws lambda create-function \
  --function-name media-content-generator \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler content_generator.lambda_handler \
  --zip-file fileb://content_generator.zip \
  --timeout 60 \
  --memory-size 512 \
  --environment Variables="{AWS_REGION=us-east-1}"

# Create DynamoDB table
aws dynamodb create-table \
  --table-name generated-content \
  --attribute-definitions \
    AttributeName=content_id,AttributeType=S \
  --key-schema \
    AttributeName=content_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

## Step 2: Implement Brand Voice Analysis

### 2.1 Create Brand Voice Analyzer

```python
# lambda/brand_voice_analyzer.py
import json
import boto3
import os

comprehend = boto3.client('comprehend', region_name=os.environ['AWS_REGION'])
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    """
    Analyze and ensure brand voice consistency
    """
    content = event.get('content', '')
    reference_content = event.get('reference_content', [])  # Sample brand content
    
    # Analyze sentiment and tone
    sentiment_response = comprehend.detect_sentiment(
        Text=content,
        LanguageCode='en'
    )
    
    # Detect key phrases
    key_phrases_response = comprehend.detect_key_phrases(
        Text=content,
        LanguageCode='en'
    )
    
    # Use Bedrock to analyze brand voice alignment
    prompt = f"""Analyze if the following content aligns with the brand voice.

Generated Content:
{content}

Reference Brand Content (examples):
{json.dumps(reference_content, indent=2)}

Analyze:
1. Tone consistency (1-10 score)
2. Language style match (1-10 score)
3. Brand messaging alignment (1-10 score)
4. Suggested improvements

Return JSON:
{{
  "tone_score": 0,
  "style_score": 0,
  "messaging_score": 0,
  "overall_alignment": 0,
  "suggestions": ["suggestion1", "suggestion2"]
}}
"""
    
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 1000,
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
    )
    
    result = json.loads(response['body'].read())
    analysis_text = result['content'][0]['text']
    analysis = json.loads(analysis_text)
    
    return {
        'statusCode': 200,
        'sentiment': sentiment_response['Sentiment'],
        'sentiment_scores': sentiment_response['SentimentScore'],
        'key_phrases': [phrase['Text'] for phrase in key_phrases_response['KeyPhrases']],
        'brand_voice_analysis': analysis
    }
```

## Step 3: Create Multi-Platform Content Workflow

### 3.1 Step Functions Workflow

```json
{
  "Comment": "Multi-Platform Content Generation Workflow",
  "StartAt": "GenerateContent",
  "States": {
    "GenerateContent": {
      "Type": "Map",
      "ItemsPath": "$.platforms",
      "Iterator": {
        "StartAt": "GenerateForPlatform",
        "States": {
          "GenerateForPlatform": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "Parameters": {
              "FunctionName": "media-content-generator",
              "Payload": {
                "content_type.$": "$.content_type",
                "platform.$": "$",
                "topic.$": "$.topic",
                "brand_voice.$": "$.brand_voice",
                "tone.$": "$.tone"
              }
            },
            "ResultPath": "$.generated",
            "Next": "AnalyzeBrandVoice"
          },
          "AnalyzeBrandVoice": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "Parameters": {
              "FunctionName": "media-brand-voice-analyzer",
              "Payload": {
                "content.$": "$.generated.Payload.content.content",
                "reference_content.$": "$.reference_content"
              }
            },
            "ResultPath": "$.analysis",
            "Next": "CheckQuality"
          },
          "CheckQuality": {
            "Type": "Choice",
            "Choices": [
              {
                "Variable": "$.analysis.Payload.brand_voice_analysis.overall_alignment",
                "NumericGreaterThan": 7,
                "Next": "ApproveContent"
              }
            ],
            "Default": "RequestRevision"
          },
          "RequestRevision": {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "Parameters": {
              "FunctionName": "media-content-generator",
              "Payload": {
                "content_type.$": "$.content_type",
                "platform.$": "$",
                "topic.$": "$.topic",
                "brand_voice.$": "$.brand_voice",
                "tone.$": "$.tone",
                "revision_notes.$": "$.analysis.Payload.brand_voice_analysis.suggestions"
              }
            },
            "ResultPath": "$.revised",
            "Next": "ApproveContent"
          },
          "ApproveContent": {
            "Type": "Succeed"
          }
        }
      },
      "End": true
    }
  }
}
```

### 3.2 Deploy Workflow

```bash
# Create state machine
aws stepfunctions create-state-machine \
  --name multi-platform-content-generation \
  --definition file://workflows/multi-platform-content.json \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/StepFunctionsExecutionRole

# Test execution
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:multi-platform-content-generation \
  --input '{
    "topic": "New movie release announcement",
    "content_type": "social_post",
    "platforms": ["twitter", "instagram", "facebook", "linkedin"],
    "brand_voice": "cinematic and exciting",
    "tone": "enthusiastic",
    "reference_content": ["Sample brand post 1", "Sample brand post 2"]
  }'
```

## Step 4: Implement Content Templates

### 4.1 Template Management System

```python
# lambda/content_template_manager.py
import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])

def lambda_handler(event, context):
    """
    Manage content generation templates
    """
    action = event.get('action')  # create, get, update, delete
    template_id = event.get('template_id')
    
    table = dynamodb.Table('content-templates')
    
    if action == 'create':
        template = {
            'template_id': template_id,
            'name': event.get('name'),
            'description': event.get('description'),
            'content_type': event.get('content_type'),
            'platforms': event.get('platforms', []),
            'prompt_template': event.get('prompt_template'),
            'variables': event.get('variables', []),
            'brand_voice': event.get('brand_voice'),
            'created_at': event.get('created_at')
        }
        
        table.put_item(Item=template)
        return {'statusCode': 200, 'template_id': template_id}
    
    elif action == 'get':
        response = table.get_item(Key={'template_id': template_id})
        return {'statusCode': 200, 'template': response.get('Item')}
    
    elif action == 'use':
        # Use template to generate content
        template = table.get_item(Key={'template_id': template_id})['Item']
        variables = event.get('variables', {})
        
        # Fill template variables
        prompt = template['prompt_template']
        for var_name, var_value in variables.items():
            prompt = prompt.replace(f'{{{var_name}}}', str(var_value))
        
        # Generate content using template
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        generated_content = result['content'][0]['text']
        
        return {
            'statusCode': 200,
            'content': generated_content,
            'template_id': template_id
        }
    
    return {'statusCode': 400, 'message': 'Invalid action'}
```

### 4.2 Create Sample Templates

```python
# scripts/create_templates.py
import boto3
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('content-templates')

templates = [
    {
        'template_id': 'movie-release-announcement',
        'name': 'Movie Release Announcement',
        'description': 'Template for announcing new movie releases',
        'content_type': 'social_post',
        'platforms': ['twitter', 'instagram', 'facebook'],
        'prompt_template': """Create a {platform} post announcing a new movie release.

Movie Title: {movie_title}
Release Date: {release_date}
Genre: {genre}
Tagline: {tagline}

Make it exciting and engaging. Include relevant hashtags.""",
        'variables': ['movie_title', 'release_date', 'genre', 'tagline'],
        'brand_voice': 'cinematic and exciting'
    },
    {
        'template_id': 'episode-premiere',
        'name': 'TV Episode Premiere',
        'description': 'Template for TV show episode announcements',
        'content_type': 'social_post',
        'platforms': ['twitter', 'instagram'],
        'prompt_template': """Create a {platform} post for a TV episode premiere.

Show Name: {show_name}
Episode Number: {episode_number}
Episode Title: {episode_title}
Premiere Date: {premiere_date}
Streaming Platform: {platform_name}

Create anticipation and excitement.""",
        'variables': ['show_name', 'episode_number', 'episode_title', 'premiere_date', 'platform_name'],
        'brand_voice': 'engaging and dramatic'
    }
]

for template in templates:
    template['created_at'] = datetime.now().isoformat()
    table.put_item(Item=template)
    print(f"Created template: {template['template_id']}")
```

## Step 5: Implement Content Scheduling

### 5.1 Content Scheduler

```python
# lambda/content_scheduler.py
import json
import boto3
import os
from datetime import datetime, timedelta

eventbridge = boto3.client('events', region_name=os.environ['AWS_REGION'])
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Schedule content for publication
    """
    content_id = event.get('content_id')
    publish_time = event.get('publish_time')  # ISO format
    platform = event.get('platform')
    
    # Create EventBridge rule for scheduled publication
    rule_name = f"content-publish-{content_id}-{platform}"
    
    # Parse publish time
    publish_datetime = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
    
    # Create cron expression (simplified - use actual cron for complex schedules)
    cron_expression = f"cron({publish_datetime.minute} {publish_datetime.hour} {publish_datetime.day} {publish_datetime.month} ? {publish_datetime.year})"
    
    eventbridge.put_rule(
        Name=rule_name,
        ScheduleExpression=cron_expression,
        State='ENABLED',
        Description=f'Schedule content {content_id} for {platform}'
    )
    
    # Add Lambda target
    lambda_arn = os.environ['PUBLISH_LAMBDA_ARN']
    eventbridge.put_targets(
        Rule=rule_name,
        Targets=[{
            'Id': '1',
            'Arn': lambda_arn,
            'Input': json.dumps({
                'content_id': content_id,
                'platform': platform
            })
        }]
    )
    
    # Update content status
    table = dynamodb.Table('generated-content')
    table.update_item(
        Key={'content_id': content_id},
        UpdateExpression='SET #status = :status, publish_time = :publish_time',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'scheduled',
            ':publish_time': publish_time
        }
    )
    
    return {
        'statusCode': 200,
        'rule_name': rule_name,
        'publish_time': publish_time
    }
```

### 5.2 Content Publisher

```python
# lambda/content_publisher.py
import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
# In production, integrate with actual platform APIs (Twitter API, Instagram API, etc.)

def lambda_handler(event, context):
    """
    Publish content to platform
    """
    content_id = event.get('content_id')
    platform = event.get('platform')
    
    # Get content from DynamoDB
    table = dynamodb.Table('generated-content')
    content_item = table.get_item(Key={'content_id': content_id})['Item']
    
    generated_content = content_item['generated_content']
    content_text = generated_content['content']
    
    # Publish to platform (placeholder - integrate with actual APIs)
    publish_result = publish_to_platform(platform, content_text, generated_content)
    
    # Update status
    table.update_item(
        Key={'content_id': content_id},
        UpdateExpression='SET #status = :status, published_at = :published_at, platform_post_id = :post_id',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'published',
            ':published_at': datetime.now().isoformat(),
            ':post_id': publish_result.get('post_id', '')
        }
    )
    
    return {
        'statusCode': 200,
        'content_id': content_id,
        'platform': platform,
        'published': True
    }

def publish_to_platform(platform, content, metadata):
    """Publish content to platform (implement with actual APIs)"""
    # Placeholder - implement with Twitter API, Instagram API, Facebook API, etc.
    return {'post_id': f"{platform}-{datetime.now().timestamp()}"}
```

## Step 6: Test Content Generation

### 6.1 Test Single Platform Generation

```bash
# Test Twitter post generation
aws lambda invoke \
  --function-name media-content-generator \
  --payload '{
    "content_type": "social_post",
    "platform": "twitter",
    "topic": "New sci-fi series premiere",
    "brand_voice": "exciting and futuristic",
    "tone": "enthusiastic",
    "length": "short"
  }' \
  twitter_output.json

cat twitter_output.json
```

### 6.2 Test Multi-Platform Workflow

```bash
# Start multi-platform generation
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-1:ACCOUNT_ID:stateMachine:multi-platform-content-generation \
  --input file://test-multi-platform-input.json

# Check execution
aws stepfunctions describe-execution \
  --execution-arn <execution-arn>
```

### 6.3 Test Template Usage

```bash
# Use template to generate content
aws lambda invoke \
  --function-name media-content-template-manager \
  --payload '{
    "action": "use",
    "template_id": "movie-release-announcement",
    "variables": {
      "movie_title": "Space Odyssey 2024",
      "release_date": "December 15, 2024",
      "genre": "Science Fiction",
      "tagline": "Journey to the stars"
    }
  }' \
  template_output.json

cat template_output.json
```

## Best Practices

### Content Generation
- Use specific, detailed prompts for better results
- Include brand guidelines in prompts
- Test different tones and styles
- Validate content before publishing

### Brand Voice
- Maintain consistent brand voice across platforms
- Use reference content for alignment
- Regularly update brand voice guidelines
- Monitor content performance for voice effectiveness

### Multi-Platform
- Adapt content format for each platform
- Respect platform character limits
- Use platform-specific features (hashtags, mentions)
- Test content on each platform before scheduling

### Templates
- Create reusable templates for common content types
- Document template variables clearly
- Version control templates
- A/B test template variations

## Troubleshooting

### Common Issues

**Low Quality Content**
- Refine prompts with more specific instructions
- Provide better reference content
- Adjust model parameters (temperature, max_tokens)
- Use brand voice analysis for feedback

**Brand Voice Mismatch**
- Improve reference content quality
- Adjust brand voice analysis thresholds
- Implement revision workflows
- Train on successful content examples

**Platform Compliance**
- Verify character limits
- Check platform policy compliance
- Validate hashtags and mentions
- Test content formatting

## Next Steps

- **Module 5**: Implement audience intelligence and analytics
- **Enhancements**: Add image generation with Bedrock
- **Integration**: Connect to social media management tools
- **Optimization**: Implement content performance tracking

---

**Ready for Module 5? Continue with [Audience Intelligence](./module-5-audience-intel.md)!**

