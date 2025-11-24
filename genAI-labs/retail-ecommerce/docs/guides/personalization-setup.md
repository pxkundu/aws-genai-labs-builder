# Personalization Engine Setup Guide

## Overview

This guide provides detailed instructions for setting up and configuring the AI-powered personalization engine for retail e-commerce applications. The personalization engine combines machine learning models with generative AI to deliver real-time, personalized product recommendations.

## Architecture

The personalization engine consists of:

1. **Event Ingestion**: Kinesis Data Streams for real-time user behavior events
2. **ML Models**: SageMaker endpoints for recommendation models
3. **GenAI Enhancement**: Bedrock for personalized content generation
4. **Caching Layer**: ElastiCache for low-latency responses
5. **API Layer**: Lambda functions and API Gateway for serving recommendations

## Prerequisites

- AWS Account with required services enabled
- Bedrock model access configured
- SageMaker endpoint deployed (or use pre-built models)
- DynamoDB tables created
- ElastiCache cluster configured

## Step 1: Deploy Infrastructure

### 1.1 Create Kinesis Data Stream

```bash
# Create Kinesis stream for user events
aws kinesis create-stream \
  --stream-name retail-user-events \
  --shard-count 2 \
  --region us-east-1

# Verify stream creation
aws kinesis describe-stream \
  --stream-name retail-user-events
```

### 1.2 Create ElastiCache Cluster

```bash
# Create ElastiCache subnet group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name retail-personalization-cache \
  --cache-subnet-group-description "Cache for personalization engine" \
  --subnet-ids subnet-12345 subnet-67890

# Create ElastiCache cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id retail-personalization-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --cache-subnet-group-name retail-personalization-cache
```

### 1.3 Create DynamoDB Tables

```bash
# User profiles table
aws dynamodb create-table \
  --table-name retail-user-profiles \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# User behavior table
aws dynamodb create-table \
  --table-name retail-user-behavior \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

## Step 2: Deploy Lambda Functions

### 2.1 Create Personalization Lambda

```bash
# Package Lambda function
cd backend/lambda/personalization-engine
zip -r personalization-engine.zip .

# Create Lambda function
aws lambda create-function \
  --function-name retail-personalization-engine \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.handler \
  --zip-file fileb://personalization-engine.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables={
    BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0,
    SAGEMAKER_ENDPOINT=retail-recommender-endpoint,
    CACHE_ENDPOINT=retail-personalization-cache.xxxxx.cache.amazonaws.com:6379
  }
```

### 2.2 Create Event Processor Lambda

```bash
# Package event processor
cd backend/lambda/event-processor
zip -r event-processor.zip .

# Create Lambda function
aws lambda create-function \
  --function-name retail-event-processor \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.handler \
  --zip-file fileb://event-processor.zip \
  --timeout 60 \
  --memory-size 256
```

### 2.3 Configure Kinesis Trigger

```bash
# Add Kinesis event source mapping
aws lambda create-event-source-mapping \
  --function-name retail-event-processor \
  --event-source-arn arn:aws:kinesis:us-east-1:ACCOUNT_ID:stream/retail-user-events \
  --starting-position LATEST \
  --batch-size 100
```

## Step 3: Configure SageMaker Endpoint

### 3.1 Deploy Recommendation Model

```python
# deploy_model.py
import boto3
import sagemaker
from sagemaker.model import Model
from sagemaker.predictor import Predictor

sagemaker_session = sagemaker.Session()
role = 'arn:aws:iam::ACCOUNT_ID:role/SageMakerExecutionRole'

# Load pre-trained model
model = Model(
    model_data='s3://retail-models/recommender/model.tar.gz',
    image_uri='your-ecr-repo/recommender:latest',
    role=role,
    sagemaker_session=sagemaker_session
)

# Deploy endpoint
predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    endpoint_name='retail-recommender-endpoint'
)
```

### 3.2 Test Endpoint

```python
# test_endpoint.py
import boto3

runtime = boto3.client('sagemaker-runtime')

response = runtime.invoke_endpoint(
    EndpointName='retail-recommender-endpoint',
    ContentType='application/json',
    Body=json.dumps({
        'user_id': 'test-user-1',
        'context': {'page_type': 'homepage'}
    })
)

print(response['Body'].read())
```

## Step 4: Implement Personalization Logic

### 4.1 Core Personalization Function

```python
# personalization_engine.py
import boto3
import json
import redis
from typing import Dict, List, Any

class PersonalizationEngine:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime')
        self.sagemaker = boto3.client('sagemaker-runtime')
        self.dynamodb = boto3.resource('dynamodb')
        self.redis = redis.Redis(
            host='retail-personalization-cache.xxxxx.cache.amazonaws.com',
            port=6379,
            decode_responses=True
        )
        
        self.user_profiles_table = self.dynamodb.Table('retail-user-profiles')
        self.products_table = self.dynamodb.Table('retail-products')
    
    def get_recommendations(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized recommendations for a user"""
        
        # Check cache first
        cache_key = f"recommendations:{user_id}:{context.get('page_type', 'homepage')}"
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Get user profile
        user_profile = self.get_user_profile(user_id)
        
        # Get ML recommendations
        ml_recommendations = self.get_ml_recommendations(user_id, context)
        
        # Enhance with GenAI
        enhanced_recommendations = self.enhance_with_genai(
            ml_recommendations, user_profile, context
        )
        
        # Cache results
        self.redis.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(enhanced_recommendations)
        )
        
        return enhanced_recommendations
    
    def get_ml_recommendations(self, user_id: str, context: Dict) -> List[Dict]:
        """Get recommendations from SageMaker model"""
        
        payload = {
            'user_id': user_id,
            'context': context,
            'num_recommendations': 10
        }
        
        response = self.sagemaker.invoke_endpoint(
            EndpointName='retail-recommender-endpoint',
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        result = json.loads(response['Body'].read())
        return result.get('recommendations', [])
    
    def enhance_with_genai(self, recommendations: List[Dict], 
                          user_profile: Dict, context: Dict) -> List[Dict]:
        """Enhance recommendations with GenAI-generated content"""
        
        enhanced = []
        
        for rec in recommendations:
            # Generate personalized description
            prompt = f"""
            Create a personalized product description for this customer:
            
            Customer Profile:
            - Age: {user_profile.get('age_group', 'unknown')}
            - Interests: {', '.join(user_profile.get('interests', []))}
            - Purchase History: {user_profile.get('purchase_categories', [])}
            
            Product: {rec['name']}
            Category: {rec['category']}
            Price: ${rec['price']}
            
            Create a compelling, personalized description (under 100 words).
            """
            
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 200,
                    'messages': [{'role': 'user', 'content': prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            rec['personalized_description'] = result['content'][0]['text']
            enhanced.append(rec)
        
        return enhanced
```

## Step 5: Configure API Gateway

### 5.1 Create API Gateway

```bash
# Create REST API
aws apigateway create-rest-api \
  --name retail-personalization-api \
  --description "Personalization API for retail e-commerce"

# Get API ID
API_ID=$(aws apigateway get-rest-apis \
  --query "items[?name=='retail-personalization-api'].id" \
  --output text)

# Create resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $(aws apigateway get-resources --rest-api-id $API_ID --query "items[0].id" --output text) \
  --path-part recommendations

# Create POST method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE
```

## Step 6: Testing

### 6.1 Test Personalization Engine

```python
# test_personalization.py
from personalization_engine import PersonalizationEngine

engine = PersonalizationEngine()

# Test recommendation generation
recommendations = engine.get_recommendations(
    user_id='test-user-1',
    context={'page_type': 'homepage', 'session_id': 'test-session-1'}
)

print(json.dumps(recommendations, indent=2))
```

### 6.2 Load Testing

```bash
# Run load test
npm run load-test -- \
  --target https://api.example.com/recommendations \
  --duration 60 \
  --rate 100
```

## Best Practices

1. **Caching Strategy**: Cache recommendations for 30-60 minutes
2. **Error Handling**: Implement fallback to non-personalized recommendations
3. **Performance**: Target < 100ms response time
4. **Monitoring**: Track recommendation quality and user engagement
5. **A/B Testing**: Test different personalization algorithms

## Troubleshooting

### High Latency

- Check ElastiCache connection
- Optimize SageMaker endpoint
- Review DynamoDB query patterns
- Enable CloudFront caching

### Low Recommendation Quality

- Review training data quality
- Tune ML model hyperparameters
- Improve user profile data collection
- Adjust GenAI prompts

## Next Steps

- Implement A/B testing framework
- Add real-time event processing
- Optimize caching strategy
- Deploy to production

---

**For more details, see the [Workshop Module 2](../workshop/module-2-personalization.md)**

